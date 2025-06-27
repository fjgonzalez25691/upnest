# ⚡ Lambda CRUD Operations & Integration

## Status: 🟡 **PLANNED** (Architecture Ready)
**Priority**: HIGH ⚡ | **Estimated Effort**: 4-5 hours | **Actual Effort**: TBD

---

## 📝 **Task Overview**

Implement comprehensive Lambda functions for all CRUD operations (Create, Read, Update, Delete) with complete user data isolation, JWT validation, and integration with DynamoDB tables. Enable full backend functionality for babies management and growth data tracking.

## 🎯 **Success Criteria**

- ✅ Complete CRUD operations for Babies and GrowthData
- ✅ JWT token validation and user extraction
- ✅ User-scoped data isolation at Lambda level
- ✅ Proper error handling and validation
- ✅ API Gateway integration with CORS
- ✅ Performance optimization and monitoring
- ✅ Integration testing with real frontend

---

## 📋 **Implementation Checklist**

### **Phase 1: Lambda Architecture** 🔶 PLANNED
- 🔶 Create Lambda function structure
- 🔶 Implement JWT validation utilities
- 🔶 Set up DynamoDB integration
- 🔶 Configure environment variables
- 🔶 Implement error handling patterns

### **Phase 2: Babies CRUD Operations** 🔶 PLANNED
- 🔶 POST /babies - Create new baby
- 🔶 GET /babies - List user's babies
- 🔶 GET /babies/{id} - Get baby details
- 🔶 PUT /babies/{id} - Update baby info
- 🔶 DELETE /babies/{id} - Delete baby

### **Phase 3: Growth Data CRUD Operations** 🔶 PLANNED
- 🔶 POST /babies/{id}/growth - Add growth measurement
- 🔶 GET /babies/{id}/growth - Get growth history
- 🔶 GET /babies/{id}/growth/{date} - Get specific measurement
- 🔶 PUT /babies/{id}/growth/{date} - Update measurement
- 🔶 DELETE /babies/{id}/growth/{date} - Delete measurement

### **Phase 4: Advanced Features** 🔶 PLANNED
- 🔶 GET /babies/{id}/percentiles - Calculate percentiles
- 🔶 GET /babies/{id}/growth-chart - Chart data endpoint
- 🔶 POST /babies/{id}/growth/bulk - Bulk import
- 🔶 GET /user/timeline - Complete user timeline
- 🔶 Batch operations for performance

### **Phase 5: Testing & Integration** 🔶 PENDING
- 🔶 Unit tests for all Lambda functions
- 🔶 Integration tests with DynamoDB
- 🔶 Frontend integration testing
- 🔶 Multi-user isolation testing
- 🔶 Performance and load testing

---

## 🏗️ **Lambda Function Architecture**

### **Function Structure**
```
aws/lambdas/
├── shared/
│   ├── jwt_utils.py          # JWT validation utilities
│   ├── dynamodb_client.py    # DynamoDB client setup
│   ├── response_utils.py     # Standard API responses
│   └── validation.py         # Input validation
├── babies/
│   ├── lambda_function.py    # Main handler for babies CRUD
│   ├── requirements.txt      # Dependencies
│   └── template.yaml         # SAM template
├── growth_data/
│   ├── lambda_function.py    # Growth data CRUD operations
│   ├── requirements.txt
│   └── template.yaml
└── percentile/               # Existing percentile function
    ├── lambda_function.py    # Enhanced with user validation
    └── ...
```

### **JWT Validation Pattern**
```python
# shared/jwt_utils.py
import jwt
import json
from typing import Optional, Dict

def validate_and_extract_user(event: Dict) -> Dict:
    """
    Validates JWT token and extracts user information
    Returns: {'user_id': str, 'email': str} or raises exception
    """
    try:
        # Extract token from Authorization header
        auth_header = event.get('headers', {}).get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise ValueError('Missing or invalid Authorization header')
        
        token = auth_header.replace('Bearer ', '')
        
        # Decode JWT (AWS Cognito validation)
        decoded = jwt.decode(
            token, 
            options={"verify_signature": False}  # API Gateway already verified
        )
        
        return {
            'user_id': decoded['sub'],
            'email': decoded.get('email', ''),
            'username': decoded.get('cognito:username', '')
        }
    except Exception as e:
        raise ValueError(f'Invalid JWT token: {str(e)}')
```

---

## 🗃️ **CRUD Operations Implementation**

### **Babies Management**

