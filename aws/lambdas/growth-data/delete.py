"""
Lambda function to delete a growth data record.
DELETE /babies/{babyId}/growth/{dataId}
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
    Delete a growth data record (hard delete).
    
    Args:
        event: API Gateway event with JWT token, babyId and dataId in path
        context: Lambda context
        
    Returns:
        dict: HTTP response with deletion confirmation
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
    
    # Extract path parameters
    path_params = event.get('pathParameters') or {}
    baby_id = path_params.get('babyId')
    data_id = path_params.get('dataId')
    
    if not baby_id or not data_id:
        logger.warning("Missing babyId or dataId in path parameters")
        return bad_request_response("Missing babyId or dataId in path parameters")
    
    # Validate ID formats
    if not is_valid_uuid(baby_id) or not is_valid_uuid(data_id):
        logger.warning(f"Invalid ID format - babyId: {baby_id}, dataId: {data_id}")
        return bad_request_response("Invalid ID format")
    
    try:
        # First verify the growth data record exists and belongs to user's baby
        growth_response = dynamodb_client.get_item(
            TableName='GrowthData',
            Key={
                'dataId': {'S': data_id}
            }
        )
        
        if 'Item' not in growth_response:
            logger.warning(f"Growth data not found: {data_id}")
            return not_found_response("Growth data record not found")
        
        growth_item = growth_response['Item']
        
        # Verify the growth data belongs to the specified baby
        if growth_item.get('babyId', {}).get('S', '') != baby_id:
            logger.warning(f"Growth data {data_id} does not belong to baby {baby_id}")
            return not_found_response("Growth data record not found")
        
        # Verify baby exists and belongs to user
        baby_response = dynamodb_client.get_item(
            TableName='Babies',
            Key={
                'babyId': {'S': baby_id}
            }
        )
        
        if 'Item' not in baby_response:
            logger.warning(f"Baby not found: {baby_id}")
            return not_found_response("Baby not found")
        
        baby_item = baby_response['Item']
        baby_user_id = baby_item.get('userId', {}).get('S', '')
        
        if baby_user_id != user_id:
            logger.warning(f"User {user_id} attempted to delete growth data for baby {baby_id} owned by {baby_user_id}")
            return not_found_response("Growth data record not found")
        
        # Check if baby is active (optional - we might want to allow deletion even for deleted babies for cleanup)
        if not baby_item.get('isActive', {'BOOL': True})['BOOL']:
            logger.info(f"Deleting growth data for inactive baby: {baby_id}")
        
        # Store record info for response before deletion
        measurement_date = growth_item.get('measurementDate', {}).get('S', '')
        measurement_type = growth_item.get('measurementType', {}).get('S', '')
        
        # Perform hard delete
        dynamodb_client.delete_item(
            TableName='GrowthData',
            Key={
                'dataId': {'S': data_id}
            }
        )
        
        logger.info(f"Growth data deleted successfully: {data_id} for baby {baby_id} by user {user_id}")
        
        return ok_response({
            'message': 'Growth data record deleted successfully',
            'dataId': data_id,
            'babyId': baby_id,
            'measurementDate': measurement_date,
            'measurementType': measurement_type,
            'deletedAt': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error deleting growth data {data_id}: {str(e)}")
        return internal_error_response("Failed to delete growth data record")
