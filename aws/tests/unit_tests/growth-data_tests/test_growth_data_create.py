"""
Unit tests for growth-data create Lambda function.
Tests growth data creation logic.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the growth-data lambda directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lambdas', 'growth-data'))

# Also add shared for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lambdas', 'shared'))

# Import the module we're testing after setting up paths - use unique alias
import growth_data_create as growth_create

class TestGrowthDataCreate(unittest.TestCase):
    """Test cases for growth data create Lambda function."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'GROWTH_DATA_TABLE': 'test-growth-data-table',
            'BABIES_TABLE': 'test-babies-table',
            'COGNITO_USER_POOL_ID': 'test-pool-id',
            'COGNITO_CLIENT_ID': 'test-client-id',
            'COGNITO_REGION': 'eu-south-2'
        })
        self.env_patcher.start()
        
        # Sample valid growth data
        self.valid_growth_data = {
            'babyId': 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
            'measurementDate': '2023-06-15',
            'measurements': {
                'weight': 9500,  # 9.5kg in grams
                'height': 75.0,  # 75cm
                'headCircumference': 42.5  # 42.5cm
            }
        }
        
        # Sample baby data for ownership validation
        self.existing_baby = {
            'babyId': 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
            'userId': 'user-1-test-123456',
            'name': 'Emma Test',
            'dateOfBirth': '2023-06-15',
            'gender': 'female',
            'isActive': True
        }
        
        # Sample API Gateway event
        self.sample_event = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps(self.valid_growth_data)
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    @patch('growth_data_create.get_jwt_validator')
    @patch('growth_data_create.get_dynamodb')
    def test_create_growth_data_success(self, mock_get_dynamodb, mock_get_jwt_validator):
        """Test successful growth data creation."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB operations
        mock_dynamodb = MagicMock()
        # Mock baby ownership verification
        mock_dynamodb.get_item.return_value = self.existing_baby
        # Mock DynamoDB put_item
        mock_dynamodb.put_item.return_value = True
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from growth_data_create import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        # Debug: print the actual response
        print(f"Response: {response}")
        if response.get('body'):
            print(f"Body: {response['body']}")
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertIn('dataId', body['data'])
    
    @patch('growth_data_create.get_jwt_validator')
    def test_create_growth_data_no_token(self, mock_get_jwt_validator):
        """Test growth data creation without authorization token."""
        # Mock JWT validator to return None (no token)
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = None
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        from growth_data_create import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    def test_create_growth_data_invalid_json(self):
        """Test growth data creation with invalid JSON."""
        invalid_event = {
            'headers': {'Authorization': 'Bearer test-token'},
            'body': 'invalid-json'
        }
        
        # Mock JWT validation to pass
        with patch('growth_data_create.get_jwt_validator') as mock_get_jwt_validator:
            mock_jwt_validator = MagicMock()
            mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
            mock_get_jwt_validator.return_value = mock_jwt_validator
            
            from growth_data_create import lambda_handler
            
            response = lambda_handler(invalid_event, {})
            
            self.assertEqual(response['statusCode'], 400)
            body = json.loads(response['body'])
            self.assertFalse(body['success'])
    
    @patch('growth_data_create.get_jwt_validator')
    @patch('growth_data_create.get_dynamodb')
    def test_create_growth_data_baby_not_found(self, mock_get_dynamodb, mock_get_jwt_validator):
        """Test growth data creation when baby doesn't exist."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB operations
        mock_dynamodb = MagicMock()
        # Mock baby not found
        mock_dynamodb.get_item.return_value = None
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from growth_data_create import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('growth_data_create.get_jwt_validator')
    @patch('growth_data_create.get_dynamodb')
    def test_create_growth_data_unauthorized_baby(self, mock_get_dynamodb, mock_get_jwt_validator):
        """Test growth data creation for baby owned by different user."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB operations
        mock_dynamodb = MagicMock()
        # Mock baby owned by different user
        different_user_baby = {**self.existing_baby, 'userId': 'different-user-456'}
        mock_dynamodb.get_item.return_value = different_user_baby
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from growth_data_create import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 404)  # Should return 404 for security
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('growth_data_create.get_jwt_validator')
    @patch('growth_data_create.get_dynamodb')
    def test_create_growth_data_validation_error(self, mock_get_dynamodb, mock_get_jwt_validator):
        """Test growth data creation with validation errors."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB operations
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.return_value = self.existing_baby
        mock_get_dynamodb.return_value = mock_dynamodb
        
        # Invalid growth data
        invalid_data = {
            'babyId': 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
            'measurementDate': 'invalid-date',
            'measurements': {
                'weight': 'invalid-weight'  # Should be a number
            }
        }
        invalid_event = {
            'headers': {'Authorization': 'Bearer test-token'},
            'body': json.dumps(invalid_data)
        }
        
        from growth_data_create import lambda_handler
        
        response = lambda_handler(invalid_event, {})
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('growth_data_create.get_jwt_validator')
    @patch('growth_data_create.get_dynamodb')
    def test_create_growth_data_dynamodb_error(self, mock_get_dynamodb, mock_get_jwt_validator):
        """Test growth data creation with DynamoDB error."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB error
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.side_effect = Exception("DynamoDB error")
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from growth_data_create import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])


if __name__ == '__main__':
    unittest.main()





