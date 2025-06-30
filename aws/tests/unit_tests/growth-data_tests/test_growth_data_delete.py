"""
Unit tests for growth-data delete lambda function.
"""

import unittest
from unittest.mock import Mock, patch
import json
import sys
import os

# Add the lambda function path to sys.path
lambda_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lambdas', 'growth-data')
sys.path.insert(0, lambda_path)

# Add shared utilities path
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lambdas', 'shared')
sys.path.insert(0, shared_path)

# Import the module we're testing after setting up paths
import growth_data_delete


class TestGrowthDataDelete(unittest.TestCase):
    """Test cases for growth data delete lambda function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_id = "550e8400-e29b-41d4-a716-446655440000"
        self.baby_id = "550e8400-e29b-41d4-a716-446655440001"
        self.data_id = "550e8400-e29b-41d4-a716-446655440002"
        
        # Sample growth data record
        self.growth_data_item = {
            'dataId': {'S': self.data_id},
            'babyId': {'S': self.baby_id},
            'measurementDate': {'S': '2025-01-15'},
            'ageInDays': {'N': '30'},
            'measurementType': {'S': 'routine'},
            'weight': {'N': '4500'},
            'height': {'N': '55'},
            'headCircumference': {'N': '37'},
            'notes': {'S': 'Test notes'},
            'createdAt': {'S': '2025-01-15T10:00:00Z'},
            'modifiedAt': {'S': '2025-01-15T10:00:00Z'}
        }
        
        # Sample baby record
        self.baby_item = {
            'babyId': {'S': self.baby_id},
            'userId': {'S': self.user_id},
            'name': {'S': 'Test Baby'},
            'dateOfBirth': {'S': '2024-12-16'},
            'isActive': {'BOOL': True}
        }
        
        # Sample JWT payload
        self.jwt_payload = {
            'sub': self.user_id,
            'email': 'test@example.com'
        }
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    @patch('delete.extract_token_from_event')
    def test_delete_growth_data_success(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test successful growth data deletion."""
        # Mock token extraction
        mock_extract_token.return_value = "valid-token"
        
        # Mock JWT validation
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        # Mock get_item calls
        mock_client.get_item.side_effect = [
            {'Item': self.growth_data_item},  # Growth data exists
            {'Item': self.baby_item}  # Baby exists and belongs to user
        ]
        
        # Mock delete_item (no return needed for delete)
        mock_client.delete_item.return_value = {}
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = delete.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['dataId'], self.data_id)
        self.assertEqual(body['data']['babyId'], self.baby_id)
        self.assertEqual(body['data']['measurementDate'], '2025-01-15')
        self.assertEqual(body['data']['measurementType'], 'routine')
        self.assertIn('deletedAt', body['data'])
        self.assertIn('deleted successfully', body['data']['message'])
        
        # Verify DynamoDB calls
        mock_client.delete_item.assert_called_once_with(
            TableName='GrowthData',
            Key={
                'dataId': {'S': self.data_id}
            }
        )
    
    @patch('delete.get_dynamodb_client')  
    @patch('delete.get_jwt_validator')
    @patch('delete.extract_token_from_event')
    def test_delete_growth_data_not_found(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test delete when growth data record doesn't exist."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        # Mock get_item to return no item
        mock_client.get_item.return_value = {}
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = delete.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    @patch('delete.extract_token_from_event')
    def test_delete_growth_data_wrong_baby(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test delete when growth data belongs to different baby."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        # Mock growth data for different baby
        wrong_growth_data = self.growth_data_item.copy()
        wrong_growth_data['babyId'] = {'S': 'different-baby-id'}
        
        mock_client.get_item.return_value = {'Item': wrong_growth_data}
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = delete.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    @patch('delete.extract_token_from_event')
    def test_delete_growth_data_unauthorized_user(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test delete when user doesn't own the baby."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        # Mock baby belonging to different user
        wrong_baby = self.baby_item.copy()
        wrong_baby['userId'] = {'S': 'different-user-id'}
        
        mock_client.get_item.side_effect = [
            {'Item': self.growth_data_item},  # Growth data exists
            {'Item': wrong_baby}  # Baby belongs to different user
        ]
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = delete.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    @patch('delete.extract_token_from_event')
    def test_delete_growth_data_inactive_baby(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test delete for inactive/deleted baby (should still work for cleanup)."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        # Mock inactive baby
        inactive_baby = self.baby_item.copy()
        inactive_baby['isActive'] = {'BOOL': False}
        
        mock_client.get_item.side_effect = [
            {'Item': self.growth_data_item},  # Growth data exists
            {'Item': inactive_baby}  # Baby is inactive
        ]
        
        # Mock delete_item
        mock_client.delete_item.return_value = {}
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = delete.lambda_handler(event, {})
        
        # Verify response - should still allow deletion for cleanup
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        # Verify DynamoDB delete was called
        mock_client.delete_item.assert_called_once()
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    @patch('delete.extract_token_from_event')
    def test_delete_growth_data_no_token(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test delete without authorization token."""
        # Mock no token
        mock_extract_token.return_value = None
        
        # Create test event
        event = {
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = delete.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Authorization', body['error']['message'])
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    @patch('delete.extract_token_from_event')
    def test_delete_growth_data_invalid_token(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test delete with invalid JWT token."""
        # Mock token extraction
        mock_extract_token.return_value = "invalid-token"
        
        # Mock JWT validation failure
        mock_validator = Mock()
        mock_validator.validate_token.return_value = None
        mock_jwt_validator.return_value = mock_validator
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer invalid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = delete.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Invalid or expired', body['error']['message'])
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    @patch('delete.extract_token_from_event')
    def test_delete_growth_data_missing_path_params(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test delete with missing path parameters."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Create test event with missing parameters
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id
                # Missing dataId
            }
        }
        
        # Call the lambda function
        response = delete.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Missing babyId or dataId', body['error']['message'])
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    @patch('delete.extract_token_from_event')
    def test_delete_growth_data_invalid_uuid(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test delete with invalid UUID format."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Create test event with invalid UUID
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': 'invalid-uuid',
                'dataId': 'also-invalid'
            }
        }
        
        # Call the lambda function
        response = delete.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Invalid ID format', body['error']['message'])
    
    @patch('delete.get_dynamodb_client')
    @patch('delete.get_jwt_validator')
    @patch('delete.extract_token_from_event')
    def test_delete_growth_data_database_error(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test delete with database error."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client with error
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        # Mock get_item to raise exception
        mock_client.get_item.side_effect = Exception("Database error")
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = delete.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Failed to delete', body['error']['message'])


if __name__ == '__main__':
    unittest.main()





