"""
Lambda function to get growth data records for a baby.
GET /babies/{babyId}/growth
"""

import json
import logging
import sys
import os

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from dynamodb_client import get_dynamodb_client
from jwt_utils import get_jwt_validator, extract_token_from_event
from response_utils import (
    success_response, unauthorized_response, not_found_response,
    bad_request_response, internal_error_response, handle_lambda_error
)
from validation_utils import is_valid_uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event, context):
    """
    Get growth data records for a baby.
    
    Path parameters:
    - babyId: UUID of the baby
    
    Query parameters (optional):
    - limit: Maximum number of records (default: 50, max: 100)
    - startDate: Filter records from this date (YYYY-MM-DD)
    - endDate: Filter records until this date (YYYY-MM-DD)
    - measurementType: Filter by measurement type (weight, height, headCircumference)
    
    Returns:
        dict: HTTP response with growth data records
    """
    
    # Get clients using lazy loading
    dynamodb_client = get_dynamodb_client()
    jwt_validator = get_jwt_validator()
    
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
    
    if not baby_id:
        logger.warning("Missing babyId in path parameters")
        return bad_request_response("Missing babyId in path parameters")
    
    # Validate ID format
    if not is_valid_uuid(baby_id):
        logger.warning(f"Invalid babyId format: {baby_id}")
        return bad_request_response("Invalid babyId format")
    
    # Parse query parameters
    query_params = event.get('queryStringParameters') or {}
    limit = min(int(query_params.get('limit', 50)), 100)  # Max 100 items
    start_date = query_params.get('startDate')
    end_date = query_params.get('endDate')
    measurement_type = query_params.get('measurementType')
    
    try:
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
            logger.warning(f"User {user_id} attempted to access growth data for baby {baby_id} owned by {baby_user_id}")
            return not_found_response("Baby not found")
        
        # Check if baby is active
        if not baby_item.get('isActive', {'BOOL': True})['BOOL']:
            logger.warning(f"Attempted to access growth data for deleted baby: {baby_id}")
            return not_found_response("Baby not found")
        
        # Query growth data for this baby
        query_params_dynamo = {
            'TableName': 'GrowthData',
            'IndexName': 'BabyGrowthIndex',
            'KeyConditionExpression': 'babyId = :baby_id',
            'ExpressionAttributeValues': {
                ':baby_id': {'S': baby_id}
            },
            'ScanIndexForward': False,  # Most recent first
            'Limit': limit
        }
        
        growth_response = dynamodb_client.query(**query_params_dynamo)
        
        # Process and format the items
        growth_records = []
        for item in growth_response.get('Items', []):
            # Apply date filters if provided
            measurement_date = item.get('measurementDate', {}).get('S', '')
            
            if start_date and measurement_date < start_date:
                continue
            if end_date and measurement_date > end_date:
                continue
            
            # Apply measurement type filter if provided
            if measurement_type:
                weight_val = item.get('weight', {}).get('N')
                height_val = item.get('height', {}).get('N')
                head_circ_val = item.get('headCircumference', {}).get('N')
                
                if measurement_type == 'weight' and (not weight_val or float(weight_val) <= 0):
                    continue
                elif measurement_type == 'height' and (not height_val or float(height_val) <= 0):
                    continue
                elif measurement_type == 'headCircumference' and (not head_circ_val or float(head_circ_val) <= 0):
                    continue
            
            # Format the record
            record = {
                'dataId': item.get('dataId', {}).get('S', ''),
                'babyId': item.get('babyId', {}).get('S', ''),
                'measurementDate': measurement_date,
                'ageInDays': int(item.get('ageInDays', {}).get('N', '0')),
                'measurementType': item.get('measurementType', {}).get('S', ''),
                'weight': float(item.get('weight', {}).get('N', '0')),
                'height': float(item.get('height', {}).get('N', '0')),
                'headCircumference': float(item.get('headCircumference', {}).get('N', '0')),
                'notes': item.get('notes', {}).get('S', ''),
                'createdAt': item.get('createdAt', {}).get('S', ''),
                'modifiedAt': item.get('modifiedAt', {}).get('S', '')
            }
            
            # Include percentile data if available
            if 'percentiles' in item:
                percentiles_item = item['percentiles']['M']
                record['percentiles'] = {
                    'weight': float(percentiles_item.get('weight', {}).get('N', '0')),
                    'height': float(percentiles_item.get('height', {}).get('N', '0')),
                    'headCircumference': float(percentiles_item.get('headCircumference', {}).get('N', '0'))
                }
            
            growth_records.append(record)
        
        logger.info(f"Retrieved {len(growth_records)} growth data records for baby {baby_id} by user {user_id}")
        
        return success_response(
            growth_records,
            metadata={
                'count': len(growth_records),
                'babyId': baby_id,
                'filters': {
                    'startDate': start_date,
                    'endDate': end_date,
                    'measurementType': measurement_type,
                    'limit': limit
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving growth data for baby {baby_id}: {str(e)}")
        return internal_error_response("Failed to retrieve growth data")
