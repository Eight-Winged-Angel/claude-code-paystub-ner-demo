# Document AI Project Generator

Generates new Document AI projects with AWS CDK infrastructure for financial document processing.

## Features

- **Template-based generation**: Creates complete project structure
- **Customizable stacks**: Enable/disable infrastructure components
- **Multiple document types**: Invoice, Paystub, Receipt, Contract, etc.
- **AWS CDK ready**: Deploy with `cdk deploy`
- **Financial compliance**: Encryption, audit logging, VPC isolation

## Usage

### Interactive Mode

```bash
python generator.py --interactive
```

### Command Line

```bash
# Basic usage
python generator.py --name PaystubProcessor --doc-type Paystub

# Full options
python generator.py \
  --name InvoiceAI \
  --prefix SCCG \
  --doc-type Invoice \
  --description "Invoice processing solution" \
  --region us-east-1 \
  --output ./projects

# From config file
python generator.py --config project-config.json
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--interactive` | `-i` | Interactive mode | - |
| `--name` | `-n` | Project name | Required |
| `--prefix` | `-p` | Project prefix | SCCG |
| `--doc-type` | `-d` | Document type | Invoice |
| `--description` | - | Project description | Auto |
| `--output` | `-o` | Output directory | ./output |
| `--region` | - | AWS region | us-east-1 |
| `--config` | `-c` | Config JSON file | - |

## Generated Structure

```
SCCG-{ProjectName}/
├── infra/                          # AWS CDK Infrastructure
│   ├── bin/
│   │   └── app.ts                  # CDK entry point
│   ├── config/
│   │   ├── dev.json
│   │   ├── stage.json
│   │   └── prod.json
│   ├── lib/
│   │   └── main-stack.ts           # Main stack definition
│   ├── test/
│   ├── cdk.json
│   ├── package.json
│   └── tsconfig.json
├── service/
│   ├── database/
│   │   └── schema.json
│   ├── lambda-functions/
│   │   └── {DocType}Processor/
│   │       ├── handler.py          # Lambda handler
│   │       └── requirements.txt
│   ├── lambda-layers/
│   │   └── {DocType}Layer/
│   ├── s3static/
│   │   └── {ProjectName}/
│   └── web-app/
│       ├── src/
│       ├── public/
│       └── package.json
├── project-config.json             # Generation config
└── README.md
```

## Document Types

- `Invoice` - Business invoices
- `Paystub` - Employee pay stubs
- `Receipt` - Transaction receipts
- `Contract` - Legal contracts
- `LoanApplication` - Loan applications
- `TaxForm` - Tax documents

## Configuration File

```json
{
  "project_name": "PaystubProcessor",
  "project_prefix": "SCCG",
  "document_type": "Paystub",
  "description": "Paystub processing solution",
  "aws_region": "us-east-1",
  "stacks": {
    "infra": true,
    "lambda_functions": true,
    "lambda_layers": true,
    "database": true,
    "s3_static": true,
    "web_app": true
  },
  "ai_services": {
    "textract": true,
    "comprehend": false,
    "bedrock": false
  }
}
```

## Deploy Generated Project

```bash
cd SCCG-PaystubProcessor/infra
npm install
cdk bootstrap   # First time only
cdk deploy --all
```

## Architecture

The generated project includes:

1. **S3 Bucket** - Document upload with encryption
2. **Lambda Function** - Textract-based document processing
3. **DynamoDB Table** - Document metadata storage
4. **API Gateway** - REST API (optional)
5. **Web App** - React frontend (optional)

## Integration with Monorepo

To add generated projects to an existing monorepo:

```bash
# Generate project
python generator.py --name NewProject --output /path/to/monorepo/packages

# Or copy after generation
cp -r ./generated/SCCG-NewProject /path/to/monorepo/packages/
```

---

*Generated with Claude Code*
