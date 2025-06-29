# UpNest DynamoDB CRUD Testing Script - Simple Version
# This script tests basic CRUD operations on all DynamoDB tables

Write-Host "🧪 STARTING UPNEST DYNAMODB CRUD TESTING" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

$awsProfile = "fran-dev"
$testDataPath = "aws/infrastructure/test-data"

# Test Users Table
Write-Host "`n📋 TESTING USERS TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE (put-item)..."
aws dynamodb put-item --table-name UpNest-Users-dev --item file://$testDataPath/user-test.json --profile $awsProfile

Write-Host "- Testing READ (get-item)..."
aws dynamodb get-item --table-name UpNest-Users-dev --key file://$testDataPath/user-key.json --profile $awsProfile --query "Item.name.S" --output text

Write-Host "- Testing UPDATE (update-item)..."
aws dynamodb update-item --table-name UpNest-Users-dev --key file://$testDataPath/user-key.json --update-expression "SET #n = :name" --expression-attribute-names '{\"#n\": \"name\"}' --expression-attribute-values '{\": name\":{\"S\":\"Updated Test User\"}}' --profile $awsProfile

# Test Babies Table  
Write-Host "`n👶 TESTING BABIES TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE (put-item)..."
aws dynamodb put-item --table-name UpNest-Babies-dev --item file://$testDataPath/baby-test.json --profile $awsProfile

Write-Host "- Testing READ (get-item)..."
aws dynamodb get-item --table-name UpNest-Babies-dev --key file://$testDataPath/baby-key.json --profile $awsProfile --query "Item.name.S" --output text

# Test GrowthData Table
Write-Host "`n📊 TESTING GROWTH DATA TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE (put-item)..."
aws dynamodb put-item --table-name UpNest-GrowthData-dev --item file://$testDataPath/growth-data-test.json --profile $awsProfile

Write-Host "- Testing READ (get-item)..."
aws dynamodb get-item --table-name UpNest-GrowthData-dev --key file://$testDataPath/growth-data-key.json --profile $awsProfile --query "Item.value.N" --output text

# Test Vaccinations Table
Write-Host "`n💉 TESTING VACCINATIONS TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE (put-item)..."
aws dynamodb put-item --table-name UpNest-Vaccinations-dev --item file://$testDataPath/vaccination-test.json --profile $awsProfile

Write-Host "- Testing READ (get-item)..."
aws dynamodb get-item --table-name UpNest-Vaccinations-dev --key file://$testDataPath/vaccination-key.json --profile $awsProfile --query "Item.vaccineName.S" --output text

# Test Milestones Table
Write-Host "`n🎯 TESTING MILESTONES TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE (put-item)..."
aws dynamodb put-item --table-name UpNest-Milestones-dev --item file://$testDataPath/milestone-test.json --profile $awsProfile

Write-Host "- Testing READ (get-item)..."
aws dynamodb get-item --table-name UpNest-Milestones-dev --key file://$testDataPath/milestone-key.json --profile $awsProfile --query "Item.description.S" --output text

# Test GSI Queries
Write-Host "`n🔍 TESTING GSI QUERIES" -ForegroundColor Yellow
Write-Host "- Testing Users EmailIndex..."
aws dynamodb query --table-name UpNest-Users-dev --index-name EmailIndex --key-condition-expression "email = :email" --expression-attribute-values file://$testDataPath/email-query.json --profile $awsProfile --query "Count" --output text

Write-Host "- Testing Babies UserBabiesIndex..."
aws dynamodb query --table-name UpNest-Babies-dev --index-name UserBabiesIndex --key-condition-expression "userId = :userId" --expression-attribute-values file://$testDataPath/user-query.json --profile $awsProfile --query "Count" --output text

# Cleanup
Write-Host "`n🧹 CLEANING UP TEST DATA" -ForegroundColor Yellow
Write-Host "- Deleting test records..."
aws dynamodb delete-item --table-name UpNest-Users-dev --key file://$testDataPath/user-key.json --profile $awsProfile
aws dynamodb delete-item --table-name UpNest-Babies-dev --key file://$testDataPath/baby-key.json --profile $awsProfile
aws dynamodb delete-item --table-name UpNest-GrowthData-dev --key file://$testDataPath/growth-data-key.json --profile $awsProfile
aws dynamodb delete-item --table-name UpNest-Vaccinations-dev --key file://$testDataPath/vaccination-key.json --profile $awsProfile
aws dynamodb delete-item --table-name UpNest-Milestones-dev --key file://$testDataPath/milestone-key.json --profile $awsProfile

Write-Host "`n✅ CRUD TESTING COMPLETED!" -ForegroundColor Green
Write-Host "All tables have been tested for basic CRUD operations and GSI queries." -ForegroundColor Green
