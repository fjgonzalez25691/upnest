"""
Simple unit tests for percentiles calculation lambda function.
Tests basic growth percentile calculation functionality.
"""

import unittest
from unittest.mock import patch, Mock
import json
import sys
import os

# Add the percentiles lambda directory to the path
percentiles_path = os.path.join(os.path.dirname(__file__), '..', '..', 'lambdas', 'percentiles')
sys.path.insert(0, percentiles_path)

# Also add shared for imports
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', 'lambdas', 'shared')
sys.path.insert(0, shared_path)

class TestPercentilesSimple(unittest.TestCase):
    """Simple test cases for percentiles calculation."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'COGNITO_USER_POOL_ID': 'test-pool-id',
            'COGNITO_CLIENT_ID': 'test-client-id',
            'COGNITO_REGION': 'eu-south-2'
        })
        self.env_patcher.start()
        
        # Mock JWT payload
        self.jwt_payload = {
            'sub': '550e8400-e29b-41d4-a716-446655440000',
            'email': 'test@example.com',
            'email_verified': True
        }
        
        # Sample calculation request
        self.weight_request = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps({
                'measurementType': 'weight',
                'value': 4500,  # 4.5 kg in grams
                'birthDate': '2024-01-15',
                'measurementDate': '2024-04-15',
                'sex': 'female'
            })
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    @patch('calculate.find_lms_values')
    @patch('calculate.extract_token_from_event')
    @patch('calculate.get_jwt_validator')
    @patch('calculate.load_table')
    def test_calculate_weight_percentile_success(self, mock_load_table, mock_get_jwt_validator, mock_extract_token, mock_find_lms):
        """Test successful weight percentile calculation."""
        # Mock token extraction
        mock_extract_token.return_value = "test-token"
        
        # Mock JWT validation
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_get_jwt_validator.return_value = mock_validator
        
        # Mock table loading (can be any mock, find_lms_values is mocked separately)
        mock_load_table.return_value = Mock()
        
        # Mock LMS values finding
        mock_find_lms.return_value = (0.3487, 4.5, 0.13)
        
        # Call the lambda function
        from calculate import lambda_handler
        response = lambda_handler(self.weight_request, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        data = body['data']
        self.assertEqual(data['measurementType'], 'weight')
        self.assertEqual(data['value'], 4500)
        self.assertEqual(data['sex'], 'female')
        self.assertEqual(data['ageInDays'], 91)
        
        # Check that percentile and zscore are calculated
        self.assertIn('percentile', data)
        self.assertIn('zscore', data)
        self.assertIn('LMS', data)
        
        # Percentile should be between 0 and 100
        self.assertGreaterEqual(data['percentile'], 0)
        self.assertLessEqual(data['percentile'], 100)
    
    @patch('calculate.extract_token_from_event')
    def test_calculate_percentile_no_token(self, mock_extract_token):
        """Test percentile calculation without authorization token."""
        mock_extract_token.return_value = None
        
        from calculate import lambda_handler
        response = lambda_handler(self.weight_request, {})
        
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('error', body)
    
    def test_calculate_percentile_missing_body(self):
        """Test percentile calculation with missing body."""
        request_without_body = {
            'headers': {
                'Authorization': 'Bearer test-token'
            }
        }
        
        with patch('calculate.extract_token_from_event', return_value="test-token"):
            with patch('calculate.get_jwt_validator') as mock_get_jwt_validator:
                mock_validator = Mock()
                mock_validator.validate_token.return_value = self.jwt_payload
                mock_get_jwt_validator.return_value = mock_validator
                
                from calculate import lambda_handler
                response = lambda_handler(request_without_body, {})
                
                self.assertEqual(response['statusCode'], 400)
                body = json.loads(response['body'])
                self.assertFalse(body['success'])
    
    def test_calculate_percentile_invalid_json(self):
        """Test percentile calculation with invalid JSON in body."""
        request_with_invalid_json = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': 'invalid json{'
        }
        
        with patch('calculate.extract_token_from_event', return_value="test-token"):
            with patch('calculate.get_jwt_validator') as mock_get_jwt_validator:
                mock_validator = Mock()
                mock_validator.validate_token.return_value = self.jwt_payload
                mock_get_jwt_validator.return_value = mock_validator
                
                from calculate import lambda_handler
                response = lambda_handler(request_with_invalid_json, {})
                
                self.assertEqual(response['statusCode'], 400)
                body = json.loads(response['body'])
                self.assertFalse(body['success'])

if __name__ == '__main__':
    unittest.main()
