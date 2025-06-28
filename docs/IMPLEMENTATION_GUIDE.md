# 🚀 UpNest DynamoDB Implementation Guide

## Quick Start Implementation

### Step 1: Deploy DynamoDB Tables (5 minutes)

```bash
# PowerShell (Windows)
cd d:\proyectos\AWSLambdaHackathon\upnest
.\scripts\deploy-dynamodb.ps1 -Environment dev -Region us-east-1

# Bash (Mac/Linux)
chmod +x scripts/deploy-dynamodb.sh
./scripts/deploy-dynamodb.sh --environment dev --region us-east-1
```

### Step 2: Update Lambda Environment Variables

Add these environment variables to your Lambda functions:

```yaml
Environment:
  Variables:
    ENVIRONMENT: dev
    AWS_REGION: us-east-1
    UPNEST_USERS_TABLE: UpNest-Users-dev
    UPNEST_BABIES_TABLE: UpNest-Babies-dev
    UPNEST_GROWTH_DATA_TABLE: UpNest-GrowthData-dev
    UPNEST_VACCINATIONS_TABLE: UpNest-Vaccinations-dev
    UPNEST_MILESTONES_TABLE: UpNest-Milestones-dev
```

### Step 3: Update IAM Permissions

Add DynamoDB permissions to your Lambda execution role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:*:table/UpNest-*",
        "arn:aws:dynamodb:us-east-1:*:table/UpNest-*/index/*"
      ]
    }
  ]
}
```

## Integration Examples

### Frontend API Service Updates

Update your `babyApi.js` to use the new DynamoDB endpoints:

```javascript
// src/services/babyApi.js
import axiosClient from './axiosClient';

export const babyApi = {
  // Create a new baby
  async createBaby(babyData) {
    const response = await axiosClient.post('/babies', babyData);
    return response.data;
  },

  // Get all user's babies
  async getBabies() {
    const response = await axiosClient.get('/babies');
    return response.data.babies;
  },

  // Get specific baby
  async getBaby(babyId) {
    const response = await axiosClient.get(`/babies/${babyId}`);
    return response.data;
  },

  // Update baby
  async updateBaby(babyId, updateData) {
    const response = await axiosClient.put(`/babies/${babyId}`, updateData);
    return response.data;
  },

  // Delete baby
  async deleteBaby(babyId) {
    const response = await axiosClient.delete(`/babies/${babyId}`);
    return response.data;
  }
};

export const growthApi = {
  // Add growth measurement
  async addMeasurement(measurementData) {
    const response = await axiosClient.post('/growth-data', measurementData);
    return response.data;
  },

  // Get baby's growth data
  async getGrowthData(babyId, options = {}) {
    const params = new URLSearchParams(options);
    const response = await axiosClient.get(`/babies/${babyId}/growth-data?${params}`);
    return response.data.data;
  },

  // Get chart data
  async getChartData(babyId, types = ['weight', 'height']) {
    const response = await axiosClient.get(`/babies/${babyId}/growth-chart?types=${types.join(',')}`);
    return response.data;
  },

  // Update measurement
  async updateMeasurement(dataId, updateData) {
    const response = await axiosClient.put(`/growth-data/${dataId}`, updateData);
    return response.data;
  },

  // Delete measurement
  async deleteMeasurement(dataId) {
    const response = await axiosClient.delete(`/growth-data/${dataId}`);
    return response.data;
  }
};
```

### React Component Integration

Update your AddBaby component to handle the new API:

```javascript
// src/components/AddBabyForm.jsx - key changes
const handleSubmit = async (e) => {
  e.preventDefault();
  setIsLoading(true);
  setError('');

  try {
    // Create baby with DynamoDB
    const babyData = {
      name: formData.name,
      dateOfBirth: formData.dateOfBirth,
      gender: formData.gender,
      premature: formData.premature,
      gestationalWeek: formData.premature ? formData.gestationalWeek : null,
      birthWeight: formData.birthWeight ? parseFloat(formData.birthWeight) : null,
      birthHeight: formData.birthHeight ? parseFloat(formData.birthHeight) : null,
      medicalInfo: {
        allergies: [],
        conditions: [],
        medications: [],
        pediatrician: null
      }
    };

    const newBaby = await babyApi.createBaby(babyData);
    
    // Redirect to baby profile or dashboard
    navigate(`/baby/${newBaby.babyId}`, { 
      state: { message: 'Baby added successfully!' }
    });

  } catch (error) {
    console.error('Error creating baby:', error);
    setError(error.response?.data?.error || 'Failed to add baby. Please try again.');
  } finally {
    setIsLoading(false);
  }
};
```

### Growth Data Form Integration

```javascript
// src/components/GrowthDataForm.jsx - key changes
const handleSubmit = async (e) => {
  e.preventDefault();
  setIsLoading(true);
  setError('');

  try {
    const measurementData = {
      babyId: selectedBaby.babyId,
      measurementDate: formData.date,
      measurementType: formData.type, // 'weight', 'height', 'head_circumference'
      value: parseFloat(formData.value),
      unit: formData.unit,
      notes: formData.notes,
      measurementSource: 'manual'
    };

    // If percentile is available from the percentile API, include it
    if (formData.percentile) {
      measurementData.percentile = parseFloat(formData.percentile);
      measurementData.zscore = formData.zscore ? parseFloat(formData.zscore) : null;
    }

    const newMeasurement = await growthApi.addMeasurement(measurementData);
    
    // Update local state or refresh data
    onMeasurementAdded(newMeasurement);
    
    // Reset form
    setFormData({
      date: new Date().toISOString().split('T')[0],
      type: 'weight',
      value: '',
      unit: 'kg',
      notes: ''
    });

    setSuccess('Measurement added successfully!');

  } catch (error) {
    console.error('Error adding measurement:', error);
    setError(error.response?.data?.error || 'Failed to add measurement. Please try again.');
  } finally {
    setIsLoading(false);
  }
};
```

## Lambda Function Implementation

### Example: Baby CRUD Lambda

```javascript
// aws/lambdas/baby-crud/index.js
import { 
  createBabyHandler,
  getUserBabiesHandler,
  getBabyHandler,
  updateBabyHandler,
  deleteBabyHandler 
} from '../../services/babyService.js';

