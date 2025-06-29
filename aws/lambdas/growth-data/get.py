"""
Lambda function to get growth data records for a baby.
GET /growth-data/{babyId}
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
    bad_request_response, handle_lambda_error
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event, context):
    """
    Get growth data records for a baby.
    
    Path parameters:
    - babyId: UUID of the baby
    
    Query parameters (optional):
    - limit: Maximum number of records (default: 50)
    - startDate: Filter records from this date (YYYY-MM-DD)
    - endDate: Filter records until this date (YYYY-MM-DD)
    - measurementType: Filter by measurement type (weight, height, headCircumference)
    
    Response:
    {
        "success": true,
        "data": [
            {
                "dataId": "uuid",
                "babyId": "baby-uuid",
                "measurementDate": "2025-06-29",
                "measurements": {...},
                "percentiles": {...}
            }
        ],
        "metadata": {
            "count": 10,
            "babyId": "baby-uuid"
        }
    }
    """
    logger.info(f"Getting growth data - Request ID: {context.aws_request_id}")
    
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
    
    # Verify baby exists and belongs to user
    try:
        baby = dynamodb_client.get_item('babies', {'babyId': baby_id})
        
        if not baby:
            return not_found_response("Baby not found")
        
        # ✅ CRITICAL: Verify baby belongs to authenticated user
        if baby.get('userId') != user_id:
            logger.warning(f"Unauthorized access: user {user_id} tried to access growth data for baby {baby_id}")
            return not_found_response("Baby not found")
            
        if not baby.get('isActive', True):
            return not_found_response("Baby not found")
            
    except Exception as e:
        logger.error(f"Error verifying baby ownership: {e}")
        return not_found_response("Baby not found")
    
    # Parse query parameters
    query_params = event.get('queryStringParameters') or {}
    limit = min(int(query_params.get('limit', 50)), 100)  # Max 100 items
    start_date = query_params.get('startDate')
    end_date = query_params.get('endDate')
    measurement_type = query_params.get('measurementType')
    
    # Query growth data using GSI (BabyGrowthIndex)
    try:
        from boto3.dynamodb.conditions import Key
        
        growth_data = dynamodb_client.query_gsi(
            table_name='growth_data',
            index_name='BabyGrowthIndex',
            key_condition=Key('babyId').eq(baby_id),
            expression_values={},
            limit=limit
        )
        
        # Apply additional filters if provided
        filtered_data = growth_data
        
        if start_date:
            filtered_data = [record for record in filtered_data 
                           if record.get('measurementDate', '') >= start_date]
        
        if end_date:
            filtered_data = [record for record in filtered_data 
                           if record.get('measurementDate', '') <= end_date]
        
        if measurement_type:
            filtered_data = [record for record in filtered_data 
                           if measurement_type in record.get('measurements', {})]
        
        # Sort by measurement date (most recent first)
        filtered_data.sort(
            key=lambda x: x.get('measurementDate', ''), 
            reverse=True
        )
        
        logger.info(f"Retrieved {len(filtered_data)} growth data records for baby {baby_id} (user: {user_id})")
        
        return success_response(
            data=filtered_data,
            metadata={
                'count': len(filtered_data),
                'babyId': baby_id,
                'filters': {
                    'startDate': start_date,
                    'endDate': end_date,
                    'measurementType': measurement_type
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving growth data: {e}")
        return success_response(data=[], metadata={'count': 0, 'babyId': baby_id})
