"""
Unit tests for DynamoDB client utilities.
Tests DynamoDB operations, error handling, and configuration.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from botocore.exceptions import ClientError

# Add the shared directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'shared'))

from dynamodb_client import DynamoDBClient

class TestDynamoDBClient(unittest.TestCase):
    """Test cases for DynamoDB client utilities."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'USERS_TABLE': 'test-users-table',
            'BABIES_TABLE': 'test-babies-table',
            'GROWTH_DATA_TABLE': 'test-growth-data-table',
            'VACCINATIONS_TABLE': 'test-vaccinations-table',
            'MILESTONES_TABLE': 'test-milestones-table'
        })
        self.env_patcher.start()
        
        # Mock boto3 resource
        self.boto3_patcher = patch('dynamodb_client.boto3.resource')
        self.mock_dynamodb = self.boto3_patcher.start()
        
        # Create client instance
        self.client = DynamoDBClient()
        
        # Sample test data
        self.sample_item = {
            'userId': 'user-1-test-123456',
            'name': 'Test User',
            'email': 'test@example.com'
        }
        
        self.sample_key = {'userId': 'user-1-test-123456'}
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
        self.boto3_patcher.stop()
    
    def test_init_with_missing_environment_variables(self):
        """Test client initialization with missing environment variables."""
        with patch.dict(os.environ, {'USERS_TABLE': 'test-table'}, clear=True):
            with self.assertRaises(ValueError) as context:
                DynamoDBClient()
            self.assertIn("Missing environment variables for tables", str(context.exception))
    
    def test_get_table_success(self):
        """Test successful table retrieval."""
        mock_table = MagicMock()
        self.mock_dynamodb.Table.return_value = mock_table
        
        table = self.client.get_table('users')
        
        self.assertEqual(table, mock_table)
        self.mock_dynamodb.Table.assert_called_once_with('test-users-table')
    
    def test_get_table_unknown_table(self):
        """Test table retrieval with unknown table name."""
        with self.assertRaises(ValueError) as context:
            self.client.get_table('unknown_table')
        self.assertIn("Unknown table: unknown_table", str(context.exception))
    
    def test_get_item_success(self):
        """Test successful item retrieval."""
        mock_table = MagicMock()
        mock_table.get_item.return_value = {'Item': self.sample_item}
        self.mock_dynamodb.Table.return_value = mock_table
        
        result = self.client.get_item('users', self.sample_key)
        
        self.assertEqual(result, self.sample_item)
        mock_table.get_item.assert_called_once_with(Key=self.sample_key)
    
    def test_get_item_not_found(self):
        """Test item retrieval when item doesn't exist."""
        mock_table = MagicMock()
        mock_table.get_item.return_value = {}
        self.mock_dynamodb.Table.return_value = mock_table
        
        result = self.client.get_item('users', self.sample_key)
        
        self.assertIsNone(result)
    
    def test_get_item_client_error(self):
        """Test item retrieval with client error."""
        mock_table = MagicMock()
        mock_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException'}}, 'GetItem'
        )
        self.mock_dynamodb.Table.return_value = mock_table
        
        with self.assertRaises(ClientError):
            self.client.get_item('users', self.sample_key)
    
    def test_put_item_success(self):
        """Test successful item insertion."""
        mock_table = MagicMock()
        self.mock_dynamodb.Table.return_value = mock_table
        
        result = self.client.put_item('users', self.sample_item)
        
        self.assertTrue(result)
        mock_table.put_item.assert_called_once_with(Item=self.sample_item)
    
    def test_put_item_client_error(self):
        """Test item insertion with client error."""
        mock_table = MagicMock()
        mock_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'ValidationException'}}, 'PutItem'
        )
        self.mock_dynamodb.Table.return_value = mock_table
        
        with self.assertRaises(ClientError):
            self.client.put_item('users', self.sample_item)
    
    def test_update_item_success(self):
        """Test successful item update."""
        mock_table = MagicMock()
        self.mock_dynamodb.Table.return_value = mock_table
        
        update_expression = "SET #name = :name"
        expression_values = {':name': 'Updated Name'}
        
        result = self.client.update_item('users', self.sample_key, update_expression, expression_values)
        
        self.assertTrue(result)
        mock_table.update_item.assert_called_once_with(
            Key=self.sample_key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
    
    def test_update_item_client_error(self):
        """Test item update with client error."""
        mock_table = MagicMock()
        mock_table.update_item.side_effect = ClientError(
            {'Error': {'Code': 'ConditionalCheckFailedException'}}, 'UpdateItem'
        )
        self.mock_dynamodb.Table.return_value = mock_table
        
        with self.assertRaises(ClientError):
            self.client.update_item('users', self.sample_key, "SET #name = :name", {':name': 'New Name'})
    
    def test_delete_item_success(self):
        """Test successful item deletion."""
        mock_table = MagicMock()
        self.mock_dynamodb.Table.return_value = mock_table
        
        result = self.client.delete_item('users', self.sample_key)
        
        self.assertTrue(result)
        mock_table.delete_item.assert_called_once_with(Key=self.sample_key)
    
    def test_delete_item_client_error(self):
        """Test item deletion with client error."""
        mock_table = MagicMock()
        mock_table.delete_item.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException'}}, 'DeleteItem'
        )
        self.mock_dynamodb.Table.return_value = mock_table
        
        with self.assertRaises(ClientError):
            self.client.delete_item('users', self.sample_key)
    
    def test_query_gsi_success(self):
        """Test successful GSI query."""
        mock_table = MagicMock()
        mock_items = [self.sample_item, {'userId': 'user-2', 'name': 'User 2'}]
        mock_table.query.return_value = {'Items': mock_items}
        self.mock_dynamodb.Table.return_value = mock_table
        
        key_condition = 'userId = :userId'
        expression_values = {':userId': 'user-1-test-123456'}
        
        result = self.client.query_gsi('babies', 'UserBabiesIndex', key_condition, expression_values)
        
        self.assertEqual(result, mock_items)
        mock_table.query.assert_called_once_with(
            IndexName='UserBabiesIndex',
            KeyConditionExpression=key_condition,
            ExpressionAttributeValues=expression_values
        )
    
    def test_query_gsi_with_limit(self):
        """Test GSI query with limit."""
        mock_table = MagicMock()
        mock_items = [self.sample_item]
        mock_table.query.return_value = {'Items': mock_items}
        self.mock_dynamodb.Table.return_value = mock_table
        
        key_condition = 'userId = :userId'
        expression_values = {':userId': 'user-1-test-123456'}
        limit = 10
        
        result = self.client.query_gsi('babies', 'UserBabiesIndex', key_condition, expression_values, limit)
        
        self.assertEqual(result, mock_items)
        mock_table.query.assert_called_once_with(
            IndexName='UserBabiesIndex',
            KeyConditionExpression=key_condition,
            ExpressionAttributeValues=expression_values,
            Limit=limit
        )
    
    def test_query_gsi_no_items(self):
        """Test GSI query with no items returned."""
        mock_table = MagicMock()
        mock_table.query.return_value = {}
        self.mock_dynamodb.Table.return_value = mock_table
        
        key_condition = 'userId = :userId'
        expression_values = {':userId': 'nonexistent-user'}
        
        result = self.client.query_gsi('babies', 'UserBabiesIndex', key_condition, expression_values)
        
        self.assertEqual(result, [])
    
    def test_query_gsi_client_error(self):
        """Test GSI query with client error."""
        mock_table = MagicMock()
        mock_table.query.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException'}}, 'Query'
        )
        self.mock_dynamodb.Table.return_value = mock_table
        
        with self.assertRaises(ClientError):
            self.client.query_gsi('babies', 'NonExistentIndex', 'userId = :userId', {':userId': 'test'})
    
    def test_table_names_property(self):
        """Test that table names are correctly set."""
        expected_tables = {
            'users': 'test-users-table',
            'babies': 'test-babies-table',
            'growth_data': 'test-growth-data-table',
            'vaccinations': 'test-vaccinations-table',
            'milestones': 'test-milestones-table'
        }
        
        self.assertEqual(self.client.table_names, expected_tables)


