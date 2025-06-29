"""
Unit tests for babies update Lambda function.
Tests baby profile update logic.
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

class TestBabiesUpdate(unittest.TestCase):
    """Test cases for babies update Lambda function."""
    
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
        
        # Sample update data
        self.update_data = {
            'name': 'Emma Updated',
            'birthWeight': 3.3,
            'notes': 'Updated notes'
        }
        
        # Sample API Gateway event
        self.sample_event = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'pathParameters': {
                'babyId': 'baby-123'
            },
            'body': json.dumps(self.update_data)
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    def test_update_baby_success(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test successful baby update."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB operations
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.side_effect = [
            self.existing_baby,  # First call for checking existence
            {**self.existing_baby, **self.update_data, 'updatedAt': '2024-01-16T10:00:00Z'}  # Updated baby
        ]
        mock_dynamodb.update_item.return_value = True
        mock_get_dynamodb.return_value = mock_dynamodb
        
        # Import the handler after mocking
        from update import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        # Debug: print the actual response
        print(f"Response: {response}")
        if response.get('body'):
            print(f"Body: {response['body']}")
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['name'], 'Emma Updated')
        self.assertEqual(body['data']['birthWeight'], 3.3)
    
    @patch('update.extract_token_from_event')
    def test_update_baby_no_token(self, mock_extract_token):
        """Test baby update without authorization token."""
        mock_extract_token.return_value = None
        
        from update import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    def test_update_baby_not_found(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby update when baby doesn't exist."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB get_item returning None
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.return_value = None
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from update import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    def test_update_baby_unauthorized_access(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby update when user doesn't own the baby."""
        # Mock JWT validation with different user
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-2-test-789012'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB get_item returning baby owned by different user
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.return_value = self.existing_baby  # belongs to user-1
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from update import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 404)  # Should return 404 for security
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('update.get_jwt_validator')
    def test_update_baby_invalid_json(self, mock_get_jwt_validator):
        """Test baby update with invalid JSON."""
        # Mock JWT validation to pass
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        invalid_event = {
            'headers': {'Authorization': 'Bearer test-token'},
            'pathParameters': {'babyId': 'baby-123'},
            'body': 'invalid-json'
        }
        
        from update import lambda_handler
        
        response = lambda_handler(invalid_event, {})
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    def test_update_baby_validation_error(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby update with validation errors."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB get_item
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.return_value = self.existing_baby
        mock_get_dynamodb.return_value = mock_dynamodb
        
        # Invalid update data
        invalid_data = {
            'birthWeight': 'invalid-weight',  # Should be a number
            'gender': 'invalid-gender'  # Should be 'male' or 'female'
        }
        invalid_event = {
            'headers': {'Authorization': 'Bearer test-token'},
            'pathParameters': {'babyId': 'baby-123'},
            'body': json.dumps(invalid_data)
        }
        
        from update import lambda_handler
        
        response = lambda_handler(invalid_event, {})
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    def test_update_baby_missing_baby_id(self):
        """Test baby update without baby ID in path parameters."""
        event_no_baby_id = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'pathParameters': None,
            'body': json.dumps(self.update_data)
        }
        
        # Mock JWT validation to pass
        with patch('update.get_jwt_validator') as mock_get_jwt_validator:
            mock_jwt_validator = MagicMock()
            mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
            mock_get_jwt_validator.return_value = mock_jwt_validator
            
            from update import lambda_handler
            
            response = lambda_handler(event_no_baby_id, {})
            
            # Should return 400 bad request when baby ID is missing
            self.assertEqual(response['statusCode'], 400)
            body = json.loads(response['body'])
            self.assertFalse(body['success'])
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    def test_update_baby_dynamodb_error(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test baby update with DynamoDB error."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB error
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.side_effect = Exception("DynamoDB error")
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from update import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])


if __name__ == '__main__':
    unittest.main()
