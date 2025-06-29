# UpNest DynamoDB CRUD Testing Script
# This script tests basic CRUD operations on all DynamoDB tables

Write-Host "STARTING UPNEST DYNAMODB CRUD TESTING" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

$awsProfile = "fran-dev"
$testDataPath = "aws/infrastructure/test-data"

# Test Users Table
Write-Host "`nTESTING USERS TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE..."
aws dynamodb put-item --table-name UpNest-Users-dev --item file://$testDataPath/user-test.json --profile $awsProfile

Write-Host "- Testing READ..."
$userName = aws dynamodb get-item --table-name UpNest-Users-dev --key file://$testDataPath/user-key.json --profile $awsProfile --query "Item.name.S" --output text
Write-Host "  User found: $userName" -ForegroundColor Green

# Test Babies Table  
Write-Host "`nTESTING BABIES TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE..."
aws dynamodb put-item --table-name UpNest-Babies-dev --item file://$testDataPath/baby-test.json --profile $awsProfile

Write-Host "- Testing READ..."
$babyName = aws dynamodb get-item --table-name UpNest-Babies-dev --key file://$testDataPath/baby-key.json --profile $awsProfile --query "Item.name.S" --output text
Write-Host "  Baby found: $babyName" -ForegroundColor Green

# Test GrowthData Table
Write-Host "`nTESTING GROWTH DATA TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE..."
aws dynamodb put-item --table-name UpNest-GrowthData-dev --item file://$testDataPath/growth-data-test.json --profile $awsProfile

Write-Host "- Testing READ..."
$growthValue = aws dynamodb get-item --table-name UpNest-GrowthData-dev --key file://$testDataPath/growth-data-key.json --profile $awsProfile --query "Item.value.N" --output text
Write-Host "  Growth data found: $growthValue" -ForegroundColor Green

# Test Vaccinations Table
Write-Host "`nTESTING VACCINATIONS TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE..."
aws dynamodb put-item --table-name UpNest-Vaccinations-dev --item file://$testDataPath/vaccination-test.json --profile $awsProfile

Write-Host "- Testing READ..."
$vaccineName = aws dynamodb get-item --table-name UpNest-Vaccinations-dev --key file://$testDataPath/vaccination-key.json --profile $awsProfile --query "Item.vaccineName.S" --output text
Write-Host "  Vaccination found: $vaccineName" -ForegroundColor Green

# Test Milestones Table
Write-Host "`nTESTING MILESTONES TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE..."
aws dynamodb put-item --table-name UpNest-Milestones-dev --item file://$testDataPath/milestone-test.json --profile $awsProfile

Write-Host "- Testing READ..."
$milestoneDesc = aws dynamodb get-item --table-name UpNest-Milestones-dev --key file://$testDataPath/milestone-key.json --profile $awsProfile --query "Item.description.S" --output text
Write-Host "  Milestone found: $milestoneDesc" -ForegroundColor Green

# Test GSI Queries
Write-Host "`nTESTING GSI QUERIES" -ForegroundColor Yellow
Write-Host "- Testing Users EmailIndex..."
$emailCount = aws dynamodb query --table-name UpNest-Users-dev --index-name EmailIndex --key-condition-expression "email = :email" --expression-attribute-values file://$testDataPath/email-query.json --profile $awsProfile --query "Count" --output text
Write-Host "  EmailIndex results: $emailCount items" -ForegroundColor Green

Write-Host "- Testing Babies UserBabiesIndex..."  
$babyCount = aws dynamodb query --table-name UpNest-Babies-dev --index-name UserBabiesIndex --key-condition-expression "userId = :userId" --expression-attribute-values file://$testDataPath/user-query.json --profile $awsProfile --query "Count" --output text
Write-Host "  UserBabiesIndex results: $babyCount items" -ForegroundColor Green

# Cleanup
Write-Host "`nCLEANING UP TEST DATA" -ForegroundColor Yellow
Write-Host "- Deleting test records..."
aws dynamodb delete-item --table-name UpNest-Users-dev --key file://$testDataPath/user-key.json --profile $awsProfile
aws dynamodb delete-item --table-name UpNest-Babies-dev --key file://$testDataPath/baby-key.json --profile $awsProfile  
aws dynamodb delete-item --table-name UpNest-GrowthData-dev --key file://$testDataPath/growth-data-key.json --profile $awsProfile
aws dynamodb delete-item --table-name UpNest-Vaccinations-dev --key file://$testDataPath/vaccination-key.json --profile $awsProfile
aws dynamodb delete-item --table-name UpNest-Milestones-dev --key file://$testDataPath/milestone-key.json --profile $awsProfile

Write-Host "`nCRUD TESTING COMPLETED!" -ForegroundColor Green
Write-Host "All tables have been tested for basic CRUD operations and GSI queries." -ForegroundColor Green
