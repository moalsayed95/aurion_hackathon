<#
.SYNOPSIS
  Deploy the Aurion Hackathon infrastructure to Azure.

.DESCRIPTION
  Creates the resource group and all Azure resources:
  - Storage Account + Key Vault (AI Hub dependencies)
  - AI Services account with GPT-4.1 deployment
  - Document Intelligence (S0)
  - AI Foundry Hub + Project (hackathon-main)

.EXAMPLE
  .\deploy.ps1
  .\deploy.ps1 -WhatIf
#>
param(
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
$InfraDir = $PSScriptRoot

Write-Host "`n=== Aurion Hackathon - Infrastructure Deployment ===" -ForegroundColor Cyan

# Verify Azure CLI login
Write-Host "`nChecking Azure CLI login..." -ForegroundColor Yellow
$account = az account show --output json 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Not logged in. Run 'az login' first." -ForegroundColor Red
    exit 1
}
Write-Host "Subscription: $($account.name) ($($account.id))" -ForegroundColor Green

# Deploy
Write-Host "`nDeploying infrastructure..." -ForegroundColor Yellow

$deployArgs = @(
    'deployment', 'sub', 'create',
    '--location', 'swedencentral',
    '--template-file', "$InfraDir\main.bicep",
    '--parameters', "$InfraDir\main.bicepparam",
    '--name', "aurion-hackathon-$(Get-Date -Format 'yyyyMMdd-HHmmss')",
    '--output', 'json'
)

if ($WhatIf) {
    Write-Host "Running what-if analysis..." -ForegroundColor Yellow
    $deployArgs += '--what-if'
}

$result = az @deployArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nDeployment failed:" -ForegroundColor Red
    Write-Host $result
    exit 1
}

$deployment = $result | ConvertFrom-Json

if (-not $WhatIf) {
    Write-Host "`n=== Deployment Outputs ===" -ForegroundColor Green
    $outputs = $deployment.properties.outputs
    Write-Host "AI Services Endpoint:       $($outputs.aiServicesEndpoint.value)"
    Write-Host "Document Intelligence:      $($outputs.documentIntelligenceEndpoint.value)"
    Write-Host "AI Services Name:           $($outputs.aiServicesName.value)"
    Write-Host "Doc Intelligence Name:      $($outputs.docIntelligenceName.value)"
    Write-Host "Hub Name:                   $($outputs.hubName.value)"
    Write-Host "Project Name:               $($outputs.projectName.value)"

    Write-Host "`n=== .env Configuration ===" -ForegroundColor Yellow
    Write-Host "Add these to your .env file:"
    Write-Host "AZURE_AI_PROJECT_ENDPOINT=$($outputs.aiServicesEndpoint.value)"
    Write-Host "AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME=gpt-4-1"
    Write-Host "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=$($outputs.documentIntelligenceEndpoint.value)"
}

Write-Host "`nDone." -ForegroundColor Green
