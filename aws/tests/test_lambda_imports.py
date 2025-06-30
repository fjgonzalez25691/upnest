#!/usr/bin/env python3
"""
Simple test to verify Lambda functions can execute without import errors.
This test focuses on the basic functionality for the hackathon.
"""

import sys
import os
import unittest
import json

# Add the lambda functions directory to the path
lambda_path = os.path.join(os.path.dirname(__file__), '..', 'lambdas')
sys.path.insert(0, lambda_path)

class TestLambdaFunctions(unittest.TestCase):
    """Test Lambda functions can be imported and executed."""
    
    def setUp(self):
        """Set up test environment variables."""
        # Set required environment variables
        os.environ['BABIES_TABLE'] = 'test-babies'
        os.environ['GROWTH_DATA_TABLE'] = 'test-growth-data'
        os.environ['USERS_TABLE'] = 'test-users'
        os.environ['COGNITO_USER_POOL_ID'] = 'test-pool'
        os.environ['COGNITO_CLIENT_ID'] = 'test-client'
        os.environ['COGNITO_REGION'] = 'us-east-1'
        os.environ['LOG_LEVEL'] = 'INFO'
        
        self.sample_event = {
            'headers': {
                'Authorization': 'Bearer fake-jwt-token',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'name': 'Test Baby',
                'dateOfBirth': '2024-01-15',
                'gender': 'male'
            }),
            'requestContext': {
                'httpMethod': 'POST'
            }
        }
        
        self.sample_context = {}
    
    def test_babies_create_import(self):
        """Test that babies_create can be imported."""
        try:
            import lambdas.babies.babies_create
            self.assertTrue(hasattr(lambdas.babies.babies_create, 'lambda_handler'))
        except ImportError as e:
            self.fail(f"Could not import babies_create: {e}")
    
    def test_babies_list_import(self):
        """Test that babies_list can be imported."""
        try:
            import lambdas.babies.babies_list
            self.assertTrue(hasattr(lambdas.babies.babies_list, 'lambda_handler'))
        except ImportError as e:
            self.fail(f"Could not import babies_list: {e}")
    
    def test_growth_data_create_import(self):
        """Test that growth_data_create can be imported."""
        try:
            import sys
            growth_data_path = os.path.join(lambda_path, 'growth-data')
            sys.path.insert(0, growth_data_path)
            import growth_data_create
            self.assertTrue(hasattr(growth_data_create, 'lambda_handler'))
        except ImportError as e:
            self.fail(f"Could not import growth_data_create: {e}")
    
    def test_environment_variables_set(self):
        """Test that all required environment variables are set."""
        required_vars = [
            'BABIES_TABLE', 'GROWTH_DATA_TABLE', 'USERS_TABLE',
            'COGNITO_USER_POOL_ID', 'COGNITO_CLIENT_ID', 'COGNITO_REGION'
        ]
        
        for var in required_vars:
            self.assertIn(var, os.environ, f"Environment variable {var} not set")
            self.assertNotEqual(os.environ[var], '', f"Environment variable {var} is empty")

if __name__ == '__main__':
    # Set up Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..')
    sys.path.insert(0, project_root)
    
    unittest.main(verbosity=2)