export const handler = async (event, context) => {
  const { httpMethod, pathParameters } = event;

  try {
    switch (httpMethod) {
      case 'POST':
        return await createBabyHandler(event, context);
      
      case 'GET':
        if (pathParameters?.babyId) {
          return await getBabyHandler(event, context);
        } else {
          return await getUserBabiesHandler(event, context);
        }
      
      case 'PUT':
        return await updateBabyHandler(event, context);
      
      case 'DELETE':
        return await deleteBabyHandler(event, context);
      
      default:
        return {
          statusCode: 405,
          body: JSON.stringify({ error: 'Method not allowed' })
        };
    }
  } catch (error) {
    console.error('Lambda error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal server error' })
    };
  }
};
```

### API Gateway Integration

```yaml
# template.yaml additions for API Gateway
Resources:
  BabyCrudFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: aws/lambdas/baby-crud/
      Handler: index.handler
      Runtime: nodejs18.x
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          UPNEST_BABIES_TABLE: !Ref BabiesTable
      Events:
        CreateBaby:
          Type: Api
          Properties:
            Path: /babies
            Method: post
            Auth:
              Authorizer: CognitoAuth
        
        GetBabies:
          Type: Api
          Properties:
            Path: /babies
            Method: get
            Auth:
              Authorizer: CognitoAuth
        
        GetBaby:
          Type: Api
          Properties:
            Path: /babies/{babyId}
            Method: get
            Auth:
              Authorizer: CognitoAuth
        
        UpdateBaby:
          Type: Api
          Properties:
            Path: /babies/{babyId}
            Method: put
            Auth:
              Authorizer: CognitoAuth
        
        DeleteBaby:
          Type: Api
          Properties:
            Path: /babies/{babyId}
            Method: delete
            Auth:
              Authorizer: CognitoAuth

  CognitoAuth:
    Type: AWS::ApiGateway::Authorizer
    Properties:
      Name: CognitoUserPoolAuthorizer
      Type: COGNITO_USER_POOLS
      IdentitySource: method.request.header.Authorization
      RestApiId: !Ref ServerlessRestApi
      ProviderARNs:
        - !GetAtt UserPool.Arn
```

## Testing Implementation

### Unit Tests Example

```javascript
// tests/babyService.test.js
import { babyService } from '../aws/services/babyService.js';

