# UpNest DynamoDB CRUD Testing Script
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
$userResult = aws dynamodb get-item --table-name UpNest-Users-dev --key file://$testDataPath/user-key.json --profile $awsProfile | ConvertFrom-Json
if ($userResult.Item) {
    Write-Host "  ✅ User found: $($userResult.Item.name.S)" -ForegroundColor Green
} else {
    Write-Host "  ❌ User not found" -ForegroundColor Red
}

# Test Babies Table
Write-Host "`n👶 TESTING BABIES TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE (put-item)..."
aws dynamodb put-item --table-name UpNest-Babies-dev --item file://$testDataPath/baby-test.json --profile $awsProfile

Write-Host "- Testing READ (get-item)..."
$babyResult = aws dynamodb get-item --table-name UpNest-Babies-dev --key file://$testDataPath/baby-key.json --profile $awsProfile | ConvertFrom-Json
if ($babyResult.Item) {
    Write-Host "  ✅ Baby found: $($babyResult.Item.name.S)" -ForegroundColor Green
} else {
    Write-Host "  ❌ Baby not found" -ForegroundColor Red
}

# Test GrowthData Table
Write-Host "`n📊 TESTING GROWTH DATA TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE (put-item)..."
aws dynamodb put-item --table-name UpNest-GrowthData-dev --item file://$testDataPath/growth-data-test.json --profile $awsProfile

Write-Host "- Testing READ (get-item)..."
$growthResult = aws dynamodb get-item --table-name UpNest-GrowthData-dev --key file://$testDataPath/growth-data-key.json --profile $awsProfile | ConvertFrom-Json
if ($growthResult.Item) {
    Write-Host "  ✅ Growth data found: $($growthResult.Item.measurementType.S) = $($growthResult.Item.value.N) $($growthResult.Item.unit.S)" -ForegroundColor Green
} else {
    Write-Host "  ❌ Growth data not found" -ForegroundColor Red
}

# Test Vaccinations Table
Write-Host "`n💉 TESTING VACCINATIONS TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE (put-item)..."
aws dynamodb put-item --table-name UpNest-Vaccinations-dev --item file://$testDataPath/vaccination-test.json --profile $awsProfile

Write-Host "- Testing READ (get-item)..."
$vaccinationResult = aws dynamodb get-item --table-name UpNest-Vaccinations-dev --key file://$testDataPath/vaccination-key.json --profile $awsProfile | ConvertFrom-Json
if ($vaccinationResult.Item) {
    Write-Host "  ✅ Vaccination found: $($vaccinationResult.Item.vaccineName.S)" -ForegroundColor Green
} else {
    Write-Host "  ❌ Vaccination not found" -ForegroundColor Red
}

# Test Milestones Table
Write-Host "`n🎯 TESTING MILESTONES TABLE" -ForegroundColor Yellow
Write-Host "- Testing CREATE (put-item)..."
aws dynamodb put-item --table-name UpNest-Milestones-dev --item file://$testDataPath/milestone-test.json --profile $awsProfile

Write-Host "- Testing READ (get-item)..."
$milestoneResult = aws dynamodb get-item --table-name UpNest-Milestones-dev --key file://$testDataPath/milestone-key.json --profile $awsProfile | ConvertFrom-Json
if ($milestoneResult.Item) {
    Write-Host "  ✅ Milestone found: $($milestoneResult.Item.milestone.S)" -ForegroundColor Green
} else {
    Write-Host "  ❌ Milestone not found" -ForegroundColor Red
}

# Test UPDATE operations
Write-Host "`n🔄 TESTING UPDATE OPERATIONS" -ForegroundColor Yellow

# Update user name
Write-Host "- Testing UPDATE user name..."
aws dynamodb update-item --table-name UpNest-Users-dev --key file://$testDataPath/user-key.json --update-expression "SET #name = :newName, updatedAt = :updatedAt" --expression-attribute-names '{\"#name\":\"name\"}' --expression-attribute-values '{\\":newName\":{\"S\":\"Updated Test User\"},\\":updatedAt\":{\"S\":\"2025-06-28T13:00:00Z\"}}' --profile $awsProfile

$updatedUserResult = aws dynamodb get-item --table-name UpNest-Users-dev --key file://$testDataPath/user-key.json --profile $awsProfile | ConvertFrom-Json
if ($updatedUserResult.Item.name.S -eq "Updated Test User") {
    Write-Host "  ✅ User updated successfully" -ForegroundColor Green
} else {
    Write-Host "  ❌ User update failed" -ForegroundColor Red
}

# Test GSI Queries
Write-Host "`n🔍 TESTING GSI QUERIES" -ForegroundColor Yellow

# Test Users EmailIndex
Write-Host "- Testing Users EmailIndex query..."
$emailQueryResult = aws dynamodb query --table-name UpNest-Users-dev --index-name EmailIndex --key-condition-expression "email = :email" --expression-attribute-values '{\\":email\":{\"S\":\"test@example.com\"}}' --profile $awsProfile | ConvertFrom-Json
if ($emailQueryResult.Items -and $emailQueryResult.Items.Count -gt 0) {
    Write-Host "  ✅ EmailIndex query successful" -ForegroundColor Green
} else {
    Write-Host "  ❌ EmailIndex query failed" -ForegroundColor Red
}

# Test Babies UserBabiesIndex
Write-Host "- Testing Babies UserBabiesIndex query..."
$userBabiesResult = aws dynamodb query --table-name UpNest-Babies-dev --index-name UserBabiesIndex --key-condition-expression "userId = :userId" --expression-attribute-values '{\\":userId\":{\"S\":\"test-user-001\"}}' --profile $awsProfile | ConvertFrom-Json
if ($userBabiesResult.Items -and $userBabiesResult.Items.Count -gt 0) {
    Write-Host "  ✅ UserBabiesIndex query successful" -ForegroundColor Green
} else {
    Write-Host "  ❌ UserBabiesIndex query failed" -ForegroundColor Red
}

Write-Host "`n🧹 CLEANING UP TEST DATA" -ForegroundColor Yellow
Write-Host "- Deleting test records..."

# Delete test records
aws dynamodb delete-item --table-name UpNest-Users-dev --key file://$testDataPath/user-key.json --profile $awsProfile
aws dynamodb delete-item --table-name UpNest-Babies-dev --key file://$testDataPath/baby-key.json --profile $awsProfile
aws dynamodb delete-item --table-name UpNest-GrowthData-dev --key file://$testDataPath/growth-data-key.json --profile $awsProfile
aws dynamodb delete-item --table-name UpNest-Vaccinations-dev --key file://$testDataPath/vaccination-key.json --profile $awsProfile
aws dynamodb delete-item --table-name UpNest-Milestones-dev --key file://$testDataPath/milestone-key.json --profile $awsProfile

Write-Host "`n✅ CRUD TESTING COMPLETED!" -ForegroundColor Green
Write-Host "All tables have been tested for basic CRUD operations and GSI queries." -ForegroundColor Green
