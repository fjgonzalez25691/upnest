"""
Unit tests for growth-data get lambda function.
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
import get


class TestGrowthDataGet(unittest.TestCase):
    """Test cases for growth data get lambda function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_id = "550e8400-e29b-41d4-a716-446655440000"
        self.baby_id = "550e8400-e29b-41d4-a716-446655440001"
        
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
        
        # Sample growth data records
        self.growth_data_items = [
            {
                'dataId': {'S': 'data-1'},
                'babyId': {'S': self.baby_id},
                'measurementDate': {'S': '2025-01-20'},
                'ageInDays': {'N': '35'},
                'measurementType': {'S': 'routine'},
                'weight': {'N': '4600'},
                'height': {'N': '56'},
                'headCircumference': {'N': '37.5'},
                'notes': {'S': 'Recent measurement'},
                'createdAt': {'S': '2025-01-20T10:00:00Z'},
                'modifiedAt': {'S': '2025-01-20T10:00:00Z'},
                'percentiles': {
                    'M': {
                        'weight': {'N': '78.0'},
                        'height': {'N': '65.0'},
                        'headCircumference': {'N': '82.0'}
                    }
                }
            },
            {
                'dataId': {'S': 'data-2'},
                'babyId': {'S': self.baby_id},
                'measurementDate': {'S': '2025-01-15'},
                'ageInDays': {'N': '30'},
                'measurementType': {'S': 'routine'},
                'weight': {'N': '4500'},
                'height': {'N': '55'},
                'headCircumference': {'N': '37'},
                'notes': {'S': 'Earlier measurement'},
                'createdAt': {'S': '2025-01-15T10:00:00Z'},
                'modifiedAt': {'S': '2025-01-15T10:00:00Z'}
            }
        ]
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_success(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test successful retrieval of growth data records."""
        # Mock token extraction
        mock_extract_token.return_value = "valid-token"
        
        # Mock JWT validation
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        # Mock get_item for baby verification
        mock_client.get_item.return_value = {'Item': self.baby_item}
        
        # Mock query response
        mock_client.query.return_value = {
            'Items': self.growth_data_items
        }
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id
            }
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        # Verify data
        data = body['data']
        self.assertEqual(len(data), 2)
        
        # Verify first record (most recent)
        first_record = data[0]
        self.assertEqual(first_record['dataId'], 'data-1')
        self.assertEqual(first_record['measurementDate'], '2025-01-20')
        self.assertEqual(first_record['weight'], 4600)
        self.assertEqual(first_record['height'], 56)
        self.assertIn('percentiles', first_record)
        
        # Verify metadata
        metadata = body['metadata']
        self.assertEqual(metadata['count'], 2)
        self.assertEqual(metadata['babyId'], self.baby_id)
        self.assertEqual(metadata['filters']['limit'], 50)  # default limit
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_with_filters(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test retrieval with query parameter filters."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        mock_client.get_item.return_value = {'Item': self.baby_item}
        mock_client.query.return_value = {'Items': self.growth_data_items}
        
        # Create test event with filters
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id
            },
            'queryStringParameters': {
                'limit': '10',
                'startDate': '2025-01-15',
                'endDate': '2025-01-25',
                'measurementType': 'weight'
            }
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        # Verify metadata includes filters
        metadata = body['metadata']
        self.assertEqual(metadata['filters']['limit'], 10)
        self.assertEqual(metadata['filters']['startDate'], '2025-01-15')
        self.assertEqual(metadata['filters']['endDate'], '2025-01-25')
        self.assertEqual(metadata['filters']['measurementType'], 'weight')
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_baby_not_found(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get when baby doesn't exist."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        # Mock get_item to return no baby
        mock_client.get_item.return_value = {}
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id
            }
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_unauthorized_user(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get when user doesn't own the baby."""
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
        
        mock_client.get_item.return_value = {'Item': wrong_baby}
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id
            }
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_inactive_baby(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get for inactive/deleted baby."""
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
        
        mock_client.get_item.return_value = {'Item': inactive_baby}
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id
            }
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('not found', body['error']['message'])
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_empty_result(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get when no growth data exists for baby."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        mock_client.get_item.return_value = {'Item': self.baby_item}
        mock_client.query.return_value = {'Items': []}  # No growth data
        
        # Create test event
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id
            }
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(len(body['data']), 0)
        self.assertEqual(body['metadata']['count'], 0)
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_date_filtering(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get with date filtering applied."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        mock_client.get_item.return_value = {'Item': self.baby_item}
        mock_client.query.return_value = {'Items': self.growth_data_items}
        
        # Create test event with date filter that should exclude first record (2025-01-20)
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id
            },
            'queryStringParameters': {
                'endDate': '2025-01-18'
            }
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        # Should only include the second record (2025-01-15)
        data = body['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['dataId'], 'data-2')
        self.assertEqual(data[0]['measurementDate'], '2025-01-15')
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_measurement_type_filtering(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get with measurement type filtering."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Mock DynamoDB client
        mock_client = Mock()
        mock_dynamodb_client.return_value = mock_client
        
        mock_client.get_item.return_value = {'Item': self.baby_item}
        
        # Create record without weight (should be filtered out)
        record_without_weight = self.growth_data_items[1].copy()
        record_without_weight['weight'] = {'N': '0'}  # Set to 0 (empty)
        
        mock_client.query.return_value = {
            'Items': [self.growth_data_items[0], record_without_weight]
        }
        
        # Create test event with weight filter
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': self.baby_id
            },
            'queryStringParameters': {
                'measurementType': 'weight'
            }
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        # Should only include records with weight > 0
        data = body['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['dataId'], 'data-1')
        self.assertGreater(data[0]['weight'], 0)
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_no_token(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get without authorization token."""
        # Mock no token
        mock_extract_token.return_value = None
        
        # Create test event
        event = {
            'pathParameters': {
                'babyId': self.baby_id
            }
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Authorization', body['error']['message'])
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_invalid_uuid(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get with invalid UUID format."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Create test event with invalid UUID
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {
                'babyId': 'invalid-uuid'
            }
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Invalid babyId format', body['error']['message'])
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_missing_baby_id(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get with missing babyId parameter."""
        # Mock token extraction and validation
        mock_extract_token.return_value = "valid-token"
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_jwt_validator.return_value = mock_validator
        
        # Create test event without babyId
        event = {
            'headers': {'Authorization': 'Bearer valid-token'},
            'pathParameters': {}
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Missing babyId', body['error']['message'])
    
    @patch('get.get_dynamodb_client')
    @patch('get.get_jwt_validator')
    @patch('get.extract_token_from_event')
    def test_get_growth_data_database_error(self, mock_extract_token, mock_jwt_validator, mock_dynamodb_client):
        """Test get with database error."""
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
                'babyId': self.baby_id
            }
        }
        
        # Call the lambda function
        response = get.lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('Failed to retrieve', body['error']['message'])


if __name__ == '__main__':
    unittest.main()
