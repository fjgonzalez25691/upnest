# DynamoDB Tables for Lambda Functions

## Environment: Development (dev)

### Table Names (for Lambda environment variables)
```javascript
const DYNAMODB_TABLES = {
  USERS: 'UpNest-Users-dev',
  BABIES: 'UpNest-Babies-dev',
  GROWTH_DATA: 'UpNest-GrowthData-dev',
  VACCINATIONS: 'UpNest-Vaccinations-dev',
  MILESTONES: 'UpNest-Milestones-dev'
};
```

### Table ARNs (for IAM policies)
```javascript
const DYNAMODB_TABLE_ARNS = {
  USERS: 'arn:aws:dynamodb:eu-south-2:568680248062:table/UpNest-Users-dev',
  BABIES: 'arn:aws:dynamodb:eu-south-2:568680248062:table/UpNest-Babies-dev',
  GROWTH_DATA: 'arn:aws:dynamodb:eu-south-2:568680248062:table/UpNest-GrowthData-dev',
  VACCINATIONS: 'arn:aws:dynamodb:eu-south-2:568680248062:table/UpNest-Vaccinations-dev',
  MILESTONES: 'arn:aws:dynamodb:eu-south-2:568680248062:table/UpNest-Milestones-dev'
};
```

### CloudFormation Template Usage
```yaml
# In Lambda function template (template.yaml)
Environment:
  Variables:
    USERS_TABLE: !ImportValue 'UpNest-DynamoDB-dev-UsersTable'
    BABIES_TABLE: !ImportValue 'UpNest-DynamoDB-dev-BabiesTable'
    GROWTH_DATA_TABLE: !ImportValue 'UpNest-DynamoDB-dev-GrowthDataTable'
    VACCINATIONS_TABLE: !ImportValue 'UpNest-DynamoDB-dev-VaccinationsTable'
    MILESTONES_TABLE: !ImportValue 'UpNest-DynamoDB-dev-MilestonesTable'

# IAM Policy for Lambda execution role
Policies:
  - DynamoDBCrudPolicy:
      TableName: !ImportValue 'UpNest-DynamoDB-dev-UsersTable'
  - DynamoDBCrudPolicy:
      TableName: !ImportValue 'UpNest-DynamoDB-dev-BabiesTable'
  - DynamoDBCrudPolicy:
      TableName: !ImportValue 'UpNest-DynamoDB-dev-GrowthDataTable'
  - DynamoDBCrudPolicy:
      TableName: !ImportValue 'UpNest-DynamoDB-dev-VaccinationsTable'
  - DynamoDBCrudPolicy:
      TableName: !ImportValue 'UpNest-DynamoDB-dev-MilestonesTable'
```

### Lambda Environment Variables Setup
```bash
# For local SAM testing (.env.local)
USERS_TABLE=UpNest-Users-dev
BABIES_TABLE=UpNest-Babies-dev
GROWTH_DATA_TABLE=UpNest-GrowthData-dev
VACCINATIONS_TABLE=UpNest-Vaccinations-dev
MILESTONES_TABLE=UpNest-Milestones-dev

# AWS Region
AWS_REGION=eu-south-2
AWS_PROFILE=fran-dev
```

### Node.js Lambda Code Usage
```javascript
// Import AWS SDK
const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, PutCommand, GetCommand, UpdateCommand, DeleteCommand } = require('@aws-sdk/lib-dynamodb');

// Initialize DynamoDB client
const client = new DynamoDBClient({ region: process.env.AWS_REGION || 'eu-south-2' });
const ddbDocClient = DynamoDBDocumentClient.from(client);

// Table names from environment variables
const TABLES = {
  USERS: process.env.USERS_TABLE,
  BABIES: process.env.BABIES_TABLE,
  GROWTH_DATA: process.env.GROWTH_DATA_TABLE,
  VACCINATIONS: process.env.VACCINATIONS_TABLE,
  MILESTONES: process.env.MILESTONES_TABLE
};

// Example usage
exports.handler = async (event) => {
  try {
    // Example: Get user from Users table
    const getUserParams = {
      TableName: TABLES.USERS,
      Key: { userId: event.userId }
    };
    
    const result = await ddbDocClient.send(new GetCommand(getUserParams));
    return {
      statusCode: 200,
      body: JSON.stringify(result.Item)
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal server error' })
    };
  }
};
```

### Global Secondary Indexes (GSI) for Queries
```javascript
// Available GSI names for each table
const GSI_NAMES = {
  USERS: ['EmailIndex'],
  BABIES: ['UserBabiesIndex', 'ActiveBabiesIndex'],
  GROWTH_DATA: ['BabyGrowthIndex', 'UserGrowthDataIndex', 'BabyMeasurementTypeIndex'],
  VACCINATIONS: ['BabyVaccinationsIndex', 'UserVaccinationsIndex', 'UpcomingVaccinationsIndex'],
  MILESTONES: ['BabyMilestonesIndex', 'UserMilestonesIndex', 'MilestoneTypeIndex']
};

// Example GSI query
const queryBabiesByUser = {
  TableName: TABLES.BABIES,
  IndexName: 'UserBabiesIndex',
  KeyConditionExpression: 'userId = :userId',
  ExpressionAttributeValues: {
    ':userId': userId
  }
};
```

### Next Steps for Lambda Integration
1. **Update existing Lambda template** (`aws/lambdas/percentile/template.yaml`)
2. **Add environment variables** using CloudFormation imports
3. **Update IAM policies** to include all table permissions
4. **Create new Lambda functions** for baby CRUD operations
5. **Test Lambda functions** with actual DynamoDB tables
