# Map of old import names to new import names, incluyendo alias
$importReplacements = @{
    'import create as growth_create'         = 'import growth_data_create as growth_create'
    'from create import'                     = 'from growth_data_create import'
    'import create'                          = 'import growth_data_create'
    'from get import'                        = 'from growth_data_get import'
    'import get'                             = 'import growth_data_get'
    'from get_single import'                 = 'from growth_data_get_single import'
    'import get_single'                      = 'import growth_data_get_single'
    'from delete import'                     = 'from growth_data_delete import'
    'import delete'                          = 'import growth_data_delete'
    'from update import'                     = 'from growth_data_update import'
    'import update'                          = 'import growth_data_update'
    'from list import'                       = 'from growth_data_list import'
    'import list'                            = 'import growth_data_list'
}

# Map of old patch targets to new patch targets (para decoradores)
$patchReplacements = @{
    '@patch.object(create'          = '@patch.object(growth_data_create'
    '@patch.object(get'             = '@patch.object(growth_data_get'
    '@patch.object(get_single'      = '@patch.object(growth_data_get_single'
    '@patch.object(delete'          = '@patch.object(growth_data_delete'
    '@patch.object(update'          = '@patch.object(growth_data_update'
    '@patch.object(list'            = '@patch.object(growth_data_list'
    '@mock.patch.object(create'     = '@mock.patch.object(growth_data_create'
    '@mock.patch.object(get'        = '@mock.patch.object(growth_data_get'
    '@mock.patch.object(get_single' = '@mock.patch.object(growth_data_get_single'
    '@mock.patch.object(delete'     = '@mock.patch.object(growth_data_delete'
    '@mock.patch.object(update'     = '@mock.patch.object(growth_data_update'
    '@mock.patch.object(list'       = '@mock.patch.object(growth_data_list'
    'with patch.object(create,'     = 'with patch.object(growth_create,'
    'with patch.object(get,'        = 'with patch.object(growth_get,'
    'with patch.object(update,'     = 'with patch.object(growth_update,'
    'with patch.object(delete,'     = 'with patch.object(growth_delete,'
}

# Extra: Arreglar targets sin comillas y con espacios
$targetReplacements = @{
    'growth data create'      = 'growth_data_create'
    'growth data get'         = 'growth_data_get'
    'growth data get_single'  = 'growth_data_get_single'
    'growth data delete'      = 'growth_data_delete'
    'growth data update'      = 'growth_data_update'
    'growth data list'        = 'growth_data_list'
}

foreach ($pattern in $targetReplacements.Keys) {
    $replacement = $targetReplacements[$pattern]
    $escapedPattern = [regex]::Escape($pattern)
    $content = $content -replace $escapedPattern, $replacement
}

$testDir = "unit_tests/growth-data_tests"

Get-ChildItem -Path $testDir -Filter *.py | ForEach-Object {
    $file = $_.FullName
    $content = Get-Content $file -Raw

    # Update imports (puede ir directo porque no usan paréntesis ni regex especial)
    foreach ($pattern in $importReplacements.Keys) {
        $replacement = $importReplacements[$pattern]
        $content = $content -replace $pattern, $replacement
    }
    # Update patch decorators (escapa los paréntesis y puntos)
    foreach ($pattern in $patchReplacements.Keys) {
        $replacement = $patchReplacements[$pattern]
        $escapedPattern = [regex]::Escape($pattern)
        $content = $content -replace $escapedPattern, $replacement
    }

    Set-Content -Path $file -Value $content
    Write-Host "Updated $file"
}

Write-Host "Import, patch and alias references updated! 🚀"
