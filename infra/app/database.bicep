param location string = resourceGroup().location
param cosmosAccountName string
param sqlServerName string

param sqlAdminTenantId string
param sqlAdminLogin string
param sqlAdminSid string
param sqlAppUserName string

param tags object = {}
param principalIds array = []

var cosmosDbDatabaseName = 'ContosoSuites'
var sqlDatabaseName = 'ContosoSuitesBookings'

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
module sqlServer '../core/database/sqlserver/sqlserver.bicep' = {
  name: 'sqlServer'
  params: {
    name: sqlServerName
    databaseName: sqlDatabaseName
    location: location
    tags: tags
    sqlAdminLogin: sqlAdminLogin
    sqlAdminSid: sqlAdminSid
    sqlAdminTenantId: sqlAdminTenantId
    appUser: sqlAppUserName
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
