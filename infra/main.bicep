targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@minLength(1)
@description('Entra ID Login name of SQL Server admin user (i.e. phjirsa@microsoft.com)')
param sqlAdminLoginName string

@description('SID of the SQL Server admin user (aka Object ID)')
param sqlAdminSid string

// Optional parameters to override the default azd resource naming conventions.
// Add the following to main.parameters.json to provide values:
// "resourceGroupName": {
//      "value": "myGroupName"
// }
param resourceGroupName string = ''

var abbrs = loadJsonContent('./abbreviations.json')

// tags that should be applied to all resources.
var tags = {
  // Tag all resources with the environment name.
  'azd-env-name': environmentName
}

// Generate a unique token to be used in naming resources.
// Remove linter suppression after using.
#disable-next-line no-unused-vars
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// User-assigned managed identity to assign permissions to
module userManagedIdentity 'core/security/user-managed-identity.bicep' = {
  scope: rg
  name: 'userManagedIdentity'
  params: {
    location: location
    userManagedIdentityName: userManagedIdentityName
    tags: tags
  }
}

@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('Model deployments for OpenAI')
var deployments = [
  {
    name: 'gpt-4o'
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-05-13'
    }
    sku: {
      name: 'GlobalStandard'
      capacity: 40
    }
  }
  {
    name: 'text-embedding-ada-002'
    model: {
      format: 'OpenAI'
      name: 'text-embedding-ada-002'
      version: '2'
    }
    capacity: 120
  }
]

@description('Restore the service instead of creating a new instance. This is useful if you previously soft-deleted the service and want to restore it. If you are restoring a service, set this to true. Otherwise, leave this as false.')
param restore bool = false

@description('The email address of the owner of the service')
@minLength(1)
param apimPublisherEmail string = 'support@contososuites.com'

var userManagedIdentityName = '${abbrs.managedIdentityUserAssignedIdentities}${resourceToken}'
var apiManagementServiceName = '${abbrs.apiManagementService}${resourceToken}'
var storageAccountName = '${abbrs.storageStorageAccounts}${resourceToken}'
var searchServiceName = '${abbrs.searchSearchServices}${resourceToken}'
var openAIName = 'openai-${resourceToken}'
var speechServiceName = '${abbrs.cognitiveServicesSpeech}${resourceToken}'
var languageServiceName = '${abbrs.cognitiveServicesTextAnalytics}${resourceToken}'
var registryName = '${abbrs.containerRegistryRegistries}${resourceToken}'
var appServicePlanName = '${abbrs.webServerFarms}${resourceToken}-cosu'
var webAppNameApi = '${abbrs.webSitesAppService}${resourceToken}-api'
var webAppNameDash = '${abbrs.webSitesAppService}${resourceToken}-dash'
var functionAppName = '${abbrs.webSitesFunctions}${resourceToken}-cosu'
var functionAppServicePlanName = '${abbrs.webServerFarms}${resourceToken}-cosu-fn'
var logAnalyticsName = '${abbrs.operationalInsightsWorkspaces}${resourceToken}-cosu'
var appInsightsName = '${abbrs.insightsComponents}${resourceToken}-cosu'
var cosmosAccountName = '${abbrs.documentDBDatabaseAccounts}${resourceToken}'
var sqlServerName = '${abbrs.sqlServers}${resourceToken}'

@description('Create monitoring resources')
module monitoring 'app/monitoring.bicep' = {
  scope: rg
  name: 'monitoring'
  params: {
    location: location
    tags: tags
    logAnalyticsName: logAnalyticsName
    appInsightsName: appInsightsName
  }
}

@description('Create Cosmos DB and SQL Server')
module database 'app/database.bicep' = {
  scope: rg
  name: 'database'
  params: {
    location: location
    cosmosAccountName: cosmosAccountName
    sqlServerName: sqlServerName
    tags: tags
    principalIds: [principalId, userManagedIdentity.outputs.principalId]
    sqlAdminTenantId: subscription().tenantId
    sqlAdminLogin: sqlAdminLoginName
    sqlAdminSid: sqlAdminSid
    sqlAppUserName: userManagedIdentity.outputs.name
  }
}

@description('Creates an Azure Storage account.')
module storageAccount 'core/storage/storage-account.bicep' = {
  scope: rg
  name: storageAccountName
  params: {
    location: location
    name: storageAccountName
    tags: tags
    sku: {
      name: 'Standard_LRS'
    }
    kind: 'StorageV2'
  }
}

@description('Creates an Azure AI services.')
module ai 'app/ai.bicep' = {
  scope: rg
  name: 'ai'
  params: {
    tags: tags
    restore: restore
    openAIName: openAIName
    speechServiceName: speechServiceName
    languageServiceName: languageServiceName
    searchServiceName: searchServiceName
    deployments: deployments
    managedIdentityName: userManagedIdentity.outputs.name
  }
}

