"""
Unit tests for custom exceptions.
Tests exception classes and error handling.
"""

import unittest
import sys
import os

# Add the shared directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lambdas', 'shared'))

from exceptions import (
    UpNestError, ValidationError, BabyNotFoundError, 
    UnauthorizedAccessError
)

class TestCustomExceptions(unittest.TestCase):
    """Test cases for custom exception classes."""
    
    def test_upnest_error_base(self):
        """Test base UpNestError exception."""
        error = UpNestError("Base error message")
        
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Base error message")
    
    def test_validation_error_basic(self):
        """Test ValidationError with basic message."""
        error = ValidationError("Invalid input")
        
        self.assertIsInstance(error, UpNestError)
        self.assertEqual(str(error), "Invalid input")
        self.assertIsNone(error.field)
        self.assertEqual(error.details, [])
    
    def test_validation_error_with_field(self):
        """Test ValidationError with field information."""
        error = ValidationError("Name is required", field="name")
        
        self.assertEqual(str(error), "Name is required")
        self.assertEqual(error.field, "name")
    
    def test_validation_error_with_details(self):
        """Test ValidationError with details list."""
        details = ["Must be at least 3 characters", "Cannot contain numbers"]
        error = ValidationError("Invalid name", field="name", details=details)
        
        self.assertEqual(error.field, "name")
        self.assertEqual(error.details, details)
    
    def test_baby_not_found_error(self):
        """Test BabyNotFoundError exception."""
        baby_id = "baby-123"
        error = BabyNotFoundError(baby_id)
        
        self.assertIsInstance(error, UpNestError)
        self.assertEqual(str(error), f"Baby with ID {baby_id} not found")
        self.assertEqual(error.baby_id, baby_id)
    
    def test_unauthorized_access_error(self):
        """Test UnauthorizedAccessError exception."""
        resource_type = "baby"
        resource_id = "baby-456"
        error = UnauthorizedAccessError(resource_type, resource_id)
        
        self.assertIsInstance(error, UpNestError)
        self.assertEqual(str(error), f"Unauthorized access to {resource_type}: {resource_id}")
        self.assertEqual(error.resource_type, resource_type)
        self.assertEqual(error.resource_id, resource_id)
    
    def test_exception_inheritance_chain(self):
        """Test that all custom exceptions inherit from UpNestError."""
        exceptions_to_test = [
            ValidationError("test"),
            BabyNotFoundError("test-id"),
            UnauthorizedAccessError("resource", "id")
        ]
        
        for error in exceptions_to_test:
            self.assertIsInstance(error, UpNestError)
            self.assertIsInstance(error, Exception)


if __name__ == '__main__':
    unittest.main()
