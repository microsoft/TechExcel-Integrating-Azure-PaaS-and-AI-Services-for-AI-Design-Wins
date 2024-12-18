param location string = resourceGroup().location
param appInsightsName string
param storageAccountName string
param tags object = {}
param functionAppServicePlanName string
param functionAppName string
param managedIdentityName string
param openAiProps object
param cosmosDbEndpoint string

var vectorizerServiceName = 'contoso-vectorizer'

resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: managedIdentityName
}

resource functionAppServicePlan 'Microsoft.Web/serverFarms@2022-09-01' = {
  name: functionAppServicePlanName
  location: location
  tags: tags
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {}
}

resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp'
  tags: union(tags, { 'azd-service-name': vectorizerServiceName })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${resourceGroup().id}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/${managedIdentity.name}': {}
    }
  }
  properties: {
    serverFarmId: functionAppServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'AZURE_CLIENT_ID'
          value: managedIdentity.properties.clientId
        }
        {
          name: 'AZURE_TENANT_ID'
          value: subscription().tenantId
        }
        {
          name: 'AzureWebJobsStorage__accountname'
          value: storageAccountName
        }
        {
          name: 'AzureOpenAIEndpoint'
          value: openAiProps.endpoint
        }        
        {
          name: 'CosmosDBConnection__accountEndpoint'
          value: cosmosDbEndpoint
        }
        {
          name: 'CosmosDBConnection__clientId'
          value: managedIdentity.properties.clientId
        }
        {
          name: 'CosmosDBConnection__credential'
          value: 'managedidentity'
        }
        {
          name: 'EmbeddingDeploymentName'
          value: openAiProps.embeddingDeploymentName
        }
        {
          name: 'WEBSITE_USE_PLACEHOLDER_DOTNETISOLATED'
          value: '1'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'dotnet-isolated'
        }
      ]
      ftpsState: 'FtpsOnly'
      minTlsVersion: '1.2'
      netFrameworkVersion: 'v8.0'
    }
    httpsOnly: true
    virtualNetworkSubnetId: null
    publicNetworkAccess: 'Enabled'
    clientAffinityEnabled: false
  }
}

output functionAppName string = functionApp.name