class TestDynamoDBClientIntegration(unittest.TestCase):
    """Integration test cases for DynamoDB client operations."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.env_patcher = patch.dict(os.environ, {
            'USERS_TABLE': 'test-users-table',
            'BABIES_TABLE': 'test-babies-table',
            'GROWTH_DATA_TABLE': 'test-growth-data-table',
            'VACCINATIONS_TABLE': 'test-vaccinations-table',
            'MILESTONES_TABLE': 'test-milestones-table'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up integration test environment."""
        self.env_patcher.stop()
    
    @patch('dynamodb_client.boto3.resource')
    def test_full_crud_operations(self, mock_boto3):
        """Test complete CRUD operations flow."""
        # Mock table
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        
        # Mock responses
        mock_table.get_item.return_value = {'Item': {'userId': 'test', 'name': 'Test'}}
        mock_table.put_item.return_value = {}
        mock_table.update_item.return_value = {}
        mock_table.delete_item.return_value = {}
        
        client = DynamoDBClient()
        
        # Test put
        self.assertTrue(client.put_item('users', {'userId': 'test', 'name': 'Test'}))
        
        # Test get
        item = client.get_item('users', {'userId': 'test'})
        self.assertEqual(item['userId'], 'test')
        
        # Test update
        self.assertTrue(client.update_item('users', {'userId': 'test'}, 'SET #name = :name', {':name': 'Updated'}))
        
        # Test delete
        self.assertTrue(client.delete_item('users', {'userId': 'test'}))


if __name__ == '__main__':
    unittest.main()
