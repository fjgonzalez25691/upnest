"""
Unit tests for JWT validation utilities.
Tests JWT token validation, user extraction, and error handling.
"""

import unittest
from unittest.mock import patch, MagicMock
import jwt
import json
import os
import sys

# Add the shared directory to the path (jwt_utils is still in shared)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lambdas', 'shared'))

from jwt_utils import JWTValidator, extract_token_from_event

class TestJWTValidator(unittest.TestCase):
    """Test cases for JWT validation utilities."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'COGNITO_USER_POOL_ID': 'test-pool-id',
            'COGNITO_CLIENT_ID': 'test-client-id',
            'COGNITO_REGION': 'eu-south-2'
        })
        self.env_patcher.start()
        
        # Create validator instance
        self.validator = JWTValidator()
        
        # Sample JWT payload
        self.sample_payload = {
            'sub': 'user-1-test-123456',
            'email': 'user1@test.com',
            'name': 'Test User',
            'email_verified': True,
            'token_use': 'access',
            'auth_time': 1640995200,
            'exp': 1640998800,
            'aud': 'test-client-id',
            'iss': 'https://cognito-idp.eu-south-2.amazonaws.com/test-pool-id'
        }
        
        # Sample JWT header
        self.sample_header = {
            'kid': 'test-key-id',
            'alg': 'RS256',
            'typ': 'JWT'
        }
        
        # Sample JWKS response
        self.sample_jwks = {
            'keys': [
                {
                    'kid': 'test-key-id',
                    'kty': 'RSA',
                    'use': 'sig',
                    'n': 'test-modulus',
                    'e': 'AQAB'
                }
            ]
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    def test_init_with_missing_environment_variables(self):
        """Test validator initialization with missing environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                JWTValidator()
            self.assertIn("Missing Cognito configuration", str(context.exception))
    
    @patch('jwt_utils.requests.get')
    def test_get_jwks_success(self, mock_get):
        """Test successful JWKS retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_jwks
        mock_get.return_value = mock_response
        
        jwks = self.validator.get_jwks()
        
        self.assertEqual(jwks, self.sample_jwks)
        mock_get.assert_called_once_with(
            f"https://cognito-idp.eu-south-2.amazonaws.com/test-pool-id/.well-known/jwks.json",
            timeout=10
        )
    
    @patch.object(JWTValidator, 'extract_user_id')
    def test_extract_user_id_success(self, mock_extract):
        """Test successful user ID extraction."""
        mock_extract.return_value = 'user-1-test-123456'
        
        user_id = self.validator.extract_user_id('test-token')
        
        self.assertEqual(user_id, 'user-1-test-123456')


class TestExtractTokenFromEvent(unittest.TestCase):
    """Test cases for token extraction from API Gateway events."""
    
    def test_extract_token_from_authorization_header(self):
        """Test token extraction from Authorization header."""
        event = {
            'headers': {
                'Authorization': 'Bearer test-token-123'
            }
        }
        
        token = extract_token_from_event(event)
        self.assertEqual(token, 'test-token-123')
    
    def test_extract_token_from_query_params(self):
        """Test token extraction from query parameters."""
        event = {
            'headers': {},
            'queryStringParameters': {
                'token': 'test-token-789'
            }
        }
        
        token = extract_token_from_event(event)
        self.assertEqual(token, 'test-token-789')
    
    def test_extract_token_no_token_found(self):
        """Test token extraction when no token is found."""
        event = {
            'headers': {},
            'queryStringParameters': {}
        }
        
        token = extract_token_from_event(event)
        self.assertIsNone(token)


if __name__ == '__main__':
    unittest.main()
