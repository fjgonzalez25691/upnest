# Integration Tests Runner
# Orchestrates the complete integration testing workflow

param(
    [string]$DynamoPort = "8000",
    [string]$ApiPort = "3001",
    [switch]$SkipSetup = $false,
    [switch]$SkipCleanup = $false
)

Write-Host "🧪 Starting UpNest Integration Tests..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"

# Step 1: Setup DynamoDB Local (unless skipped)
if (-not $SkipSetup) {
    Write-Host "`n🔧 Step 1: Setting up DynamoDB Local..." -ForegroundColor Yellow
    
    # Kill any existing DynamoDB processes
    Get-Process | Where-Object {$_.Name -like "*dynamodb*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Run setup script
    & ".\infrastructure\dynamodb\setup-local.ps1" -Port $DynamoPort
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to setup DynamoDB Local" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "`n📊 Step 2: Populating test data..." -ForegroundColor Yellow
    & ".\infrastructure\dynamodb\populate-test-data.ps1" -Port $DynamoPort
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to populate test data" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Build Lambda functions
Write-Host "`n🔨 Step 3: Building Lambda functions..." -ForegroundColor Yellow
Set-Location lambdas
sam build
Set-Location ..

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build Lambda functions" -ForegroundColor Red
    exit 1
}

# Step 4: Start SAM Local API
Write-Host "`n🚀 Step 4: Starting SAM Local API..." -ForegroundColor Yellow

# Kill any existing SAM processes
Get-Process | Where-Object {$_.Name -like "*sam*" -or $_.ProcessName -like "*sam*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Start SAM local in background
Set-Location lambdas
$samProcess = Start-Process -FilePath "sam" -ArgumentList "local", "start-api", "--port", $ApiPort, "--env-vars", "env.json" -PassThru -WindowStyle Hidden
Set-Location ..

Write-Host "⏳ Waiting for SAM Local API to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Test API connection
try {
    Invoke-WebRequest -Uri "http://localhost:$ApiPort" -Method GET -ErrorAction SilentlyContinue | Out-Null
    Write-Host "✅ SAM Local API is running on port $ApiPort" -ForegroundColor Green
} catch {
    Write-Host "⚠️  SAM Local API may still be starting..." -ForegroundColor Yellow
}

# Step 5: Run integration tests
Write-Host "`n🧪 Step 5: Running integration tests..." -ForegroundColor Yellow

# Set environment variables for testing
$env:API_BASE_URL = "http://localhost:$ApiPort"
$env:DYNAMODB_ENDPOINT = "http://localhost:$DynamoPort"

# Run Python integration tests
Set-Location tests\integration
python -m pytest test_endpoints.py -v --tb=short
$testResult = $LASTEXITCODE
Set-Location ..\..

# Step 6: Cleanup (unless skipped)
if (-not $SkipCleanup) {
    Write-Host "`n🧹 Step 6: Cleanup..." -ForegroundColor Yellow
    
    # Stop SAM process
    if ($samProcess -and -not $samProcess.HasExited) {
        Stop-Process -Id $samProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "🛑 Stopped SAM Local API" -ForegroundColor Blue
    }
    
    # Stop DynamoDB processes
    Get-Process | Where-Object {$_.Name -like "*dynamodb*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "🛑 Stopped DynamoDB Local" -ForegroundColor Blue
}

# Final result
Write-Host "`n=================================" -ForegroundColor Green
if ($testResult -eq 0) {
    Write-Host "✅ Integration tests PASSED!" -ForegroundColor Green
    Write-Host "🎯 All endpoints working correctly" -ForegroundColor Blue
} else {
    Write-Host "❌ Integration tests FAILED!" -ForegroundColor Red
    Write-Host "🔍 Check test output above for details" -ForegroundColor Yellow
}

Write-Host "`n🏁 Integration testing complete." -ForegroundColor Green

# Keep processes running if cleanup was skipped
if ($SkipCleanup) {
    Write-Host "`n🔄 Services still running:" -ForegroundColor Blue
    Write-Host "   - DynamoDB Local: http://localhost:$DynamoPort" -ForegroundColor Cyan
    Write-Host "   - SAM Local API: http://localhost:$ApiPort" -ForegroundColor Cyan
    Write-Host "   Use -SkipSetup flag to rerun tests without restarting services" -ForegroundColor Yellow
}

exit $testResult
