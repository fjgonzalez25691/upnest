"""
Lambda function to get growth chart data for a baby.
GET /babies/{babyId}/growth-chart
"""

import json
import logging
import math
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
    from calculate import calculate_zscore, zscore_to_percentile, load_table
    import pandas as pd
    from scipy.stats import norm
    percentile_calculation_available = True
except ImportError:
    percentile_calculation_available = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event, context):
    """
    Get growth chart data optimized for frontend visualization.
    
    Path parameters:
    - babyId: UUID of the baby
    
    Query parameters (optional):
    - startDate: Filter data from this date (YYYY-MM-DD)
    - endDate: Filter data until this date (YYYY-MM-DD)
    - measurementType: Filter by specific measurement (weight, height, headCircumference)
    - includePercentileCurves: Include WHO percentile curves (true/false, default: true)
    
    Response:
    {
        "success": true,
        "data": {
            "babyInfo": {
                "babyId": "uuid",
                "name": "Emma",
                "gender": "female",
                "dateOfBirth": "2023-06-15",
                "ageInDays": 365
            },
            "chartData": {
                "weight": [
                    {
                        "date": "2024-01-15",
                        "ageInDays": 214,
                        "value": 7500,
                        "percentile": 65.2,
                        "zscore": 0.38
                    }
                ],
                "height": [...],
                "headCircumference": [...]
            },
            "percentileCurves": {
                "weight": {
                    "p5": [...],
                    "p50": [...],
                    "p95": [...]
                }
            },
            "metadata": {
                "totalMeasurements": 15,
                "dateRange": {
                    "start": "2023-07-01",
                    "end": "2024-06-15"
                },
                "measurementTypes": ["weight", "height", "headCircumference"]
            }
        }
    }
    """
    logger.info(f"Getting growth chart data for baby - Request ID: {context.aws_request_id}")
    
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
    
    # Parse query parameters
    query_params = event.get('queryStringParameters') or {}
    start_date = query_params.get('startDate')
    end_date = query_params.get('endDate')
    measurement_type = query_params.get('measurementType')
    include_curves = query_params.get('includePercentileCurves', 'true').lower() == 'true'
    
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
        
        # Calculate current age
        birth_date_str = baby.get('dateOfBirth')
        if not birth_date_str:
            return bad_request_response("Baby birth date not found")
        
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            today = date.today()
            age_in_days = (today - birth_date).days
        except ValueError:
            return bad_request_response("Invalid birth date format")
        
        # 2. Get all growth data for this baby
        growth_data = get_growth_data_for_chart(baby_id, start_date, end_date, measurement_type)
        
        # 3. Aggregate and structure data by measurement type
        chart_data = aggregate_chart_data(growth_data, baby.get('gender', 'male'), birth_date_str)
        
        # 4. Generate percentile curves if requested
        percentile_curves = {}
        if include_curves and percentile_calculation_available:
            percentile_curves = generate_percentile_curves(
                baby.get('gender', 'male'), 
                age_in_days,
                measurement_type
            )
        
        # 5. Build metadata
        metadata = build_chart_metadata(growth_data, start_date, end_date)
        
        # 6. Structure response
        response_data = {
            'babyInfo': {
                'babyId': baby_id,
                'name': baby.get('name'),
                'gender': baby.get('gender'),
                'dateOfBirth': birth_date_str,
                'ageInDays': age_in_days,
                'isPremature': baby.get('premature', False)
            },
            'chartData': chart_data,
            'percentileCurves': percentile_curves,
            'metadata': metadata
        }
        
        logger.info(f"Retrieved chart data for baby {baby_id}: {metadata['totalMeasurements']} measurements")
        return success_response(data=response_data)
        
    except Exception as e:
        logger.error(f"Error getting chart data for baby {baby_id}: {e}")
        return internal_error_response("Failed to get growth chart data")

