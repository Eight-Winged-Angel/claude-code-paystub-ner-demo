# -*- coding: utf-8 -*-
"""
Document AI Project Generator

Generates new projects based on a template structure for financial document processing.
Supports AWS CDK infrastructure with Lambda functions, layers, and web apps.

Usage:
    python generator.py --name MyProject --doc-type invoice --output ./output
    python generator.py --interactive
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re


# ============================================
# PROJECT CONFIGURATION SCHEMA
# ============================================

DEFAULT_CONFIG = {
    "project_name": "NewDocumentAI",
    "project_prefix": "SCCG",
    "document_type": "Invoice",
    "description": "Document AI processing solution",
    "aws_region": "us-east-1",
    "aws_account": "123456789012",

    # Tech stack options
    "stacks": {
        "infra": True,           # AWS CDK infrastructure
        "lambda_functions": True, # Lambda for document processing
        "lambda_layers": True,    # Python/Node layers
        "database": True,         # DynamoDB tables
        "s3_static": True,        # S3 static hosting
        "web_app": True,          # Frontend web application
    },

    # Document processing config
    "ai_services": {
        "textract": True,         # AWS Textract OCR
        "comprehend": False,      # AWS Comprehend NLP
        "bedrock": False,         # AWS Bedrock LLM
        "custom_model": False,    # Custom ML model
    },

    # Language preferences
    "infra_language": "typescript",  # typescript or python
    "lambda_language": "python",     # python or nodejs
    "web_framework": "react",        # react, vue, or angular

    # Compliance features (financial institution)
    "compliance": {
        "audit_logging": True,
        "encryption_at_rest": True,
        "vpc_isolation": True,
        "waf_protection": False,
    }
}


# ============================================
# TEMPLATE STRUCTURES
# ============================================

INFRA_STRUCTURE = {
    "bin": {
        "__files__": ["app.ts"]
    },
    "config": {
        "__files__": ["dev.json", "prod.json", "stage.json"]
    },
    "lib": {
        "__files__": [
            "main-stack.ts",
            "lambda-stack.ts",
            "database-stack.ts",
            "s3-stack.ts",
            "api-stack.ts"
        ]
    },
    "test": {
        "__files__": ["main-stack.test.ts"]
    },
    "__files__": [
        ".gitignore",
        ".npmignore",
        "cdk.json",
        "controller.json",
        "jest.config.js",
        "package.json",
        "README.md",
        "tsconfig.json"
    ]
}

SERVICE_STRUCTURE = {
    "database": {
        "__files__": ["schema.json", "migrations.sql"]
    },
    "lambda-functions": {
        "{DocumentType}Processor": {
            "__files__": [
                "handler.py",
                "processor.py",
                "requirements.txt",
                "README.md"
            ]
        }
    },
    "lambda-layers": {
        "{DocumentType}Layer": {
            "python": {
                "__files__": ["requirements.txt"]
            },
            "__files__": ["README.md"]
        }
    },
    "s3static": {
        "{ProjectName}": {
            "__files__": ["index.html", "config.json"]
        }
    },
    "web-app": {
        "src": {
            "components": {"__files__": []},
            "pages": {"__files__": []},
            "services": {"__files__": ["api.ts", "document.ts"]},
            "utils": {"__files__": ["helpers.ts"]},
            "__files__": ["App.tsx", "index.tsx"]
        },
        "public": {
            "__files__": ["index.html", "favicon.ico"]
        },
        "__files__": [
            "package.json",
            "tsconfig.json",
            "README.md",
            ".env.example"
        ]
    },
    "__files__": [
        ".gitkeep",
        ".gitignore",
        "pre-commit-config.yaml"
    ]
}


# ============================================
# FILE TEMPLATES
# ============================================

TEMPLATES = {}

TEMPLATES["cdk.json"] = '''{
  "app": "npx ts-node --prefer-ts-exts bin/app.ts",
  "context": {
    "@aws-cdk/aws-apigateway:usagePlanKeyOrderInsensitiveId": true,
    "@aws-cdk/core:stackRelativeExports": true,
    "@aws-cdk/aws-lambda:recognizeVersionProps": true,
    "@aws-cdk/aws-kms:defaultKeyPolicies": true
  }
}
'''

TEMPLATES["package.json_infra"] = '''{
  "name": "{{project_name_lower}}-infra",
  "version": "1.0.0",
  "description": "{{description}}",
  "scripts": {
    "build": "tsc",
    "watch": "tsc -w",
    "test": "jest",
    "cdk": "cdk",
    "deploy": "cdk deploy --all",
    "destroy": "cdk destroy --all"
  },
  "devDependencies": {
    "@types/jest": "^29.5.0",
    "@types/node": "^20.0.0",
    "aws-cdk": "^2.100.0",
    "jest": "^29.5.0",
    "ts-jest": "^29.1.0",
    "ts-node": "^10.9.0",
    "typescript": "^5.0.0"
  },
  "dependencies": {
    "aws-cdk-lib": "^2.100.0",
    "constructs": "^10.0.0"
  }
}
'''

TEMPLATES["tsconfig.json_infra"] = '''{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "declaration": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": false,
    "inlineSourceMap": true,
    "inlineSources": true,
    "experimentalDecorators": true,
    "strictPropertyInitialization": false,
    "typeRoots": ["./node_modules/@types"],
    "outDir": "dist"
  },
  "exclude": ["node_modules", "cdk.out"]
}
'''

TEMPLATES["app.ts"] = '''#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { {{ProjectName}}Stack } from '../lib/main-stack';

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT || '{{aws_account}}',
  region: process.env.CDK_DEFAULT_REGION || '{{aws_region}}'
};

new {{ProjectName}}Stack(app, '{{ProjectName}}Stack', {
  env,
  description: '{{description}}'
});

app.synth();
'''

TEMPLATES["main-stack.ts"] = '''import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';

export class {{ProjectName}}Stack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 Bucket for document uploads
    const documentBucket = new s3.Bucket(this, '{{ProjectName}}DocumentBucket', {
      bucketName: `{{project_name_lower}}-documents-${this.account}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // DynamoDB table for document metadata
    const documentTable = new dynamodb.Table(this, '{{ProjectName}}DocumentTable', {
      tableName: '{{project_name_lower}}-documents',
      partitionKey: { name: 'documentId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true
      }
    });

    // Lambda function for document processing
    const processorFunction = new lambda.Function(this, '{{ProjectName}}Processor', {
      functionName: '{{project_name_lower}}-processor',
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'handler.lambda_handler',
      code: lambda.Code.fromAsset('../service/lambda-functions/{{DocumentType}}Processor'),
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
'''

TEMPLATES["handler.py"] = '''"""
{{ProjectName}} Document Processor

