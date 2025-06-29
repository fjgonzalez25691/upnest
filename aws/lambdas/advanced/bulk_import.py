"""
UpNest - Bulk Import Growth Data Endpoint
POST /babies/{babyId}/growth/bulk

Accepts an array of growth measurements and processes them in batch,
with proper validation and percentile calculation for each measurement.
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any, Optional
import uuid

import boto3
from botocore.exceptions import ClientError

# Import shared utilities
from shared.jwt_utils import validate_jwt_token
from shared.dynamodb_client import DynamoDBClient
from shared.response_utils import create_response, create_error_response
from shared.validation_utils import validate_uuid, validate_measurement_data, validate_date
from shared.exceptions import ValidationError, NotFoundError, UnauthorizedError

# Import percentile calculation
from percentiles.calculate import calculate_percentiles

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb_client = DynamoDBClient()

def lambda_handler(event, context):
    """
    Lambda handler for POST /babies/{babyId}/growth/bulk
    Bulk import growth measurements with validation and percentile calculation
    """
    try:
        # Extract and validate JWT token
        auth_header = event.get('headers', {}).get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise UnauthorizedError("Missing or invalid Authorization header")
        
        token = auth_header.replace('Bearer ', '')
        user_claims = validate_jwt_token(token)
        user_id = user_claims['sub']
        
        # Extract and validate baby ID
        baby_id = event.get('pathParameters', {}).get('babyId')
        if not baby_id:
            raise ValidationError("Baby ID is required")
        
        validate_uuid(baby_id)
        
        # Parse request body
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON in request body")
        
        measurements = body.get('measurements', [])
        if not measurements:
            raise ValidationError("No measurements provided")
        
        if not isinstance(measurements, list):
            raise ValidationError("Measurements must be an array")
        
        if len(measurements) > 25:  # DynamoDB batch limit
            raise ValidationError("Maximum 25 measurements per batch")
        
        logger.info(f"Processing bulk import for baby {baby_id}, user {user_id}, {len(measurements)} measurements")
        
        # Verify baby exists and user owns it
        baby = dynamodb_client.get_item_by_key('BABIES_TABLE', baby_id)
        if not baby:
            raise NotFoundError("Baby not found")
        
        if baby.get('userId') != user_id:
            raise UnauthorizedError("Access denied: You don't own this baby")
        
        # Get baby info for percentile calculations
        baby_birth_date = baby.get('birthDate')
        baby_gender = baby.get('gender', 'unknown')
        baby_name = baby.get('name', 'Unknown')
        
        if not baby_birth_date:
            raise ValidationError("Baby birth date not found")
        
        # Validate all measurements before processing
        validated_measurements = []
        validation_errors = []
        
        for i, measurement in enumerate(measurements):
            try:
                validated_measurement = validate_single_measurement(
                    measurement, 
                    baby_id, 
                    user_id, 
                    baby_birth_date,
                    i
                )
                validated_measurements.append(validated_measurement)
            except ValidationError as e:
                validation_errors.append(f"Measurement {i+1}: {str(e)}")
        
        # If there are validation errors, return them
        if validation_errors:
            raise ValidationError(f"Validation failed: {'; '.join(validation_errors)}")
        
        # Process measurements in batch
        processing_results = process_measurements_batch(
            validated_measurements,
            baby_birth_date,
            baby_gender
        )
        
        # Prepare response
        response_data = {
            'babyId': baby_id,
            'babyName': baby_name,
            'totalMeasurements': len(measurements),
            'processedCount': processing_results['success_count'],
            'failedCount': processing_results['failed_count'],
            'results': processing_results['results'],
            'summary': processing_results['summary'],
            'processedAt': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Return appropriate status code
        if processing_results['failed_count'] > 0:
            # Partial success - some measurements failed
            status_code = 207  # Multi-Status
            response_data['message'] = f"Bulk import completed with {processing_results['failed_count']} failures"
        else:
            # Complete success
            status_code = 201
            response_data['message'] = "All measurements imported successfully"
        
        logger.info(f"Bulk import completed: {processing_results['success_count']} success, {processing_results['failed_count']} failed")
        
        return create_response(status_code, response_data)
        
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        return create_error_response(400, str(e))
    except NotFoundError as e:
        logger.warning(f"Not found: {str(e)}")
        return create_error_response(404, str(e))
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized: {str(e)}")
        return create_error_response(403, str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return create_error_response(500, "Internal server error")

def validate_single_measurement(
    measurement: Dict[str, Any], 
    baby_id: str, 
    user_id: str, 
    baby_birth_date: str,
    index: int
) -> Dict[str, Any]:
    """
    Validate a single measurement from the bulk import
    """
    if not isinstance(measurement, dict):
        raise ValidationError(f"Measurement must be an object")
    
    # Required fields
    required_fields = ['measurementType', 'value', 'measuredAt']
    for field in required_fields:
        if field not in measurement:
            raise ValidationError(f"Missing required field: {field}")
    
    measurement_type = measurement.get('measurementType')
    value = measurement.get('value')
    measured_at = measurement.get('measuredAt')
    unit = measurement.get('unit', '')
    notes = measurement.get('notes', '')
    
    # Validate measurement data
    validate_measurement_data(measurement_type, value, unit)
    validate_date(measured_at)
    
    # Validate measurement date is not in the future
    measured_date = datetime.fromisoformat(measured_at.replace('Z', '+00:00'))
    if measured_date > datetime.utcnow().replace(tzinfo=measured_date.tzinfo):
        raise ValidationError("Measurement date cannot be in the future")
    
    # Validate measurement date is not before birth date
    birth_date = datetime.fromisoformat(baby_birth_date.replace('Z', '+00:00'))
    if measured_date < birth_date:
        raise ValidationError("Measurement date cannot be before birth date")
    
    # Generate unique record ID
    record_id = str(uuid.uuid4())
    
    # Calculate age at measurement
    age_in_days = (measured_date - birth_date).days
    
    # Prepare validated measurement
    validated_measurement = {
        'recordId': record_id,
        'babyId': baby_id,
        'userId': user_id,
        'measurementType': measurement_type,
        'value': Decimal(str(value)),
        'unit': unit,
        'measuredAt': measured_at,
        'ageInDays': age_in_days,
        'notes': notes,
        'createdAt': datetime.utcnow().isoformat() + 'Z',
        'modifiedAt': datetime.utcnow().isoformat() + 'Z'
    }
    
    return validated_measurement

def process_measurements_batch(
    measurements: List[Dict[str, Any]],
    baby_birth_date: str,
    baby_gender: str
) -> Dict[str, Any]:
    """
    Process measurements in batch with percentile calculations
    """
    success_count = 0
    failed_count = 0
    results = []
    summary = {
        'byType': {},
        'dateRange': {
            'earliest': None,
            'latest': None
        }
    }
    
    # Process each measurement
    for measurement in measurements:
        try:
            # Calculate percentiles
            percentile_data = calculate_percentiles_for_measurement(
                measurement,
                baby_birth_date,
                baby_gender
            )
            
            # Add percentile data to measurement
            if percentile_data:
                measurement.update(percentile_data)
            
            # Save to DynamoDB
            dynamodb_client.put_item('GROWTH_DATA_TABLE', measurement)
            
            # Update summary
            update_summary(summary, measurement)
            
            results.append({
                'recordId': measurement['recordId'],
                'measurementType': measurement['measurementType'],
                'value': float(measurement['value']),
                'status': 'success',
                'percentile': percentile_data.get('percentile') if percentile_data else None
            })
            
            success_count += 1
            
        except Exception as e:
            logger.error(f"Failed to process measurement {measurement.get('recordId')}: {str(e)}")
            
            results.append({
                'recordId': measurement.get('recordId', 'unknown'),
                'measurementType': measurement.get('measurementType', 'unknown'),
                'status': 'failed',
                'error': str(e)
            })
            
            failed_count += 1
    
    return {
        'success_count': success_count,
        'failed_count': failed_count,
        'results': results,
        'summary': summary
    }

def calculate_percentiles_for_measurement(
    measurement: Dict[str, Any],
    baby_birth_date: str,
    baby_gender: str
) -> Optional[Dict[str, Any]]:
    """
    Calculate percentiles for a single measurement
    """
    try:
        # Prepare data for percentile calculation
        percentile_input = {
            'babyId': measurement['babyId'],
            'measurementType': measurement['measurementType'],
            'value': float(measurement['value']),
            'measuredAt': measurement['measuredAt'],
            'birthDate': baby_birth_date,
            'gender': baby_gender,
            'ageInDays': measurement['ageInDays']
        }
        
        # Calculate percentiles
        percentiles = calculate_percentiles(percentile_input)
        
        if percentiles and 'percentile' in percentiles:
            return {
                'percentile': Decimal(str(percentiles['percentile'])),
                'zScore': Decimal(str(percentiles.get('zScore', 0))),
                'percentileCategory': percentiles.get('category', 'normal')
            }
        
        return None
        
    except Exception as e:
        logger.warning(f"Could not calculate percentiles for measurement: {str(e)}")
        return None

def update_summary(summary: Dict[str, Any], measurement: Dict[str, Any]):
    """
    Update summary statistics with processed measurement
    """
    measurement_type = measurement['measurementType']
    measured_at = measurement['measuredAt']
    
    # Update by type
    if measurement_type not in summary['byType']:
        summary['byType'][measurement_type] = {
            'count': 0,
            'values': []
        }
    
    summary['byType'][measurement_type]['count'] += 1
    summary['byType'][measurement_type]['values'].append({
        'value': float(measurement['value']),
        'date': measured_at,
        'percentile': float(measurement.get('percentile', 0))
    })
    
    # Update date range
    if summary['dateRange']['earliest'] is None or measured_at < summary['dateRange']['earliest']:
        summary['dateRange']['earliest'] = measured_at
    
    if summary['dateRange']['latest'] is None or measured_at > summary['dateRange']['latest']:
        summary['dateRange']['latest'] = measured_at
