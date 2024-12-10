param location string = resourceGroup().location
param userManagedIdentityName string = 'userManagedIdentity'
param tags object = {}

resource userManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: userManagedIdentityName
  location: location
  tags: tags
}

output id string = userManagedIdentity.id
output principalId string = userManagedIdentity.properties.principalId
