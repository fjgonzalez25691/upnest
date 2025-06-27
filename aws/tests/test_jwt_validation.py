import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the lambda directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'percentile'))

from aws.lambdas.percentile.jwt_validator import (
    extract_token_from_event, 
    validate_jwt_token, 
    require_jwt_auth,
    find_jwk_by_kid
)
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the lambda directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'percentile'))

from ..lambdas.percentile.jwt_validator import (
    extract_token_from_event, 
    validate_jwt_token, 
    require_jwt_auth,
    find_jwk_by_kid
)

class TestJWTValidator(unittest.TestCase):

    def test_extract_token_from_event_success(self):
        """Test successful token extraction from event"""
        event = {
            'headers': {
                'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.test.token'
            }
        }
        
        token = extract_token_from_event(event)
        self.assertEqual(token, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.test.token')

    def test_extract_token_missing_header(self):
        """Test error when Authorization header is missing"""
        event = {'headers': {}}
        
        with self.assertRaises(ValueError) as cm:
            extract_token_from_event(event)
        self.assertIn('Missing Authorization header', str(cm.exception))

    def test_extract_token_invalid_format(self):
        """Test error when Authorization header doesn't start with Bearer"""
        event = {
            'headers': {
                'Authorization': 'Basic dGVzdDp0ZXN0'
            }
        }
        
        with self.assertRaises(ValueError) as cm:
            extract_token_from_event(event)
        self.assertIn('Authorization header must start with', str(cm.exception))

    def test_extract_token_case_insensitive_header(self):
        """Test case insensitive header extraction"""
        event = {
            'headers': {
                'authorization': 'Bearer test.token.here'
            }
        }
        
        token = extract_token_from_event(event)
        self.assertEqual(token, 'test.token.here')

    @patch('aws.lambdas.percentile.jwt_validator.requests.get')
    def test_get_jwks_success(self, mock_get):
        """Test successful JWKS retrieval"""
        from aws.lambdas.percentile.jwt_validator import get_jwks
        
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'keys': [
                {
                    'kid': 'test-key-id',
                    'kty': 'RSA',
                    'use': 'sig',
                    'n': 'test-n',
                    'e': 'AQAB'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Clear cache
        import aws.lambdas.percentile.jwt_validator as jwt_validator_module
        jwt_validator_module._jwks_cache = None
        
        jwks = get_jwks()
        self.assertIn('keys', jwks)
        self.assertEqual(jwks['keys'][0]['kid'], 'test-key-id')

    @patch('aws.lambdas.percentile.jwt_validator.get_jwks')
    def test_find_jwk_by_kid_success(self, mock_get_jwks):
        """Test successful JWK lookup by kid"""
        mock_get_jwks.return_value = {
            'keys': [
                {
                    'kid': 'key1',
                    'kty': 'RSA',
                    'use': 'sig'
                },
                {
                    'kid': 'key2', 
                    'kty': 'RSA',
                    'use': 'sig'
                }
            ]
        }
        
        jwk = find_jwk_by_kid('key2')
        self.assertEqual(jwk['kid'], 'key2')

    @patch('aws.lambdas.percentile.jwt_validator.get_jwks')
    def test_find_jwk_by_kid_not_found(self, mock_get_jwks):
        """Test JWK lookup when kid is not found"""
        mock_get_jwks.return_value = {
            'keys': [
                {
                    'kid': 'key1',
                    'kty': 'RSA',
                    'use': 'sig'
                }
            ]
        }
        
        with self.assertRaises(ValueError) as cm:
            find_jwk_by_kid('nonexistent-key')
        self.assertIn('Unable to find JWK', str(cm.exception))

    @patch.dict(os.environ, {
        'COGNITO_USER_POOL_ID': 'test-pool-id',
        'COGNITO_CLIENT_ID': 'test-client-id',
        'COGNITO_REGION': 'us-east-1'
    })
    def test_require_jwt_auth_decorator_missing_header(self):
        """Test decorator returns 401 when Authorization header is missing"""
        
        @require_jwt_auth
        def dummy_handler(event, context):
            return {'statusCode': 200, 'body': 'success'}
        
        event = {'headers': {}}
        context = {}
        
        response = dummy_handler(event, context)
        
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertEqual(body['error'], 'Unauthorized')
        self.assertIn('Missing Authorization header', body['message'])

    @patch.dict(os.environ, {
        'COGNITO_USER_POOL_ID': 'test-pool-id',
        'COGNITO_CLIENT_ID': 'test-client-id', 
        'COGNITO_REGION': 'us-east-1'
    })
    @patch('aws.lambdas.percentile.jwt_validator.validate_jwt_token')
    def test_require_jwt_auth_decorator_success(self, mock_validate):
        """Test decorator allows access with valid token"""
        
        # Mock successful token validation
        mock_validate.return_value = {
            'sub': 'user-123',
            'email': 'test@example.com',
            'cognito:username': 'testuser',
            'token_use': 'access'
        }
        
        @require_jwt_auth
        def dummy_handler(event, context):
            return {
                'statusCode': 200, 
                'body': json.dumps({
                    'message': 'success',
                    'user_id': event['user']['sub']
                })
            }
        
        event = {
            'headers': {
                'Authorization': 'Bearer valid.jwt.token'
            }
        }
        context = {}
        
        response = dummy_handler(event, context)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'success')
        self.assertEqual(body['user_id'], 'user-123')

if __name__ == '__main__':
    unittest.main()
