param location string = resourceGroup().location
param appInsightsName string
param tags object = {}
param registryName string
param appServicePlanName string
param webAppNameApi string
param webAppNameDash string
param managedIdentityName string
param openAiProps object
param cosmosDbEndpoint string

var registrySku = 'Standard'
var webAppSku = 'S1'

// Name of the service defined in azure.yaml
// A tag named azd-service-name with this value should be applied to the service host resource, such as:
//   Microsoft.Web/sites for appservice, function
// Example usage:
//   tags: union(tags, { 'azd-service-name': apiServiceName })
var apiServiceName = 'contoso-api'
var dashServiceName = 'contoso-dash'

resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: managedIdentityName
}

@description('Creates an Azure Container Registry.')
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2022-12-01' = {
  name: registryName
  location: location
  tags: tags
  sku: {
    name: registrySku
  }
  properties: {
    adminUserEnabled: true
  }
}

@description('Creates an Azure App Service Plan.')
resource appServicePlan 'Microsoft.Web/serverFarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  tags: tags
  kind: 'linux'
  properties: {
    reserved: true
  }
  sku: {
    name: webAppSku
  }
}

@description('Creates an Azure App Service for the API.')
resource appServiceApp 'Microsoft.Web/sites@2022-09-01' = {
  name: webAppNameApi
  location: location
  tags: union(tags, { 'azd-service-name': apiServiceName })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${resourceGroup().id}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/${managedIdentity.name}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    clientAffinityEnabled: false
    siteConfig: {
      linuxFxVersion: 'DOCKER|${containerRegistry.name}.azurecr.io/${uniqueString(resourceGroup().id)}/techexcel/csapi'
      http20Enabled: true
      minTlsVersion: '1.2'
      appCommandLine: ''
      
      appSettings: [
        {
          name: 'AZURE_CLIENT_ID'
          value: managedIdentity.properties.clientId
        }
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://${containerRegistry.name}.azurecr.io'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_USERNAME'
          value: containerRegistry.name
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
          value: containerRegistry.listCredentials().passwords[0].value
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'CosmosDB__AccountEndpoint'
          value: cosmosDbEndpoint
        }        
        {
          name: 'AzureOpenAI__DeploymentName'
          value: openAiProps.deploymentName
        }
        {
          name: 'AzureOpenAI__EmbeddingDeploymentName'
          value: openAiProps.embeddingDeploymentName
        }
        {
          name: 'AzureOpenAI__Endpoint'
          value: openAiProps.endpoint
        }
        ]
      }
    }
}

@description('Creates an Azure App Service for the Dashboard.')
resource appServiceAppDash 'Microsoft.Web/sites@2022-09-01' = {
  name: webAppNameDash
  location: location
  tags: union(tags, { 'azd-service-name': dashServiceName })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${resourceGroup().id}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/${managedIdentity.name}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    clientAffinityEnabled: false
    siteConfig: {
      linuxFxVersion: 'DOCKER|${containerRegistry.name}.azurecr.io/${uniqueString(resourceGroup().id)}/techexcel/csdash'
      http20Enabled: true
      minTlsVersion: '1.2'
      appCommandLine: ''
      appSettings: [
        {
          name: 'AZURE_CLIENT_ID'
          value: managedIdentity.properties.clientId
        }
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://${containerRegistry.name}.azurecr.io'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_USERNAME'
          value: containerRegistry.name
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
          value: containerRegistry.listCredentials().passwords[0].value
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        ]
      }
    }
}

output webapi object = {
  name: appServiceApp.name
  url: appServiceApp.properties.hostNames[0]
}

output webdash object = {
  name: appServiceAppDash.name
  url: appServiceAppDash.properties.hostNames[0]
}

output containerRegistryName string = containerRegistry.name