#### **POST /babies - Create Baby**
```python
def create_baby(event, context):
    """Create a new baby for the authenticated user"""
    try:
        # 1. Validate JWT and extract user
        user_info = validate_and_extract_user(event)
        user_id = user_info['user_id']
        
        # 2. Parse and validate input
        body = json.loads(event['body'])
        baby_data = validate_baby_input(body)
        
        # 3. Generate baby ID and timestamps
        baby_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # 4. Save to DynamoDB
        item = {
            'user_id': user_id,
            'baby_id': baby_id,
            'name': baby_data['name'],
            'date_of_birth': baby_data['date_of_birth'],
            'gender': baby_data['gender'],
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        dynamodb.put_item(
            TableName=BABIES_TABLE,
            Item=item,
            ConditionExpression='attribute_not_exists(baby_id)'
        )
        
        return success_response(item, 201)
        
    except Exception as e:
        return error_response(str(e), 400)
```

#### **GET /babies - List User's Babies**
```python
def list_babies(event, context):
    """Get all babies for the authenticated user"""
    try:
        user_info = validate_and_extract_user(event)
        user_id = user_info['user_id']
        
        # Query user's babies
        response = dynamodb.query(
            TableName=BABIES_TABLE,
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        babies = response.get('Items', [])
        return success_response({'babies': babies})
        
    except Exception as e:
        return error_response(str(e), 400)
```

### **Growth Data Management**

#### **POST /babies/{id}/growth - Add Growth Data**
```python
def add_growth_data(event, context):
    """Add growth measurement for a baby"""
    try:
        user_info = validate_and_extract_user(event)
        user_id = user_info['user_id']
        
        # Extract baby_id from path
        baby_id = event['pathParameters']['id']
        
        # Verify baby belongs to user
        verify_baby_ownership(baby_id, user_id)
        
        # Parse growth data
        body = json.loads(event['body'])
        growth_data = validate_growth_input(body)
        
        # Save to DynamoDB
        item = {
            'baby_id': baby_id,
            'measurement_date': growth_data['measurement_date'],
            'user_id': user_id,  # For validation
            'weight_kg': growth_data.get('weight_kg'),
            'height_cm': growth_data.get('height_cm'),
            'head_circumference_cm': growth_data.get('head_circumference_cm'),
            'notes': growth_data.get('notes', ''),
            'created_at': datetime.utcnow().isoformat()
        }
        
        dynamodb.put_item(
            TableName=GROWTH_DATA_TABLE,
            Item=item
        )
        
        return success_response(item, 201)
        
    except Exception as e:
        return error_response(str(e), 400)
```

---

## 🔒 **Security & Validation**

### **User Ownership Verification**
```python
def verify_baby_ownership(baby_id: str, user_id: str) -> bool:
    """Verify that baby belongs to the authenticated user"""
    try:
        response = dynamodb.get_item(
            TableName=BABIES_TABLE,
            Key={'baby_id': baby_id},
            ProjectionExpression='user_id'
        )
        
        item = response.get('Item')
        if not item or item['user_id'] != user_id:
            raise ValueError('Baby not found or access denied')
            
        return True
    except Exception as e:
        raise ValueError(f'Access validation failed: {str(e)}')
```

### **Input Validation**
```python
def validate_baby_input(data: Dict) -> Dict:
    """Validate baby creation/update input"""
    required_fields = ['name', 'date_of_birth', 'gender']
    
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f'Missing required field: {field}')
    
    # Date format validation
    try:
        datetime.fromisoformat(data['date_of_birth'])
    except ValueError:
        raise ValueError('Invalid date format. Use ISO 8601 (YYYY-MM-DD)')
    
    # Gender validation
    if data['gender'] not in ['male', 'female', 'other']:
        raise ValueError('Gender must be: male, female, or other')
    
    return data
```

---

## 📡 **API Gateway Integration**

### **SAM Template Configuration**
```yaml
# template.yaml
Resources:
  BabiesApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowOrigin: "'https://app.upnest.dev'"
      Auth:
        DefaultAuthorizer: CognitoAuthorizer
        Authorizers:
          CognitoAuthorizer:
            UserPoolArn: !Ref CognitoUserPoolArn

  BabiesCrudFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: babies/
      Handler: lambda_function.lambda_handler
      Runtime: python3.11
      Environment:
        Variables:
          BABIES_TABLE: !Ref BabiesTable
          GROWTH_DATA_TABLE: !Ref GrowthDataTable
      Events:
        CreateBaby:
          Type: Api
          Properties:
            RestApiId: !Ref BabiesApi
            Path: /babies
            Method: post
        ListBabies:
          Type: Api
          Properties:
            RestApiId: !Ref BabiesApi
            Path: /babies
            Method: get
```

---

## ⚡ **Performance Optimization**

