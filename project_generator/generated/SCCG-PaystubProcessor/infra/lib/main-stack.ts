import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';

export class PaystubProcessorStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 Bucket for document uploads
    const documentBucket = new s3.Bucket(this, 'PaystubProcessorDocumentBucket', {
      bucketName: `paystubprocessor-documents-${this.account}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // DynamoDB table for document metadata
    const documentTable = new dynamodb.Table(this, 'PaystubProcessorDocumentTable', {
      tableName: 'paystubprocessor-documents',
      partitionKey: { name: 'documentId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true
      }
    });

    // Lambda function for document processing
    const processorFunction = new lambda.Function(this, 'PaystubProcessorProcessor', {
      functionName: 'paystubprocessor-processor',
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'handler.lambda_handler',
      code: lambda.Code.fromAsset('../service/lambda-functions/PaystubProcessor'),
      timeout: cdk.Duration.minutes(5),
      memorySize: 1024,
      environment: {
        DOCUMENT_BUCKET: documentBucket.bucketName,
        DOCUMENT_TABLE: documentTable.tableName,
      }
    });

    // Grant permissions
    documentBucket.grantReadWrite(processorFunction);
    documentTable.grantReadWriteData(processorFunction);

    // Add Textract permissions
    processorFunction.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        'textract:AnalyzeDocument',
        'textract:DetectDocumentText',
        'textract:AnalyzeExpense',
        'textract:StartDocumentAnalysis',
        'textract:GetDocumentAnalysis'
      ],
      resources: ['*']
    }));

    // Outputs
    new cdk.CfnOutput(this, 'DocumentBucketName', {
      value: documentBucket.bucketName,
      description: 'Document upload bucket'
    });

    new cdk.CfnOutput(this, 'ProcessorFunctionArn', {
      value: processorFunction.functionArn,
      description: 'Document processor Lambda ARN'
    });
  }
}
