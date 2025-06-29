"""
Lambda function to create a new growth data record.
POST /growth-data
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
from validation_utils import GrowthDataValidator, generate_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event, context):
    """
    Create a new growth data record.
    
    Request body:
    {
        "babyId": "baby-uuid-123",
        "measurementDate": "2025-06-29",
        "measurements": {
            "weight": 4500,
            "height": 65.2,
            "headCircumference": 42.1
        },
        "notes": "Regular checkup - baby healthy",
        "measurementSource": "pediatrician"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "dataId": "uuid",
            "babyId": "baby-uuid-123",
            "userId": "user-cognito-sub",
            "measurementDate": "2025-06-29",
            "measurements": {...},
            "percentiles": {...},
            "zscores": {...}
        },
        "message": "Growth data created successfully"
    }
    """
    logger.info(f"Creating new growth data record - Request ID: {context.aws_request_id}")
    
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
    
    # Validate required fields
    required_fields = ['babyId', 'measurementDate', 'measurements']
    missing_fields = [field for field in required_fields if field not in body]
    if missing_fields:
        return bad_request_response(f"Missing required fields: {', '.join(missing_fields)}")
    
    baby_id = body['babyId']
    
    # Verify baby exists and belongs to user
    try:
        baby = dynamodb_client.get_item('babies', {'babyId': baby_id})
        
        if not baby:
            return bad_request_response("Baby not found")
        
        # ✅ CRITICAL: Verify baby belongs to authenticated user
        if baby.get('userId') != user_id:
            logger.warning(f"Unauthorized access: user {user_id} tried to add growth data for baby {baby_id}")
            return bad_request_response("Baby not found")
            
        if not baby.get('isActive', True):
            return bad_request_response("Baby not found")
            
    except Exception as e:
        logger.error(f"Error verifying baby ownership: {e}")
        return internal_error_response("Failed to verify baby")
    
    # Validate measurements
    try:
        validated_measurements = GrowthDataValidator.validate_measurements(body['measurements'])
    except Exception as e:
        return bad_request_response(f"Invalid measurements: {str(e)}")
    
    # Generate growth data ID and add metadata
    data_id = generate_id()
    current_time = datetime.utcnow().isoformat() + 'Z'
    
    # ✅ AUTOMATICALLY INCLUDE USER_ID IN GROWTH DATA RECORD
    growth_record = {
        'dataId': data_id,
        'babyId': baby_id,
        'userId': user_id,  # 🔥 CRITICAL: Associate growth data with authenticated user
        'measurementDate': body['measurementDate'],
        'measurements': validated_measurements,
        'percentiles': {},  # Will be calculated by percentile service
        'zscores': {},      # Will be calculated by percentile service
        'measurementSource': body.get('measurementSource', 'manual'),
        'deviceInfo': body.get('deviceInfo'),
        'notes': body.get('notes', ''),
        'isEstimated': body.get('isEstimated', False),
        'createdAt': current_time,
        'updatedAt': current_time
    }
    
    # Store in DynamoDB
    try:
        dynamodb_client.put_item('growth_data', growth_record)
        logger.info(f"Growth data created successfully: {data_id} for baby: {baby_id} (user: {user_id})")
    except Exception as e:
        logger.error(f"Error creating growth data: {e}")
        return internal_error_response("Failed to create growth data")
    
    return created_response(
        data=growth_record,
        message="Growth data created successfully"
    )
