"""
Base test class for percentiles tests.
Contains shared setup and configuration.
"""

import unittest
from unittest.mock import patch
import json
import sys
import os

# Add the percentiles lambda directory to the path (absolute path)
percentiles_path = r"d:\proyectos\AWSLambdaHackathon\upnest\aws\lambdas\percentiles"
sys.path.insert(0, percentiles_path)

# Also add shared for imports (absolute path)
shared_path = r"d:\proyectos\AWSLambdaHackathon\upnest\aws\lambdas\shared"
sys.path.insert(0, shared_path)

# import percentiles_calculate as calculate module directly
import percentiles_calculate as calculate

class BasePercentilesTest(unittest.TestCase):
    """Base test class with common setup for percentiles tests."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'COGNITO_USER_POOL_ID': 'test-pool-id',
            'COGNITO_CLIENT_ID': 'test-client-id',
            'COGNITO_REGION': 'eu-south-2'
        })
        self.env_patcher.start()
        
        # Clear global cache
        calculate._data_cache.clear()
        calculate._jwt_validator = None
        
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
        
        # Mock growth table data (as dict, will be converted to DataFrame by mocks)
        self.mock_growth_data = {
            'Day': [91, 92, 93],  # ~3 months (corrected from 90 to 91)
            'L': [0.3487, 0.3487, 0.3487],
            'M': [4.5, 4.52, 4.54],
            'S': [0.13, 0.13, 0.13]
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    def create_mock_dataframe(self, data_override=None):
        """Create a mock DataFrame for testing."""
        from unittest.mock import Mock, MagicMock
        
        data = data_override or self.mock_growth_data
        
        mock_df = Mock()
        
        # Mock the loc accessor for DataFrame operations
        mock_loc = Mock()
        mock_df.loc = mock_loc
        
        # Mock exact match scenario (returns a row)
        mock_row = Mock()
        mock_row.empty = False
        mock_row.iloc = Mock()
        mock_row.iloc.__getitem__ = Mock(side_effect=lambda x: [data['L'][0], data['M'][0], data['S'][0]])
        
        # Mock no exact match scenario (returns empty)
        mock_empty_row = Mock()
        mock_empty_row.empty = True
        
        # Configure loc to return appropriate results
        mock_loc.__getitem__ = Mock(return_value=mock_row)
        
        # Mock column access for finding closest day
        mock_day_column = Mock()
        mock_day_column.sub = Mock(return_value=Mock(
            abs=Mock(return_value=Mock(
                idxmin=Mock(return_value=0)
            ))
        ))
        mock_df.__getitem__ = Mock(return_value=mock_day_column)
        
        # Mock iloc for accessing specific rows
        mock_iloc = Mock()
        mock_iloc.__getitem__ = Mock(return_value=Mock(values=[data['L'][0], data['M'][0], data['S'][0]]))
        mock_df.iloc = mock_iloc
        
        return mock_df
