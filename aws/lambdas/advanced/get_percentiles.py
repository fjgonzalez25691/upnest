"""
Lambda function to get current percentiles for a baby.
GET /babies/{babyId}/percentiles
"""

import json
import logging
from datetime import datetime, date
import sys
import os

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'percentiles'))

from dynamodb_client import dynamodb_client
from jwt_utils import jwt_validator, extract_token_from_event
from response_utils import (
    success_response, bad_request_response, unauthorized_response,
    not_found_response, internal_error_response, handle_lambda_error
)
from validation_utils import is_valid_uuid

# Import percentile calculation logic
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'percentiles'))
    from calculate import calculate_zscore, zscore_to_percentile, load_table
    import pandas as pd
    percentile_calculation_available = True
except ImportError as e:
    percentile_calculation_available = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event, context):
    """
    Get current percentiles for a baby based on latest measurements.
    
    Path parameters:
    - babyId: UUID of the baby
    
    Response:
    {
        "success": true,
        "data": {
            "babyId": "uuid",
            "name": "Emma",
            "ageInDays": 365,
            "ageInMonths": 12,
            "latestMeasurements": {
                "weight": 9500,
                "height": 75.2,
                "headCircumference": 46.1,
                "measurementDate": "2025-06-29"
            },
            "currentPercentiles": {
                "weight": 75.5,
                "height": 80.2,
                "headCircumference": 65.8
            },
            "whoReferences": {
                "weight": "75th percentile - Normal range",
                "height": "80th percentile - Above average",
                "headCircumference": "66th percentile - Normal range"
            }
        }
    }
    """
    logger.info(f"Getting current percentiles for baby - Request ID: {context.aws_request_id}")
    
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
    
    # Validate baby ID format
    if not is_valid_uuid(baby_id):
        return bad_request_response("Invalid baby ID format")
    
    try:
        # 1. Verify baby exists and belongs to user
        baby = dynamodb_client.get_item('babies', {'babyId': baby_id})
        
        if not baby:
            return not_found_response("Baby not found")
        
        # Verify ownership
        if baby.get('userId') != user_id:
            logger.warning(f"Unauthorized access: user {user_id} tried to access baby {baby_id}")
            return not_found_response("Baby not found")
        
        # Check if baby is active
        if not baby.get('isActive', True):
            return not_found_response("Baby not found")
        
        # 2. Calculate current age in days and months
        birth_date_str = baby.get('dateOfBirth')
        if not birth_date_str:
            return bad_request_response("Baby birth date not found")
        
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            today = date.today()
            age_in_days = (today - birth_date).days
            age_in_months = round(age_in_days / 30.44, 1)  # Average days per month
        except ValueError:
            return bad_request_response("Invalid birth date format")
        
        # 3. Get latest measurements for this baby
        latest_measurements = get_latest_measurements(baby_id)
        
        if not latest_measurements:
            return success_response(
                data={
                    'babyId': baby_id,
                    'name': baby.get('name'),
                    'ageInDays': age_in_days,
                    'ageInMonths': age_in_months,
                    'latestMeasurements': None,
                    'currentPercentiles': None,
                    'message': 'No measurements found for this baby'
                }
            )
        
        # 4. Calculate percentiles using existing service
        percentiles_data = None
        if percentile_calculation_available:
            try:
                # Calculate percentiles for each measurement type
                percentiles_data = calculate_percentiles_for_baby(
                    baby.get('gender', 'male'),
                    age_in_days,
                    latest_measurements['measurements'],
                    birth_date_str,
                    latest_measurements['measurementDate']
                )
                logger.info(f"Calculated percentiles for baby {baby_id}")
                
            except Exception as e:
                logger.error(f"Error calculating percentiles: {e}")
                # Continue without percentiles rather than failing
        
        # 5. Add WHO reference interpretations
        who_references = interpret_percentiles(percentiles_data) if percentiles_data else {}
        
        response_data = {
            'babyId': baby_id,
            'name': baby.get('name'),
            'gender': baby.get('gender'),
            'ageInDays': age_in_days,
            'ageInMonths': age_in_months,
            'latestMeasurements': latest_measurements,
            'currentPercentiles': percentiles_data,
            'whoReferences': who_references
        }
        
        logger.info(f"Retrieved current percentiles for baby {baby_id} (user: {user_id})")
        return success_response(data=response_data)
        
    except Exception as e:
        logger.error(f"Error getting percentiles for baby {baby_id}: {e}")
        return internal_error_response("Failed to get current percentiles")

