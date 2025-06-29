# pytest configuration file
# This file is automatically loaded by pytest before running tests

import pytest
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import test configuration to set up environment variables
import test_config

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test."""
    # This fixture runs automatically before each test
    # Environment variables are already set in test_config.py
    pass
