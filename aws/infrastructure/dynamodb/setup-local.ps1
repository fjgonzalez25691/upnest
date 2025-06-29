# DynamoDB Local Setup Script
# Starts DynamoDB Local and creates all required tables with test data

param(
    [string]$Port = "8000",
    [string]$DataDir = "./dynamodb-local-data"
)

Write-Host "Setting up DynamoDB Local for UpNest development..." -ForegroundColor Green

# Check if DynamoDB Local is available
$dynamoPath = Get-Command "dynamodb-local" -ErrorAction SilentlyContinue
if (-not $dynamoPath) {
    Write-Host "DynamoDB Local not found. Installing via npm..." -ForegroundColor Yellow
    npm install -g dynamodb-local
}

# Create data directory if it doesn't exist
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force
    Write-Host "Created data directory: $DataDir" -ForegroundColor Blue
}

# Start DynamoDB Local in background
Write-Host "🔧 Starting DynamoDB Local on port $Port..." -ForegroundColor Blue
Start-Process -FilePath "dynamodb-local" -ArgumentList "--port", $Port, "--dbPath", $DataDir, "--sharedDb" -WindowStyle Hidden

# Wait for DynamoDB to start
Write-Host "⏳ Waiting for DynamoDB Local to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Test connection
try {
    Invoke-WebRequest -Uri "http://localhost:$Port" -Method GET -ErrorAction Stop | Out-Null
    Write-Host "✅ DynamoDB Local is running on port $Port" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to connect to DynamoDB Local" -ForegroundColor Red
    exit 1
}

# Create tables
Write-Host "📊 Creating DynamoDB tables..." -ForegroundColor Blue

# Set environment variables for AWS CLI
$env:AWS_ACCESS_KEY_ID = "fake"
$env:AWS_SECRET_ACCESS_KEY = "fake"
$env:AWS_DEFAULT_REGION = "us-east-1"

# Create Users table
Write-Host "Creating Users table..." -ForegroundColor Cyan
aws dynamodb create-table `
    --table-name upnest-users-local `
    --attribute-definitions `
        AttributeName=userId,AttributeType=S `
        AttributeName=email,AttributeType=S `
    --key-schema `
        AttributeName=userId,KeyType=HASH `
    --global-secondary-indexes `
        IndexName=EmailIndex,KeySchema=['{AttributeName=email,KeyType=HASH}'],Projection='{ProjectionType=ALL}' `
    --billing-mode PAY_PER_REQUEST `
    --endpoint-url http://localhost:$Port

# Create Babies table
Write-Host "Creating Babies table..." -ForegroundColor Cyan
aws dynamodb create-table `
    --table-name upnest-babies-local `
    --attribute-definitions `
        AttributeName=babyId,AttributeType=S `
        AttributeName=userId,AttributeType=S `
    --key-schema `
        AttributeName=babyId,KeyType=HASH `
    --global-secondary-indexes `
        IndexName=UserBabiesIndex,KeySchema=['{AttributeName=userId,KeyType=HASH}'],Projection='{ProjectionType=ALL}' `
    --billing-mode PAY_PER_REQUEST `
    --endpoint-url http://localhost:$Port

# Create GrowthData table
Write-Host "Creating GrowthData table..." -ForegroundColor Cyan
aws dynamodb create-table `
    --table-name upnest-growth-data-local `
    --attribute-definitions `
        AttributeName=dataId,AttributeType=S `
        AttributeName=babyId,AttributeType=S `
        AttributeName=measurementDate,AttributeType=S `
    --key-schema `
        AttributeName=dataId,KeyType=HASH `
    --global-secondary-indexes `
        IndexName=BabyGrowthIndex,KeySchema=['{AttributeName=babyId,KeyType=HASH}','{AttributeName=measurementDate,KeyType=RANGE}'],Projection='{ProjectionType=ALL}' `
    --billing-mode PAY_PER_REQUEST `
    --endpoint-url http://localhost:$Port

# Create Vaccinations table
Write-Host "Creating Vaccinations table..." -ForegroundColor Cyan
aws dynamodb create-table `
    --table-name upnest-vaccinations-local `
    --attribute-definitions `
        AttributeName=vaccinationId,AttributeType=S `
        AttributeName=babyId,AttributeType=S `
    --key-schema `
        AttributeName=vaccinationId,KeyType=HASH `
    --global-secondary-indexes `
        IndexName=BabyVaccinationsIndex,KeySchema=['{AttributeName=babyId,KeyType=HASH}'],Projection='{ProjectionType=ALL}' `
    --billing-mode PAY_PER_REQUEST `
    --endpoint-url http://localhost:$Port

# Create Milestones table
Write-Host "Creating Milestones table..." -ForegroundColor Cyan
aws dynamodb create-table `
    --table-name upnest-milestones-local `
    --attribute-definitions `
        AttributeName=milestoneId,AttributeType=S `
        AttributeName=babyId,AttributeType=S `
    --key-schema `
        AttributeName=milestoneId,KeyType=HASH `
    --global-secondary-indexes `
        IndexName=BabyMilestonesIndex,KeySchema=['{AttributeName=babyId,KeyType=HASH}'],Projection='{ProjectionType=ALL}' `
    --billing-mode PAY_PER_REQUEST `
    --endpoint-url http://localhost:$Port

Write-Host "⏳ Waiting for tables to be created..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "✅ DynamoDB Local setup complete!" -ForegroundColor Green
Write-Host "📊 Tables created and ready for testing" -ForegroundColor Green
Write-Host "🌐 Endpoint: http://localhost:$Port" -ForegroundColor Blue
