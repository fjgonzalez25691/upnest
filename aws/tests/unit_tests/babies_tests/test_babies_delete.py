"""
Unit tests for babies delete Lambda function.
Tests baby profile soft deletion logic.
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

class TestBabiesDelete(unittest.TestCase):
    """Test cases for babies delete Lambda function."""
    
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
        
        # Sample existing baby data
        self.existing_baby = {
            'babyId': 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
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
                'babyId': 'f47ac10b-58cc-4372-a567-0e02b2c3d479'
            }
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    def test_delete_baby_success(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test successful baby soft deletion."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB operations
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.return_value = self.existing_baby
        mock_dynamodb.update_item.return_value = True
        mock_get_dynamodb.return_value = mock_dynamodb
        
        # Import the handler after mocking
        from delete import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        # Debug: print the actual response
        print(f"Response: {response}")
        if response.get('body'):
            print(f"Body: {response['body']}")
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['babyId'], 'f47ac10b-58cc-4372-a567-0e02b2c3d479')
        self.assertIn('deletedAt', body['data'])
        self.assertEqual(body['message'], 'Baby deleted successfully')
        
        # Verify update_item was called with correct parameters
        mock_dynamodb.update_item.assert_called_once()
        call_args = mock_dynamodb.update_item.call_args
        self.assertEqual(call_args[1]['table_name'], 'babies')
        self.assertEqual(call_args[1]['key'], {'babyId': 'f47ac10b-58cc-4372-a567-0e02b2c3d479'})
        self.assertIn('isActive', call_args[1]['update_expression'])
        self.assertFalse(call_args[1]['expression_values'][':is_active'])
    
    @patch('delete.extract_token_from_event')
    def test_delete_baby_no_token(self, mock_extract_token):
        """Test baby deletion without authorization token."""
        mock_extract_token.return_value = None
        
        from delete import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    def test_delete_baby_not_found(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby deletion when baby doesn't exist."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB get_item returning None
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.return_value = None
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from delete import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    def test_delete_baby_unauthorized_access(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby deletion when user doesn't own the baby."""
        # Mock JWT validation with different user
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-2-test-789012'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB get_item returning baby owned by different user
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.return_value = self.existing_baby  # belongs to user-1
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from delete import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 404)  # Should return 404 for security
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    def test_delete_baby_already_deleted(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby deletion when baby is already deleted."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB with already deleted baby
        deleted_baby = {**self.existing_baby, 'isActive': False}
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.return_value = deleted_baby
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from delete import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('already deleted', body['error']['message'])
    
    def test_delete_baby_missing_baby_id(self):
        """Test baby deletion without baby ID in path parameters."""
        event_no_baby_id = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'pathParameters': None
        }
        
        # Mock JWT validation to pass
        with patch('delete.get_jwt_validator') as mock_get_jwt_validator:
            mock_jwt_validator = MagicMock()
            mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
            mock_get_jwt_validator.return_value = mock_jwt_validator
            
            from delete import lambda_handler
            
            response = lambda_handler(event_no_baby_id, {})
            
            # Should return 400 bad request when baby ID is missing
            self.assertEqual(response['statusCode'], 400)
            body = json.loads(response['body'])
            self.assertFalse(body['success'])
    
    @patch('delete.get_jwt_validator')
    def test_delete_baby_invalid_baby_id(self, mock_get_jwt_validator):
        """Test baby deletion with invalid baby ID format."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        invalid_event = {
            'headers': {'Authorization': 'Bearer test-token'},
            'pathParameters': {'babyId': 'invalid-uuid'}
        }
        
        from delete import lambda_handler
        
        response = lambda_handler(invalid_event, {})
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    def test_delete_baby_dynamodb_error(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby deletion with DynamoDB error."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB error
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.side_effect = Exception("DynamoDB error")
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from delete import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])


if __name__ == '__main__':
    unittest.main()
