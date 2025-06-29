"""
Unit tests for babies list Lambda function.
Tests baby profiles listing logic.
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

class TestBabiesList(unittest.TestCase):
    """Test cases for babies list Lambda function."""
    
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
        
        # Sample babies data
        self.sample_babies = [
            {
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
            },
            {
                'babyId': 'baby-456',
                'userId': 'user-1-test-123456',
                'name': 'Liam Test',
                'dateOfBirth': '2023-08-20',
                'gender': 'male',
                'premature': False,
                'birthWeight': 3.5,
                'createdAt': '2024-01-16T10:00:00Z',
                'updatedAt': '2024-01-16T10:00:00Z',
                'isActive': True
            }
        ]
        
        # Sample API Gateway event
        self.sample_event = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'queryStringParameters': None
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    @patch('list.get_dynamodb_client')
    @patch('list.get_jwt_validator')
    def test_list_babies_success(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test successful babies listing."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB query_gsi
        mock_dynamodb = MagicMock()
        mock_dynamodb.query_gsi.return_value = self.sample_babies
        mock_get_dynamodb.return_value = mock_dynamodb
        
        # Import the handler after mocking
        from list import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(len(body['data']), 2)
        self.assertEqual(body['data'][0]['babyId'], 'baby-123')
        self.assertEqual(body['data'][1]['babyId'], 'baby-456')
    
    @patch('list.get_dynamodb_client')
    @patch('list.get_jwt_validator')
    def test_list_babies_empty_result(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test babies listing when user has no babies."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB query_gsi returning empty list
        mock_dynamodb = MagicMock()
        mock_dynamodb.query_gsi.return_value = []
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from list import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(len(body['data']), 0)
        self.assertEqual(body['data'], [])
    
    @patch('list.extract_token_from_event')
    def test_list_babies_no_token(self, mock_extract_token):
        """Test babies listing without authorization token."""
        mock_extract_token.return_value = None
        
        from list import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('list.get_dynamodb_client')
    @patch('list.get_jwt_validator')
    def test_list_babies_with_pagination(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test babies listing with pagination parameters."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB query_gsi
        mock_dynamodb = MagicMock()
        mock_dynamodb.query_gsi.return_value = [self.sample_babies[0]]  # Only first baby
        mock_get_dynamodb.return_value = mock_dynamodb
        
        # Event with pagination parameters
        event_with_pagination = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'queryStringParameters': {
                'limit': '1',
                'lastKey': 'baby-123'
            }
        }
        
        from list import lambda_handler
        
        response = lambda_handler(event_with_pagination, {})
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(len(body['data']), 1)
        
        # Verify that query_gsi was called with limit parameter
        mock_dynamodb.query_gsi.assert_called_once()
        call_args = mock_dynamodb.query_gsi.call_args
        self.assertEqual(call_args.kwargs['limit'], 1)
    
    @patch('list.get_dynamodb_client')
    @patch('list.get_jwt_validator')
    def test_list_babies_active_only(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test babies listing filters active babies only."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB query_gsi returning both active and inactive babies
        babies_with_inactive = self.sample_babies + [{
            'babyId': 'baby-789',
            'userId': 'user-1-test-123456',
            'name': 'Inactive Baby',
            'isActive': False  # This one should be filtered out
        }]
        
        mock_dynamodb = MagicMock()
        mock_dynamodb.query_gsi.return_value = babies_with_inactive
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from list import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        # Should only return the 2 active babies
        self.assertEqual(len(body['data']), 2)
        for baby in body['data']:
            self.assertTrue(baby.get('isActive', True))
    
    @patch('list.get_dynamodb_client')
    @patch('list.get_jwt_validator')
    def test_list_babies_dynamodb_error(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test babies listing with DynamoDB error."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB error
        mock_dynamodb = MagicMock()
        mock_dynamodb.query_gsi.side_effect = Exception("DynamoDB error")
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from list import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        # Note: list.py returns success with empty data on error instead of 500
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['data'], [])
        self.assertEqual(body['metadata']['count'], 0)


if __name__ == '__main__':
    unittest.main()
