"""
Lambda function to create a new baby profile.
POST /babies
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
    created_response, bad_request_response, unauthorized_response,
    internal_error_response, handle_lambda_error
)
from validation_utils import BabyValidator, generate_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event, context):
    """
    Create a new baby profile.
    
    Request body:
    {
        "name": "Emma",
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
            "name": "Emma",
            "dateOfBirth": "2023-06-15",
            "gender": "female",
            ...
        },
        "message": "Baby profile created successfully"
    }
    """
    logger.info(f"Creating new baby profile - Request ID: {context.aws_request_id}")
    
    # Extract and validate JWT token
    token = extract_token_from_event(event)
    if not token:
        return unauthorized_response("Authorization token is required")
    
    try:
        user_id = jwt_validator.extract_user_id(token)
        logger.info(f"Authenticated user: {user_id}")
    except ValueError as e:
        return unauthorized_response(str(e))
    
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
        validated_data = BabyValidator.validate_baby_data(body)
    except Exception as e:
        return bad_request_response(f"Validation failed: {str(e)}")
    
    # Generate baby ID and add metadata
    baby_id = generate_id()
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    baby_record = {
        'babyId': baby_id,
        'userId': user_id,
        'isActive': True,
        'createdAt': current_time,
        'updatedAt': current_time,
        **validated_data
    }
    
    # Store in DynamoDB
    try:
        dynamodb_client.put_item('babies', baby_record)
        logger.info(f"Baby profile created successfully: {baby_id}")
    except Exception as e:
        logger.error(f"Error creating baby profile: {e}")
        return internal_error_response("Failed to create baby profile")
    
    return created_response(
        data=baby_record,
        message="Baby profile created successfully"
    )