def get_growth_data_for_chart(baby_id: str, start_date: str = None, end_date: str = None, measurement_type: str = None) -> list:
    """
    Get all growth data for a baby with optional filtering.
    
    Args:
        baby_id: UUID of the baby
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        measurement_type: Optional measurement type filter
        
    Returns:
        List of growth data records
    """
    try:
        # Query all growth data for this baby
        growth_data = dynamodb_client.query_gsi(
            table_name='growth_data',
            index_name='BabyGrowthIndex',
            key_condition={'babyId': baby_id},
            scan_index_forward=True,  # Oldest first for chart
            limit=500  # Reasonable limit for charts
        )
        
        # Apply date filters
        if start_date or end_date:
            filtered_data = []
            for record in growth_data:
                measurement_date = record.get('measurementDate', '')
                
                # Apply start date filter
                if start_date and measurement_date < start_date:
                    continue
                
                # Apply end date filter
                if end_date and measurement_date > end_date:
                    continue
                
                filtered_data.append(record)
            
            growth_data = filtered_data
        
        # Apply measurement type filter
        if measurement_type:
            filtered_data = []
            for record in growth_data:
                measurements = record.get('measurements', {})
                if measurement_type in measurements and measurements[measurement_type]:
                    filtered_data.append(record)
            
            growth_data = filtered_data
        
        return growth_data
        
    except Exception as e:
        logger.error(f"Error getting growth data for chart: {e}")
        return []

def aggregate_chart_data(growth_data: list, gender: str, birth_date: str) -> dict:
    """
    Aggregate growth data by measurement type for chart visualization.
    
    Args:
        growth_data: List of growth data records
        gender: Baby's gender
        birth_date: Baby's birth date
        
    Returns:
        Dict with data organized by measurement type
    """
    chart_data = {
        'weight': [],
        'height': [],
        'headCircumference': []
    }
    
    birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()
    
    for record in growth_data:
        measurements = record.get('measurements', {})
        measurement_date = record.get('measurementDate', '')
        
        if not measurement_date:
            continue
        
        try:
            measurement_date_obj = datetime.strptime(measurement_date, '%Y-%m-%d').date()
            age_in_days = (measurement_date_obj - birth_date_obj).days
        except ValueError:
            continue
        
        # Process each measurement type
        for measure_type, value in measurements.items():
            if measure_type in chart_data and value:
                
                # Calculate percentile if possible
                percentile = None
                zscore = None
                
                if percentile_calculation_available and measure_type == 'weight':
                    percentile, zscore = calculate_percentile_for_measurement(
                        value / 1000,  # Convert grams to kg
                        gender,
                        age_in_days
                    )
                
                chart_point = {
                    'date': measurement_date,
                    'ageInDays': age_in_days,
                    'value': value,
                    'percentile': percentile,
                    'zscore': zscore,
                    'dataId': record.get('dataId'),
                    'measurementSource': record.get('measurementSource', 'unknown')
                }
                
                chart_data[measure_type].append(chart_point)
    
    # Sort all arrays by age
    for measure_type in chart_data:
        chart_data[measure_type].sort(key=lambda x: x['ageInDays'])
    
    return chart_data

def calculate_percentile_for_measurement(value_kg: float, gender: str, age_in_days: int) -> tuple:
    """
    Calculate percentile and z-score for a single measurement.
    
    Args:
        value_kg: Weight value in kg
        gender: 'male' or 'female'
        age_in_days: Age in days
        
    Returns:
        Tuple of (percentile, zscore) or (None, None) if calculation fails
    """
    try:
        df = load_table(gender)
        
        # Find row for age
        row = df.loc[df['Day'] == age_in_days]
        if row.empty:
            # Find closest age
            idx = (df['Day'] - age_in_days).abs().idxmin()
            row = df.loc[[idx]]
        
        if not row.empty:
            L, M, S = float(row['L'].iloc[0]), float(row['M'].iloc[0]), float(row['S'].iloc[0])
            zscore = calculate_zscore(value_kg, L, M, S)
            percentile = round(zscore_to_percentile(zscore), 1)
            return percentile, round(zscore, 2)
    
    except Exception as e:
        logger.error(f"Error calculating percentile: {e}")
    
    return None, None

