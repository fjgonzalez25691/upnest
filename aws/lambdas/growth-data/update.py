"""
Lambda function to update a growth data record.
PUT /babies/{babyId}/growth/{dataId}
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
from validation_utils import GrowthDataValidator, is_valid_uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event, context):
    """
    Update a growth data record.
    
    Args:
        event: API Gateway event with JWT token, babyId and dataId in path, and update data in body
        context: Lambda context
        
    Returns:
        dict: HTTP response with updated growth data
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
    
    # Parse request body
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in request body")
        return bad_request_response("Invalid JSON in request body")
    
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
            logger.warning(f"User {user_id} attempted to update growth data for baby {baby_id} owned by {baby_user_id}")
            return not_found_response("Growth data record not found")
        
        # Check if baby is active
        if not baby_item.get('isActive', {'BOOL': True})['BOOL']:
            logger.warning(f"Attempted to update growth data for deleted baby: {baby_id}")
            return not_found_response("Baby not found")
        
        # Validate the update data
        validator = GrowthDataValidator(body)
        validation_result = validator.validate_update()
        
        if not validation_result['is_valid']:
            logger.warning(f"Validation failed: {validation_result['errors']}")
            return bad_request_response("Validation failed", validation_result['errors'])
        
        # Prepare update expression and values
        update_expressions = []
        expression_values = {}
        
        # Build dynamic update expression based on provided fields
        updatable_fields = ['weight', 'height', 'headCircumference', 'notes', 'measurementDate']
        
        for field in updatable_fields:
            if field in body:
                if field in ['weight', 'height', 'headCircumference']:
                    update_expressions.append(f'{field} = :{field}')
                    expression_values[f':{field}'] = {'N': str(body[field])}
                else:
                    update_expressions.append(f'{field} = :{field}')
                    expression_values[f':{field}'] = {'S': str(body[field])}
        
        # Always update modifiedAt
        current_time = datetime.utcnow().isoformat()
        update_expressions.append('modifiedAt = :modified_at')
        expression_values[':modified_at'] = {'S': current_time}
        
        # If measurement date changed, recalculate age
        if 'measurementDate' in body:
            # Get baby's birth date to calculate age
            birth_date_str = baby_item.get('dateOfBirth', {}).get('S', '')
            if birth_date_str:
                try:
                    birth_date = datetime.fromisoformat(birth_date_str.replace('Z', '+00:00'))
                    measurement_date = datetime.fromisoformat(body['measurementDate'].replace('Z', '+00:00'))
                    age_in_days = (measurement_date - birth_date).days
                    
                    update_expressions.append('ageInDays = :age_in_days')
                    expression_values[':age_in_days'] = {'N': str(age_in_days)}
                except ValueError as e:
                    logger.warning(f"Date parsing error: {e}")
                    return bad_request_response("Invalid date format")
        
        # TODO: Recalculate percentiles if measurement values changed
        # This would require calling the percentile calculation service
        
        # Perform the update
        update_response = dynamodb_client.update_item(
            TableName='GrowthData',
            Key={
                'dataId': {'S': data_id}
            },
            UpdateExpression='SET ' + ', '.join(update_expressions),
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        
        # Convert updated item back to response format
        updated_item = update_response['Attributes']
        
        growth_data = {
            'dataId': updated_item.get('dataId', {}).get('S', ''),
            'babyId': updated_item.get('babyId', {}).get('S', ''),
            'measurementDate': updated_item.get('measurementDate', {}).get('S', ''),
            'ageInDays': int(updated_item.get('ageInDays', {}).get('N', '0')),
            'measurementType': updated_item.get('measurementType', {}).get('S', ''),
            'weight': float(updated_item.get('weight', {}).get('N', '0')),
            'height': float(updated_item.get('height', {}).get('N', '0')),
            'headCircumference': float(updated_item.get('headCircumference', {}).get('N', '0')),
            'notes': updated_item.get('notes', {}).get('S', ''),
            'createdAt': updated_item.get('createdAt', {}).get('S', ''),
            'modifiedAt': updated_item.get('modifiedAt', {}).get('S', '')
        }
        
        # Include percentile data if available
        if 'percentiles' in updated_item:
            percentiles_item = updated_item['percentiles']['M']
            growth_data['percentiles'] = {
                'weight': float(percentiles_item.get('weight', {}).get('N', '0')),
                'height': float(percentiles_item.get('height', {}).get('N', '0')),
                'headCircumference': float(percentiles_item.get('headCircumference', {}).get('N', '0'))
            }
        
        logger.info(f"Growth data updated successfully: {data_id} for baby {baby_id} by user {user_id}")
        
        return ok_response(growth_data)
        
    except Exception as e:
        logger.error(f"Error updating growth data {data_id}: {str(e)}")
        return internal_error_response("Failed to update growth data")
