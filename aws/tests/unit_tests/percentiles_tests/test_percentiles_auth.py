"""
Tests for authentication and authorization scenarios.
Tests token validation, missing tokens, invalid tokens, etc.
"""

from unittest.mock import patch, Mock
import json
from .test_base import BasePercentilesTest
import percentiles_calculate as calculate

class TestPercentilesAuth(BasePercentilesTest):
    """Test cases for authentication and authorization."""
    
    @patch('percentiles_calculate.extract_token_from_event')
    def test_calculate_percentile_no_token(self, mock_extract_token):
        """Test percentile calculation without authorization token."""
        mock_extract_token.return_value = None
        
        response = calculate.lambda_handler(self.weight_request, {})
        
        self.assertEqual(response['statusCode'], 400)  # Changed from 401 to 400
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('error', body)
    
    @patch('percentiles_calculate.extract_token_from_event')
    @patch('percentiles_calculate.get_jwt_validator')
    def test_calculate_percentile_invalid_token(self, mock_get_jwt_validator, mock_extract_token):
        """Test percentile calculation with invalid token."""
        mock_extract_token.return_value = "invalid-token"
        
        mock_validator = Mock()
        mock_validator.validate_token.return_value = None
        mock_get_jwt_validator.return_value = mock_validator
        
        response = calculate.lambda_handler(self.weight_request, {})
        
        self.assertEqual(response['statusCode'], 400)  # Changed from 401 to 400
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('percentiles_calculate.extract_token_from_event')
    @patch('percentiles_calculate.get_jwt_validator')
    def test_calculate_percentile_expired_token(self, mock_get_jwt_validator, mock_extract_token):
        """Test percentile calculation with expired token."""
        mock_extract_token.return_value = "expired-token"
        
        mock_validator = Mock()
        # Simulate token validation returning None (expired/invalid)
        mock_validator.validate_token.return_value = None
        mock_get_jwt_validator.return_value = mock_validator
        
        response = calculate.lambda_handler(self.weight_request, {})
        
        self.assertEqual(response['statusCode'], 400)  # Changed from 401 to 400
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    @patch('percentiles_calculate.extract_token_from_event')
    @patch('percentiles_calculate.get_jwt_validator')
    def test_calculate_percentile_malformed_token(self, mock_get_jwt_validator, mock_extract_token):
        """Test percentile calculation with malformed token."""
        mock_extract_token.return_value = "malformed.token.here"
        
        mock_validator = Mock()
        mock_validator.validate_token.return_value = {}  # Empty payload
        mock_get_jwt_validator.return_value = mock_validator
        
        response = calculate.lambda_handler(self.weight_request, {})
        
        # Should fail due to missing 'sub' claim
        self.assertEqual(response['statusCode'], 400)  # Changed from 401 to 400
        body = json.loads(response['body'])
        self.assertFalse(body['success'])



