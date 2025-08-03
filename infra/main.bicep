targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name of the resource group. Optional. If not provided, a default name will be generated.')
param resourceGroupName string = ''

// Generate a unique token for resource naming
var resourceToken = uniqueString(subscription().id, location, environmentName)
var prefix = 'az'

// Default resource group name if not provided
var actualResourceGroupName = !empty(resourceGroupName) ? resourceGroupName : 'rg-${environmentName}'

// Create resource group
resource rg 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: actualResourceGroupName
  location: location
  tags: {
    'azd-env-name': environmentName
  }
}

// Deploy main resources
module main 'modules/main.bicep' = {
  name: 'main'
  scope: rg
  params: {
    environmentName: environmentName
    location: location
    resourceToken: resourceToken
    prefix: prefix
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output RESOURCE_GROUP_ID string = rg.id
output FUNCTION_APP_NAME string = main.outputs.FUNCTION_APP_NAME
output FUNCTION_APP_URI string = main.outputs.FUNCTION_APP_URI
output STORAGE_ACCOUNT_NAME string = main.outputs.STORAGE_ACCOUNT_NAME
output APPLICATION_INSIGHTS_NAME string = main.outputs.APPLICATION_INSIGHTS_NAME
