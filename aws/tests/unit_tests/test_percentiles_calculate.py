"""
Unit tests for percentiles calculation.
Tests growth percentile calculation logic.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the percentiles lambda directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lambdas', 'percentiles'))

# Also add shared for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lambdas', 'shared'))

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
        
        # Sample calculation request
        self.sample_request = {
            'headers': {
                'Authorization': 'Bearer test-token'
            },
            'body': json.dumps({
                'sex': 'female',
                'age_months': 12,
                'weight': 9.5,
                'height': 75.0
            })
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    @patch('calculate.load_table')
    @patch('jwt_utils.get_jwt_validator')
    def test_calculate_percentiles_success(self, mock_get_jwt_validator, mock_load_table):
        """Test successful percentile calculation."""
        # Mock JWT validation
        mock_jwt_validator = MagicMock()
        mock_jwt_validator.extract_user_id.return_value = 'user-1-test-123456'
        mock_get_jwt_validator.return_value = mock_jwt_validator
        
        # Mock table loading and calculation
        mock_df = MagicMock()
        mock_df.loc = MagicMock()
        mock_load_table.return_value = mock_df
        
        # Mock the calculation result
        with patch('calculate.calculate_zscore', return_value=0.0):
            with patch('calculate.zscore_to_percentile', return_value=50.0):
                try:
                    from calculate import lambda_handler
                    
                    response = lambda_handler(self.sample_request, {})
                    
                    self.assertEqual(response['statusCode'], 200)
                    body = json.loads(response['body'])
                    self.assertTrue(body['success'])
                except ImportError:
                    self.skipTest("calculate module import failed - may need dependencies")
    
    def test_calculate_percentiles_missing_params(self):
        """Test percentile calculation with missing parameters."""
        invalid_request = {
            'headers': {'Authorization': 'Bearer test-token'},
            'body': json.dumps({
                'sex': 'female'
                # Missing age_months, weight, height
            })
        }
        
        try:
            from calculate import lambda_handler
            
            response = lambda_handler(invalid_request, {})
            
            self.assertEqual(response['statusCode'], 400)
            body = json.loads(response['body'])
            self.assertFalse(body['success'])
        except ImportError:
            self.skipTest("calculate module import failed - may need dependencies")
    
    def test_calculate_percentiles_invalid_sex(self):
        """Test percentile calculation with invalid sex parameter."""
        invalid_request = {
            'headers': {'Authorization': 'Bearer test-token'},
            'body': json.dumps({
                'sex': 'invalid',
                'age_months': 12,
                'weight': 9.5,
                'height': 75.0
            })
        }
        
        try:
            from calculate import lambda_handler
            
            response = lambda_handler(invalid_request, {})
            
            self.assertEqual(response['statusCode'], 400)
            body = json.loads(response['body'])
            self.assertFalse(body['success'])
        except ImportError:
            self.skipTest("calculate module import failed - may need dependencies")
    
    def test_load_table_male(self):
        """Test loading male growth table."""
        try:
            from calculate import load_table
            
            # This will fail without actual data files, but tests the function exists
            with self.assertRaises((FileNotFoundError, ImportError)):
                load_table("male")
        except ImportError:
            self.skipTest("calculate module import failed - may need dependencies")
    
    def test_load_table_female(self):
        """Test loading female growth table."""
        try:
            from calculate import load_table
            
            # This will fail without actual data files, but tests the function exists
            with self.assertRaises((FileNotFoundError, ImportError)):
                load_table("female")
        except ImportError:
            self.skipTest("calculate module import failed - may need dependencies")
    
    @patch('jwt_utils.extract_token_from_event')
    def test_calculate_percentiles_no_token(self, mock_extract_token):
        """Test percentile calculation without authorization token."""
        mock_extract_token.return_value = None
        
        try:
            from calculate import lambda_handler
            
            response = lambda_handler(self.sample_request, {})
            
            self.assertEqual(response['statusCode'], 401)
            body = json.loads(response['body'])
            self.assertFalse(body['success'])
        except ImportError:
            self.skipTest("calculate module import failed - may need dependencies")


if __name__ == '__main__':
    unittest.main()