@description('Creates Dashboard and API web applications.')
module webapps 'app/webapps.bicep' = {
  scope: rg
  name: 'webapps'
  params: {
    location: location
    tags: tags
    appInsightsName: monitoring.outputs.appInsightsName
    appServicePlanName: appServicePlanName
    registryName: registryName
    webAppNameApi: webAppNameApi
    webAppNameDash: webAppNameDash
    managedIdentityName: userManagedIdentity.outputs.name
    openAiProps: {
      endpoint: ai.outputs.openAIEndpoint
      deploymentName: 'gpt-4o'
      embeddingDeploymentName: 'text-embedding-ada-002'
    }
    cosmosDbEndpoint: database.outputs.cosmos.dbEndpoint
  }
}

@description('Creates a Function App.')
module functionapp 'app/functionapp.bicep' = {
  scope: rg
  name: 'functionapp'
  params: {
    location: location
    tags: tags
    storageAccountName: storageAccountName
    appInsightsName: monitoring.outputs.appInsightsName
    functionAppName: functionAppName
    functionAppServicePlanName: functionAppServicePlanName
    openAiProps: {
      endpoint: ai.outputs.openAIEndpoint
      deploymentName: 'gpt-4o'
      embeddingDeploymentName: 'text-embedding-ada-002'
    }
    cosmosDbEndpoint: database.outputs.cosmos.dbEndpoint
    managedIdentityName: userManagedIdentity.outputs.name
  }
}

@description('Creates an Azure API Management service.')
module apiManagementService 'app/apim.bicep' = {
  scope: rg
  name: 'apiManagementService'
  params: {
    location: location
    apimPublisherEmail: apimPublisherEmail
    tags: tags
    apiManagementServiceName: apiManagementServiceName
    restore: restore
    managedIdentityName: userManagedIdentity.outputs.name
  }
}

// Assign permissions to user and managed identities

// STORAGE
// Storage Blob Data Owner
module storageOwnerRoleUser 'core/security/role.bicep' = {
  scope: rg
  name: 'storageOwnerRoleUser'
  params: {
    roleDefinitionId: 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b' //Storage Blob Data Owner
    principalId: principalId
    principalType: 'User'
  }
}

module storageOwnerRoleManagedIdentity 'core/security/role.bicep' = {
  scope: rg
  name: 'storageOwnerRoleManagedIdentity'
  params: {
    roleDefinitionId: 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b' //Storage Blob Data Owner
    principalId: userManagedIdentity.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

// Storage Account Contributor
module storageContributorRoleUser 'core/security/role.bicep' = {
  scope: rg
  name: 'storageContributorOwnerRoleUser'
  params: {
    roleDefinitionId: '17d1049b-9a84-46fb-8f53-869881c3d3ab' //Storage Account Contributor
    principalId: principalId
    principalType: 'User'
  }
}

module storageContributorRoleManagedIdentity 'core/security/role.bicep' = {
  scope: rg
  name: 'storageContributorRoleManagedIdentity'
  params: {
    roleDefinitionId: '17d1049b-9a84-46fb-8f53-869881c3d3ab' //Storage Account Contributor
    principalId: userManagedIdentity.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

// Storage Queue Contributor
module storageQueueContributorRoleUser 'core/security/role.bicep' = {
  scope: rg
  name: 'storageQueueContributorOwnerRoleUser'
  params: {
    roleDefinitionId: '974c5e8b-45b9-4653-ba55-5f855dd0fb88' // Storage Queue Data Contributor
    principalId: principalId
    principalType: 'User'
  }
}

module storageQueueContributorRoleManagedIdentity 'core/security/role.bicep' = {
  scope: rg
  name: 'storageQueueContributorRoleManagedIdentity'
  params: {
    roleDefinitionId: '974c5e8b-45b9-4653-ba55-5f855dd0fb88' // Storage Queue Data Contributor
    principalId: userManagedIdentity.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

// OpenAI User
module openAiUserRoleUser 'core/security/role.bicep' = {
  scope: rg
  name: 'openAiUserRoleUser'
  params: {
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
    principalId: principalId
    principalType: 'User'
  }
}

module openAiUserRoleManagedIdentity 'core/security/role.bicep' = {
  scope: rg
  name: 'openAiUserRoleManagedIdentity'
  params: {
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
    principalId: userManagedIdentity.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

output cosmosDbEndpoint string = database.outputs.cosmos.dbEndpoint
output storageAccountName string = storageAccount.name
output searchServiceName string = ai.outputs.searchServiceName
output openAIEndpoint string = ai.outputs.openAIEndpoint
output speechServiceName string = ai.outputs.speechServiceName
output application_name string = webapps.outputs.webapi.name
output application_url string = webapps.outputs.webapi.url
output container_registry_name string = webapps.outputs.containerRegistryName
output application_name_dash string = webapps.outputs.webdash.name
output application_url_dash string = webapps.outputs.webdash.url
output function_app_name string = functionapp.outputs.functionAppName
output apiManagementServiceName string = apiManagementService.name
