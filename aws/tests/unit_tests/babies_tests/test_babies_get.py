"""
Unit tests for babies get Lambda function.
Tests baby profile retrieval logic.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the babies lambda directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lambdas', 'babies'))

# Also add shared for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lambdas', 'shared'))

class TestBabiesGet(unittest.TestCase):
    """Test cases for babies get Lambda function."""
    
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
        
        # Sample baby data
        self.sample_baby = {
            'babyId': 'baby-123',
            'userId': 'user-1-test-123456',
            'name': 'Emma Test',
            'dateOfBirth': '2023-06-15',
            'gender': 'female',
            'premature': False,
            'birthWeight': 3.2,
            'createdAt': '2024-01-15T10:00:00Z',
            'updatedAt': '2024-01-15T10:00:00Z',
            'isActive': True
        }
        
        # Sample API Gateway event
        self.sample_event = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'pathParameters': {
                'babyId': 'baby-123'
            }
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    def test_get_baby_success(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test successful baby retrieval."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB get_item
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.return_value = self.sample_baby
        mock_get_dynamodb.return_value = mock_dynamodb
        
        # Import the handler after mocking
        from get import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['babyId'], 'baby-123')
        self.assertEqual(body['data']['name'], 'Emma Test')
    
    @patch('get.extract_token_from_event')
    def test_get_baby_no_token(self, mock_extract_token):
        """Test baby retrieval without authorization token."""
        mock_extract_token.return_value = None
        
        from get import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    def test_get_baby_not_found(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby retrieval when baby doesn't exist."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB get_item returning None
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.return_value = None
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from get import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    def test_get_baby_unauthorized_access(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby retrieval when user doesn't own the baby."""
        # Mock JWT validation with different user
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-2-test-789012'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB get_item returning baby owned by different user
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.return_value = self.sample_baby  # belongs to user-1
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from get import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 404)  # Should return 404 for security
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('get.get_jwt_validator')
    def test_get_baby_missing_baby_id(self, mock_get_jwt_validator):
        """Test baby retrieval without baby ID in path parameters."""
        # Mock JWT validation to pass
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        event_no_baby_id = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'pathParameters': None
        }
        
        from get import lambda_handler
        
        response = lambda_handler(event_no_baby_id, {})
        
        # Note: When pathParameters is None, it causes an internal error
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    def test_get_baby_dynamodb_error(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby retrieval with DynamoDB error."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB error
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.side_effect = Exception("DynamoDB error")
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from get import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        # Note: get.py returns 404 for any error (including DynamoDB errors) for security
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])


if __name__ == '__main__':
    unittest.main()
