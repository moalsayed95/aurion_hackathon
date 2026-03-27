targetScope = 'subscription'

@description('Location for all resources')
param location string = 'swedencentral'

@description('Resource group name')
param resourceGroupName string = 'rg-aurion-1'

@description('Base name used to derive resource names')
param baseName string = 'aurion'

@description('GPT model deployment name')
param gptDeploymentName string = 'gpt-4.1'

@description('GPT model name')
param gptModelName string = 'gpt-4.1'

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: {
    project: 'aurion-hackathon'
    purpose: 'AI Claim Intake'
  }
}

// Deploy all resources into the resource group
module resources 'resources.bicep' = {
  scope: rg
  params: {
    location: location
    baseName: baseName
    gptDeploymentName: gptDeploymentName
    gptModelName: gptModelName
  }
}

output resourceGroupName string = rg.name
output aiServicesEndpoint string = resources.outputs.aiServicesEndpoint
output documentIntelligenceEndpoint string = resources.outputs.documentIntelligenceEndpoint
output aiServicesName string = resources.outputs.aiServicesName
output docIntelligenceName string = resources.outputs.docIntelligenceName
