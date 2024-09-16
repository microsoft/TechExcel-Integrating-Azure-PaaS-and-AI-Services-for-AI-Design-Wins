@description('Location of the resources')
param location string = resourceGroup().location

@description('The email address of the owner of the service')
@minLength(1)
param apimPublisherEmail string = 'support@contososuites.com'

var apiManagementServiceName = '${uniqueString(resourceGroup().id)}-apim'
var apimSku = 'Basicv2'
var apimSkuCount = 1
var apimPublisherName = 'Contoso Suites'
var redisCacheName = '${uniqueString(resourceGroup().id)}-redis'
var redisCacheSku = 'Enterprise_E1'
var redisCacheCapacity = 2

resource apiManagementService 'Microsoft.ApiManagement/service@2023-09-01-preview' = {
  name: apiManagementServiceName
  location: location
  sku: {
    name: apimSku
    capacity: apimSkuCount
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publisherEmail: apimPublisherEmail
    publisherName: apimPublisherName
  }
}

resource redisCache 'Microsoft.Cache/redisEnterprise@2024-03-01-preview' = {
  name: redisCacheName
  location: location
  sku: {
    name: redisCacheSku
    capacity: redisCacheCapacity
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

resource redisCacheDatabase 'Microsoft.Cache/redisEnterprise/databases@2024-03-01-preview' = {
  parent: redisCache
  name: 'default'
  properties: {
    clientProtocol: 'Encrypted'
    evictionPolicy: 'NoEviction'
    clusteringPolicy: 'EnterpriseCluster'
    deferUpgrade: 'NotDeferred'
    modules: [
      {
        name: 'RediSearch'
      }
    ]
    persistence: {
      aofEnabled: false
      rdbEnabled: false
    }
  }
}

output apiManagementServiceName string = apiManagementService.name
output redisCacheName string = redisCache.name
output redisCacheDatabaseName string = redisCacheDatabase.name
