# Populate Test Data Script
# Loads test data into local DynamoDB tables

param(
    [string]$Port = "8000",
    [string]$TestDataPath = "infrastructure/test-data"
)

Write-Host "Populating DynamoDB Local with test data..." -ForegroundColor Green

# Set environment variables for AWS CLI
$env:AWS_ACCESS_KEY_ID = "fake"
$env:AWS_SECRET_ACCESS_KEY = "fake"
$env:AWS_DEFAULT_REGION = "us-east-1"
$endpoint = "http://localhost:$Port"

# Check if test data directory exists
if (-not (Test-Path $TestDataPath)) {
    Write-Host "❌ Test data directory not found: $TestDataPath" -ForegroundColor Red
    exit 1
}

Write-Host "Using test data from: $TestDataPath" -ForegroundColor Blue

# Function to import data from JSON file
function Import-TestData {
    param(
        [string]$TableName,
        [string]$JsonFile,
        [string]$Description
    )
    
    $filePath = Join-Path $TestDataPath $JsonFile
    if (Test-Path $filePath) {
        Write-Host "Loading $Description..." -ForegroundColor Cyan
        $absolutePath = Resolve-Path $filePath
        aws dynamodb put-item `
            --table-name $TableName `
            --item file://$absolutePath `
            --endpoint-url $endpoint
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Description loaded successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to load $Description" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️  File not found: $JsonFile" -ForegroundColor Yellow
    }
}

# Function to import array data from JSON file
function Import-ArrayTestData {
    param(
        [string]$TableName,
        [string]$JsonFile,
        [string]$Description
    )
    
    $filePath = Join-Path $TestDataPath $JsonFile
    if (Test-Path $filePath) {
        Write-Host "Loading $Description..." -ForegroundColor Cyan
        
        # Read and parse JSON array
        $jsonContent = Get-Content $filePath -Raw | ConvertFrom-Json
        
        foreach ($item in $jsonContent) {
            $tempFile = [System.IO.Path]::GetTempFileName()
            $item | ConvertTo-Json -Depth 10 | Set-Content $tempFile
            
            aws dynamodb put-item `
                --table-name $TableName `
                --item file://$tempFile `
                --endpoint-url $endpoint
            
            Remove-Item $tempFile
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Description loaded successfully ($($jsonContent.Count) items)" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to load $Description" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️  File not found: $JsonFile" -ForegroundColor Yellow
    }
}

# Load Users data
Write-Host "`nLoading Users..." -ForegroundColor Magenta
Import-ArrayTestData "upnest-users-local" "users-test-data.json" "Test Users"
Import-TestData "upnest-users-local" "user-test.json" "Individual User 1"
Import-TestData "upnest-users-local" "user2-test.json" "Individual User 2"

# Load Babies data
Write-Host "`nLoading Babies..." -ForegroundColor Magenta
Import-ArrayTestData "upnest-babies-local" "baby1-user1.json" "Baby for User 1"
Import-ArrayTestData "upnest-babies-local" "baby1-user2.json" "Baby for User 2"
Import-TestData "upnest-babies-local" "baby-test.json" "Test Baby"
Import-TestData "upnest-babies-local" "baby-user1.json" "Additional Baby User 1"

# Load Growth Data
Write-Host "`nLoading Growth Data..." -ForegroundColor Magenta
Import-TestData "upnest-growth-data-local" "growth-data-test.json" "Test Growth Data"

# Load Milestones
Write-Host "`nLoading Milestones..." -ForegroundColor Magenta
Import-TestData "upnest-milestones-local" "milestone-test.json" "Test Milestone"

# Load Vaccinations
Write-Host "`nLoading Vaccinations..." -ForegroundColor Magenta
Import-TestData "upnest-vaccinations-local" "vaccination-test.json" "Test Vaccination"

Write-Host "`n✅ Test data population complete!" -ForegroundColor Green
Write-Host "🎯 Ready for integration testing" -ForegroundColor Blue
