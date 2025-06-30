# Script para corregir TODOS los imports de 'calculate' a 'percentiles_calculate' en tests de percentiles

$testDir = "unit_tests/percentiles_tests"

# Patrones para reemplazar
$replacements = @{
    # Imports dentro de funciones con 'with patch'
    "with patch\('calculate\." = "with patch('percentiles_calculate."
    
    # Decoradores @patch
    "@patch\('calculate\." = "@patch('percentiles_calculate."
    "@mock\.patch\('calculate\." = "@mock.patch('percentiles_calculate."
    
    # Imports directos que intentan importar funciones específicas del módulo 
    "from percentiles_calculate import percentiles_calculate as calculate_" = "from percentiles_calculate import "
    
    # Import statements
    "from calculate import" = "from percentiles_calculate import"
    "import calculate as" = "import percentiles_calculate as"
    "import calculate" = "import percentiles_calculate"
    
    # Cualquier referencia a 'calculate.' debe ser 'percentiles_calculate.'
    "\bcalculate\." = "percentiles_calculate."
}

Write-Host "🔧 Iniciando corrección masiva de imports en tests de percentiles..."

Get-ChildItem -Path $testDir -Filter *.py | ForEach-Object {
    $file = $_.FullName
    $content = Get-Content $file -Raw -Encoding UTF8
    $originalContent = $content
    
    # Aplicar todos los reemplazos usando regex
    foreach ($pattern in $replacements.Keys) {
        $replacement = $replacements[$pattern]
        $content = $content -replace $pattern, $replacement
    }
    
    # Solo escribir si hay cambios
    if ($content -ne $originalContent) {
        Set-Content -Path $file -Value $content -Encoding UTF8
        Write-Host "✅ Actualizado: $($_.Name)"
    } else {
        Write-Host "⏭️  Sin cambios: $($_.Name)"
    }
}

Write-Host "🚀 ¡Corrección de imports completada!"
Write-Host "📝 Ejecuta: python -m pytest tests/unit_tests/percentiles_tests/ -v"
