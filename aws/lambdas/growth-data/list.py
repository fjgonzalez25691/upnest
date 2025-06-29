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
    List growth data for a specific baby.
    
    Args:
        event: API Gateway event with JWT token and babyId in path
        context: Lambda context
        
    Returns:
        dict: HTTP response with growth data array
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
    
    # Extract query parameters for pagination and filtering
    query_params = event.get('queryStringParameters') or {}
    limit = int(query_params.get('limit', 50))  # Default to 50 records
    measurement_type = query_params.get('measurementType')  # Optional filter
    
    # Limit maximum records per request
    if limit > 100:
        limit = 100
    
    try:
        # First verify baby exists and belongs to user
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
            logger.warning(f"User {user_id} attempted to access baby {baby_id} owned by {baby_user_id}")
            return not_found_response("Baby not found")  # Don't reveal existence
        
        # Check if baby is active
        if not baby_item.get('isActive', {'BOOL': True})['BOOL']:
            logger.warning(f"Attempted to access deleted baby: {baby_id}")
            return not_found_response("Baby not found")
        
        # Query growth data using GSI (Global Secondary Index)
        query_params = {
            'TableName': 'GrowthData',
            'IndexName': 'BabyGrowthIndex',
            'KeyConditionExpression': 'babyId = :baby_id',
            'ExpressionAttributeValues': {
                ':baby_id': {'S': baby_id}
            },
            'ScanIndexForward': False,  # Sort by measurementDate descending (newest first)
            'Limit': limit
        }
        
        # Add measurement type filter if specified
        if measurement_type:
            query_params['FilterExpression'] = 'measurementType = :measurement_type'
            query_params['ExpressionAttributeValues'][':measurement_type'] = {'S': measurement_type}
        
        growth_response = dynamodb_client.query(**query_params)
        
        # Convert DynamoDB items to Python objects
        growth_data = []
        for item in growth_response.get('Items', []):
            growth_record = {
                'dataId': item.get('dataId', {}).get('S', ''),
                'babyId': item.get('babyId', {}).get('S', ''),
                'measurementDate': item.get('measurementDate', {}).get('S', ''),
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
                growth_record['percentiles'] = {
                    'weight': float(percentiles_item.get('weight', {}).get('N', '0')),
                    'height': float(percentiles_item.get('height', {}).get('N', '0')),
                    'headCircumference': float(percentiles_item.get('headCircumference', {}).get('N', '0'))
                }
            
            growth_data.append(growth_record)
        
        # Get baby info for context
        baby_name = baby_item.get('name', {}).get('S', 'Unknown')
        
        logger.info(f"Retrieved {len(growth_data)} growth records for baby {baby_id} by user {user_id}")
        
        return ok_response({
            'baby': {
                'babyId': baby_id,
                'name': baby_name
            },
            'growthData': growth_data,
            'totalRecords': len(growth_data),
            'hasMore': 'LastEvaluatedKey' in growth_response
        })
        
    except Exception as e:
        logger.error(f"Error retrieving growth data for baby {baby_id}: {str(e)}")
        return internal_error_response("Failed to retrieve growth data")
