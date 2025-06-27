import jwt
import json
import requests
import os
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from functools import wraps

# Cognito configuration
COGNITO_REGION = os.environ.get('COGNITO_REGION', 'us-east-1')
COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')

# Cache for JWKS
_jwks_cache = None

def get_jwks():
    """Fetch JWKS from Cognito"""
    global _jwks_cache
    if _jwks_cache is None:
        jwks_url = f'https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json'
        response = requests.get(jwks_url)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache

def find_jwk_by_kid(kid):
    """Find the correct JWK by key ID"""
    jwks = get_jwks()
    for key in jwks['keys']:
        if key['kid'] == kid:
            return key
    raise ValueError(f"Unable to find JWK with kid: {kid}")

def validate_jwt_token(token):
    """
    Validate JWT token from AWS Cognito
    Returns decoded token payload if valid, raises exception if invalid
    """
    try:
        # Decode header to get key ID
        header = jwt.get_unverified_header(token)
        kid = header['kid']
        
        # Find the correct JWK
        jwk = find_jwk_by_kid(kid)
        
        # Convert JWK to public key
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
        
        # Decode and verify token
        decoded_token = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=COGNITO_CLIENT_ID,
            issuer=f'https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}'
        )
        
        return decoded_token
        
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    except InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")
    except Exception as e:
        raise ValueError(f"Token validation failed: {str(e)}")

def extract_token_from_event(event):
    """
    Extract JWT token from API Gateway event
    Looks for token in Authorization header
    """
    headers = event.get('headers', {})
    
    # Check for Authorization header (case insensitive)
    auth_header = None
    for key, value in headers.items():
        if key.lower() == 'authorization':
            auth_header = value
            break
    
    if not auth_header:
        raise ValueError("Missing Authorization header")
    
    # Expected format: "Bearer <token>"
    if not auth_header.startswith('Bearer '):
        raise ValueError("Authorization header must start with 'Bearer '")
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    if not token:
        raise ValueError("Empty token in Authorization header")
    
    return token

def require_jwt_auth(f):
    """
    Decorator to require JWT authentication for Lambda handlers
    """
    @wraps(f)
    def decorated_function(event, context):
        try:
            # Extract and validate token
            token = extract_token_from_event(event)
            decoded_token = validate_jwt_token(token)
            
            # Add user info to event for use in handler
            event['user'] = {
                'sub': decoded_token.get('sub'),
                'email': decoded_token.get('email'), 
                'username': decoded_token.get('cognito:username'),
                'token_use': decoded_token.get('token_use'),
                'decoded_token': decoded_token
            }
            
            # Call original function
            return f(event, context)
            
        except ValueError as e:
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Unauthorized',
                    'message': str(e),
                    'success': False
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Internal Server Error',
                    'message': 'JWT validation failed',
                    'success': False
                })
            }
    
    return decorated_function
