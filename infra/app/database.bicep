param location string = resourceGroup().location
param cosmosAccountName string
param sqlServerName string

@secure()
param sqlAdminPassword string

param tags object = {}
param principalIds array = []

var cosmosDbDatabaseName = 'ContosoSuites'

var sqlDatabaseName = 'ContosoSuitesBookings'
var sqlAdminUsername = 'contosoadmin'

@description('Creates an Azure Cosmos DB NoSQL API database.')
module cosmosDbDatabase '../core/database/cosmos/sql/cosmos-sql-db.bicep' = {
  name: cosmosDbDatabaseName
  params: {
    location: location
    databaseName: cosmosDbDatabaseName
    accountName: cosmosAccountName
    tags: tags
    principalIds: principalIds
  }
}

@description('Creates an Azure SQL Server.')
resource sqlServer 'Microsoft.Sql/servers@2021-11-01' = {
  name: sqlServerName
  location: location
  tags: tags
  properties: {    
    administratorLogin: sqlAdminUsername
    administratorLoginPassword: sqlAdminPassword
  }
}

@description('Creates an Azure SQL Database.')
resource sqlDatabase 'Microsoft.Sql/servers/databases@2021-11-01' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
  }
  sku: {
    name: 'S2'
    tier: 'Standard'
    capacity: 50
  }
}

module roleDefinition '../core/database/cosmos/sql/cosmos-sql-role-def.bicep' = {
  name: 'cosmos-sql-role-definition'
  params: {
    accountName: cosmosDbDatabase.outputs.accountName
  }
}

// We need batchSize(1) here because sql role assignments have to be done sequentially
@batchSize(1)
module userRole '../core/database/cosmos/sql/cosmos-sql-role-assign.bicep' = [for principalId in principalIds: if (!empty(principalId)) {
  name: 'cosmos-sql-user-role-${uniqueString(principalId)}'
  params: {
    accountName: cosmosDbDatabase.outputs.accountName
    roleDefinitionId: roleDefinition.outputs.id
    principalId: principalId
  }
}]

output cosmos object = {
  dbName: cosmosDbDatabase.outputs.accountName
  dbDatabaseName: cosmosDbDatabase.outputs.databaseName
  dbEndpoint: cosmosDbDatabase.outputs.endpoint
}
