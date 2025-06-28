# UpNest DynamoDB Tables Deployment Script (PowerShell)
# This script deploys all DynamoDB tables for the UpNest application

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-east-1",
    
    [Parameter(Mandatory=$false)]
    [string]$StackName = "",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("PAY_PER_REQUEST", "PROVISIONED")]
    [string]$BillingMode = "PAY_PER_REQUEST",
    
    [Parameter(Mandatory=$false)]
    [switch]$Help
)

# Show help
if ($Help) {
    Write-Host "Usage: .\deploy-dynamodb.ps1 [OPTIONS]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Deploy UpNest DynamoDB tables using CloudFormation" -ForegroundColor White
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor Yellow
    Write-Host "  -Environment ENV      Environment (dev, staging, prod) [default: dev]" -ForegroundColor Gray
    Write-Host "  -Region REGION        AWS region [default: us-east-1]" -ForegroundColor Gray
    Write-Host "  -StackName NAME       CloudFormation stack name [default: upnest-dynamodb-ENV]" -ForegroundColor Gray
    Write-Host "  -BillingMode MODE     Billing mode (PAY_PER_REQUEST, PROVISIONED) [default: PAY_PER_REQUEST]" -ForegroundColor Gray
    Write-Host "  -Help                 Show this help message" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\deploy-dynamodb.ps1 -Environment dev -Region us-east-1" -ForegroundColor Gray
    Write-Host "  .\deploy-dynamodb.ps1 -Environment prod -Region us-west-2" -ForegroundColor Gray
    Write-Host "  .\deploy-dynamodb.ps1 -Environment staging -StackName my-custom-stack-name" -ForegroundColor Gray
    exit 0
}

# Set default stack name if not provided
if ([string]::IsNullOrEmpty($StackName)) {
    $StackName = "upnest-dynamodb-$Environment"
}

# Check if AWS CLI is installed
try {
    $null = Get-Command aws -ErrorAction Stop
} catch {
    Write-Host "❌ Error: AWS CLI is not installed" -ForegroundColor Red
    exit 1
}

# Check if CloudFormation template exists
$TemplateFile = "aws\infrastructure\dynamodb-tables.yaml"
if (-not (Test-Path $TemplateFile)) {
    Write-Host "❌ Error: CloudFormation template not found: $TemplateFile" -ForegroundColor Red
    exit 1
}

# Print deployment info
Write-Host "🚀 UpNest DynamoDB Deployment" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host "Environment: " -NoNewline -ForegroundColor White
Write-Host $Environment -ForegroundColor Yellow
Write-Host "Region: " -NoNewline -ForegroundColor White
Write-Host $Region -ForegroundColor Yellow
Write-Host "Stack Name: " -NoNewline -ForegroundColor White
Write-Host $StackName -ForegroundColor Yellow
Write-Host "Billing Mode: " -NoNewline -ForegroundColor White
Write-Host $BillingMode -ForegroundColor Yellow
Write-Host "Template: " -NoNewline -ForegroundColor White
Write-Host $TemplateFile -ForegroundColor Yellow
Write-Host ""

# Check if stack already exists
Write-Host "Checking if stack exists..." -ForegroundColor Blue
try {
    $null = aws cloudformation describe-stacks --stack-name $StackName --region $Region 2>$null
    Write-Host "Stack exists. This will be an update operation." -ForegroundColor Yellow
    $Operation = "update"
} catch {
    Write-Host "Stack does not exist. This will be a create operation." -ForegroundColor Green
    $Operation = "create"
}

# Validate CloudFormation template
Write-Host "Validating CloudFormation template..." -ForegroundColor Blue
try {
    $null = aws cloudformation validate-template --template-body file://$TemplateFile --region $Region 2>$null
    Write-Host "✅ Template is valid" -ForegroundColor Green
} catch {
    Write-Host "❌ Template validation failed" -ForegroundColor Red
    exit 1
}

# Deploy the stack
Write-Host "Deploying CloudFormation stack..." -ForegroundColor Blue
try {
    aws cloudformation deploy `
        --template-file $TemplateFile `
        --stack-name $StackName `
        --region $Region `
        --parameter-overrides Environment=$Environment BillingMode=$BillingMode `
        --capabilities CAPABILITY_IAM `
        --no-fail-on-empty-changeset
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Deployment successful!" -ForegroundColor Green
        
        # Get stack outputs
        Write-Host "Stack Outputs:" -ForegroundColor Blue
        aws cloudformation describe-stacks `
            --stack-name $StackName `
            --region $Region `
            --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' `
            --output table
            
        Write-Host ""
        Write-Host "🎉 All DynamoDB tables have been deployed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Blue
        Write-Host "1. Update your Lambda functions to use these table names" -ForegroundColor Gray
        Write-Host "2. Update your frontend API endpoints" -ForegroundColor Gray
        Write-Host "3. Test the database connections" -ForegroundColor Gray
        Write-Host "4. Run integration tests" -ForegroundColor Gray
        
    } else {
        Write-Host "❌ Deployment failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
    exit 1
}

# Show table status
Write-Host "Checking table status..." -ForegroundColor Blue
$Tables = @(
    "UpNest-Users-$Environment",
    "UpNest-Babies-$Environment", 
    "UpNest-GrowthData-$Environment",
    "UpNest-Vaccinations-$Environment",
    "UpNest-Milestones-$Environment"
)

foreach ($table in $Tables) {
    try {
        $status = aws dynamodb describe-table --table-name $table --region $Region --query 'Table.TableStatus' --output text 2>$null
        if ($status -eq "ACTIVE") {
            Write-Host "  ✅ $table`: $status" -ForegroundColor Green
        } else {
            Write-Host "  ⏳ $table`: $status" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ $table`: NOT_FOUND" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🚀 UpNest DynamoDB deployment completed!" -ForegroundColor Green
