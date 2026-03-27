@description('Location for all resources')
param location string

@description('Base name used to derive resource names')
param baseName string

@description('GPT model deployment name')
param gptDeploymentName string

@description('GPT model name')
param gptModelName string

// Unique suffix for globally unique names
var uniqueSuffix = uniqueString(resourceGroup().id)
var aiServicesName = 'ais-${baseName}-${take(uniqueSuffix, 8)}'
var docIntelligenceName = 'di-${baseName}-${take(uniqueSuffix, 8)}'

// ── AI Services Account (Azure OpenAI + other AI services) ──
resource aiServices 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: aiServicesName
  location: location
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: aiServicesName
    publicNetworkAccess: 'Enabled'
  }
  tags: {
    project: 'aurion-hackathon'
  }
}

// ── GPT-4.1 Model Deployment ──
resource gptDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aiServices
  name: gptDeploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: gptModelName
    }
  }
}

// ── Document Intelligence ──
resource docIntelligence 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: docIntelligenceName
  location: location
  kind: 'FormRecognizer'
  sku: { name: 'S0' }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: docIntelligenceName
    publicNetworkAccess: 'Enabled'
  }
  tags: {
    project: 'aurion-hackathon'
  }
}

// ── Outputs ──
output aiServicesEndpoint string = aiServices.properties.endpoint
output documentIntelligenceEndpoint string = docIntelligence.properties.endpoint
output aiServicesName string = aiServices.name
output docIntelligenceName string = docIntelligence.name