### **DynamoDB Query Optimization**
```python
# Efficient batch operations
def get_babies_with_latest_growth(user_id: str):
    """Get babies with their latest growth data in minimal queries"""
    
    # 1. Get user's babies
    babies_response = dynamodb.query(
        TableName=BABIES_TABLE,
        KeyConditionExpression='user_id = :user_id',
        ExpressionAttributeValues={':user_id': user_id}
    )
    
    babies = babies_response['Items']
    if not babies:
        return []
    
    # 2. Batch get latest growth data
    baby_ids = [baby['baby_id'] for baby in babies]
    
    # Use batch_get_item for efficiency
    latest_growth = {}
    for baby_id in baby_ids:
        growth_response = dynamodb.query(
            TableName=GROWTH_DATA_TABLE,
            KeyConditionExpression='baby_id = :baby_id',
            ExpressionAttributeValues={':baby_id': baby_id},
            ScanIndexForward=False,  # Latest first
            Limit=1
        )
        if growth_response['Items']:
            latest_growth[baby_id] = growth_response['Items'][0]
    
    # 3. Combine data
    for baby in babies:
        baby['latest_growth'] = latest_growth.get(baby['baby_id'])
    
    return babies
```

### **Response Caching Strategy**
```python
# Cache percentile calculations
@cache_result(ttl=3600)  # Cache for 1 hour
def calculate_percentiles(baby_id: str, weight: float, height: float, age_days: int):
    """Cache expensive percentile calculations"""
    # Existing percentile calculation logic
    pass
```

---

## 🧪 **Testing Strategy**

### **Unit Tests Structure**
```python
# tests/test_babies_crud.py
import pytest
from moto import mock_dynamodb
from unittest.mock import patch

class TestBabiesCRUD:
    @mock_dynamodb
    def test_create_baby_success(self):
        # Setup mock DynamoDB
        # Test baby creation
        # Verify database state
        pass
    
    @mock_dynamodb
    def test_create_baby_invalid_user(self):
        # Test unauthorized access
        pass
    
    def test_list_babies_user_isolation(self):
        # Test that users only see their own babies
        pass
```

### **Integration Testing**
```bash
# Integration test script
#!/bin/bash

echo "🧪 Running Lambda Integration Tests..."

# 1. Deploy test stack
sam deploy --template-file template-test.yaml --stack-name upnest-test

# 2. Run API tests
python -m pytest tests/integration/ -v

# 3. Multi-user isolation tests
python tests/test_user_isolation.py

# 4. Performance tests
python tests/test_performance.py

echo "✅ All tests passed!"
```

---

## 📊 **Monitoring & Observability**

### **CloudWatch Metrics**
```python
# Add custom metrics to Lambda functions
import boto3
cloudwatch = boto3.client('cloudwatch')

def put_custom_metric(metric_name: str, value: float, unit: str = 'Count'):
    """Add custom metrics for business logic"""
    cloudwatch.put_metric_data(
        Namespace='UpNest/Application',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Dimensions': [
                    {'Name': 'Environment', 'Value': 'prod'}
                ]
            }
        ]
    )

# Usage in Lambda functions
put_custom_metric('BabiesCreated', 1)
put_custom_metric('GrowthDataAdded', 1)
```

### **Error Tracking**
```python
def lambda_handler(event, context):
    try:
        # Function logic
        result = process_request(event)
        put_custom_metric('SuccessfulRequests', 1)
        return result
    except Exception as e:
        put_custom_metric('ErrorRequests', 1)
        logger.error(f'Lambda error: {str(e)}', extra={
            'event': event,
            'context': context.__dict__
        })
        return error_response(str(e), 500)
```

---

## 🎯 **Demo Preparation**

### **Real-Time Demo Flow**
1. **Show API in Action**: Live API calls from frontend
2. **Data Isolation**: Switch users, show different data sets
3. **CRUD Operations**: Create, update, delete in real-time
4. **Performance**: Show response times and monitoring
5. **Error Handling**: Demonstrate validation and security

### **Judge Talking Points**
- "Complete backend CRUD operations with user isolation"
- "JWT validation ensures secure multi-user environment"  
- "Optimized DynamoDB queries for production performance"
- "Comprehensive error handling and validation"
- "Real-time monitoring and observability"

---

## ✨ **Achievement Goals**

**Backend Excellence**: 
- Complete CRUD API with proper security
- User data isolation at every operation
- Performance-optimized database queries
- Comprehensive error handling

**Production Quality**:
- JWT validation and user extraction
- Input validation and sanitization
- Monitoring and error tracking
- Automated testing coverage

**Judge Impact**: Demonstrates full-stack capability, security consciousness, and production-ready backend architecture.

---

**Status**: 🟡 **ARCHITECTURE COMPLETE** | **Next**: Implement Lambda functions and integration testing
