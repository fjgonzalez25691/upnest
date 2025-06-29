# UpNest AWS Infrastructure

This directory contains the organized AWS infrastructure for the UpNest baby tracking application.

## 📁 Directory Structure

```
aws/
├── infrastructure/           # Infrastructure as Code
│   ├── dynamodb/            # DynamoDB tables and scripts
│   │   ├── tables-schema.yaml        # Table definitions
│   │   ├── deploy-aws.ps1           # Deploy to AWS
│   │   ├── setup-local.ps1          # Setup DynamoDB Local
│   │   └── populate-test-data.ps1   # Load test data
│   ├── test-data/           # Test data files
│   └── api-gateway/         # API Gateway templates (Phase 5)
├── lambdas/                 # Lambda functions
├── tests/                   # Testing framework
│   ├── unit/               # Unit tests with mocks
│   ├── integration/        # Integration tests with local services
│   └── e2e/               # End-to-end tests with AWS
└── scripts/                # General AWS scripts
```

## 🚀 Quick Start for Integration Testing

### Prerequisites
- AWS CLI installed and configured
- SAM CLI installed
- Node.js (for DynamoDB Local)
- Python 3.11+ with pytest

### Run Complete Integration Tests

```powershell
# From upnest/aws directory
.\tests\integration\run-integration-tests.ps1
```

This will:
1. Start DynamoDB Local
2. Create all tables
3. Populate test data
4. Build Lambda functions
5. Start SAM Local API
6. Run all endpoint tests
7. Cleanup (optional)

### Manual Setup for Development

```powershell
# Setup DynamoDB Local
.\infrastructure\dynamodb\setup-local.ps1

# Populate with test data
.\infrastructure\dynamodb\populate-test-data.ps1

# Build and start SAM Local (in lambdas directory)
cd lambdas
sam build ; sam local start-api --port 3001 --env-vars env.json
```

### Run Only Tests (with services already running)

```powershell
# Skip setup and cleanup
.\tests\integration\run-integration-tests.ps1 -SkipSetup -SkipCleanup
```

## 🧪 Testing Levels

### 1. Unit Tests (`tests/unit/`)
- Test individual functions with mocks
- Fast execution, no external dependencies
- Run with: `python -m pytest tests/unit/ -v`

### 2. Integration Tests (`tests/integration/`)
- Test API endpoints with local services
- DynamoDB Local + SAM Local
- Real HTTP requests, real data flow
- Run with: `.\tests\integration\run-integration-tests.ps1`

### 3. E2E Tests (`tests/e2e/`) - Future
- Test against real AWS environment
- Real DynamoDB, API Gateway, Cognito
- Production-like testing

## 🔧 Configuration

### Environment Variables
- `API_BASE_URL`: SAM Local API endpoint (default: http://localhost:3001)
- `DYNAMODB_ENDPOINT`: DynamoDB Local endpoint (default: http://localhost:8000)

### Test JWT Tokens
Located in `tests/integration/test_endpoints.py`:
- `user1`: user-1-test-123456
- `user2`: user-2-test-789012  
- `admin`: admin-test-456789

## 📊 DynamoDB Local

### Tables Created:
- `upnest-users-local`
- `upnest-babies-local`
- `upnest-growth-data-local`
- `upnest-vaccinations-local`
- `upnest-milestones-local`

### Endpoints:
- DynamoDB Local: http://localhost:8000
- SAM Local API: http://localhost:3001

### Useful Commands:

```powershell
# List tables
aws dynamodb list-tables --endpoint-url http://localhost:8000

# Scan table
aws dynamodb scan --table-name upnest-users-local --endpoint-url http://localhost:8000

# Stop DynamoDB Local
Get-Process | Where-Object {$_.Name -like "*dynamodb*"} | Stop-Process -Force
```

## 🔍 Troubleshooting

### Common Issues:

1. **Port already in use**
   ```powershell
   # Kill processes using the ports
   Get-Process | Where-Object {$_.Name -like "*dynamodb*" -or $_.Name -like "*sam*"} | Stop-Process -Force
   ```

2. **DynamoDB tables not found**
   ```powershell
   # Re-run setup
   .\infrastructure\dynamodb\setup-local.ps1
   ```

3. **JWT tokens expired**
   - Update tokens in `test_endpoints.py`
   - Or regenerate using `lambdas/tests/jwt_generator.py`

4. **SAM build fails**
   ```powershell
   cd lambdas
   sam clean ; sam build
   ```

## 📈 Next Steps

1. **Phase 5**: API Gateway integration
2. **Phase 6**: AWS deployment and production testing
3. **Performance testing**: Load testing with realistic data
4. **Monitoring**: CloudWatch integration

## 🤝 Contributing

When adding new tests:
1. Unit tests go in `tests/unit/`
2. Integration tests go in `tests/integration/`
3. Update this README with new procedures
4. Ensure all tests pass before committing
