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

from dynamodb_client import get_dynamodb_client
from jwt_utils import get_jwt_validator, extract_token_from_event
from response_utils import (
    success_response, bad_request_response, unauthorized_response,
    not_found_response, internal_error_response, handle_lambda_error
)
from validation_utils import Validator

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
    request_id = getattr(context, 'aws_request_id', 'test-request')
    logger.info(f"Deleting baby profile - Request ID: {request_id}")
    
    # Extract and validate JWT token
    token = extract_token_from_event(event)
    if not token:
        return unauthorized_response("Authorization token is required")
    
    try:
        jwt_validator = get_jwt_validator()
        user_id = jwt_validator.extract_user_id(token)
        logger.info(f"Authenticated user: {user_id}")
    except ValueError as e:
        return unauthorized_response(str(e))
    
    # Get baby ID from path parameters
    path_parameters = event.get('pathParameters') or {}
    baby_id = path_parameters.get('babyId')
    if not baby_id:
        return bad_request_response("Baby ID is required")
    
    # Validate babyId format
    try:
        Validator.validate_uuid(baby_id, "Baby ID")
    except Exception as e:
        return bad_request_response(f"Invalid baby ID: {str(e)}")
    
    try:
        dynamodb_client = get_dynamodb_client()
        
        # Check if baby exists and user owns it
        existing_baby = dynamodb_client.get_item('babies', {'babyId': baby_id})
        
        if not existing_baby:
            return not_found_response("Baby not found")
        
        # Verify ownership
        if existing_baby.get('userId') != user_id:
            return not_found_response("Baby not found")
        
        # Check if baby is already deleted
        if not existing_baby.get('isActive', True):
            return bad_request_response("Baby already deleted")
        
        # Perform soft delete
        current_time = datetime.utcnow().isoformat() + 'Z'
        
        update_expression = "SET isActive = :is_active, updatedAt = :updated_at, deletedAt = :deleted_at"
        expression_values = {
            ":is_active": False,
            ":updated_at": current_time,
            ":deleted_at": current_time
        }
        
        dynamodb_client.update_item(
            table_name='babies',
            key={'babyId': baby_id},
            update_expression=update_expression,
            expression_values=expression_values
        )
        
        logger.info(f"Baby soft deleted successfully: {baby_id}")
        
        return success_response(
            data={
                'babyId': baby_id,
                'deletedAt': current_time
            },
            message='Baby deleted successfully'
        )
        
    except Exception as e:
        logger.error(f"Error deleting baby profile: {e}")
        return internal_error_response("Failed to delete baby profile")
