"""
Percentiles tests package.
Contains tests for percentile calculation lambda function.
"""

# Test modules
from .test_percentiles_success import TestPercentilesSuccess
from .test_percentiles_auth import TestPercentilesAuth
from .test_percentiles_validation import TestPercentilesValidation
from .test_percentiles_utils import TestPercentilesUtils

__all__ = [
    'TestPercentilesSuccess',
    'TestPercentilesAuth', 
    'TestPercentilesValidation',
    'TestPercentilesUtils'
]
