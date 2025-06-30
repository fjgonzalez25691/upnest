# Script para corregir decoradores @patch.object defectuosos en tests de growth-data

$testFiles = @(
    "unit_tests/growth-data_tests/test_growth_data_create.py"
    "unit_tests/growth-data_tests/test_growth_data_get.py"
    "unit_tests/growth-data_tests/test_growth_data_list.py"
    "unit_tests/growth-data_tests/test_growth_data_update.py"
    "unit_tests/growth-data_tests/test_growth_data_delete.py"
    "unit_tests/growth-data_tests/test_growth_data_get_single.py"
)

foreach ($testFile in $testFiles) {
    if (Test-Path $testFile) {
        Write-Host "Fixing $testFile"
        
        $content = Get-Content $testFile -Raw
        
        # Fix broken @patch decorators
        $content = $content -replace "@patch\('growth_data_create\.\)\)", "@patch('growth_data_create.get_dynamodb_client')"
        $content = $content -replace "@patch\('growth_data_create\.\)\)", "@patch('growth_data_create.get_jwt_validator')"
        
        # Fix any remaining patch.object references
        $content = $content -replace "@patch\.object\(growth_create, 'get_dynamodb_client'\)", "@patch('growth_data_create.get_dynamodb_client')"
        $content = $content -replace "@patch\.object\(growth_create, 'get_jwt_validator'\)", "@patch('growth_data_create.get_jwt_validator')"
        $content = $content -replace "@patch\.object\(growth_get, 'get_dynamodb_client'\)", "@patch('growth_data_get.get_dynamodb_client')"
        $content = $content -replace "@patch\.object\(growth_get, 'get_jwt_validator'\)", "@patch('growth_data_get.get_jwt_validator')"
        $content = $content -replace "@patch\.object\(growth_list, 'get_dynamodb_client'\)", "@patch('growth_data_list.get_dynamodb_client')"
        $content = $content -replace "@patch\.object\(growth_list, 'get_jwt_validator'\)", "@patch('growth_data_list.get_jwt_validator')"
        $content = $content -replace "@patch\.object\(growth_update, 'get_dynamodb_client'\)", "@patch('growth_data_update.get_dynamodb_client')"
        $content = $content -replace "@patch\.object\(growth_update, 'get_jwt_validator'\)", "@patch('growth_data_update.get_jwt_validator')"
        $content = $content -replace "@patch\.object\(growth_delete, 'get_dynamodb_client'\)", "@patch('growth_data_delete.get_dynamodb_client')"
        $content = $content -replace "@patch\.object\(growth_delete, 'get_jwt_validator'\)", "@patch('growth_data_delete.get_jwt_validator')"
        $content = $content -replace "@patch\.object\(growth_get_single, 'get_dynamodb_client'\)", "@patch('growth_data_get_single.get_dynamodb_client')"
        $content = $content -replace "@patch\.object\(growth_get_single, 'get_jwt_validator'\)", "@patch('growth_data_get_single.get_jwt_validator')"
        
        # Fix with patch.object in function bodies  
        $content = $content -replace "with patch\.object\(growth_create, 'get_jwt_validator'\)", "with patch('growth_data_create.get_jwt_validator')"
        $content = $content -replace "with patch\.object\(growth_get, 'get_jwt_validator'\)", "with patch('growth_data_get.get_jwt_validator')"
        $content = $content -replace "with patch\.object\(growth_list, 'get_jwt_validator'\)", "with patch('growth_data_list.get_jwt_validator')"
        $content = $content -replace "with patch\.object\(growth_update, 'get_jwt_validator'\)", "with patch('growth_data_update.get_jwt_validator')"
        $content = $content -replace "with patch\.object\(growth_delete, 'get_jwt_validator'\)", "with patch('growth_data_delete.get_jwt_validator')"
        $content = $content -replace "with patch\.object\(growth_get_single, 'get_jwt_validator'\)", "with patch('growth_data_get_single.get_jwt_validator')"
        
        Set-Content -Path $testFile -Value $content
        Write-Host "Fixed $testFile ✅"
    }
}

Write-Host "`nAll patch decorators fixed! 🚀"
