# Simple Integration Test Runner
Write-Host "🧪 Starting Simple Integration Tests..." -ForegroundColor Green

# Test 1: Check if we can build SAM
Write-Host "Testing SAM build..." -ForegroundColor Yellow
Set-Location lambdas
sam build
$buildResult = $LASTEXITCODE
Set-Location ..

if ($buildResult -eq 0) {
    Write-Host "✅ SAM build successful" -ForegroundColor Green
} else {
    Write-Host "❌ SAM build failed" -ForegroundColor Red
}

Write-Host "🏁 Simple test complete. Build result: $buildResult" -ForegroundColor Blue
