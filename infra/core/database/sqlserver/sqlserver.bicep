metadata description = 'Creates an Azure SQL Server instance.'
param name string
param location string = resourceGroup().location
param tags object = {}

param appUser string
param databaseName string
param sqlAdminLogin string
param sqlAdminSid string
param sqlAdminTenantId string

@description('Creates an Azure SQL Server.')
resource sqlServer 'Microsoft.Sql/servers@2024-05-01-preview' = {
  name: name
  location: location
  tags: tags
  properties: { 
    version: '12.0'
    minimalTlsVersion: '1.2'
    administrators: {
      administratorType: 'ActiveDirectory'
      principalType: 'User'
      login: sqlAdminLogin
      sid: sqlAdminSid
      tenantId: sqlAdminTenantId
      azureADOnlyAuthentication: true
    }
  }


  @description('Creates an Azure SQL Database.')
  resource database 'databases' = {
    name: databaseName
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

  resource firewall 'firewallRules' = {
    name: 'Azure Services'
    properties: {
      // Allow all clients
      // Note: range [0.0.0.0-0.0.0.0] means "allow all Azure-hosted clients only".
      // This is not sufficient, because we also want to allow direct access from developer machine, for debugging purposes.
      startIpAddress: '0.0.0.1'
      endIpAddress: '255.255.255.254'
    }
  }
}

/*
resource sqlDeploymentScript 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
  name: '${name}-deployment-script'
  location: location
  kind: 'AzureCLI'
  properties: {
    azCliVersion: '2.37.0'
    retentionInterval: 'PT1H' // Retain the script resource for 1 hour after it ends running
    timeout: 'PT5M' // Five minutes
    cleanupPreference: 'OnSuccess'
    environmentVariables: [
      {
        name: 'APPUSERNAME'
        value: appUser
      }      
      {
        name: 'DBNAME'
        value: databaseName
      }
      {
        name: 'DBSERVER'
        value: sqlServer.properties.fullyQualifiedDomainName
      }
    ]

    scriptContent: '''
wget https://github.com/microsoft/go-sqlcmd/releases/download/v1.8.0/sqlcmd-linux-amd64.tar.bz2
tar x -f sqlcmd-linux-amd64.tar.bz2 -C .

cat <<SCRIPT_END > ./initDb.sql
drop user if exists ${APPUSERNAME}
go
create user ${APPUSERNAME} FROM EXTERNAL PROVIDER
go
alter role db_owner add member ${APPUSERNAME}
go
SCRIPT_END

./sqlcmd -S ${DBSERVER} -d ${DBNAME} -i ./initDb.sql
    '''
  }
}
*/

output endpoint string = sqlServer.properties.fullyQualifiedDomainName
output databaseName string = sqlServer::database.name
