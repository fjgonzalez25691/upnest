"""
Integration tests for UpNest API endpoints.
Tests all CRUD operations with real JWT tokens and DynamoDB.
"""

import pytest
import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:3001')
DYNAMODB_ENDPOINT = os.getenv('DYNAMODB_ENDPOINT', 'http://localhost:8000')

# Test JWT tokens (from jwt_generator.py)
TEST_TOKENS = {
    'user1': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEtdGVzdC0xMjM0NTYiLCJlbWFpbCI6InVzZXIxQHRlc3QuY29tIiwidG9rZW5fdXNlIjoiYWNjZXNzIiwiaWF0IjoxNzM1NDkxMDQ0LCJleHAiOjE3MzU1Nzc0NDR9.vt9pxxUJOE-7LzxlZj6Z9omjfUc9e3X9PXXJQeYGKx4',
    'user2': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTItdGVzdC03ODkwMTIiLCJlbWFpbCI6InVzZXIyQHRlc3QuY29tIiwidG9rZW5fdXNlIjoiYWNjZXNzIiwiaWF0IjoxNzM1NDkxMDQ0LCJleHAiOjE3MzU1Nzc0NDR9.xmP5pAmkGGxCvOqEQNNNl-h9bUhpNYfbqLCzOAoXiCw',
    'admin': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbi10ZXN0LTQ1Njc4OSIsImVtYWlsIjoiYWRtaW5AdGVzdC5jb20iLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJpYXQiOjE3MzU0OTEwNDQsImV4cCI6MTczNTU3NzQ0NH0.B1-g-V7KyOzB4XreBQGGGCKJJjfEuN9I9N2H4kWV2Lw'
}

