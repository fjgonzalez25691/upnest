"""
Tests for the OMS percentile Lambda function.
Checks correct calculation for a typical baby girl,
and verifies error handling for missing fields.
"""

from aws.lambdas.percentil.lambda_function import lambda_handler

def test_percentile_girl_3months():
    """
    Test percentile calculation for a baby girl of 5.35kg at 89 days.
    """
    event = {
        "weight": 5.35,
        "date_birth": "2025-03-25",
        "date_measurement": "2025-06-22",
        "sex": "female"
    }
    response = lambda_handler(event, None)
    # print(response)  # Uncomment for debug
    assert response["success"] is True
    # Accept small margin of error for floating point
    assert abs(response["percentile"] - 26.32) < 0.5

def test_percentile_missing_field():
    """
    Test error handling for missing required field.
    """
    event = {
        "weight": 5.35,
        # Missing 'date_measurement'
        "date_birth": "2025-03-25",
        "sex": "female"
    }
    response = lambda_handler(event, None)
    assert response["success"] is False
    assert "Missing" in response["error"]

# You can add more tests for edge cases and different inputs if needed.

