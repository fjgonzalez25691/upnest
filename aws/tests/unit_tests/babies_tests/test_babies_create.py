"""
Unit tests for babies create Lambda function.
Tests baby profile creation logic.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the babies lambda directory to the path (one more '..' because we're in babies_test/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lambdas', 'babies'))

# Also add shared for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lambdas', 'shared'))
from jwt_utils import get_jwt_validator, extract_token_from_event
from dynamodb_client import get_dynamodb_client

class TestBabiesCreate(unittest.TestCase):
    """Test cases for babies create Lambda function."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'BABIES_TABLE': 'test-babies-table',
            'COGNITO_USER_POOL_ID': 'test-pool-id',
            'COGNITO_CLIENT_ID': 'test-client-id',
            'COGNITO_REGION': 'eu-south-2'
        })
        self.env_patcher.start()
        
        # Sample valid baby data
        self.valid_baby_data = {
            'name': 'Emma Test',
            'dateOfBirth': '2023-06-15',
            'gender': 'female',
            'premature': False,
            'birthWeight': 3.2
        }
        
        # Sample API Gateway event
        self.sample_event = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps(self.valid_baby_data)
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    @patch('create.get_dynamodb_client')
    @patch('create.get_jwt_validator')
    def test_create_baby_success(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test successful baby creation."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB put_item
        mock_dynamodb = MagicMock()
        mock_dynamodb.put_item.return_value = True
        mock_get_dynamodb.return_value = mock_dynamodb
        
        # Import the handler after mocking
        from create import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 201)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertIn('babyId', body['data'])
    
    @patch('create.extract_token_from_event')
    def test_create_baby_no_token(self, mock_extract_token):
        """Test baby creation without authorization token."""
        mock_extract_token.return_value = None
        
        from create import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('create.get_jwt_validator')
    def test_create_baby_invalid_json(self, mock_get_jwt_validator):
        """Test baby creation with invalid JSON."""
        # Mock JWT validation to pass
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        invalid_event = {
            'headers': {'Authorization': 'Bearer test-token'},
            'body': 'invalid-json'
        }
        
        from create import lambda_handler
        
        response = lambda_handler(invalid_event, {})
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('create.get_dynamodb_client')
    @patch('create.get_jwt_validator')
    def test_create_baby_validation_error(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby creation with validation errors."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Invalid baby data (missing required fields)
        invalid_data = {'name': 'Test Baby'}
        invalid_event = {
            'headers': {'Authorization': 'Bearer test-token'},
            'body': json.dumps(invalid_data)
        }
        
        from create import lambda_handler
        
        response = lambda_handler(invalid_event, {})
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('create.get_dynamodb_client')
    @patch('create.get_jwt_validator')
    def test_create_baby_dynamodb_error(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby creation with DynamoDB error."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB error
        mock_dynamodb = MagicMock()
        mock_dynamodb.put_item.side_effect = Exception("DynamoDB error")
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from create import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])


if __name__ == '__main__':
    unittest.main()
