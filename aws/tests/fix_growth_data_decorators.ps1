# Script para corregir decoradores @patch rotos en archivos de growth-data

$testDir = "tests/unit_tests/growth-data_tests"

Write-Host "🔧 Corrigiendo decoradores @patch rotos en growth-data tests..."

# Lista de archivos a corregir
$files = @(
    "test_growth_data_delete.py",
    "test_growth_data_get.py", 
    "test_growth_data_get_single.py",
    "test_growth_data_update.py"
)

foreach ($filename in $files) {
    $filePath = Join-Path $testDir $filename
    
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw -Encoding UTF8
        $originalContent = $content
        
        # Reemplazar decoradores rotos con los correctos
        $content = $content -replace "@patch\('growth_data_delete\.\'\)", "@patch('growth_data_delete.extract_token_from_event')"
        $content = $content -replace "@patch\('growth_data_get\.\'\)", "@patch('growth_data_get.extract_token_from_event')"
        $content = $content -replace "@patch\('growth_data_get_single\.\'\)", "@patch('growth_data_get_single.extract_token_from_event')"
        $content = $content -replace "@patch\('growth_data_update\.\'\)", "@patch('growth_data_update.extract_token_from_event')"
        
        # Patrones más específicos para decoradores con múltiples mocks
        $content = $content -replace "@patch\('growth_data_([^']+)\.\'\)\s*\n\s*@patch\('growth_data_\1\.\'\)", "@patch('growth_data_`$1.get_dynamodb_client')`n    @patch('growth_data_`$1.get_jwt_validator')"
        
        # Buscar y reemplazar patrones específicos
        $content = $content -replace "@patch\('growth_data_(\w+)\.\'\)\s*\n\s*def\s+(\w+)\s*\(\s*self\s*,\s*mock_extract_token", "@patch('growth_data_`$1.extract_token_from_event')`n    def `$2(self, mock_extract_token"
        
        # Para casos de dos decoradores consecutivos (get_jwt_validator, get_dynamodb_client)
        $content = $content -replace "@patch\('growth_data_(\w+)\.\'\)\s*\n\s*@patch\('growth_data_\1\.\'\)\s*\n\s*def\s+(\w+)\s*\(\s*self\s*,\s*mock_get_jwt_validator\s*,\s*mock_get_dynamodb", "@patch('growth_data_`$1.get_dynamodb_client')`n    @patch('growth_data_`$1.get_jwt_validator')`n    def `$2(self, mock_get_jwt_validator, mock_get_dynamodb"
        
        # Solo escribir si hay cambios
        if ($content -ne $originalContent) {
            Set-Content -Path $filePath -Value $content -Encoding UTF8
            Write-Host "✅ Corregido: $filename"
        } else {
            Write-Host "⏭️  Sin cambios: $filename"
        }
    } else {
        Write-Host "❌ Archivo no encontrado: $filename"
    }
}

Write-Host "🚀 ¡Corrección de decoradores completada!"
