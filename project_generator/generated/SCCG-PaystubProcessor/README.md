# PaystubProcessor - Document AI Solution

Paystub processing solution

## Project Structure

```
PaystubProcessor/
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
cd service/lambda-functions/PaystubProcessor
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
