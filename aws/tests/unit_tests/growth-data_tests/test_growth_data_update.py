"""
Unit tests for growth-data update lambda function.
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
import growth_data_update


class TestGrowthDataUpdate(unittest.TestCase):
    """Test cases for growth data update lambda function."""
    
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
            'notes': {'S': 'Original notes'},
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
        
        # Sample update data
        self.update_data = {
            'weight': 4600,
            'height': 56,
            'notes': 'Updated notes'
        }
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    @patch('update.extract_token_from_event')
    def test_update_growth_data_success(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test successful growth data update."""
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
        
        # Mock update_item response
        updated_item = self.growth_data_item.copy()
        updated_item['weight'] = {'N': '4600'}
        updated_item['height'] = {'N': '56'}
        updated_item['notes'] = {'S': 'Updated notes'}
        updated_item['modifiedAt'] = {'S': '2025-01-15T11:00:00Z'}
        
        mock_client.update_item.return_value = {
            'Attributes': updated_item
        }
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            },
            'body': json.dumps(self.update_data)
        }
        
        # Call the lambda function
        response = update.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['weight'], 4600)
        self.assertEqual(body['data']['height'], 56)
        self.assertEqual(body['data']['notes'], 'Updated notes')
        
        # Verify DynamoDB calls
        mock_client.update_item.assert_called_once()
        update_call = mock_client.update_item.call_args
        self.assertIn('weight = :weight', update_call[1]['UpdateExpression'])
        self.assertIn('height = :height', update_call[1]['UpdateExpression'])
        self.assertIn('notes = :notes', update_call[1]['UpdateExpression'])
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    @patch('update.extract_token_from_event')
    def test_update_growth_data_not_found(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test update when growth data record doesn't exist."""
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
            },
            'body': json.dumps(self.update_data)
        }
        
        # Call the lambda function
        response = update.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    @patch('update.extract_token_from_event')
    def test_update_growth_data_wrong_baby(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test update when growth data belongs to different baby."""
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
            },
            'body': json.dumps(self.update_data)
        }
        
        # Call the lambda function
        response = update.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    @patch('update.extract_token_from_event')
    def test_update_growth_data_unauthorized_user(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test update when user doesn't own the baby."""
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
            },
            'body': json.dumps(self.update_data)
        }
        
        # Call the lambda function
        response = update.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    @patch('update.extract_token_from_event')
    def test_update_growth_data_invalid_data(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test update with invalid data."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        mock_client.get_item.side_effect = [
            {'Item': self.growth_data_item},  # Growth data exists
            {'Item': self.baby_item}  # Baby exists and belongs to user
        ]
        
        # Create test event with invalid data
        invalid_data = {
            'weight': -100,  # Invalid weight
            'height': 'invalid'  # Invalid height
        }
        
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            },
            'body': json.dumps(invalid_data)
        }
        
        # Call the lambda function
        response = update.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Validation failed', body['error']['message'])
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    @patch('update.extract_token_from_event')
    def test_update_growth_data_no_token(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test update without authorization token."""
        # Mock no token
        mock_extract_token.return_value = None
        
        # Create test event
        event = {
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            },
            'body': json.dumps(self.update_data)
        }
        
        # Call the lambda function
        response = update.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Authorization', body['error']['message'])
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    @patch('update.extract_token_from_event')
    def test_update_growth_data_invalid_uuid(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test update with invalid UUID format."""
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
            },
            'body': json.dumps(self.update_data)
        }
        
        # Call the lambda function
        response = update.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Invalid ID format', body['error']['message'])
    
    @patch('update.get_dynamodb_client')
    @patch('update.get_jwt_validator')
    @patch('update.extract_token_from_event')
    def test_update_growth_data_with_date_change(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test update with measurement date change (should recalculate age)."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        mock_client.get_item.side_effect = [
            {'Item': self.growth_data_item},  # Growth data exists
            {'Item': self.baby_item}  # Baby exists and belongs to user
        ]
        
        # Mock update_item response
        updated_item = self.growth_data_item.copy()
        updated_item['measurementDate'] = {'S': '2025-01-20'}
        updated_item['ageInDays'] = {'N': '35'}  # Recalculated age
        updated_item['modifiedAt'] = {'S': '2025-01-15T11:00:00Z'}
        
        mock_client.update_item.return_value = {
            'Attributes': updated_item
        }
        
        # Create test event with new measurement date
        update_data_with_date = {
            'measurementDate': '2025-01-20',
            'weight': 4700
        }
        
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            },
            'body': json.dumps(update_data_with_date)
        }
        
        # Call the lambda function
        response = update.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['measurementDate'], '2025-01-20')
        self.assertEqual(body['data']['ageInDays'], 35)
        
        # Verify that ageInDays was included in update expression
        mock_client.update_item.assert_called_once()
        update_call = mock_client.update_item.call_args
        self.assertIn('ageInDays = :age_in_days', update_call[1]['UpdateExpression'])


if __name__ == '__main__':
    unittest.main()





