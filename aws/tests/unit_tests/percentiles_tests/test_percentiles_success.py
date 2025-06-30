"""
Tests for successful percentile calculations.
Tests weight, height, and head circumference calculations.
"""

from unittest.mock import patch, Mock
import json
from .test_base import BasePercentilesTest
import calculate

class TestPercentilesSuccess(BasePercentilesTest):
    """Test cases for successful percentile calculations."""
    
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
        
        # Mock table loading
        mock_load_table.return_value = self.create_mock_dataframe()
        
        # Mock LMS values function
        mock_find_lms.return_value = (0.3487, 4.5, 0.13)
        
        # Call the lambda function
        response = calculate.lambda_handler(self.weight_request, {})
        
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
    
    @patch('calculate.find_lms_values')
    @patch('calculate.extract_token_from_event')
    @patch('calculate.get_jwt_validator')
    @patch('calculate.load_table')
    def test_calculate_height_percentile_success(self, mock_load_table, mock_get_jwt_validator, mock_extract_token, mock_find_lms):
        """Test successful height percentile calculation."""
        # Mock token extraction
        mock_extract_token.return_value = "test-token"
        
        # Mock JWT validation
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_get_jwt_validator.return_value = mock_validator
        
        # Mock table loading with height-appropriate data
        height_data = self.mock_growth_data.copy()
        height_data['M'] = [55.0, 55.2, 55.4]  # Height values in cm
        mock_load_table.return_value = self.create_mock_dataframe(height_data)
        
        # Mock LMS values function
        mock_find_lms.return_value = (0.3487, 55.2, 0.13)
        
        # Call the lambda function
        response = calculate.lambda_handler(self.height_request, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        data = body['data']
        self.assertEqual(data['measurementType'], 'height')
        self.assertEqual(data['value'], 55.5)
        self.assertEqual(data['sex'], 'male')
        
        # Check basic response structure
        self.assertIn('percentile', data)
        self.assertIn('zscore', data)
        self.assertIn('LMS', data)
    
    @patch('calculate.find_lms_values')
    @patch('calculate.extract_token_from_event')
    @patch('calculate.get_jwt_validator')
    @patch('calculate.load_table')
    def test_calculate_head_circumference_percentile_success(self, mock_load_table, mock_get_jwt_validator, mock_extract_token, mock_find_lms):
        """Test successful head circumference percentile calculation."""
        # Mock token extraction
        mock_extract_token.return_value = "test-token"
        
        # Mock JWT validation
        mock_validator = Mock()
        mock_validator.validate_token.return_value = self.jwt_payload
        mock_get_jwt_validator.return_value = mock_validator
        
        # Mock table loading with head circumference-appropriate data
        head_data = self.mock_growth_data.copy()
        head_data['M'] = [40.0, 40.1, 40.2]  # Head circumference values in cm
        mock_load_table.return_value = self.create_mock_dataframe(head_data)
        
        # Mock LMS values function
        mock_find_lms.return_value = (0.3487, 40.1, 0.13)
        
        # Call the lambda function
        response = calculate.lambda_handler(self.head_circ_request, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        
        data = body['data']
        self.assertEqual(data['measurementType'], 'headCircumference')
        self.assertEqual(data['value'], 40.2)
        self.assertEqual(data['sex'], 'female')
        
        # Check basic response structure
        self.assertIn('percentile', data)
        self.assertIn('zscore', data)
        self.assertIn('LMS', data)
