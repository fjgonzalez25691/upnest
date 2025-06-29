"""
Lambda function to get a baby profile by ID.
GET /babies/{babyId}
"""

import json
import logging
import sys
import os

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from dynamodb_client import dynamodb_client
from jwt_utils import jwt_validator, extract_token_from_event
from response_utils import (
    success_response, unauthorized_response, not_found_response,
    handle_lambda_error
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event, context):
    """
    Get a baby profile by ID.
    
    Path parameters:
    - babyId: UUID of the baby
    
    Response:
    {
        "success": true,
        "data": {
            "babyId": "uuid",
            "name": "Emma",
            "dateOfBirth": "2023-06-15",
            "gender": "female",
            ...
        }
    }
    """
    logger.info(f"Getting baby profile - Request ID: {context.aws_request_id}")
    
    # Extract and validate JWT token
    token = extract_token_from_event(event)
    if not token:
        return unauthorized_response("Authorization token is required")
    
    try:
        user_id = jwt_validator.extract_user_id(token)
        logger.info(f"Authenticated user: {user_id}")
    except ValueError as e:
        return unauthorized_response(str(e))
    
    # Get baby ID from path parameters
    baby_id = event.get('pathParameters', {}).get('babyId')
    if not baby_id:
        return not_found_response("Baby ID is required")
    
    # Retrieve baby from DynamoDB
    try:
        baby = dynamodb_client.get_item('babies', {'babyId': baby_id})
        
        if not baby:
            return not_found_response("Baby not found")
        
        # Verify ownership - user can only access their own babies
        if baby.get('userId') != user_id:
            return not_found_response("Baby not found")
        
        # Check if baby is active
        if not baby.get('isActive', True):
            return not_found_response("Baby not found")
        
        logger.info(f"Baby profile retrieved successfully: {baby_id}")
        return success_response(data=baby)
        
    except Exception as e:
        logger.error(f"Error retrieving baby profile: {e}")
        return not_found_response("Baby not found")
