@description('Location of the resources')
param location string = resourceGroup().location

@description('Restore the service instead of creating a new instance. This is useful if you previously soft-deleted the service and want to restore it. If you are restoring a service, set this to true. Otherwise, leave this as false.')
param restore bool = false

@description('Model deployments for OpenAI')
param deployments array = [
  {
    name: 'gpt-4o'
    capacity: 40
    version: '2024-05-13'
  }
  {
    name: 'text-embedding-ada-002'
    capacity: 120
    version: '2'
  }
]

var openAIName = '${uniqueString(resourceGroup().id)}-openai'

@description('Creates an Azure OpenAI resource.')
resource openAI 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAIName
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
    tier: 'Standard'
  }
  properties: {
    customSubDomainName: openAIName
    publicNetworkAccess: 'Enabled'
    restore: restore
  }
}

@batchSize(1)
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for deployment in deployments: {
  parent: openAI
  name: deployment.name
  sku: {
    name: 'Standard'
    capacity: deployment.capacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: deployment.name
      version: deployment.version
    }
  }
}]
