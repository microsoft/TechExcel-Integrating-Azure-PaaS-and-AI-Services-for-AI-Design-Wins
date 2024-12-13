param location string = resourceGroup().location
param deployments array
param tags object = {}
param restore bool = false
param openAIName string
param speechServiceName string
param languageServiceName string
param searchServiceName string
param managedIdentityName string

@description('Creates an Azure AI Search service.')
module searchService '../core/search/search-services.bicep' = {
  name: searchServiceName
  params: {
    location: location
    name: searchServiceName
    sku: {
      name: 'standard'
    }
    managedIdentityName: managedIdentityName
  }
}

@description('Creates an Azure OpenAI resource.')
module openAI '../core/ai/cognitiveservices.bicep' = {
  name: openAIName
  params: {
    location: location
    name: openAIName
    deployments: deployments
    tags: tags
  }
}

@description('Creates an Azure AI Services Speech service.')
resource speechService 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: speechServiceName
  location: location
  kind: 'SpeechServices'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: speechServiceName
    publicNetworkAccess: 'Enabled'
    restore: restore
  }
}

@description('Creates an Azure AI Services Language service.')
resource languageService 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: languageServiceName
  location: location
  kind: 'TextAnalytics'
  sku: {
    name: 'S'
  }
  properties: {
    customSubDomainName: languageServiceName
    publicNetworkAccess: 'Enabled'
    restore: restore
  }
}

output searchServiceName string = searchService.outputs.name
output openAIName string = openAI.outputs.name
output openAIEndpoint string = openAI.outputs.endpoint
output speechServiceName string = speechService.name
output languageServiceName string = languageService.name
