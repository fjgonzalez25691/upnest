# pytest configuration file
# This file is automatically loaded by pytest before running tests

import pytest
import sys
import os
from unittest.mock import patch

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import test configuration to set up environment variables
import test_config

# Modules that can conflict between different lambda functions
CONFLICTING_MODULES = [
    'create', 'get', 'list', 'update', 'delete', 'get_single',
    'calculate', 'lambda_function'
]

@pytest.fixture(autouse=True)
def isolate_modules():
    """
    Automatically isolate modules before each test to prevent namespace conflicts.
    This fixture runs before every test and cleans up after.
    """
    # Store original sys.modules state
    original_modules = sys.modules.copy()
    
    # Remove conflicting modules before test
    modules_to_remove = []
    for module_name in list(sys.modules.keys()):
        if any(conflict in module_name for conflict in CONFLICTING_MODULES):
            modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        if module_name in sys.modules:
            del sys.modules[module_name]
    
    yield  # Run the test
    
    # Clean up after test - restore original state
    current_modules = set(sys.modules.keys())
    original_modules_set = set(original_modules.keys())
    
    # Remove modules that were added during test
    for module_name in current_modules - original_modules_set:
        if module_name in sys.modules:
            del sys.modules[module_name]

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test."""
    # This fixture runs automatically before each test
    # Environment variables are already set in test_config.py
    pass

@pytest.fixture
def sample_jwt_token():
    """Standard JWT token for testing."""
    return "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMzQ1Njc4LTkwYWItY2RlZi0xMjM0LTU2Nzg5MGFiY2RlZiIsImV4cCI6OTk5OTk5OTk5OSwiaWF0IjoxNjAwMDAwMDAwLCJpc3MiOiJodHRwczovL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tL3VzLWVhc3QtMV90ZXN0cG9vbCIsImF1ZCI6InRlc3RjbGllbnQifQ.mock_signature"


@pytest.fixture
def sample_user_id():
    """Standard user ID for testing."""
    return "user-12345678-90ab-cdef-1234-567890abcdef"


@pytest.fixture
def sample_baby_id():
    """Standard baby ID for testing."""
    return "baby-12345678-90ab-cdef-1234-567890abcdef"


@pytest.fixture
def sample_record_id():
    """Standard record ID for testing."""
    return "record-12345678-90ab-cdef-1234-567890abcdef"


@pytest.fixture
def sample_baby_data():
    """Standard baby data for testing."""
    return {
        'name': 'Test Baby',
        'birth_date': '2024-01-15',
        'sex': 'male',
        'birth_weight': 3500,
        'birth_height': 50,
        'birth_head_circumference': 35
    }


@pytest.fixture
def sample_growth_data():
    """Standard growth data for testing."""
    return {
        'baby_id': 'baby-12345678-90ab-cdef-1234-567890abcdef',
        'measurement_date': '2024-02-15',
        'measurements': {
            'weight': 4200,
            'height': 55,
            'head_circumference': 38
        },
        'notes': 'Regular checkup'
    }