describe('BabyService', () => {
  test('should create a baby successfully', async () => {
    const babyData = {
      name: 'Test Baby',
      dateOfBirth: '2023-06-15',
      gender: 'female'
    };
    
    const userId = 'test-user-123';
    const baby = await babyService.createBaby(babyData, userId);
    
    expect(baby.babyId).toBeDefined();
    expect(baby.name).toBe('Test Baby');
    expect(baby.userId).toBe(userId);
    expect(baby.isActive).toBe(true);
  });

  test('should calculate baby age correctly', () => {
    const birthDate = '2023-06-15';
    const asOf = new Date('2024-01-15');
    
    const age = babyService.calculateAge(birthDate, asOf);
    
    expect(age.months).toBe(7);
    expect(age.formatted).toBe('7 months');
  });
});
```

### Integration Testing

```javascript
// tests/integration/api.test.js
import axios from 'axios';

const API_BASE = process.env.API_GATEWAY_URL || 'https://your-api-gateway-url.com/dev';

describe('API Integration Tests', () => {
  let authToken;
  let testBabyId;

  beforeAll(async () => {
    // Get auth token from Cognito
    authToken = await getTestAuthToken();
  });

  test('should create baby via API', async () => {
    const response = await axios.post(`${API_BASE}/babies`, {
      name: 'API Test Baby',
      dateOfBirth: '2023-06-15',
      gender: 'male'
    }, {
      headers: { Authorization: `Bearer ${authToken}` }
    });

    expect(response.status).toBe(200);
    expect(response.data.name).toBe('API Test Baby');
    testBabyId = response.data.babyId;
  });

  test('should retrieve babies via API', async () => {
    const response = await axios.get(`${API_BASE}/babies`, {
      headers: { Authorization: `Bearer ${authToken}` }
    });

    expect(response.status).toBe(200);
    expect(Array.isArray(response.data.babies)).toBe(true);
    expect(response.data.babies.length).toBeGreaterThan(0);
  });
});
```

## Monitoring and Troubleshooting

### CloudWatch Metrics to Monitor

1. **DynamoDB Metrics**:
   - `UserErrors` (should be 0)
   - `SystemErrors` (should be 0)
   - `ThrottledRequests` (should be 0)
   - `ConsumedReadCapacityUnits`
   - `ConsumedWriteCapacityUnits`

2. **Lambda Metrics**:
   - `Duration`
   - `Errors`
   - `Throttles`
   - `Invocations`

### Common Issues and Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Access Denied** | 403 errors in Lambda | Check IAM permissions for DynamoDB |
| **Table Not Found** | ResourceNotFoundException | Verify table names and environment variables |
| **Validation Errors** | 400 errors | Check required fields in request body |
| **Timeout Errors** | Lambda timeout | Optimize queries, add pagination |
| **High Costs** | Unexpected billing | Review query patterns, use filters |

### Debug Commands

```bash
# Check table status
aws dynamodb describe-table --table-name UpNest-Babies-dev

# View recent Lambda logs
aws logs filter-log-events --log-group-name /aws/lambda/your-function-name --start-time $(date -d '1 hour ago' +%s)000

# Test Lambda function locally
sam local invoke BabyCrudFunction -e events/create-baby.json

# Monitor DynamoDB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=UpNest-Babies-dev \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Sum
```

## Performance Optimization

### Query Optimization

1. **Use GSIs effectively**: Always query using GSIs when possible
2. **Add filter expressions**: Reduce data transfer with filters
3. **Implement pagination**: Use `Limit` and `ExclusiveStartKey`
4. **Avoid scans**: Always prefer queries over scans

### Cost Optimization

1. **Use PAY_PER_REQUEST**: For variable workloads
2. **Set up alarms**: Monitor costs with CloudWatch
3. **Optimize item sizes**: Keep items under 4KB when possible
4. **Archive old data**: Move old records to S3

## Next Steps After Implementation

1. **✅ Deploy tables**: Run deployment scripts
2. **✅ Update Lambda functions**: Use new service classes
3. **✅ Update frontend**: Connect to new APIs
4. **✅ Test thoroughly**: Run integration tests
5. **✅ Monitor performance**: Set up CloudWatch dashboards
6. **✅ Document APIs**: Update API documentation
7. **✅ Train team**: Share implementation guide

## Success Checklist

- [ ] All 5 DynamoDB tables deployed successfully
- [ ] Lambda functions using new service classes
- [ ] Frontend successfully creating and retrieving babies
- [ ] Growth data entry and visualization working
- [ ] User data isolation tested and confirmed
- [ ] Error handling implemented and tested
- [ ] Monitoring and alerts configured
- [ ] Performance benchmarks established
- [ ] Documentation updated and shared
- [ ] Team trained on new architecture

**Estimated Total Implementation Time**: 6-8 hours for complete backend integration
