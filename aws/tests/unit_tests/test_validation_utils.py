"""
Unit tests for validation utilities.
Tests input validation, error handling, and business rules.
"""

import unittest
from datetime import date, datetime, timedelta
import sys
import os

# Add the shared directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'shared'))

from validation_utils import (
    Validator, BabyValidator, GrowthDataValidator, 
    ValidationError, generate_id
)

class TestValidator(unittest.TestCase):
    """Test cases for general validation utilities."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = Validator()
    
    def test_validate_required_fields_all_present(self):
        """Test required fields validation when all fields are present."""
        data = {'name': 'Test', 'email': 'test@example.com', 'age': 25}
        required_fields = ['name', 'email', 'age']
        
        missing = self.validator.validate_required_fields(data, required_fields)
        
        self.assertEqual(missing, [])
    
    def test_validate_required_fields_missing_fields(self):
        """Test required fields validation with missing fields."""
        data = {'name': 'Test', 'age': 25}
        required_fields = ['name', 'email', 'age']
        
        missing = self.validator.validate_required_fields(data, required_fields)
        
        self.assertEqual(missing, ['email'])
    
    def test_validate_required_fields_empty_values(self):
        """Test required fields validation with empty values."""
        data = {'name': '', 'email': None, 'age': 0}
        required_fields = ['name', 'email', 'age']
        
        missing = self.validator.validate_required_fields(data, required_fields)
        
        self.assertEqual(set(missing), {'name', 'email'})
    
    def test_validate_uuid_valid(self):
        """Test UUID validation with valid UUID."""
        valid_uuid = 'f47ac10b-58cc-4372-a567-0e02b2c3d479'
        
        result = self.validator.validate_uuid(valid_uuid)
        
        self.assertEqual(result, valid_uuid)
    
    def test_validate_uuid_invalid_format(self):
        """Test UUID validation with invalid format."""
        invalid_uuid = 'not-a-uuid'
        
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_uuid(invalid_uuid)
        self.assertIn("must be a valid UUID", str(context.exception))
    
    def test_validate_uuid_empty(self):
        """Test UUID validation with empty value."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_uuid('')
        self.assertIn("is required", str(context.exception))
    
    def test_validate_date_valid_string(self):
        """Test date validation with valid date string."""
        valid_date = '2024-01-15'
        
        result = self.validator.validate_date(valid_date)
        
        self.assertEqual(result, valid_date)
    
    def test_validate_date_valid_date_object(self):
        """Test date validation with date object."""
        date_obj = date(2024, 1, 15)
        
        result = self.validator.validate_date(date_obj)
        
        self.assertEqual(result, '2024-01-15')
    
    def test_validate_date_invalid_format(self):
        """Test date validation with invalid format."""
        invalid_date = '15/01/2024'
        
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_date(invalid_date)
        self.assertIn("YYYY-MM-DD format", str(context.exception))
    
    def test_validate_date_invalid_date(self):
        """Test date validation with invalid date."""
        invalid_date = '2024-02-30'
        
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_date(invalid_date)
        self.assertIn("YYYY-MM-DD format", str(context.exception))
    
    def test_validate_gender_valid(self):
        """Test gender validation with valid values."""
        valid_genders = ['male', 'female', 'other', 'MALE', 'Female', 'OTHER']
        expected = ['male', 'female', 'other', 'male', 'female', 'other']
        
        for i, gender in enumerate(valid_genders):
            result = self.validator.validate_gender(gender)
            self.assertEqual(result, expected[i])
    
    def test_validate_gender_invalid(self):
        """Test gender validation with invalid value."""
        invalid_gender = 'unknown'
        
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_gender(invalid_gender)
        self.assertIn("must be one of", str(context.exception))
    
    def test_validate_gender_empty(self):
        """Test gender validation with empty value."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_gender('')
        self.assertIn("is required", str(context.exception))
    
    def test_validate_positive_number_valid(self):
        """Test positive number validation with valid values."""
        valid_numbers = [1, 1.5, '2.5', '10']
        expected = [1.0, 1.5, 2.5, 10.0]
        
        for i, number in enumerate(valid_numbers):
            result = self.validator.validate_positive_number(number)
            self.assertEqual(result, expected[i])
    
    def test_validate_positive_number_zero(self):
        """Test positive number validation with zero."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_positive_number(0)
        self.assertIn("must be a positive number", str(context.exception))
    
    def test_validate_positive_number_negative(self):
        """Test positive number validation with negative number."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_positive_number(-5)
        self.assertIn("must be a positive number", str(context.exception))
    
    def test_validate_positive_number_invalid(self):
        """Test positive number validation with invalid value."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_positive_number('not-a-number')
        self.assertIn("must be a valid number", str(context.exception))
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails."""
        valid_emails = [
            'user@example.com',
            'test.email+tag@domain.co.uk',
            'user123@test-domain.org'
        ]
        
        for email in valid_emails:
            result = self.validator.validate_email(email)
            self.assertEqual(result, email.lower())
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        invalid_emails = [
            'not-an-email',
            '@domain.com',
            'user@',
            'user@domain',
            'user.domain.com'
        ]
        
        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                self.validator.validate_email(email)
    
    def test_validate_email_empty(self):
        """Test email validation with empty value."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_email('')
        self.assertIn("is required", str(context.exception))
    
    def test_validate_string_length_valid(self):
        """Test string length validation with valid strings."""
        result = self.validator.validate_string_length('Valid Name', 'Name', 1, 50)
        self.assertEqual(result, 'Valid Name')
    
    def test_validate_string_length_too_short(self):
        """Test string length validation with too short string."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_string_length('', 'Name', 1, 50)
        self.assertIn("is required", str(context.exception))
    
    def test_validate_string_length_too_long(self):
        """Test string length validation with too long string."""
        long_string = 'a' * 256
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_string_length(long_string, 'Name', 1, 255)
        self.assertIn("must be no more than 255", str(context.exception))
    
    def test_validate_string_length_trimmed(self):
        """Test string length validation trims whitespace."""
        result = self.validator.validate_string_length('  Trimmed  ', 'Name', 1, 50)
        self.assertEqual(result, 'Trimmed')


class TestBabyValidator(unittest.TestCase):
    """Test cases for baby-specific validation."""
    
    def test_validate_baby_data_valid(self):
        """Test baby data validation with valid data."""
        valid_data = {
            'name': 'Baby Test',
            'dateOfBirth': '2024-01-15',
            'gender': 'male',
            'premature': False,
            'birthWeight': 3500
        }
        
        result = BabyValidator.validate_baby_data(valid_data)
        
        self.assertEqual(result['name'], 'Baby Test')
        self.assertEqual(result['dateOfBirth'], '2024-01-15')
        self.assertEqual(result['gender'], 'male')
        self.assertEqual(result['premature'], False)
        self.assertEqual(result['birthWeight'], 3500.0)
    
    def test_validate_baby_data_missing_required_fields(self):
        """Test baby data validation with missing required fields."""
        invalid_data = {'name': 'Baby Test'}  # Missing dateOfBirth and gender
        
        with self.assertRaises(ValidationError) as context:
            BabyValidator.validate_baby_data(invalid_data)
        
        # The validation should fail because dateOfBirth and gender are missing
        # Check that the exception contains information about validation failure
        exception_str = str(context.exception)
        self.assertIn("Validation failed", exception_str)
        
        # Also check that the exception has details about the specific errors
        self.assertTrue(hasattr(context.exception, 'details'))
        self.assertGreater(len(context.exception.details), 0)
    
    def test_validate_baby_data_future_birth_date(self):
        """Test baby data validation with future birth date."""
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        invalid_data = {
            'name': 'Baby Test',
            'dateOfBirth': future_date,
            'gender': 'female'
        }
        
        with self.assertRaises(ValidationError) as context:
            BabyValidator.validate_baby_data(invalid_data)
        self.assertIn("cannot be in the future", str(context.exception.details[0]))
    
    def test_validate_baby_data_invalid_gestational_week(self):
        """Test baby data validation with invalid gestational week."""
        invalid_data = {
            'name': 'Baby Test',
            'dateOfBirth': '2024-01-15',
            'gender': 'female',
            'gestationalWeek': 50
        }
        
        with self.assertRaises(ValidationError) as context:
            BabyValidator.validate_baby_data(invalid_data)
        self.assertIn("cannot be more than 42", str(context.exception.details[0]))
    
    def test_validate_baby_data_invalid_name_length(self):
        """Test baby data validation with invalid name length."""
        invalid_data = {
            'name': 'a' * 101,  # Too long
            'dateOfBirth': '2024-01-15',
            'gender': 'other'
        }
        
        with self.assertRaises(ValidationError) as context:
            BabyValidator.validate_baby_data(invalid_data)
        self.assertIn("must be no more than 100", str(context.exception.details[0]))


class TestGrowthDataValidator(unittest.TestCase):
    """Test cases for growth data validation."""
    
    def test_validate_measurements_valid(self):
        """Test measurement validation with valid data."""
        valid_measurements = {
            'weight': 4500,
            'height': 65,
            'headCircumference': 40
        }
        
        result = GrowthDataValidator.validate_measurements(valid_measurements)
        
        self.assertEqual(result['weight'], 4500.0)
        self.assertEqual(result['height'], 65.0)
        self.assertEqual(result['headCircumference'], 40.0)
    
    def test_validate_measurements_out_of_range(self):
        """Test measurement validation with out-of-range values."""
        invalid_measurements = {
            'weight': 100000,  # Too high
            'height': 5,       # Too low
            'headCircumference': 80  # Too high
        }
        
        with self.assertRaises(ValidationError) as context:
            GrowthDataValidator.validate_measurements(invalid_measurements)
        
        # Should have errors for all three measurements
        self.assertEqual(len(context.exception.details), 3)
    
    def test_validate_measurements_unknown_type(self):
        """Test measurement validation with unknown measurement type."""
        invalid_measurements = {
            'unknownMeasurement': 100
        }
        
        with self.assertRaises(ValidationError) as context:
            GrowthDataValidator.validate_measurements(invalid_measurements)
        self.assertIn("Unknown measurement type", str(context.exception.details[0]))
    
    def test_validate_measurements_invalid_values(self):
        """Test measurement validation with invalid values."""
        invalid_measurements = {
            'weight': 'not-a-number',
            'height': -10
        }
        
        with self.assertRaises(ValidationError) as context:
            GrowthDataValidator.validate_measurements(invalid_measurements)
        
        # Should have errors for both measurements
        self.assertEqual(len(context.exception.details), 2)
    
    def test_validate_measurements_empty(self):
        """Test measurement validation with empty measurements."""
        result = GrowthDataValidator.validate_measurements({})
        self.assertEqual(result, {})


class TestValidationError(unittest.TestCase):
    """Test cases for ValidationError exception."""
    
    def test_validation_error_with_message_only(self):
        """Test ValidationError with message only."""
        error = ValidationError("Test error")
        
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.details, [])
        self.assertEqual(str(error), "Test error")
    
    def test_validation_error_with_details(self):
        """Test ValidationError with message and details."""
        details = ["Error 1", "Error 2"]
        error = ValidationError("Multiple errors", details)
        
        self.assertEqual(error.message, "Multiple errors")
        self.assertEqual(error.details, details)
        self.assertEqual(str(error), "Multiple errors")


class TestGenerateId(unittest.TestCase):
    """Test cases for ID generation utility."""
    
    def test_generate_id_format(self):
        """Test that generated ID is a valid UUID format."""
        generated_id = generate_id()
        
        # Should be 36 characters with hyphens in correct positions
        self.assertEqual(len(generated_id), 36)
        self.assertEqual(generated_id[8], '-')
        self.assertEqual(generated_id[13], '-')
        self.assertEqual(generated_id[18], '-')
        self.assertEqual(generated_id[23], '-')
    
    def test_generate_id_uniqueness(self):
        """Test that generated IDs are unique."""
        ids = [generate_id() for _ in range(100)]
        unique_ids = set(ids)
        
        # All IDs should be unique
        self.assertEqual(len(ids), len(unique_ids))
    
    def test_generate_id_type(self):
        """Test that generated ID is a string."""
        generated_id = generate_id()
        self.assertIsInstance(generated_id, str)


if __name__ == '__main__':
    unittest.main()

