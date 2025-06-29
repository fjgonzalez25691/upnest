"""
Unit tests for response utilities.
Tests HTTP response formatting and error handling.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the shared directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lambdas', 'shared'))

from response_utils import (
    create_response, success_response, created_response, 
    validation_error_response, not_found_response, 
    unauthorized_response, bad_request_response, internal_error_response
)

class TestResponseUtils(unittest.TestCase):
    """Test cases for response utilities."""
    
    def test_create_response_success(self):
        """Test basic response creation."""
        response = create_response(200, {'result': 'success'}, 'Operation completed')
        
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('body', response)
        body = json.loads(response['body'])
        self.assertEqual(body['success'], True)
        self.assertEqual(body['data']['result'], 'success')
        self.assertEqual(body['message'], 'Operation completed')
    
    def test_create_response_error(self):
        """Test error response creation."""
        error_info = {'code': 'VALIDATION_ERROR', 'details': 'Invalid input'}
        response = create_response(400, error=error_info)
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['success'], False)
        self.assertEqual(body['error']['code'], 'VALIDATION_ERROR')
    
    def test_success_response(self):
        """Test success response helper."""
        response = success_response({'user_id': '123'}, 'User created')
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['success'], True)
        self.assertEqual(body['data']['user_id'], '123')
    
    def test_internal_error_response(self):
        """Test internal error response helper."""
        response = internal_error_response('Something went wrong')
        
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertEqual(body['success'], False)
        self.assertEqual(body['error']['message'], 'Something went wrong')
    
    def test_validation_error_response(self):
        """Test validation error response."""
        errors = ['Name is required', 'Email is invalid']
        response = validation_error_response(errors)
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['error']['code'], 'VALIDATION_ERROR')
        self.assertEqual(body['error']['errors'], errors)
    
    def test_not_found_response(self):
        """Test not found response."""
        response = not_found_response('User not found')
        
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertEqual(body['error']['message'], 'User not found')
    
    def test_unauthorized_response(self):
        """Test unauthorized response."""
        response = unauthorized_response()
        
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertEqual(body['error']['code'], 'UNAUTHORIZED')
    
    def test_cors_headers(self):
        """Test CORS headers are included."""
        response = success_response({})
        
        self.assertIn('headers', response)
        self.assertEqual(response['headers']['Access-Control-Allow-Origin'], '*')
        self.assertIn('Access-Control-Allow-Headers', response['headers'])


if __name__ == '__main__':
    unittest.main()
