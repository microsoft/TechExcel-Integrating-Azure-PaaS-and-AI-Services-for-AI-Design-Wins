param location string = resourceGroup().location
param tags object = {}
param logAnalyticsName string
param appInsightsName string

@description('Creates an Azure Log Analytics workspace.')
module logAnalytics '../core/monitor/loganalytics.bicep' = {
  name: logAnalyticsName
  params: {
    location: location
    name: logAnalyticsName
    tags: tags
  }
}

@description('Creates an Azure Application Insights resource.')
module appInsights '../core/monitor/applicationinsights.bicep' = {
  name: appInsightsName
  params: {
    location: location
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
    name: appInsightsName
    tags: tags
  }
}

output logAnalyticsWorkspaceId string = logAnalytics.outputs.id
output appInsightsId string = appInsights.outputs.id
output appInsightsName string = appInsights.outputs.name
