"""
Tests for data validation scenarios.
Tests invalid input data, missing fields, invalid formats, etc.
"""

from unittest.mock import patch, Mock
import json
from .test_base import BasePercentilesTest
import percentiles_calculate as calculate

class TestPercentilesValidation(BasePercentilesTest):
    """Test cases for input data validation."""
    
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
                
                response = calculate.lambda_handler(request_without_body, {})
                
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
                
                response = calculate.lambda_handler(request_with_invalid_json, {})
                
                self.assertEqual(response['statusCode'], 400)
                body = json.loads(response['body'])
                self.assertFalse(body['success'])
    
    def test_calculate_percentile_missing_required_fields(self):
        """Test percentile calculation with missing required fields."""
        request_missing_fields = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps({
                'measurementType': 'weight',
                'value': 4500
                # Missing birthDate, measurementDate, sex
            })
        }
        
        with patch('calculate.extract_token_from_event', return_value="test-token"):
            with patch('calculate.get_jwt_validator') as mock_get_jwt_validator:
                mock_validator = Mock()
                mock_validator.validate_token.return_value = self.jwt_payload
                mock_get_jwt_validator.return_value = mock_validator
                
                response = calculate.lambda_handler(request_missing_fields, {})
                
                self.assertEqual(response['statusCode'], 400)
                body = json.loads(response['body'])
                self.assertFalse(body['success'])
                self.assertIn('Missing required fields', body['error']['message'])
    
    def test_calculate_percentile_invalid_measurement_type(self):
        """Test percentile calculation with invalid measurement type."""
        request_invalid_type = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps({
                'measurementType': 'invalid_type',
                'value': 4500,
                'birthDate': '2024-01-15',
                'measurementDate': '2024-04-15',
                'sex': 'female'
            })
        }
        
        with patch('calculate.extract_token_from_event', return_value="test-token"):
            with patch('calculate.get_jwt_validator') as mock_get_jwt_validator:
                mock_validator = Mock()
                mock_validator.validate_token.return_value = self.jwt_payload
                mock_get_jwt_validator.return_value = mock_validator
                
                response = calculate.lambda_handler(request_invalid_type, {})
                
                self.assertEqual(response['statusCode'], 400)
                body = json.loads(response['body'])
                self.assertFalse(body['success'])
    
    def test_calculate_percentile_invalid_sex(self):
        """Test percentile calculation with invalid sex."""
        request_invalid_sex = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps({
                'measurementType': 'weight',
                'value': 4500,
                'birthDate': '2024-01-15',
                'measurementDate': '2024-04-15',
                'sex': 'invalid_sex'
            })
        }
        
        with patch('calculate.extract_token_from_event', return_value="test-token"):
            with patch('calculate.get_jwt_validator') as mock_get_jwt_validator:
                mock_validator = Mock()
                mock_validator.validate_token.return_value = self.jwt_payload
                mock_get_jwt_validator.return_value = mock_validator
                
                response = calculate.lambda_handler(request_invalid_sex, {})
                
                self.assertEqual(response['statusCode'], 400)
                body = json.loads(response['body'])
                self.assertFalse(body['success'])
    
    def test_calculate_percentile_negative_value(self):
        """Test percentile calculation with negative measurement value."""
        request_negative_value = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps({
                'measurementType': 'weight',
                'value': -100,
                'birthDate': '2024-01-15',
                'measurementDate': '2024-04-15',
                'sex': 'female'
            })
        }
        
        with patch('calculate.extract_token_from_event', return_value="test-token"):
            with patch('calculate.get_jwt_validator') as mock_get_jwt_validator:
                mock_validator = Mock()
                mock_validator.validate_token.return_value = self.jwt_payload
                mock_get_jwt_validator.return_value = mock_validator
                
                response = calculate.lambda_handler(request_negative_value, {})
                
                self.assertEqual(response['statusCode'], 400)
                body = json.loads(response['body'])
                self.assertFalse(body['success'])
    
    def test_calculate_percentile_future_birth_date(self):
        """Test percentile calculation with measurement date before birth date."""
        request_future_birth = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps({
                'measurementType': 'weight',
                'value': 4500,
                'birthDate': '2024-04-15',
                'measurementDate': '2024-01-15',  # Before birth date
                'sex': 'female'
            })
        }
        
        with patch('calculate.extract_token_from_event', return_value="test-token"):
            with patch('calculate.get_jwt_validator') as mock_get_jwt_validator:
                mock_validator = Mock()
                mock_validator.validate_token.return_value = self.jwt_payload
                mock_get_jwt_validator.return_value = mock_validator
                
                response = calculate.lambda_handler(request_future_birth, {})
                
                self.assertEqual(response['statusCode'], 400)
                body = json.loads(response['body'])
                self.assertFalse(body['success'])
    
    def test_calculate_percentile_invalid_date_format(self):
        """Test percentile calculation with invalid date format."""
        request_invalid_date = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps({
                'measurementType': 'weight',
                'value': 4500,
                'birthDate': '15/01/2024',  # Wrong format
                'measurementDate': '2024-04-15',
                'sex': 'female'
            })
        }
        
        with patch('calculate.extract_token_from_event', return_value="test-token"):
            with patch('calculate.get_jwt_validator') as mock_get_jwt_validator:
                mock_validator = Mock()
                mock_validator.validate_token.return_value = self.jwt_payload
                mock_get_jwt_validator.return_value = mock_validator
                
                response = calculate.lambda_handler(request_invalid_date, {})
                
                self.assertEqual(response['statusCode'], 400)
                body = json.loads(response['body'])
                self.assertFalse(body['success'])
