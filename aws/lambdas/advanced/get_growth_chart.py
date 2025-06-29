"""
Growth Chart Data Endpoint
GET /babies/{babyId}/growth-chart

This endpoint provides aggregated growth data optimized for chart visualization.
It includes:
- All measurements grouped by measurement type (weight, height, head_circumference)
- Data points with age calculations
- Optional percentile curves for reference
- Filtering by date range
- Optimized data structure for frontend charting libraries

Author: AWS Lambda Hackathon Team
Date: 2024
"""

import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
import os
import sys

# Add the shared directory to the Python path
sys.path.append('/opt/python')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.jwt_utils import verify_jwt_token
from shared.dynamodb_client import get_dynamodb_client
from shared.response_utils import create_response, create_error_response
from shared.validation_utils import validate_baby_id, validate_date_format
from shared.exceptions import ValidationError, AuthenticationError, DatabaseError

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

def lambda_handler(event, context):
    """
    Lambda handler for getting growth chart data for a specific baby
    
    Expected path parameters:
    - babyId: UUID of the baby
    
    Optional query parameters:
    - start_date: Start date for filtering (YYYY-MM-DD format)
    - end_date: End date for filtering (YYYY-MM-DD format)
    - include_percentiles: Whether to include percentile reference curves (true/false)
    - measurement_types: Comma-separated list of measurement types to include
    
    Returns:
    - 200: Growth chart data with measurements grouped by type
    - 400: Invalid request parameters
    - 401: Unauthorized (invalid or missing JWT token)
    - 403: Forbidden (baby doesn't belong to user)
    - 404: Baby not found
    - 500: Internal server error
    """
    try:
        logger.info(f"Processing growth chart request for event: {json.dumps(event, default=str)}")
        
        # Extract and validate JWT token
        user_id = verify_jwt_token(event)
        logger.info(f"Authenticated user: {user_id}")
        
        # Extract path parameters
        path_params = event.get('pathParameters', {}) or {}
        baby_id = path_params.get('babyId')
        
        if not baby_id:
            raise ValidationError("babyId path parameter is required")
        
        # Validate baby_id format
        validate_baby_id(baby_id)
        
        # Extract and validate query parameters
        query_params = event.get('queryStringParameters') or {}
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        include_percentiles = query_params.get('include_percentiles', 'false').lower() == 'true'
        measurement_types_param = query_params.get('measurement_types', 'weight,height,head_circumference')
        
        # Parse measurement types
        valid_measurement_types = {'weight', 'height', 'head_circumference'}
        measurement_types = set()
        for mt in measurement_types_param.split(','):
            mt = mt.strip().lower()
            if mt in valid_measurement_types:
                measurement_types.add(mt)
        
        if not measurement_types:
            measurement_types = valid_measurement_types
        
        # Validate date formats if provided
        if start_date:
            validate_date_format(start_date)
        if end_date:
            validate_date_format(end_date)
            
        # Validate date range
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                raise ValidationError("start_date cannot be later than end_date")
        
        # Get DynamoDB client
        dynamodb = get_dynamodb_client()
        
        # Verify baby ownership and get baby data
        baby_data = get_baby_with_ownership_check(dynamodb, baby_id, user_id)
        
        # Get growth data for the baby
        growth_data = get_growth_data_for_chart(
            dynamodb, baby_id, start_date, end_date, measurement_types
        )
        
        # Process and aggregate data for chart
        chart_data = process_growth_data_for_chart(growth_data, baby_data, measurement_types)
        
        # Add percentile curves if requested
        if include_percentiles:
            chart_data['percentile_curves'] = get_percentile_curves(baby_data, measurement_types)
        
        # Add metadata
        chart_data['metadata'] = {
            'baby_id': baby_id,
            'baby_name': baby_data.get('name', ''),
            'baby_gender': baby_data.get('gender', ''),
            'baby_birth_date': baby_data.get('birth_date', ''),
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'measurement_types': list(measurement_types),
            'total_measurements': len(growth_data),
            'include_percentiles': include_percentiles,
            'generated_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        logger.info(f"Successfully retrieved growth chart data for baby {baby_id}")
        return create_response(200, chart_data)
        
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except AuthenticationError as e:
        logger.warning(f"Authentication error: {str(e)}")
        return create_error_response(401, "AUTHENTICATION_ERROR", str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {str(e)}")
        return create_error_response(500, "DATABASE_ERROR", "An error occurred while accessing the database")
    except Exception as e:
        logger.error(f"Unexpected error in get_growth_chart: {str(e)}", exc_info=True)
        return create_error_response(500, "INTERNAL_ERROR", "An unexpected error occurred")

def get_baby_with_ownership_check(dynamodb, baby_id, user_id):
    """
    Get baby data and verify ownership
    """
    try:
        babies_table = dynamodb.Table(os.getenv('BABIES_TABLE'))
        
        response = babies_table.get_item(
            Key={'id': baby_id}
        )
        
        if 'Item' not in response:
            raise DatabaseError("Baby not found")
        
        baby_data = response['Item']
        
        # Check ownership
        if baby_data.get('userId') != user_id:
            raise AuthenticationError("Access denied: baby does not belong to user")
        
        return baby_data
        
    except Exception as e:
        if isinstance(e, (DatabaseError, AuthenticationError)):
            raise
        logger.error(f"Error getting baby data: {str(e)}")
        raise DatabaseError(f"Error retrieving baby data: {str(e)}")

def get_growth_data_for_chart(dynamodb, baby_id, start_date, end_date, measurement_types):
    """
    Get all growth data for a baby within the specified date range and measurement types
    """
    try:
        growth_data_table = dynamodb.Table(os.getenv('GROWTH_DATA_TABLE'))
        
        # Build filter expression
        filter_expressions = []
        expression_attribute_names = {}
        expression_attribute_values = {}
        
        # Filter by measurement types
        if measurement_types:
            measurement_conditions = []
            for i, mt in enumerate(measurement_types):
                key = f":measurement_type_{i}"
                measurement_conditions.append(f"measurement_type = {key}")
                expression_attribute_values[key] = mt
            filter_expressions.append(f"({' OR '.join(measurement_conditions)})")
        
        # Filter by date range
        if start_date:
            filter_expressions.append("measurement_date >= :start_date")
            expression_attribute_values[':start_date'] = start_date
        
        if end_date:
            filter_expressions.append("measurement_date <= :end_date")
            expression_attribute_values[':end_date'] = end_date
        
        # Query parameters
        query_params = {
            'IndexName': 'baby-date-index',  # Assuming we have a GSI on babyId and measurement_date
            'KeyConditionExpression': 'babyId = :baby_id',
            'ExpressionAttributeValues': {
                ':baby_id': baby_id,
                **expression_attribute_values
            }
        }
        
        if filter_expressions:
            query_params['FilterExpression'] = ' AND '.join(filter_expressions)
        
        if expression_attribute_names:
            query_params['ExpressionAttributeNames'] = expression_attribute_names
        
        # Execute query
        response = growth_data_table.query(**query_params)
        
        # If GSI doesn't exist, fall back to scan
        if 'Items' not in response:
            logger.warning("GSI not found, falling back to scan operation")
            scan_params = {
                'FilterExpression': 'babyId = :baby_id',
                'ExpressionAttributeValues': {':baby_id': baby_id}
            }
            
            if filter_expressions:
                all_filters = ['babyId = :baby_id'] + filter_expressions
                scan_params['FilterExpression'] = ' AND '.join(all_filters)
                scan_params['ExpressionAttributeValues'].update(expression_attribute_values)
            
            response = growth_data_table.scan(**scan_params)
        
        return response.get('Items', [])
        
    except Exception as e:
        logger.error(f"Error getting growth data: {str(e)}")
        raise DatabaseError(f"Error retrieving growth data: {str(e)}")

def calculate_age_in_days(birth_date, measurement_date):
    """
    Calculate age in days between birth date and measurement date
    """
    try:
        birth_dt = datetime.strptime(birth_date, '%Y-%m-%d')
        measurement_dt = datetime.strptime(measurement_date, '%Y-%m-%d')
        return (measurement_dt - birth_dt).days
    except Exception as e:
        logger.warning(f"Error calculating age: {str(e)}")
        return None

def process_growth_data_for_chart(growth_data, baby_data, measurement_types):
    """
    Process and aggregate growth data for chart visualization
    """
    chart_data = {
        'datasets': {},
        'age_ranges': {
            'min_days': None,
            'max_days': None,
            'min_date': None,
            'max_date': None
        }
    }
    
    birth_date = baby_data.get('birth_date')
    if not birth_date:
        logger.warning("Birth date not found for baby, age calculations will be skipped")
    
    # Initialize datasets for each measurement type
    for mt in measurement_types:
        chart_data['datasets'][mt] = {
            'label': mt.replace('_', ' ').title(),
            'unit': get_measurement_unit(mt),
            'data_points': [],
            'statistics': {
                'count': 0,
                'min_value': None,
                'max_value': None,
                'latest_value': None,
                'latest_date': None
            }
        }
    
    # Process each measurement
    for measurement in growth_data:
        measurement_type = measurement.get('measurement_type', '').lower()
        measurement_date = measurement.get('measurement_date')
        measurement_value = measurement.get('value')
        
        if measurement_type not in measurement_types:
            continue
        
        if not measurement_date or measurement_value is None:
            continue
        
        # Convert Decimal to float for JSON serialization
        if isinstance(measurement_value, Decimal):
            measurement_value = float(measurement_value)
        
        # Calculate age if birth date is available
        age_in_days = None
        if birth_date:
            age_in_days = calculate_age_in_days(birth_date, measurement_date)
        
        # Create data point
        data_point = {
            'date': measurement_date,
            'value': measurement_value,
            'age_days': age_in_days,
            'id': measurement.get('id'),
            'notes': measurement.get('notes', '')
        }
        
        # Add to dataset
        dataset = chart_data['datasets'][measurement_type]
        dataset['data_points'].append(data_point)
        
        # Update statistics
        stats = dataset['statistics']
        stats['count'] += 1
        
        if stats['min_value'] is None or measurement_value < stats['min_value']:
            stats['min_value'] = measurement_value
        
        if stats['max_value'] is None or measurement_value > stats['max_value']:
            stats['max_value'] = measurement_value
        
        if stats['latest_date'] is None or measurement_date > stats['latest_date']:
            stats['latest_value'] = measurement_value
            stats['latest_date'] = measurement_date
        
        # Update age ranges
        if age_in_days is not None:
            if chart_data['age_ranges']['min_days'] is None or age_in_days < chart_data['age_ranges']['min_days']:
                chart_data['age_ranges']['min_days'] = age_in_days
                chart_data['age_ranges']['min_date'] = measurement_date
            
            if chart_data['age_ranges']['max_days'] is None or age_in_days > chart_data['age_ranges']['max_days']:
                chart_data['age_ranges']['max_days'] = age_in_days
                chart_data['age_ranges']['max_date'] = measurement_date
    
    # Sort data points by date for each dataset
    for mt in chart_data['datasets']:
        chart_data['datasets'][mt]['data_points'].sort(key=lambda x: x['date'])
    
    return chart_data

def get_measurement_unit(measurement_type):
    """
    Get the appropriate unit for a measurement type
    """
    units = {
        'weight': 'kg',
        'height': 'cm',
        'head_circumference': 'cm'
    }
    return units.get(measurement_type, '')

def get_percentile_curves(baby_data, measurement_types):
    """
    Get percentile reference curves for the chart
    This would typically involve calling the percentile calculation service
    For now, returns placeholder structure
    """
    # This is a placeholder - in a full implementation, this would:
    # 1. Determine the appropriate WHO curves based on baby's gender
    # 2. Generate percentile curves (3rd, 10th, 25th, 50th, 75th, 90th, 97th)
    # 3. Calculate points for the age range being displayed
    
    curves = {}
    gender = baby_data.get('gender', 'unknown')
    
    for measurement_type in measurement_types:
        curves[measurement_type] = {
            'gender': gender,
            'curves': {
                'p3': {'label': '3rd Percentile', 'data_points': []},
                'p10': {'label': '10th Percentile', 'data_points': []},
                'p25': {'label': '25th Percentile', 'data_points': []},
                'p50': {'label': '50th Percentile (Median)', 'data_points': []},
                'p75': {'label': '75th Percentile', 'data_points': []},
                'p90': {'label': '90th Percentile', 'data_points': []},
                'p97': {'label': '97th Percentile', 'data_points': []}
            },
            'note': "Percentile curves would be calculated based on WHO growth standards"
        }
    
    return curves
