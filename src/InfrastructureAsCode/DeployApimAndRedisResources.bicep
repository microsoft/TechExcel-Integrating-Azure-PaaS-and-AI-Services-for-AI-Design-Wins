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

@description('Restore the service instead of creating a new instance. This is useful if you previously soft-deleted the service and want to restore it. If you are restoring a service, set this to true. Otherwise, leave this as false.')
param restore bool = false

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
    restore: restore
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
}

resource redisCacheDatabase 'Microsoft.Cache/redisEnterprise/databases@2024-03-01-preview' = {
  name: 'default'
  parent: redisCache
  properties: {
    evictionPolicy: 'NoEviction'
    clusteringPolicy: 'EnterpriseCluster'
    deferUpgrade: 'NotDeferred'
    modules: [
      {
        name: 'RedisJSON'
      }
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
