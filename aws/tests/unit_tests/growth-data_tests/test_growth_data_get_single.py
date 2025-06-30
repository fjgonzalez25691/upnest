"""
Unit tests for growth-data get_single lambda function.
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
import get_single


class TestGrowthDataGetSingle(unittest.TestCase):
    """Test cases for growth data get_single lambda function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_id = "550e8400-e29b-41d4-a716-446655440000"
        self.baby_id = "550e8400-e29b-41d4-a716-446655440001"
        self.data_id = "550e8400-e29b-41d4-a716-446655440002"
        
        # Sample growth data record with percentiles
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
            'modifiedAt': {'S': '2025-01-15T10:00:00Z'},
            'percentiles': {
                'M': {
                    'weight': {'N': '75.5'},
                    'height': {'N': '60.2'},
                    'headCircumference': {'N': '80.1'}
                }
            }
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
        
        # Sample historical data for context
        self.historical_data = {
            'Items': [
                {
                    'dataId': {'S': 'prev-data-id'},
                    'babyId': {'S': self.baby_id},
                    'measurementDate': {'S': '2025-01-10'},
                    'weight': {'N': '4400'}
                },
                {
                    'dataId': {'S': 'next-data-id'},
                    'babyId': {'S': self.baby_id},
                    'measurementDate': {'S': '2025-01-20'},
                    'weight': {'N': '4600'}
                }
            ]
        }
    
    @patch('get_single.get_dynamodb_client')
    @patch('get_single.get_jwt_validator')
    @patch('get_single.extract_token_from_event')
    def test_get_single_growth_data_success(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test successful retrieval of single growth data record."""
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
        
        # Mock query for historical context
        mock_client.query.return_value = self.historical_data
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = get_single.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        # Verify growth data
        data = body['data']
        self.assertEqual(data['dataId'], self.data_id)
        self.assertEqual(data['babyId'], self.baby_id)
        self.assertEqual(data['measurementDate'], '2025-01-15')
        self.assertEqual(data['ageInDays'], 30)
        self.assertEqual(data['weight'], 4500)
        self.assertEqual(data['height'], 55)
        self.assertEqual(data['headCircumference'], 37)
        self.assertEqual(data['notes'], 'Test notes')
        
        # Verify percentiles
        self.assertIn('percentiles', data)
        self.assertEqual(data['percentiles']['weight'], 75.5)
        self.assertEqual(data['percentiles']['height'], 60.2)
        self.assertEqual(data['percentiles']['headCircumference'], 80.1)
        
        # Verify baby context
        self.assertIn('baby', data)
        self.assertEqual(data['baby']['babyId'], self.baby_id)
        self.assertEqual(data['baby']['name'], 'Test Baby')
        self.assertEqual(data['baby']['dateOfBirth'], '2024-12-16')
        
        # Verify historical context
        self.assertIn('context', data)
        self.assertIsNotNone(data['context']['previousMeasurement'])
        self.assertIsNotNone(data['context']['nextMeasurement'])
    
    @patch('get_single.get_dynamodb_client')
    @patch('get_single.get_jwt_validator')
    @patch('get_single.extract_token_from_event')
    def test_get_single_growth_data_not_found(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get single when growth data record doesn't exist."""
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
        response = get_single.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('get_single.get_dynamodb_client')
    @patch('get_single.get_jwt_validator')
    @patch('get_single.extract_token_from_event')
    def test_get_single_growth_data_wrong_baby(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get single when growth data belongs to different baby."""
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
        response = get_single.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('get_single.get_dynamodb_client')
    @patch('get_single.get_jwt_validator')
    @patch('get_single.extract_token_from_event')
    def test_get_single_growth_data_unauthorized_user(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get single when user doesn't own the baby."""
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
        response = get_single.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('get_single.get_dynamodb_client')
    @patch('get_single.get_jwt_validator')
    @patch('get_single.extract_token_from_event')
    def test_get_single_growth_data_inactive_baby(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get single for inactive/deleted baby."""
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
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = get_single.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('get_single.get_dynamodb_client')
    @patch('get_single.get_jwt_validator')
    @patch('get_single.extract_token_from_event')
    def test_get_single_growth_data_without_percentiles(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get single for growth data without percentiles."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        # Growth data without percentiles
        growth_data_no_percentiles = self.growth_data_item.copy()
        del growth_data_no_percentiles['percentiles']
        
        mock_client.get_item.side_effect = [
            {'Item': growth_data_no_percentiles},  # Growth data without percentiles
            {'Item': self.baby_item}  # Baby exists and belongs to user
        ]
        
        # Mock query for historical context
        mock_client.query.return_value = {'Items': []}
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = get_single.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        # Verify percentiles are not included
        self.assertNotIn('percentiles', body['data'])
    
    @patch('get_single.get_dynamodb_client')
    @patch('get_single.get_jwt_validator')
    @patch('get_single.extract_token_from_event')
    def test_get_single_growth_data_context_error(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get single when historical context query fails."""
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
        
        # Mock query to raise exception
        mock_client.query.side_effect = Exception("Query failed")
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id,
                'dataId': self.data_id
            }
        }
        
        # Call the lambda function
        response = get_single.lambda_handler(event, {})
        
        # Verify response - should still succeed without context
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        # Context should not be included or be empty
        if 'context' in body['data']:
            self.assertIsNone(body['data']['context']['previousMeasurement'])
            self.assertIsNone(body['data']['context']['nextMeasurement'])
    
    @patch('get_single.get_dynamodb_client')
    @patch('get_single.get_jwt_validator')
    @patch('get_single.extract_token_from_event')
    def test_get_single_no_token(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get single without authorization token."""
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
        response = get_single.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Authorization', body['error']['message'])
    
    @patch('get_single.get_dynamodb_client')
    @patch('get_single.get_jwt_validator')
    @patch('get_single.extract_token_from_event')
    def test_get_single_invalid_uuid(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get single with invalid UUID format."""
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
        response = get_single.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Invalid ID format', body['error']['message'])
    
    @patch('get_single.get_dynamodb_client')
    @patch('get_single.get_jwt_validator')
    @patch('get_single.extract_token_from_event')
    def test_get_single_missing_path_params(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get single with missing path parameters."""
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
        response = get_single.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Missing babyId or dataId', body['error']['message'])


if __name__ == '__main__':
    unittest.main()
