#!/usr/bin/env python3
"""
Script to set up DynamoDB local tables for integration testing.
This script creates all necessary tables with proper indexes.
"""

import boto3
import json
import os
import time
from botocore.exceptions import ClientError

# Configure DynamoDB local endpoint
DYNAMODB_ENDPOINT = 'http://localhost:8000'
AWS_REGION = 'us-east-1'

def create_dynamodb_client():
    """Create DynamoDB client for local endpoint."""
    return boto3.client(
        'dynamodb',
        endpoint_url=DYNAMODB_ENDPOINT,
        region_name=AWS_REGION,
        aws_access_key_id='fake',
        aws_secret_access_key='fake'
    )

def create_users_table(dynamodb):
    """Create Users table."""
    table_name = 'upnest-users-local'
    
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'userId',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'EmailIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'email',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )
        print(f"✅ Created table: {table_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"ℹ️  Table {table_name} already exists")
            return True
        else:
            print(f"❌ Error creating table {table_name}: {e}")
            return False

def create_babies_table(dynamodb):
    """Create Babies table."""
    table_name = 'upnest-babies-local'
    
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'babyId',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'babyId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'UserBabiesIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'userId',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )
        print(f"✅ Created table: {table_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"ℹ️  Table {table_name} already exists")
            return True
        else:
            print(f"❌ Error creating table {table_name}: {e}")
            return False

def create_growth_data_table(dynamodb):
    """Create Growth Data table."""
    table_name = 'upnest-growth-data-local'
    
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'dataId',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'dataId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'babyId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'measurementDate',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'BabyGrowthIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'babyId',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'measurementDate',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'UserGrowthDataIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'userId',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )
        print(f"✅ Created table: {table_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"ℹ️  Table {table_name} already exists")
            return True
        else:
            print(f"❌ Error creating table {table_name}: {e}")
            return False

def create_vaccinations_table(dynamodb):
    """Create Vaccinations table."""
    table_name = 'upnest-vaccinations-local'
    
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'vaccinationId',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'vaccinationId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'babyId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'BabyVaccinationsIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'babyId',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'UserVaccinationsIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'userId',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )
        print(f"✅ Created table: {table_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"ℹ️  Table {table_name} already exists")
            return True
        else:
            print(f"❌ Error creating table {table_name}: {e}")
            return False

def create_milestones_table(dynamodb):
    """Create Milestones table."""
    table_name = 'upnest-milestones-local'
    
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'milestoneId',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'milestoneId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'babyId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'BabyMilestonesIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'babyId',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'UserMilestonesIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'userId',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )
        print(f"✅ Created table: {table_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"ℹ️  Table {table_name} already exists")
            return True
        else:
            print(f"❌ Error creating table {table_name}: {e}")
            return False

def wait_for_tables(dynamodb):
    """Wait for tables to be active."""
    tables = [
        'upnest-users-local',
        'upnest-babies-local',
        'upnest-growth-data-local',
        'upnest-vaccinations-local',
        'upnest-milestones-local'
    ]
    
    print("⏳ Waiting for tables to be active...")
    for table_name in tables:
        waiter = dynamodb.get_waiter('table_exists')
        try:
            waiter.wait(TableName=table_name)
            print(f"✅ Table {table_name} is active")
        except Exception as e:
            print(f"❌ Error waiting for table {table_name}: {e}")

def load_test_data(dynamodb):
    """Load test data into tables."""
    print("📄 Loading test data...")
    
    test_data_dir = '../infrastructure/test-data'
    
    # Load users data
    try:
        with open(f'{test_data_dir}/users-test-data.json', 'r') as f:
            users_data = json.load(f)
        
        for user in users_data:
            try:
                dynamodb.put_item(
                    TableName='upnest-users-local',
                    Item=user
                )
            except Exception as e:
                print(f"❌ Error loading user: {e}")
        
        print(f"✅ Loaded {len(users_data)} users")
    except Exception as e:
        print(f"❌ Error loading users data: {e}")
    
    # Load babies data
    baby_files = ['baby1-user1.json', 'baby1-user2.json']
    baby_count = 0
    
    for baby_file in baby_files:
        try:
            with open(f'{test_data_dir}/{baby_file}', 'r') as f:
                babies_data = json.load(f)
                
            if isinstance(babies_data, list):
                for baby in babies_data:
                    try:
                        dynamodb.put_item(
                            TableName='upnest-babies-local',
                            Item=baby
                        )
                        baby_count += 1
                    except Exception as e:
                        print(f"❌ Error loading baby: {e}")
            else:
                try:
                    dynamodb.put_item(
                        TableName='upnest-babies-local',
                        Item=babies_data
                    )
                    baby_count += 1
                except Exception as e:
                    print(f"❌ Error loading baby: {e}")
                    
        except Exception as e:
            print(f"❌ Error loading babies data from {baby_file}: {e}")
    
    print(f"✅ Loaded {baby_count} babies")

def main():
    """Main function to set up DynamoDB local."""
    print("🚀 Setting up DynamoDB Local for integration testing...")
    
    # Create DynamoDB client
    try:
        dynamodb = create_dynamodb_client()
        
        # Test connection
        dynamodb.list_tables()
        print("✅ Connected to DynamoDB Local")
        
    except Exception as e:
        print(f"❌ Could not connect to DynamoDB Local: {e}")
        print("💡 Make sure DynamoDB Local is running on port 8000")
        print("💡 You can start it with: java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb")
        return False
    
    # Create tables
    success = True
    success &= create_users_table(dynamodb)
    success &= create_babies_table(dynamodb)
    success &= create_growth_data_table(dynamodb)
    success &= create_vaccinations_table(dynamodb)
    success &= create_milestones_table(dynamodb)
    
    if not success:
        print("❌ Some tables failed to create")
        return False
    
    # Wait for tables to be active
    wait_for_tables(dynamodb)
    
    # Load test data
    load_test_data(dynamodb)
    
    print("🎉 DynamoDB Local setup complete!")
    print("📋 Tables created:")
    print("   - upnest-users-local")
    print("   - upnest-babies-local") 
    print("   - upnest-growth-data-local")
    print("   - upnest-vaccinations-local")
    print("   - upnest-milestones-local")
    
    return True

if __name__ == '__main__':
    main()