def generate_percentile_curves(gender: str, max_age_days: int, measurement_type: str = None) -> dict:
    """
    Generate WHO percentile curves for chart overlay.
    
    Args:
        gender: 'male' or 'female'
        max_age_days: Maximum age to generate curves for
        measurement_type: Specific measurement type or None for all
        
    Returns:
        Dict with percentile curves
    """
    curves = {}
    
    if not percentile_calculation_available:
        return curves
    
    # Only generate weight curves for now (since we have those tables)
    if measurement_type is None or measurement_type == 'weight':
        try:
            curves['weight'] = generate_weight_percentile_curves(gender, max_age_days)
        except Exception as e:
            logger.error(f"Error generating weight curves: {e}")
    
    # TODO: Add height and head circumference curves when tables are available
    if measurement_type is None or measurement_type == 'height':
        curves['height'] = {'p5': [], 'p50': [], 'p95': [], 'note': 'Height curves not yet available'}
    
    if measurement_type is None or measurement_type == 'headCircumference':
        curves['headCircumference'] = {'p5': [], 'p50': [], 'p95': [], 'note': 'Head circumference curves not yet available'}
    
    return curves

def generate_weight_percentile_curves(gender: str, max_age_days: int) -> dict:
    """
    Generate weight percentile curves (5th, 50th, 95th).
    
    Args:
        gender: 'male' or 'female'
        max_age_days: Maximum age in days
        
    Returns:
        Dict with percentile curves
    """
    try:
        df = load_table(gender)
        
        # Filter to available age range
        df_filtered = df[df['Day'] <= max_age_days].copy()
        
        # Generate curves by calculating weight values for specific percentiles
        curves = {'p5': [], 'p50': [], 'p95': []}
        
        for _, row in df_filtered.iterrows():
            age_days = int(row['Day'])
            L, M, S = float(row['L']), float(row['M']), float(row['S'])
            
            # Calculate weight values for 5th, 50th, and 95th percentiles
            for percentile, curve_key in [(5, 'p5'), (50, 'p50'), (95, 'p95')]:
                # Convert percentile to z-score
                from scipy.stats import norm
                zscore = norm.ppf(percentile / 100)
                
                # Calculate weight value from z-score using LMS method
                if L == 0:
                    weight_kg = M * math.exp(S * zscore)
                else:
                    weight_kg = M * ((1 + L * S * zscore) ** (1 / L))
                
                curves[curve_key].append({
                    'ageInDays': age_days,
                    'value': round(weight_kg * 1000),  # Convert to grams
                    'percentile': percentile
                })
        
        return curves
        
    except Exception as e:
        logger.error(f"Error generating weight percentile curves: {e}")
        return {'p5': [], 'p50': [], 'p95': []}

def build_chart_metadata(growth_data: list, start_date: str = None, end_date: str = None) -> dict:
    """
    Build metadata for the chart data.
    
    Args:
        growth_data: List of growth data records
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        Dict with metadata
    """
    if not growth_data:
        return {
            'totalMeasurements': 0,
            'dateRange': {'start': None, 'end': None},
            'measurementTypes': []
        }
    
    # Find date range
    dates = [record.get('measurementDate') for record in growth_data if record.get('measurementDate')]
    dates = [d for d in dates if d]  # Remove None values
    
    date_range = {
        'start': min(dates) if dates else start_date,
        'end': max(dates) if dates else end_date
    }
    
    # Find available measurement types
    measurement_types = set()
    for record in growth_data:
        measurements = record.get('measurements', {})
        for measure_type, value in measurements.items():
            if value:  # Only include types with actual values
                measurement_types.add(measure_type)
    
    return {
        'totalMeasurements': len(growth_data),
        'dateRange': date_range,
        'measurementTypes': sorted(list(measurement_types)),
        'filters': {
            'startDate': start_date,
            'endDate': end_date
        }
    }
