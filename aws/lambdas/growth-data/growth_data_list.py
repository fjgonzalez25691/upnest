"""
Lambda function to list growth data for a baby.
GET /babies/{babyId}/growth
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
    List growth data for a specific baby.
    
    Args:
        event: API Gateway event with JWT token and babyId in path
        context: Lambda context
        
    Returns:
        dict: HTTP response with growth data array
    """
    request_id = getattr(context, 'aws_request_id', 'test-request')
    logger.info(f"Listing growth data - Request ID: {request_id}")
    
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
    
    # Extract query parameters for pagination and filtering
    query_params = event.get('queryStringParameters') or {}
    limit = min(int(query_params.get('limit', 50)), 100)  # Max 100 records
    measurement_type = query_params.get('measurementType')  # Optional filter
    
    try:
        dynamodb_client = get_dynamodb_client()
        
        # Check if baby exists and user owns it
        existing_baby = dynamodb_client.get_item('babies', {'babyId': baby_id})
        
        if not existing_baby:
            return not_found_response("Baby not found")
        
        # Verify ownership
        if existing_baby.get('userId') != user_id:
            return not_found_response("Baby not found")
        
        # Check if baby is active
        if not existing_baby.get('isActive', True):
            return not_found_response("Baby not found")
        
        # Query growth data for this baby
        # Assuming we have a method to query by babyId
        growth_data = dynamodb_client.query_items(
            table_name='growth_data',
            index_name='BabyGrowthIndex',
            key_condition='babyId = :baby_id',
            expression_values={':baby_id': baby_id},
            limit=limit,
            scan_index_forward=False  # Newest first
        )
        
        # Filter by measurement type if specified
        if measurement_type and growth_data:
            growth_data = [
                record for record in growth_data 
                if record.get('measurementType') == measurement_type
            ]
        
        logger.info(f"Retrieved {len(growth_data)} growth records for baby {baby_id}")
        
        return success_response(
            data=growth_data,
            message=f"Retrieved {len(growth_data)} growth records"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving growth data for baby {baby_id}: {e}")
        return internal_error_response("Failed to retrieve growth data")