Processes {{DocumentType}} documents using AWS Textract and custom extraction logic.
"""

import json
import boto3
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')

# Environment variables
DOCUMENT_BUCKET = os.environ.get('DOCUMENT_BUCKET')
DOCUMENT_TABLE = os.environ.get('DOCUMENT_TABLE')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for document processing.

    Args:
        event: S3 event or API Gateway event
        context: Lambda context

    Returns:
        Processing result
    """
    logger.info(f"Processing event: {json.dumps(event)}")

    try:
        # Extract document info from event
        document_key = extract_document_key(event)

        if not document_key:
            return error_response(400, "No document key found in event")

        # Process document with Textract
        extraction_result = process_document(document_key)

        # Store results
        document_id = store_results(document_key, extraction_result)

        return success_response({
            'documentId': document_id,
            'documentKey': document_key,
            'extractedFields': extraction_result.get('fields', {}),
            'confidence': extraction_result.get('confidence', 0.0)
        })

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return error_response(500, str(e))


def extract_document_key(event: Dict[str, Any]) -> Optional[str]:
    """Extract S3 document key from event."""
    # S3 event
    if 'Records' in event:
        for record in event['Records']:
            if record.get('eventSource') == 'aws:s3':
                return record['s3']['object']['key']

    # API Gateway event
    if 'body' in event:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        return body.get('documentKey')

    # Direct invocation
    return event.get('documentKey')


