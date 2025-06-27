# JWT Validation Implementation for UpNest Lambda Functions

## Overview

This implementation adds JWT (JSON Web Token) validation to AWS Lambda functions to secure API endpoints. The validation ensures that only authenticated users with valid Cognito tokens can access protected resources.

## Components

### 1. JWT Validator Module (`jwt_validator.py`)

Located at: `aws/lambdas/percentile/jwt_validator.py`

**Key Features:**
- Validates JWT tokens issued by AWS Cognito
- Fetches and caches JWKS (JSON Web Key Set) from Cognito
- Provides decorator for easy authentication integration
- Returns proper HTTP responses for unauthorized access

**Main Functions:**
- `validate_jwt_token(token)`: Validates a JWT token against Cognito JWKS
- `extract_token_from_event(event)`: Extracts Bearer token from API Gateway event
- `@require_jwt_auth`: Decorator to protect Lambda handlers

### 2. Updated Lambda Handler (`lambda_function.py`)

**Changes Made:**
- Added `@require_jwt_auth` decorator to `lambda_handler`
- Updated response format to include proper HTTP status codes and CORS headers
- Added user ID to response payload for tracking

### 3. Frontend Integration (`axiosClient.js`)

**Enhancements:**
- Automatic token attachment to all API requests
- Token refresh handling for expired tokens
- Integration with `react-oidc-context` for seamless authentication
- Fallback to localStorage for backward compatibility

### 4. SAM Template Updates (`template.yaml`)

**New Features:**
- Added Cognito configuration parameters
- Added environment variables for JWT validation
- Added API Gateway configuration with CORS support
- Added proper event mapping for HTTP endpoints

## Environment Variables Required

The following environment variables must be set for JWT validation to work:

```bash
COGNITO_USER_POOL_ID=your-user-pool-id
COGNITO_CLIENT_ID=your-client-id
COGNITO_REGION=your-aws-region (default: us-east-1)
```

## How It Works

### 1. Token Flow
1. User logs in through frontend (Cognito Hosted UI)
2. Frontend receives JWT access token
3. Frontend includes token in `Authorization: Bearer <token>` header
4. Lambda extracts and validates token against Cognito JWKS
5. If valid, request proceeds; if invalid, returns 401 Unauthorized

### 2. Token Validation Process
1. Extract token from Authorization header
2. Decode JWT header to get Key ID (kid)
3. Fetch JWKS from Cognito (cached after first request)
4. Find matching key by kid
5. Verify token signature using public key
6. Validate token claims (audience, issuer, expiration)
7. Extract user information for use in handler

### 3. Error Handling
- **401 Unauthorized**: Missing, invalid, or expired token
- **500 Internal Server Error**: JWT validation system errors
- Proper CORS headers included in all responses

## Security Features

- **Token Signature Verification**: Uses RSA256 with Cognito's public keys
- **Expiration Checking**: Automatically rejects expired tokens  
- **Audience Validation**: Ensures token was issued for correct client
- **Issuer Validation**: Verifies token came from correct Cognito User Pool
- **Key Rotation Support**: Dynamically fetches current JWKS

## Testing

Test files located at: `aws/tests/test_jwt_validation.py`

**Test Coverage:**
- Token extraction from various header formats
- JWKS retrieval and caching
- Key lookup by ID
- Decorator functionality
- Error handling scenarios

Run tests with:
```bash
cd aws/tests
python -m pytest test_jwt_validation.py -v
```

## Deployment

1. **Install Dependencies**:
   ```bash
   cd aws/lambdas/percentile
   pip install -r requirements.txt
   ```

2. **Deploy with SAM**:
   ```bash
   sam build
   sam deploy --parameter-overrides \
     CognitoUserPoolId=your-pool-id \
     CognitoClientId=your-client-id \
     CognitoRegion=your-region
   ```

3. **Update Frontend Configuration**:
   - Ensure `axiosClient.js` points to new API Gateway URL
   - Verify CORS settings allow your frontend domain

## API Usage Examples

### Valid Request
```bash
curl -X POST https://your-api-gateway/Prod/percentile \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Q..." \
  -H "Content-Type: application/json" \
  -d '{
    "weight": 10.5,
    "date_birth": "2023-01-01",
    "date_measurement": "2024-01-01", 
    "sex": "male"
  }'
```

### Response with User Info
```json
{
  "percentile": 75.2,
  "zscore": 0.68,
  "LMS": {"L": 0.1, "M": 10.2, "S": 0.15},
  "user_id": "cognito-user-sub-id",
  "success": true
}
```

### Unauthorized Response
```json
{
  "error": "Unauthorized",
  "message": "Missing Authorization header",
  "success": false
}
```

## Next Steps

1. **Add User Data Persistence**: Store user-specific data using `user_id`
2. **Implement Role-Based Access**: Add user roles for different access levels
3. **Add Rate Limiting**: Prevent abuse by implementing request rate limits
4. **Monitor Usage**: Add CloudWatch metrics for token validation
5. **Implement Refresh Token Flow**: Handle long-lived sessions securely

## Troubleshooting

### Common Issues:

1. **"Unable to find JWK with kid"**: 
   - Check Cognito User Pool ID is correct
   - Verify region matches Cognito setup

2. **"Token has expired"**:
   - Implement token refresh in frontend
   - Check token lifetime settings in Cognito

3. **CORS Errors**:
   - Verify API Gateway CORS configuration
   - Check preflight OPTIONS handling

4. **"Invalid token"**:
   - Ensure token is from correct User Pool
   - Verify client ID matches configuration
