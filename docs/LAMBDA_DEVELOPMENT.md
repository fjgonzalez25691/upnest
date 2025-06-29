# Lambda Development Configuration

## Environment Setup

### Prerequisites
- AWS CLI configured with `fran-dev` profile
- SAM CLI installed
- Docker running
- Python 3.11 environment

### Local Development Commands

```powershell
# Navigate to lambdas directory
cd upnest\aws\lambdas

# Build SAM application
sam build --profile fran-dev

# Validate template
sam validate --lint --profile fran-dev --region eu-south-2

# Test individual function locally
sam local invoke CreateBabyFunction --profile fran-dev --env-vars env.json --event test-event-create-baby.json

# Start local API server
sam local start-api --profile fran-dev --env-vars env.json --port 3001
```

### Environment Variables

Local environment variables are configured in:
- `aws/lambdas/.env.example` - Template with placeholder values
- `aws/lambdas/.env` - Actual values (not committed to git)
- `aws/lambdas/env.json` - JSON format for SAM CLI testing

### Test Events

Test events for local development:
- `test-event.json` - Basic GET request
- `test-event-no-auth.json` - Request without authorization
- `test-event-create-baby.json` - POST request to create baby

### Deployment

```powershell
# First time deployment (guided setup)
sam deploy --guided --profile fran-dev

# Subsequent deployments
sam deploy --profile fran-dev
```

### Project Structure

```
aws/
├── infrastructure/
│   └── dynamodb-tables.yaml        # DynamoDB CloudFormation
└── lambdas/
    ├── shared/                      # Common utilities
    ├── babies/                      # Baby CRUD operations
    ├── percentiles/                 # Percentile calculations
    ├── growth-data/                 # Future growth data operations
    ├── advanced/                    # Future advanced features
    └── template.yaml                # SAM template
```
