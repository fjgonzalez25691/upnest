"""
Lambda function to list all babies for a user.
GET /babies
"""

import json
import logging
import sys
import os

# Add shared utilities to path
current_dir = os.path.dirname(os.path.abspath(__file__))
shared_dir = os.path.join(current_dir, '..', 'shared')
sys.path.insert(0, shared_dir)

try:
    from dynamodb_client import dynamodb_client
    from jwt_utils import jwt_validator, extract_token_from_event
    from response_utils import (
        success_response, unauthorized_response, handle_lambda_error
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback for testing without shared modules
    def handle_lambda_error(func):
        return func
    def success_response(data=None, metadata=None):
        return {
            'statusCode': 200,
            'body': json.dumps({'success': True, 'data': data, 'metadata': metadata})
        }
    def unauthorized_response(message):
        return {
            'statusCode': 401,
            'body': json.dumps({'success': False, 'error': message})
        }

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event, context):
    """
    List all active babies for the authenticated user.
    
    Query parameters (optional):
    - limit: Maximum number of babies to return (default: 50)
    - orderBy: 'name' or 'dateOfBirth' (default: 'name')
    - order: 'asc' or 'desc' (default: 'asc')
    
    Response:
    {
        "success": true,
        "data": [
            {
                "babyId": "uuid",
                "name": "Emma",
                "dateOfBirth": "2023-06-15",
                "gender": "female",
                ...
            }
        ],
        "count": 1
    }
    """
    logger.info(f"Listing babies for user - Request ID: {context.aws_request_id}")
    
    # Extract and validate JWT token
    token = extract_token_from_event(event)
    if not token:
        return unauthorized_response("Authorization token is required")
    
    try:
        user_id = jwt_validator.extract_user_id(token)
        logger.info(f"Authenticated user: {user_id}")
    except ValueError as e:
        return unauthorized_response(str(e))
    
    # Parse query parameters
    query_params = event.get('queryStringParameters') or {}
    limit = min(int(query_params.get('limit', 50)), 100)  # Max 100 items
    order_by = query_params.get('orderBy', 'name')
    order = query_params.get('order', 'asc')
    
    # Query babies using GSI (UserIndex)
    try:
        from boto3.dynamodb.conditions import Key
        
        babies = dynamodb_client.query_gsi(
            table_name='babies',
            index_name='UserIndex',
            key_condition=Key('userId').eq(user_id),
            expression_values={},
            limit=limit
        )
        
        # Filter only active babies
        active_babies = [baby for baby in babies if baby.get('isActive', True)]
        
        # Sort babies based on parameters
        if order_by == 'dateOfBirth':
            active_babies.sort(
                key=lambda x: x.get('dateOfBirth', ''), 
                reverse=(order == 'desc')
            )
        else:  # default to name
            active_babies.sort(
                key=lambda x: x.get('name', '').lower(), 
                reverse=(order == 'desc')
            )
        
        logger.info(f"Retrieved {len(active_babies)} babies for user {user_id}")
        
        return success_response(
            data=active_babies,
            metadata={'count': len(active_babies)}
        )
        
    except Exception as e:
        logger.error(f"Error listing babies: {e}")
        return success_response(data=[], metadata={'count': 0})
