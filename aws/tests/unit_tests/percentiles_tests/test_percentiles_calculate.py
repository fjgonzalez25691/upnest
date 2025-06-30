"""
Unit tests for percentiles calculation lambda function.
Tests growth percentile calculation for weight, height, and head circumference.
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

class TestPercentilesCalculate(unittest.TestCase):
    """Test cases for percentiles calculation."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'COGNITO_USER_POOL_ID': 'test-pool-id',
            'COGNITO_CLIENT_ID': 'test-client-id',
            'COGNITO_REGION': 'eu-south-2'
        })
        self.env_patcher.start()
        
        # Clear any cached modules/data if needed
        if 'calculate' in sys.modules:
            if hasattr(sys.modules['calculate'], '_data_cache'):
                sys.modules['calculate']._data_cache.clear()
            if hasattr(sys.modules['calculate'], '_jwt_validator'):
                sys.modules['calculate']._jwt_validator = None
        
        # Mock JWT payload
        self.jwt_payload = {
            'sub': '550e8400-e29b-41d4-a716-446655440000',
            'email': 'test@example.com',
            'email_verified': True
        }
        
        # Sample calculation requests
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
        
        self.height_request = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps({
                'measurementType': 'height',
                'value': 55.5,  # cm
                'birthDate': '2024-01-15',
                'measurementDate': '2024-04-15',
                'sex': 'male'
            })
        }
        
        self.head_circ_request = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps({
                'measurementType': 'headCircumference',
                'value': 40.2,  # cm
                'birthDate': '2024-01-15',
                'measurementDate': '2024-04-15',
                'sex': 'female'
            })
        }
        
        # Mock growth table data (as dict, not DataFrame)
        self.mock_growth_data = {
            'Day': [91, 92, 93],  # ~3 months (corrected from 90 to 91)
            'L': [0.3487, 0.3487, 0.3487],
            'M': [4.5, 4.52, 4.54],
            'S': [0.13, 0.13, 0.13]
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    @patch('calculate.extract_token_from_event')
    @patch('calculate.get_jwt_validator')
    @patch('calculate.find_lms_values')
    def test_calculate_weight_percentile_success(self, mock_find_lms, mock_get_jwt_validator, mock_extract_token):
        """Test successful weight percentile calculation."""
        # Mock token extraction
        mock_extract_token.return_value = "test-token"
        
        # Mock JWT validation
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_get_jwt_validator.return_value = mock_validator
        
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
        
        # Check LMS values
        self.assertIn('L', data['LMS'])
        self.assertIn('M', data['LMS'])
        self.assertIn('S', data['LMS'])
    
    @patch('calculate.extract_token_from_event')
    @patch('calculate.get_jwt_validator')
    @patch('calculate.find_lms_values')
    def test_calculate_height_percentile_success(self, mock_find_lms, mock_get_jwt_validator, mock_extract_token):
        """Test successful height percentile calculation."""
        # Mock token extraction
        mock_extract_token.return_value = "test-token"
        
        # Mock JWT validation
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_get_jwt_validator.return_value = mock_validator
        
        # Mock LMS values finding with height-appropriate data
        mock_find_lms.return_value = (0.3487, 55.2, 0.13)
        
        # Call the lambda function
        from calculate import lambda_handler
        response = lambda_handler(self.height_request, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        data = body['data']
        self.assertEqual(data['measurementType'], 'height')
        self.assertEqual(data['value'], 55.5)
        self.assertEqual(data['sex'], 'male')
        self.assertEqual(data['ageInDays'], 91)
        
        # Check that percentile and zscore are calculated
        self.assertIn('percentile', data)
        self.assertIn('zscore', data)
        self.assertIn('LMS', data)
        
        # Percentile should be between 0 and 100
        self.assertGreaterEqual(data['percentile'], 0)
        self.assertLessEqual(data['percentile'], 100)
    
    @patch('calculate.extract_token_from_event')
    @patch('calculate.get_jwt_validator')
    @patch('calculate.find_lms_values')
    def test_calculate_head_circumference_percentile_success(self, mock_find_lms, mock_get_jwt_validator, mock_extract_token):
        """Test successful head circumference percentile calculation."""
        # Mock token extraction
        mock_extract_token.return_value = "test-token"
        
        # Mock JWT validation
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_get_jwt_validator.return_value = mock_validator
        
        # Mock LMS values finding with head circumference-appropriate data
        mock_find_lms.return_value = (0.3487, 40.1, 0.13)
        
        # Call the lambda function
        from calculate import lambda_handler
        response = lambda_handler(self.head_circ_request, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        data = body['data']
        self.assertEqual(data['measurementType'], 'headCircumference')
        self.assertEqual(data['value'], 40.2)
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
    
    @patch('calculate.extract_token_from_event')
    @patch('calculate.get_jwt_validator')
    def test_calculate_percentile_invalid_token(self, mock_get_jwt_validator, mock_extract_token):
        """Test percentile calculation with invalid token."""
        mock_extract_token.return_value = "invalid-token"
        
        mock_validator = Mock()
        mock_validator.validate_token.return_value = None
        mock_get_jwt_validator.return_value = mock_validator
        
        from calculate import lambda_handler
        response = lambda_handler(self.weight_request, {})
        
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
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
                
                from calculate import lambda_handler
                response = lambda_handler(request_missing_fields, {})
                
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
                
                from calculate import lambda_handler
                response = lambda_handler(request_invalid_type, {})
                
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
                
                from calculate import lambda_handler
                response = lambda_handler(request_invalid_sex, {})
                
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
                
                from calculate import lambda_handler
                response = lambda_handler(request_negative_value, {})
                
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
                
                from calculate import lambda_handler
                response = lambda_handler(request_future_birth, {})
                
                self.assertEqual(response['statusCode'], 400)
                body = json.loads(response['body'])
                self.assertFalse(body['success'])
    
    def test_calculate_zscore_function(self):
        """Test the z-score calculation function directly."""
        from calculate import calculate_zscore
        
        # Test normal case
        zscore = calculate_zscore(4.5, 0.3487, 4.5, 0.13)
        self.assertAlmostEqual(zscore, 0.0, places=1)
        
        # Test L=0 case
        zscore_l0 = calculate_zscore(4.5, 0.0, 4.5, 0.13)
        self.assertAlmostEqual(zscore_l0, 0.0, places=1)
    
    def test_zscore_to_percentile_function(self):
        """Test the z-score to percentile conversion function."""
        from calculate import zscore_to_percentile
        
        # Z-score of 0 should give 50th percentile
        percentile = zscore_to_percentile(0.0)
        self.assertAlmostEqual(percentile, 50.0, places=1)
        
        # Z-score of 1 should give approximately 84th percentile (with margin)
        percentile_positive = zscore_to_percentile(1.0)
        self.assertAlmostEqual(percentile_positive, 84.13, places=1)
        
        # Z-score of -1 should give approximately 16th percentile (with margin)
        percentile_negative = zscore_to_percentile(-1.0)
        self.assertAlmostEqual(percentile_negative, 15.87, places=1)
    
    def test_calculate_age_in_days_function(self):
        """Test the age calculation function."""
        from calculate import calculate_age_in_days
        
        # Test normal case
        age = calculate_age_in_days('2024-01-15', '2024-04-15')
        self.assertEqual(age, 91)  # 91 days between these dates
        
        # Test same date
        age_same = calculate_age_in_days('2024-01-15', '2024-01-15')
        self.assertEqual(age_same, 0)
        
        # Test one day difference
        age_one_day = calculate_age_in_days('2024-01-15', '2024-01-16')
        self.assertEqual(age_one_day, 1)
    
    def test_get_table_info_function(self):
        """Test the table info function."""
        from calculate import get_table_info
        
        # Test weight table info
        table_dir, filename = get_table_info('weight', 'male')
        self.assertEqual(table_dir, 'weight')
        self.assertEqual(filename, 'wfa-boys-zscore-expanded-tables.xlsx')
        
        table_dir, filename = get_table_info('weight', 'female')
        self.assertEqual(table_dir, 'weight')
        self.assertEqual(filename, 'wfa-girls-zscore-expanded-tables.xlsx')
        
        # Test height table info
        table_dir, filename = get_table_info('height', 'male')
        self.assertEqual(table_dir, 'height')
        self.assertEqual(filename, 'lhfa-boys-zscore-expanded-tables.xlsx')
        
        # Test head circumference table info
        table_dir, filename = get_table_info('headCircumference', 'female')
        self.assertEqual(table_dir, 'head-circumference')
        self.assertEqual(filename, 'hcfa-girls-zscore-expanded-tables.xlsx')
        
        # Test invalid measurement type
        with self.assertRaises(ValueError):
            get_table_info('invalid_type', 'male')
    
    def test_find_lms_values_function(self):
        """Test the LMS values finding function."""
        from calculate import find_lms_values
        import pandas as pd
        
        # Create a real DataFrame for testing
        test_data = {
            'Day': [89, 90, 91],
            'L': [0.3400, 0.3487, 0.3500],
            'M': [4.4, 4.5, 4.6],
            'S': [0.12, 0.13, 0.14]
        }
        df = pd.DataFrame(test_data)
        
        # Test exact match
        L, M, S = find_lms_values(df, 90)
        self.assertEqual(L, 0.3487)
        self.assertEqual(M, 4.5)
        self.assertEqual(S, 0.13)
        
        # Test closest match (should find closest)
        L2, M2, S2 = find_lms_values(df, 89)
        self.assertEqual(L2, 0.3400)
        self.assertEqual(M2, 4.4)
        self.assertEqual(S2, 0.12)


if __name__ == '__main__':
    unittest.main()
