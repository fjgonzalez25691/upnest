"""
Unit tests for growth-data list Lambda function.
Tests listing growth data for a baby.
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

# Import the module we're testing after setting up paths
import list as growth_list

class TestGrowthDataList(unittest.TestCase):
    """Test cases for growth data list Lambda function."""
    
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
        
        # Sample baby data for ownership validation
        self.existing_baby = {
            'babyId': 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
            'userId': 'user-1-test-123456',
            'name': 'Emma Test',
            'dateOfBirth': '2023-06-15',
            'gender': 'female',
            'isActive': True
        }
        
        # Sample growth data
        self.sample_growth_data = [
            {
                'dataId': 'data-1',
                'babyId': 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
                'userId': 'user-1-test-123456',
                'measurementDate': '2023-06-15',
                'measurements': {
                    'weight': 9500,
                    'height': 75.0,
                    'headCircumference': 42.5
                },
                'createdAt': '2023-06-15T10:00:00Z'
            },
            {
                'dataId': 'data-2',
                'babyId': 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
                'userId': 'user-1-test-123456',
                'measurementDate': '2023-07-15',
                'measurements': {
                    'weight': 10200,
                    'height': 78.0,
                    'headCircumference': 43.0
                },
                'createdAt': '2023-07-15T10:00:00Z'
            }
        ]
        
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
    
    @patch.object(growth_list, 'get_dynamodb_client')
    @patch.object(growth_list, 'get_jwt_validator')
    def test_list_growth_data_success(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test successful growth data listing."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB operations
        mock_dynamodb = MagicMock()
        # Mock baby ownership verification
        mock_dynamodb.get_item.return_value = self.existing_baby
        # Mock growth data query
        mock_dynamodb.query_items.return_value = self.sample_growth_data
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from list import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        # Debug: print the actual response
        print(f"Response: {response}")
        if response.get('body'):
            print(f"Body: {response['body']}")
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(len(body['data']), 2)
        self.assertEqual(body['data'][0]['dataId'], 'data-1')
    
    @patch.object(growth_list, 'extract_token_from_event')
    def test_list_growth_data_no_token(self, mock_extract_token):
        """Test growth data listing without authorization token."""
        mock_extract_token.return_value = None
        
        from list import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch.object(growth_list, 'get_dynamodb_client')
    @patch.object(growth_list, 'get_jwt_validator')
    def test_list_growth_data_baby_not_found(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test growth data listing when baby doesn't exist."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB operations
        mock_dynamodb = MagicMock()
        # Mock baby not found
        mock_dynamodb.get_item.return_value = None
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from list import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch.object(growth_list, 'get_dynamodb_client')
    @patch.object(growth_list, 'get_jwt_validator')
    def test_list_growth_data_unauthorized_baby(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test growth data listing for baby owned by different user."""
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
        
        from list import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 404)  # Should return 404 for security
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch.object(growth_list, 'get_dynamodb_client')
    @patch.object(growth_list, 'get_jwt_validator')
    def test_list_growth_data_empty_result(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test growth data listing with no data."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB operations
        mock_dynamodb = MagicMock()
        # Mock baby ownership verification
        mock_dynamodb.get_item.return_value = self.existing_baby
        # Mock empty growth data query
        mock_dynamodb.query_items.return_value = []
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from list import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(len(body['data']), 0)
    
    def test_list_growth_data_missing_baby_id(self):
        """Test growth data listing without baby ID in path parameters."""
        event_no_baby_id = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'pathParameters': None
        }
        
        # Mock JWT validation to pass
        with patch.object(growth_list, 'get_jwt_validator') as mock_get_jwt_validator:
            mock_jwt_validator = MagicMock()
            mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
            mock_get_jwt_validator.return_value = mock_jwt_validator
            
            from list import lambda_handler
            
            response = lambda_handler(event_no_baby_id, {})
            
            # Should return 400 bad request when baby ID is missing
            self.assertEqual(response['statusCode'], 400)
            body = json.loads(response['body'])
            self.assertFalse(body['success'])
    
    @patch.object(growth_list, 'get_dynamodb_client')
    @patch.object(growth_list, 'get_jwt_validator')
    def test_list_growth_data_dynamodb_error(self, mock_get_jwt_validator, mock_get_dynamodb):
        """Test growth data listing with DynamoDB error."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock DynamoDB error
        mock_dynamodb = MagicMock()
        mock_dynamodb.get_item.side_effect = Exception("DynamoDB error")
        mock_get_dynamodb.return_value = mock_dynamodb
        
        from list import lambda_handler
        
        response = lambda_handler(self.sample_event, {})
        
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])


if __name__ == '__main__':
    unittest.main()
