"""
Lambda function to update a baby profile.
PUT /babies/{babyId}
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
    success_response, bad_request_response, unauthorized_response,
    not_found_response, internal_error_response, handle_lambda_error
)
from validation_utils import BabyValidator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event, context):
    """
    Update a baby profile.
    
    Path parameters:
    - babyId: UUID of the baby
    
    Request body:
    {
        "name": "Emma Updated",
        "dateOfBirth": "2023-06-15",
        "gender": "female",
        "premature": false,
        "gestationalWeek": null,
        "birthWeight": 3500,
        "birthHeight": 50
    }
    
    Response:
    {
        "success": true,
        "data": {
            "babyId": "uuid",
            "name": "Emma Updated",
            ...
        },
        "message": "Baby profile updated successfully"
    }
    """
    logger.info(f"Updating baby profile - Request ID: {context.aws_request_id}")
    
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
        return bad_request_response("Baby ID is required")
    
    # Parse request body
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    
    # Validate baby data
    try:
        validated_data = BabyValidator.validate_baby_data(body, is_update=True)
    except Exception as e:
        return bad_request_response(f"Validation failed: {str(e)}")
    
    # Check if baby exists and user owns it
    try:
        existing_baby = dynamodb_client.get_item('babies', {'babyId': baby_id})
        
        if not existing_baby:
            return not_found_response("Baby not found")
        
        # Verify ownership
        if existing_baby.get('userId') != user_id:
            return not_found_response("Baby not found")
        
        # Check if baby is active
        if not existing_baby.get('isActive', True):
            return not_found_response("Baby not found")
    except Exception as e:
        logger.error(f"Error checking baby existence: {e}")
        return internal_error_response("Failed to update baby profile")
    
    # Build update expression
    update_expressions = []
    expression_values = {}
    
    for key, value in validated_data.items():
        update_expressions.append(f"{key} = :{key}")
        expression_values[f":{key}"] = value
    
    # Add updatedAt timestamp
    current_time = datetime.utcnow().isoformat() + 'Z'
    update_expressions.append("updatedAt = :updatedAt")
    expression_values[":updatedAt"] = current_time
    
    update_expression = "SET " + ", ".join(update_expressions)
    
    # Update baby in DynamoDB
    try:
        dynamodb_client.update_item(
            table_name='babies',
            key={'babyId': baby_id},
            update_expression=update_expression,
            expression_values=expression_values
        )
        
        # Retrieve updated baby
        updated_baby = dynamodb_client.get_item('babies', {'babyId': baby_id})
        
        logger.info(f"Baby profile updated successfully: {baby_id}")
        
        return success_response(
            data=updated_baby,
            message="Baby profile updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating baby profile: {e}")
        return internal_error_response("Failed to update baby profile")
