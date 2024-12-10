param location string = resourceGroup().location
param tags object = {}
param apiManagementServiceName string
param restore bool = false
param apimPublisherEmail string
param managedIdentityName string

var apimSku = 'Basicv2'
var apimSkuCount = 1
var apimPublisherName = 'Contoso Suites'

resource userAssignedManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: managedIdentityName
}

resource apiManagementService 'Microsoft.ApiManagement/service@2023-09-01-preview' = {
  name: apiManagementServiceName
  tags: tags
  location: location
  sku: {
    name: apimSku
    capacity: apimSkuCount
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${resourceGroup().id}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/${userAssignedManagedIdentity.name}': {}
    }
  }
  properties: {
    publisherEmail: apimPublisherEmail
    publisherName: apimPublisherName
    restore: restore
  }
}
