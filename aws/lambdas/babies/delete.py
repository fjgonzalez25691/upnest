"""
Lambda function to delete a baby profile (soft delete).
DELETE /babies/{babyId}
"""

import json
import logging
from datetime import datetime
import sys
import os

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from dynamodb_client import dynamodb_client
from jwt_utils import jwt_validator, extract_token_from_event
from response_utils import (
    ok_response, bad_request_response, unauthorized_response,
    not_found_response, internal_error_response, handle_lambda_error
)
from validation_utils import is_valid_uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event, context):
    """
    Soft delete a baby profile.
    
    Args:
        event: API Gateway event with JWT token and babyId in path
        context: Lambda context
        
    Returns:
        dict: HTTP response with status and body
    """
    
    # Extract and validate JWT token
    token = extract_token_from_event(event)
    if not token:
        logger.warning("Missing Authorization token")
        return unauthorized_response("Missing Authorization token")
    
    # Validate JWT and extract user info
    jwt_payload = jwt_validator.validate_token(token)
    if not jwt_payload:
        logger.warning("Invalid JWT token")
        return unauthorized_response("Invalid or expired token")
    
    user_id = jwt_payload.get('sub')
    if not user_id:
        logger.error("Missing 'sub' claim in JWT token")
        return unauthorized_response("Invalid token: missing user ID")
    
    # Extract babyId from path parameters
    path_params = event.get('pathParameters') or {}
    baby_id = path_params.get('babyId')
    
    if not baby_id:
        logger.warning("Missing babyId in path parameters")
        return bad_request_response("Missing babyId in path parameters")
    
    # Validate babyId format
    if not is_valid_uuid(baby_id):
        logger.warning(f"Invalid babyId format: {baby_id}")
        return bad_request_response("Invalid babyId format")
    
    try:
        # First check if baby exists and belongs to user
        get_response = dynamodb_client.get_item(
            TableName='Babies',
            Key={
                'babyId': {'S': baby_id}
            }
        )
        
        if 'Item' not in get_response:
            logger.warning(f"Baby not found: {baby_id}")
            return not_found_response("Baby not found")
        
        baby_item = get_response['Item']
        
        # Check if baby already deleted
        if baby_item.get('isActive', {'BOOL': True})['BOOL'] == False:
            logger.warning(f"Baby already deleted: {baby_id}")
            return bad_request_response("Baby already deleted")
        
        # Check ownership
        baby_user_id = baby_item.get('userId', {}).get('S', '')
        if baby_user_id != user_id:
            logger.warning(f"User {user_id} attempted to delete baby {baby_id} owned by {baby_user_id}")
            return not_found_response("Baby not found")  # Don't reveal existence
        
        # Perform soft delete
        current_time = datetime.utcnow().isoformat()
        
        update_response = dynamodb_client.update_item(
            TableName='Babies',
            Key={
                'babyId': {'S': baby_id}
            },
            UpdateExpression='SET isActive = :is_active, modifiedAt = :modified_at, deletedAt = :deleted_at',
            ExpressionAttributeValues={
                ':is_active': {'BOOL': False},
                ':modified_at': {'S': current_time},
                ':deleted_at': {'S': current_time}
            },
            ReturnValues='ALL_NEW'
        )
        
        logger.info(f"Baby soft deleted successfully: {baby_id} by user {user_id}")
        
        # Return success response with deletion confirmation
        return ok_response({
            'message': 'Baby profile deleted successfully',
            'babyId': baby_id,
            'deletedAt': current_time
        })
        
    except Exception as e:
        logger.error(f"Error deleting baby {baby_id}: {str(e)}")
        return internal_error_response("Failed to delete baby profile")