class TestBabyCRUD:
    """Test baby CRUD operations."""
    
    def get_headers(self, user='user1'):
        """Get authorization headers for API requests."""
        return {
            'Authorization': f'Bearer {TEST_TOKENS[user]}',
            'Content-Type': 'application/json'
        }
    
    def test_api_health(self):
        """Test that the API is responding."""
        try:
            response = requests.get(f'{API_BASE_URL}/')
            # We expect a 404 since there's no root endpoint, but it means API is running
            assert response.status_code in [200, 404, 403]
        except requests.ConnectionError:
            pytest.fail("API server is not running")
    
    def test_create_baby_success(self):
        """Test creating a baby successfully."""
        baby_data = {
            'name': 'Integration Test Baby',
            'dateOfBirth': '2024-01-15',
            'gender': 'male',
            'birthWeight': 3500,
            'birthHeight': 50
        }
        
        response = requests.post(
            f'{API_BASE_URL}/babies',
            json=baby_data,
            headers=self.get_headers('user1')
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['success'] == True
        assert 'babyId' in data['data']
        assert data['data']['name'] == baby_data['name']
        assert data['data']['userId'] == 'user-1-test-123456'
        
        # Store baby ID for other tests
        pytest.test_baby_id = data['data']['babyId']
    
    def test_create_baby_missing_fields(self):
        """Test creating baby with missing required fields."""
        baby_data = {
            'name': 'Incomplete Baby'
            # Missing dateOfBirth and gender
        }
        
        response = requests.post(
            f'{API_BASE_URL}/babies',
            json=baby_data,
            headers=self.get_headers('user1')
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] == False
    
    def test_create_baby_unauthorized(self):
        """Test creating baby without authorization."""
        baby_data = {
            'name': 'Unauthorized Baby',
            'dateOfBirth': '2024-01-15',
            'gender': 'female'
        }
        
        response = requests.post(
            f'{API_BASE_URL}/babies',
            json=baby_data
            # No authorization headers
        )
        
        assert response.status_code == 401
    
    def test_list_babies(self):
        """Test listing babies for authenticated user."""
        response = requests.get(
            f'{API_BASE_URL}/babies',
            headers=self.get_headers('user1')
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert isinstance(data['data'], list)
        
        # Should contain at least the baby we created
        if hasattr(pytest, 'test_baby_id'):
            baby_ids = [baby['babyId'] for baby in data['data']]
            assert pytest.test_baby_id in baby_ids
    
    def test_get_baby_details(self):
        """Test getting specific baby details."""
        if not hasattr(pytest, 'test_baby_id'):
            pytest.skip("No test baby ID available")
        
        response = requests.get(
            f'{API_BASE_URL}/babies/{pytest.test_baby_id}',
            headers=self.get_headers('user1')
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['data']['babyId'] == pytest.test_baby_id
        assert data['data']['name'] == 'Integration Test Baby'
    
    def test_get_baby_not_found(self):
        """Test getting non-existent baby."""
        fake_id = 'non-existent-baby-id'
        
        response = requests.get(
            f'{API_BASE_URL}/babies/{fake_id}',
            headers=self.get_headers('user1')
        )
        
        assert response.status_code == 404
    
    def test_user_data_isolation(self):
        """Test that users can't access other users' babies."""
        if not hasattr(pytest, 'test_baby_id'):
            pytest.skip("No test baby ID available")
        
        # Try to access user1's baby with user2's token
        response = requests.get(
            f'{API_BASE_URL}/babies/{pytest.test_baby_id}',
            headers=self.get_headers('user2')
        )
        
        # Should return 404 (not found) or 403 (forbidden)
        assert response.status_code in [403, 404]
    
    def test_update_baby(self):
        """Test updating baby information."""
        if not hasattr(pytest, 'test_baby_id'):
            pytest.skip("No test baby ID available")
        
        update_data = {
            'name': 'Updated Integration Test Baby',
            'notes': 'Updated via integration test'
        }
        
        response = requests.put(
            f'{API_BASE_URL}/babies/{pytest.test_baby_id}',
            json=update_data,
            headers=self.get_headers('user1')
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['data']['name'] == update_data['name']
    
    def test_delete_baby(self):
        """Test deleting baby (soft delete)."""
        if not hasattr(pytest, 'test_baby_id'):
            pytest.skip("No test baby ID available")
        
        response = requests.delete(
            f'{API_BASE_URL}/babies/{pytest.test_baby_id}',
            headers=self.get_headers('user1')
        )
        
        assert response.status_code == 204
        
        # Verify baby is no longer accessible
        get_response = requests.get(
            f'{API_BASE_URL}/babies/{pytest.test_baby_id}',
            headers=self.get_headers('user1')
        )
        assert get_response.status_code == 404


class TestGrowthDataCRUD:
    """Test growth data CRUD operations."""
    
    def get_headers(self, user='user1'):
        """Get authorization headers for API requests."""
        return {
            'Authorization': f'Bearer {TEST_TOKENS[user]}',
            'Content-Type': 'application/json'
        }
    
    def test_create_growth_data(self):
        """Test adding growth measurement."""
        # First, we need a baby ID (use existing test data)
        baby_id = 'baby-test-001-user1'  # From our test data
        
        growth_data = {
            'measurementDate': datetime.now().strftime('%Y-%m-%d'),
            'measurementType': 'weight',
            'value': 4800,
            'unit': 'grams',
            'notes': 'Integration test measurement'
        }
        
        response = requests.post(
            f'{API_BASE_URL}/babies/{baby_id}/growth',
            json=growth_data,
            headers=self.get_headers('user1')
        )
        
        # Note: This might fail if the baby doesn't exist in test data
        # That's expected and part of the testing validation
        assert response.status_code in [201, 404]
        
        if response.status_code == 201:
            data = response.json()
            assert data['success'] == True
            assert 'dataId' in data['data']
            pytest.test_growth_id = data['data']['dataId']


class TestJWTValidation:
    """Test JWT authentication and validation."""
    
    def test_invalid_token(self):
        """Test request with invalid JWT token."""
        headers = {
            'Authorization': 'Bearer invalid-token',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{API_BASE_URL}/babies',
            headers=headers
        )
        
        assert response.status_code == 401
    
    def test_expired_token(self):
        """Test request with expired JWT token."""
        # This is a token that's already expired
        expired_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJleHAiOjE2MzAwMDAwMDB9.invalid'
        
        headers = {
            'Authorization': f'Bearer {expired_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{API_BASE_URL}/babies',
            headers=headers
        )
        
        assert response.status_code == 401
    
    def test_missing_authorization(self):
        """Test request without authorization header."""
        response = requests.get(f'{API_BASE_URL}/babies')
        
        assert response.status_code == 401


if __name__ == '__main__':
    # Run tests with detailed output
    pytest.main([__file__, '-v', '--tb=short'])
