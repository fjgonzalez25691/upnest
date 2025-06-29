# Test environment configuration
import os

# Mock AWS region for testing
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_REGION'] = 'us-east-1'

# Mock DynamoDB table names for testing
os.environ['USERS_TABLE'] = 'test-users-table'
os.environ['BABIES_TABLE'] = 'test-babies-table'
os.environ['GROWTH_DATA_TABLE'] = 'test-growth-data-table'
os.environ['VACCINATIONS_TABLE'] = 'test-vaccinations-table'
os.environ['MILESTONES_TABLE'] = 'test-milestones-table'

# Mock Cognito configuration for testing
os.environ['COGNITO_USER_POOL_ID'] = 'us-east-1_test123456'
os.environ['COGNITO_CLIENT_ID'] = 'test-client-id'
os.environ['COGNITO_REGION'] = 'us-east-1'

# Enable testing mode
os.environ['TESTING_MODE'] = 'true'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-local-testing-only'

# Mock AWS credentials for testing (these won't be used for real AWS calls)
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
