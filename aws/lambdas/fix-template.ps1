# Script para arreglar template.yaml - Reemplazar !ImportValue con valores directos

$templatePath = "template.yaml"

# Leer el contenido del archivo
$content = Get-Content $templatePath -Raw

# Reemplazar todas las referencias !ImportValue
$content = $content -replace "!ImportValue UpNest-DynamoDB-dev-BabiesTableName", "UpNest-Babies-dev"
$content = $content -replace "!ImportValue UpNest-DynamoDB-dev-GrowthDataTableName", "UpNest-GrowthData-dev"
$content = $content -replace "!ImportValue UpNest-DynamoDB-dev-UsersTableName", "UpNest-Users-dev"
$content = $content -replace "!ImportValue UpNest-DynamoDB-dev-VaccinationsTableName", "UpNest-Vaccinations-dev"
$content = $content -replace "!ImportValue UpNest-DynamoDB-dev-MilestonesTableName", "UpNest-Milestones-dev"

# Escribir el contenido modificado
$content | Set-Content $templatePath -Encoding UTF8

Write-Host "✅ Template.yaml arreglado - Todas las referencias !ImportValue reemplazadas" -ForegroundColor Green