def process_document(document_key: str) -> Dict[str, Any]:
    """
    Process document using AWS Textract.

    Args:
        document_key: S3 object key

    Returns:
        Extraction results with fields and confidence
    """
    # Call Textract
    response = textract_client.analyze_document(
        Document={
            'S3Object': {
                'Bucket': DOCUMENT_BUCKET,
                'Name': document_key
            }
        },
        FeatureTypes=['FORMS', 'TABLES']
    )

    # Extract key-value pairs
    fields = {}
    total_confidence = 0.0
    field_count = 0

    key_map = {}
    value_map = {}
    block_map = {}

    for block in response['Blocks']:
        block_id = block['Id']
        block_map[block_id] = block

        if block['BlockType'] == 'KEY_VALUE_SET':
            if 'KEY' in block.get('EntityTypes', []):
                key_map[block_id] = block
            elif 'VALUE' in block.get('EntityTypes', []):
                value_map[block_id] = block

    # Match keys with values
    for key_id, key_block in key_map.items():
        key_text = get_text(key_block, block_map)

        for rel in key_block.get('Relationships', []):
            if rel['Type'] == 'VALUE':
                for value_id in rel['Ids']:
                    value_block = value_map.get(value_id, {})
                    value_text = get_text(value_block, block_map)

                    if key_text and value_text:
                        fields[key_text] = value_text
                        confidence = key_block.get('Confidence', 0) / 100
                        total_confidence += confidence
                        field_count += 1

    avg_confidence = total_confidence / field_count if field_count > 0 else 0.0

    return {
        'fields': fields,
        'confidence': round(avg_confidence, 4),
        'raw_blocks': len(response['Blocks'])
    }


def get_text(block: Dict[str, Any], block_map: Dict[str, Any]) -> str:
    """Extract text from a Textract block."""
    text = ''

    for rel in block.get('Relationships', []):
        if rel['Type'] == 'CHILD':
            for child_id in rel['Ids']:
                child_block = block_map.get(child_id, {})
                if child_block.get('BlockType') == 'WORD':
                    text += child_block.get('Text', '') + ' '

    return text.strip()


def store_results(document_key: str, extraction_result: Dict[str, Any]) -> str:
    """Store extraction results in DynamoDB."""
    table = dynamodb.Table(DOCUMENT_TABLE)

    document_id = document_key.replace('/', '-').replace('.', '-')
    timestamp = datetime.utcnow().isoformat()

    item = {
        'documentId': document_id,
        'timestamp': timestamp,
        'documentKey': document_key,
        'extractedFields': extraction_result.get('fields', {}),
        'confidence': str(extraction_result.get('confidence', 0.0)),
        'status': 'PROCESSED',
        'createdAt': timestamp
    }

    table.put_item(Item=item)

    return document_id


def success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a success response."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'data': data
        })
    }


def error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create an error response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': False,
            'error': message
        })
    }
'''

TEMPLATES["requirements.txt_lambda"] = '''boto3>=1.28.0
botocore>=1.31.0
python-dateutil>=2.8.2
'''

TEMPLATES["gitignore"] = '''# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Build outputs
dist/
build/
cdk.out/
*.js.map

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.env.local
*.env

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Test coverage
coverage/
.coverage
htmlcov/
'''

TEMPLATES["pre-commit-config.yaml"] = '''repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
'''

TEMPLATES["README.md_project"] = '''# {{ProjectName}} - Document AI Solution

{{description}}

