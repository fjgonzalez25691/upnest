"""
Lambda function to get a specific growth data record.
GET /babies/{babyId}/growth/{dataId}
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
    Get a specific growth data record.
    
    Args:
        event: API Gateway event with JWT token, babyId and dataId in path
        context: Lambda context
        
    Returns:
        dict: HTTP response with growth data record
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
        # Get the specific growth data record
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
            logger.warning(f"User {user_id} attempted to access growth data for baby {baby_id} owned by {baby_user_id}")
            return not_found_response("Growth data record not found")
        
        # Check if baby is active
        if not baby_item.get('isActive', {'BOOL': True})['BOOL']:
            logger.warning(f"Attempted to access growth data for deleted baby: {baby_id}")
            return not_found_response("Baby not found")
        
        # Convert DynamoDB item to response format
        growth_data = {
            'dataId': growth_item.get('dataId', {}).get('S', ''),
            'babyId': growth_item.get('babyId', {}).get('S', ''),
            'measurementDate': growth_item.get('measurementDate', {}).get('S', ''),
            'ageInDays': int(growth_item.get('ageInDays', {}).get('N', '0')),
            'measurementType': growth_item.get('measurementType', {}).get('S', ''),
            'weight': float(growth_item.get('weight', {}).get('N', '0')),
            'height': float(growth_item.get('height', {}).get('N', '0')),
            'headCircumference': float(growth_item.get('headCircumference', {}).get('N', '0')),
            'notes': growth_item.get('notes', {}).get('S', ''),
            'createdAt': growth_item.get('createdAt', {}).get('S', ''),
            'modifiedAt': growth_item.get('modifiedAt', {}).get('S', '')
        }
        
        # Include percentile data if available
        if 'percentiles' in growth_item:
            percentiles_item = growth_item['percentiles']['M']
            growth_data['percentiles'] = {
                'weight': float(percentiles_item.get('weight', {}).get('N', '0')),
                'height': float(percentiles_item.get('height', {}).get('N', '0')),
                'headCircumference': float(percentiles_item.get('headCircumference', {}).get('N', '0'))
            }
        
        # Get historical context (previous and next measurements) - optional enhancement
        try:
            # Query other measurements for this baby to provide context
            context_query = dynamodb_client.query(
                TableName='GrowthData',
                IndexName='BabyGrowthIndex',
                KeyConditionExpression='babyId = :baby_id',
                ExpressionAttributeValues={
                    ':baby_id': {'S': baby_id}
                },
                ScanIndexForward=True,  # Sort ascending by date
                Limit=10  # Limit for context
            )
            
            # Find previous and next measurements
            current_date = growth_item.get('measurementDate', {}).get('S', '')
            previous_measurement = None
            next_measurement = None
            
            for item in context_query.get('Items', []):
                item_date = item.get('measurementDate', {}).get('S', '')
                item_id = item.get('dataId', {}).get('S', '')
                
                if item_id == data_id:
                    continue  # Skip current record
                
                if item_date < current_date:
                    previous_measurement = {
                        'dataId': item_id,
                        'measurementDate': item_date,
                        'weight': float(item.get('weight', {}).get('N', '0'))
                    }
                elif item_date > current_date and not next_measurement:
                    next_measurement = {
                        'dataId': item_id,
                        'measurementDate': item_date,
                        'weight': float(item.get('weight', {}).get('N', '0'))
                    }
                    break  # Only need the next one
            
            # Add historical context to response
            growth_data['context'] = {
                'previousMeasurement': previous_measurement,
                'nextMeasurement': next_measurement
            }
            
        except Exception as context_error:
            logger.warning(f"Could not retrieve historical context: {context_error}")
            # Don't fail the main request if context retrieval fails
        
        # Add baby information for context
        growth_data['baby'] = {
            'babyId': baby_id,
            'name': baby_item.get('name', {}).get('S', 'Unknown'),
            'dateOfBirth': baby_item.get('dateOfBirth', {}).get('S', '')
        }
        
        logger.info(f"Retrieved growth data record {data_id} for baby {baby_id} by user {user_id}")
        
        return ok_response(growth_data)
        
    except Exception as e:
        logger.error(f"Error retrieving growth data {data_id}: {str(e)}")
        return internal_error_response("Failed to retrieve growth data record")