def get_latest_measurements(baby_id: str) -> dict:
    """
    Get the most recent measurements for a baby.
    
    Args:
        baby_id: UUID of the baby
        
    Returns:
        Dict with latest measurements or None if no measurements found
    """
    try:
        # Query growth data using GSI, sorted by date descending
        growth_data = dynamodb_client.query_gsi(
            table_name='growth_data',
            index_name='BabyGrowthIndex',
            key_condition={'babyId': baby_id},
            scan_index_forward=False,  # Most recent first
            limit=1
        )
        
        if not growth_data:
            return None
        
        latest = growth_data[0]
        
        return {
            'dataId': latest.get('dataId'),
            'measurementDate': latest.get('measurementDate'),
            'measurements': latest.get('measurements', {}),
            'ageInDays': latest.get('ageInDays'),
            'measurementSource': latest.get('measurementSource', 'unknown')
        }
        
    except Exception as e:
        logger.error(f"Error getting latest measurements for baby {baby_id}: {e}")
        return None

def interpret_percentiles(percentiles: dict) -> dict:
    """
    Interpret percentile values according to WHO standards.
    
    Args:
        percentiles: Dict with percentile values
        
    Returns:
        Dict with WHO interpretations
    """
    if not percentiles:
        return {}
    
    interpretations = {}
    
    for measurement_type, percentile in percentiles.items():
        if not isinstance(percentile, (int, float)):
            continue
            
        if percentile < 3:
            interpretation = f"{percentile:.1f}th percentile - Below normal range (requires attention)"
        elif percentile < 10:
            interpretation = f"{percentile:.1f}th percentile - Low normal range"
        elif percentile < 25:
            interpretation = f"{percentile:.1f}th percentile - Lower normal range"
        elif percentile < 75:
            interpretation = f"{percentile:.1f}th percentile - Normal range"
        elif percentile < 90:
            interpretation = f"{percentile:.1f}th percentile - Upper normal range"
        elif percentile < 97:
            interpretation = f"{percentile:.1f}th percentile - Above average"
        else:
            interpretation = f"{percentile:.1f}th percentile - Well above average (monitor growth)"
        
        interpretations[measurement_type] = interpretation
    
    return interpretations

def calculate_percentiles_for_baby(gender: str, age_in_days: int, measurements: dict, birth_date: str, measurement_date: str) -> dict:
    """
    Calculate percentiles for all measurements of a baby.
    
    Args:
        gender: 'male' or 'female'
        age_in_days: Age in days
        measurements: Dict with weight, height, headCircumference
        birth_date: Birth date string
        measurement_date: Measurement date string
        
    Returns:
        Dict with percentiles for each measurement type
    """
    if not percentile_calculation_available:
        return {}
    
    percentiles = {}
    
    try:
        # Calculate weight percentile if available
        if 'weight' in measurements and measurements['weight']:
            weight_kg = measurements['weight'] / 1000  # Convert grams to kg
            
            # Load weight table for gender
            df = load_table(gender)
            
            # Find row for age
            row = df.loc[df['Day'] == age_in_days]
            if row.empty:
                # Find closest age
                idx = (df['Day'] - age_in_days).abs().idxmin()
                row = df.loc[[idx]]
            
            if not row.empty:
                L, M, S = float(row['L'].iloc[0]), float(row['M'].iloc[0]), float(row['S'].iloc[0])
                zscore = calculate_zscore(weight_kg, L, M, S)
                percentiles['weight'] = round(zscore_to_percentile(zscore), 1)
    
        # Note: For height and head circumference, we would need similar tables
        # For now, we'll just return weight percentile
        # TODO: Add height and head circumference calculation when tables are available
        
        if 'height' in measurements and measurements['height']:
            # Placeholder - would need height-for-age tables
            percentiles['height'] = None
            
        if 'headCircumference' in measurements and measurements['headCircumference']:
            # Placeholder - would need head circumference-for-age tables
            percentiles['headCircumference'] = None
        
    except Exception as e:
        logger.error(f"Error calculating percentiles: {e}")
        return {}
    
    return percentiles