## Project Structure

```
{{project_name}}/
├── infra/                    # AWS CDK Infrastructure
│   ├── bin/                  # CDK app entry point
│   ├── config/               # Environment configs
│   ├── lib/                  # CDK stack definitions
│   └── test/                 # Infrastructure tests
├── service/                  # Application services
│   ├── database/             # Database schemas
│   ├── lambda-functions/     # Lambda handlers
│   ├── lambda-layers/        # Shared Lambda layers
│   ├── s3static/             # Static web assets
│   └── web-app/              # Frontend application
└── README.md
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- AWS CLI configured
- AWS CDK CLI (`npm install -g aws-cdk`)

### Deploy Infrastructure

```bash
cd infra
npm install
cdk bootstrap  # First time only
cdk deploy --all
```

### Test Lambda Locally

```bash
cd service/lambda-functions/{{DocumentType}}Processor
pip install -r requirements.txt
python -c "from handler import lambda_handler; print(lambda_handler({'documentKey': 'test.pdf'}, None))"
```

## Architecture

- **Document Upload**: S3 bucket with encryption
- **Processing**: Lambda function with Textract integration
- **Storage**: DynamoDB for document metadata
- **Frontend**: React web application (optional)

## Configuration

Environment-specific configs are in `infra/config/`:

- `dev.json` - Development environment
- `stage.json` - Staging environment
- `prod.json` - Production environment

## Security

- All data encrypted at rest (S3, DynamoDB)
- VPC isolation (optional)
- IAM least-privilege access
- Audit logging enabled

---

Generated with Claude Code Project Generator
'''


# ============================================
# GENERATOR CLASS
# ============================================

class ProjectGenerator:
    """Generates Document AI projects from templates."""

    def __init__(self, config: Dict[str, Any]):
        self.config = {**DEFAULT_CONFIG, **config}
        self.project_name = self.config['project_name']
        self.project_prefix = self.config.get('project_prefix', 'SCCG')
        self.document_type = self.config.get('document_type', 'Document')
        self.output_dir = Path(self.config.get('output_dir', './output'))

    def generate(self) -> Path:
        """Generate the complete project structure."""
        # Create root directory
        full_project_name = f"{self.project_prefix}-{self.project_name}"
        project_root = self.output_dir / full_project_name

        if project_root.exists():
            shutil.rmtree(project_root)

        project_root.mkdir(parents=True, exist_ok=True)

        print(f"\nGenerating project: {full_project_name}")
        print(f"Output directory: {project_root}\n")

        # Generate infra directory
        if self.config['stacks'].get('infra', True):
            self._generate_infra(project_root / 'infra')

        # Generate service directory
        self._generate_service(project_root / 'service')

        # Generate root files
        self._create_file(project_root / 'README.md',
                         self._render_template(TEMPLATES['README.md_project']))
        self._create_file(project_root / '.gitignore',
                         TEMPLATES['gitignore'])

        # Generate config file
        config_path = project_root / 'project-config.json'
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

        print(f"\n{'='*50}")
        print(f"Project generated successfully!")
        print(f"Location: {project_root}")
        print(f"{'='*50}\n")

        return project_root

    def _generate_infra(self, infra_dir: Path):
        """Generate infrastructure directory."""
        print("Generating infra/...")
        infra_dir.mkdir(parents=True, exist_ok=True)

        # bin/
        bin_dir = infra_dir / 'bin'
        bin_dir.mkdir(exist_ok=True)
        self._create_file(bin_dir / 'app.ts',
                         self._render_template(TEMPLATES['app.ts']))

        # config/
        config_dir = infra_dir / 'config'
        config_dir.mkdir(exist_ok=True)
        for env in ['dev', 'stage', 'prod']:
            config = {
                'environment': env,
                'projectName': self.project_name,
                'awsRegion': self.config['aws_region']
            }
            self._create_file(config_dir / f'{env}.json', json.dumps(config, indent=2))

        # lib/
        lib_dir = infra_dir / 'lib'
        lib_dir.mkdir(exist_ok=True)
        self._create_file(lib_dir / 'main-stack.ts',
                         self._render_template(TEMPLATES['main-stack.ts']))

        # test/
        test_dir = infra_dir / 'test'
        test_dir.mkdir(exist_ok=True)
        self._create_file(test_dir / 'main-stack.test.ts',
                         f"// Tests for {self.project_name}Stack\n")

        # Root files
        self._create_file(infra_dir / 'cdk.json', TEMPLATES['cdk.json'])
        self._create_file(infra_dir / 'package.json',
                         self._render_template(TEMPLATES['package.json_infra']))
        self._create_file(infra_dir / 'tsconfig.json', TEMPLATES['tsconfig.json_infra'])
        self._create_file(infra_dir / '.gitignore', TEMPLATES['gitignore'])
        self._create_file(infra_dir / 'jest.config.js',
                         "module.exports = { preset: 'ts-jest', testEnvironment: 'node' };")
        self._create_file(infra_dir / 'controller.json', '{}')
        self._create_file(infra_dir / '.npmignore', '*.ts\n!*.d.ts\ncdk.out')
        self._create_file(infra_dir / 'README.md', f'# {self.project_name} Infrastructure\n')

    def _generate_service(self, service_dir: Path):
        """Generate service directory."""
        print("Generating service/...")
        service_dir.mkdir(parents=True, exist_ok=True)

        # database/
        if self.config['stacks'].get('database', True):
            db_dir = service_dir / 'database'
            db_dir.mkdir(exist_ok=True)
            self._create_file(db_dir / 'schema.json', '{}')
            self._create_file(db_dir / 'migrations.sql', '-- Database migrations\n')

        # lambda-functions/
        if self.config['stacks'].get('lambda_functions', True):
            lambda_dir = service_dir / 'lambda-functions' / f'{self.document_type}Processor'
            lambda_dir.mkdir(parents=True, exist_ok=True)
            self._create_file(lambda_dir / 'handler.py',
                             self._render_template(TEMPLATES['handler.py']))
            self._create_file(lambda_dir / 'requirements.txt',
                             TEMPLATES['requirements.txt_lambda'])
            self._create_file(lambda_dir / 'README.md',
                             f'# {self.document_type} Processor\n')

        # lambda-layers/
        if self.config['stacks'].get('lambda_layers', True):
            layer_dir = service_dir / 'lambda-layers' / f'{self.document_type}Layer' / 'python'
            layer_dir.mkdir(parents=True, exist_ok=True)
            self._create_file(layer_dir / 'requirements.txt',
                             TEMPLATES['requirements.txt_lambda'])
            self._create_file(layer_dir.parent / 'README.md',
                             f'# {self.document_type} Lambda Layer\n')

        # s3static/
        if self.config['stacks'].get('s3_static', True):
            static_dir = service_dir / 's3static' / self.project_name
            static_dir.mkdir(parents=True, exist_ok=True)
            self._create_file(static_dir / 'index.html',
                             f'<!DOCTYPE html><html><head><title>{self.project_name}</title></head><body></body></html>')
            self._create_file(static_dir / 'config.json', '{}')

        # web-app/
        if self.config['stacks'].get('web_app', True):
            self._generate_web_app(service_dir / 'web-app')

        # Root service files
        self._create_file(service_dir / '.gitkeep', '')
        self._create_file(service_dir / '.gitignore', TEMPLATES['gitignore'])
        self._create_file(service_dir / 'pre-commit-config.yaml',
                         TEMPLATES['pre-commit-config.yaml'])

    def _generate_web_app(self, web_dir: Path):
        """Generate web application structure."""
        print("Generating service/web-app/...")

        # src/
        src_dir = web_dir / 'src'
        for subdir in ['components', 'pages', 'services', 'utils']:
            (src_dir / subdir).mkdir(parents=True, exist_ok=True)

        self._create_file(src_dir / 'App.tsx', self._get_react_app())
        self._create_file(src_dir / 'index.tsx', self._get_react_index())
        self._create_file(src_dir / 'services' / 'api.ts', self._get_api_service())
        self._create_file(src_dir / 'services' / 'document.ts', self._get_document_service())
        self._create_file(src_dir / 'utils' / 'helpers.ts', '// Utility functions\n')

        # public/
        public_dir = web_dir / 'public'
        public_dir.mkdir(parents=True, exist_ok=True)
        self._create_file(public_dir / 'index.html', self._get_html_template())

        # Root web-app files
        self._create_file(web_dir / 'package.json', self._get_web_package_json())
        self._create_file(web_dir / 'tsconfig.json', self._get_web_tsconfig())
        self._create_file(web_dir / '.env.example', 'REACT_APP_API_URL=http://localhost:3001\n')
        self._create_file(web_dir / 'README.md', f'# {self.project_name} Web Application\n')

    def _render_template(self, template: str) -> str:
        """Render a template with project variables."""
        replacements = {
            '{{ProjectName}}': self.project_name,
            '{{project_name}}': self.project_name,
            '{{project_name_lower}}': self.project_name.lower().replace(' ', '-'),
            '{{DocumentType}}': self.document_type,
            '{{description}}': self.config.get('description', ''),
            '{{aws_region}}': self.config.get('aws_region', 'us-east-1'),
            '{{aws_account}}': self.config.get('aws_account', '123456789012'),
        }

        result = template
        for key, value in replacements.items():
            result = result.replace(key, value)

        return result

    def _create_file(self, path: Path, content: str):
        """Create a file with content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Created: {path.relative_to(self.output_dir)}")

    def _get_react_app(self) -> str:
        return f'''import React from 'react';

function App() {{
  return (
    <div className="App">
      <h1>{self.project_name}</h1>
      <p>Document AI Processing Solution</p>
    </div>
  );
}}

export default App;
'''

    def _get_react_index(self) -> str:
        return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''

    def _get_api_service(self) -> str:
        return '''const API_URL = process.env.REACT_APP_API_URL || '';

export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}
'''

    def _get_document_service(self) -> str:
        return '''import { apiRequest } from './api';

export interface DocumentResult {
  documentId: string;
  extractedFields: Record<string, string>;
  confidence: number;
}

export async function processDocument(file: File): Promise<DocumentResult> {
  const formData = new FormData();
  formData.append('document', file);

  return apiRequest<DocumentResult>('/process', {
    method: 'POST',
    body: formData,
  });
}

export async function getDocument(documentId: string): Promise<DocumentResult> {
  return apiRequest<DocumentResult>(`/documents/${documentId}`);
}
'''

    def _get_html_template(self) -> str:
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{self.project_name}</title>
</head>
<body>
  <noscript>You need to enable JavaScript to run this app.</noscript>
  <div id="root"></div>
</body>
</html>
'''

    def _get_web_package_json(self) -> str:
        return json.dumps({
            'name': f'{self.project_name.lower()}-web',
            'version': '1.0.0',
            'private': True,
            'dependencies': {
                'react': '^18.2.0',
                'react-dom': '^18.2.0',
                'react-scripts': '5.0.1',
                'typescript': '^5.0.0'
            },
            'scripts': {
                'start': 'react-scripts start',
                'build': 'react-scripts build',
                'test': 'react-scripts test',
                'eject': 'react-scripts eject'
            }
        }, indent=2)

    def _get_web_tsconfig(self) -> str:
        return json.dumps({
            'compilerOptions': {
                'target': 'es5',
                'lib': ['dom', 'dom.iterable', 'esnext'],
                'allowJs': True,
                'skipLibCheck': True,
                'esModuleInterop': True,
                'allowSyntheticDefaultImports': True,
                'strict': True,
                'forceConsistentCasingInFileNames': True,
                'noFallthroughCasesInSwitch': True,
                'module': 'esnext',
                'moduleResolution': 'node',
                'resolveJsonModule': True,
                'isolatedModules': True,
                'noEmit': True,
                'jsx': 'react-jsx'
            },
            'include': ['src']
        }, indent=2)


# ============================================
# CLI INTERFACE
# ============================================

def interactive_mode() -> Dict[str, Any]:
    """Run interactive configuration mode."""
    print("\n" + "="*50)
    print("Document AI Project Generator - Interactive Mode")
    print("="*50 + "\n")

    config = {}

    # Project name
    config['project_name'] = input("Project name [NewDocumentAI]: ").strip() or "NewDocumentAI"

    # Project prefix
    config['project_prefix'] = input("Project prefix [SCCG]: ").strip() or "SCCG"

    # Document type
    print("\nDocument types: Invoice, Paystub, Receipt, Contract, LoanApplication")
    config['document_type'] = input("Document type [Invoice]: ").strip() or "Invoice"

    # Description
    config['description'] = input("Description [Document AI processing solution]: ").strip() or "Document AI processing solution"

    # AWS region
    config['aws_region'] = input("AWS Region [us-east-1]: ").strip() or "us-east-1"

    # Stacks
    print("\nSelect stacks to include (y/n):")
    stacks = {}
    stacks['infra'] = input("  Infrastructure (CDK) [Y]: ").strip().lower() != 'n'
    stacks['lambda_functions'] = input("  Lambda Functions [Y]: ").strip().lower() != 'n'
    stacks['lambda_layers'] = input("  Lambda Layers [Y]: ").strip().lower() != 'n'
    stacks['database'] = input("  Database [Y]: ").strip().lower() != 'n'
    stacks['s3_static'] = input("  S3 Static [Y]: ").strip().lower() != 'n'
    stacks['web_app'] = input("  Web App [Y]: ").strip().lower() != 'n'
    config['stacks'] = stacks

    # Output directory
    config['output_dir'] = input("\nOutput directory [./output]: ").strip() or "./output"

    return config


def main():
    parser = argparse.ArgumentParser(
        description='Generate Document AI project from template',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python generator.py --interactive
  python generator.py --name PaystubProcessor --doc-type Paystub
  python generator.py --name InvoiceAI --doc-type Invoice --output ./projects
        '''
    )

    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--name', '-n', type=str,
                       help='Project name')
    parser.add_argument('--prefix', '-p', type=str, default='SCCG',
                       help='Project prefix (default: SCCG)')
    parser.add_argument('--doc-type', '-d', type=str, default='Invoice',
                       help='Document type (default: Invoice)')
    parser.add_argument('--description', type=str,
                       help='Project description')
    parser.add_argument('--output', '-o', type=str, default='./output',
                       help='Output directory (default: ./output)')
    parser.add_argument('--region', type=str, default='us-east-1',
                       help='AWS region (default: us-east-1)')
    parser.add_argument('--config', '-c', type=str,
                       help='Path to JSON config file')

    args = parser.parse_args()

    # Determine configuration source
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    elif args.interactive:
        config = interactive_mode()
    elif args.name:
        config = {
            'project_name': args.name,
            'project_prefix': args.prefix,
            'document_type': args.doc_type,
            'description': args.description or f'{args.doc_type} processing solution',
            'aws_region': args.region,
            'output_dir': args.output
        }
    else:
        parser.print_help()
        sys.exit(1)

    # Generate project
    generator = ProjectGenerator(config)
    project_path = generator.generate()

    print(f"\nNext steps:")
    print(f"  cd {project_path}/infra")
    print(f"  npm install")
    print(f"  cdk deploy --all")


if __name__ == '__main__':
    main()
