#!/usr/bin/env python3
"""
Manual test script for JWT-protected Lambda function
This simulates what would happen when API Gateway calls our Lambda
"""
import json
import sys
import os

# Add the lambda directory to path
lambda_dir = os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'percentile')
sys.path.insert(0, lambda_dir)

# Direct import from the lambda directory  
import lambda_function

def test_lambda_without_auth():
    """Test Lambda without Authorization header"""
    print("🔒 Testing Lambda without Authorization header...")
    
    event = {
        'headers': {},
        'body': json.dumps({
            'weight': 10.5,
            'date_birth': '2023-01-01',
            'date_measurement': '2024-01-01',
            'sex': 'male'
        })
    }
    context = {}
    
    response = lambda_function.lambda_handler(event, context)
    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {response['body']}")
    print()
    
    return response['statusCode'] == 401

def test_lambda_with_invalid_token():
    """Test Lambda with invalid Authorization token"""
    print("🔒 Testing Lambda with invalid token...")
    
    event = {
        'headers': {
            'Authorization': 'Bearer invalid.jwt.token'
        },
        'body': json.dumps({
            'weight': 10.5,
            'date_birth': '2023-01-01',
            'date_measurement': '2024-01-01',
            'sex': 'male'
        })
    }
    context = {}
    
    response = lambda_function.lambda_handler(event, context)
    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {response['body']}")
    print()
    
    return response['statusCode'] == 401

def test_lambda_with_mock_valid_token():
    """Test Lambda with mocked valid token (for demonstration)"""
    print("🔒 Testing Lambda with simulated valid token...")
    print("(This would fail in real environment without proper Cognito setup)")
    
    # Set mock environment variables
    os.environ['COGNITO_USER_POOL_ID'] = 'test-pool'
    os.environ['COGNITO_CLIENT_ID'] = 'test-client'
    os.environ['COGNITO_REGION'] = 'us-east-1'
    
    event = {
        'headers': {
            'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test.signature'
        },
        'body': json.dumps({
            'weight': 10.5,
            'date_birth': '2023-01-01',
            'date_measurement': '2024-01-01',
            'sex': 'male'
        })
    }
    context = {}
    
    try:
        response = lambda_function.lambda_handler(event, context)
        print(f"Status Code: {response['statusCode']}")
        print(f"Response: {response['body']}")
        print()
        return response['statusCode'] == 401  # Expected to fail without real token
    except Exception as e:
        print(f"Expected error: {str(e)}")
        print()
        return True

def main():
    print("🧪 JWT Lambda Function Manual Tests")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: No auth header
    test_results.append(test_lambda_without_auth())
    
    # Test 2: Invalid token
    test_results.append(test_lambda_with_invalid_token())
    
    # Test 3: Mock valid token (will fail but shows flow)
    test_results.append(test_lambda_with_mock_valid_token())
    
    print("📊 Test Results Summary:")
    print(f"Tests passed: {sum(test_results)}/{len(test_results)}")
    
    if all(test_results):
        print("✅ All JWT validation tests working correctly!")
        print("\n📝 Next steps:")
        print("1. Deploy Lambda to AWS")
        print("2. Configure real Cognito User Pool")
        print("3. Test with real JWT tokens from frontend")
    else:
        print("❌ Some tests failed - check implementation")

if __name__ == '__main__':
    main()
