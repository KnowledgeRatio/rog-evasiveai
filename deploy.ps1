# Azure Function Deployment Script
# Run this script to deploy the Meta Scraper to Azure Functions

# Prerequisites:
# 1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
# 2. Install Azure Functions Core Tools: https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local
# 3. Login to Azure: az login

# Variables - Update these with your values
$resourceGroup = "rg-meta-scraper"
$functionAppName = "meta-scraper-function"
$location = "East US"
$storageAccount = "metascraperstorage"

# Create resource group
Write-Host "Creating resource group..." -ForegroundColor Green
az group create --name $resourceGroup --location $location

# Create storage account
Write-Host "Creating storage account..." -ForegroundColor Green
az storage account create --name $storageAccount --location $location --resource-group $resourceGroup --sku Standard_LRS

# Create function app
Write-Host "Creating function app..." -ForegroundColor Green
az functionapp create --resource-group $resourceGroup --consumption-plan-location $location --runtime python --runtime-version 3.11 --functions-version 4 --name $functionAppName --storage-account $storageAccount --os-type Linux

# Deploy function code
Write-Host "Deploying function code..." -ForegroundColor Green
func azure functionapp publish $functionAppName

Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host "Function URLs:" -ForegroundColor Yellow
Write-Host "- Full scraper: https://$functionAppName.azurewebsites.net/api/meta_scraper" -ForegroundColor Cyan
Write-Host "- Single section: https://$functionAppName.azurewebsites.net/api/meta_scraper_single" -ForegroundColor Cyan
Write-Host ""
Write-Host "Example usage:" -ForegroundColor Yellow
Write-Host "- Scrape all sections: https://$functionAppName.azurewebsites.net/api/meta_scraper" -ForegroundColor Cyan
Write-Host "- Scrape specific sections: https://$functionAppName.azurewebsites.net/api/meta_scraper?sections=Spam,Misinformation" -ForegroundColor Cyan
Write-Host "- Get summary only: https://$functionAppName.azurewebsites.net/api/meta_scraper?format=summary" -ForegroundColor Cyan
Write-Host "- Single section: https://$functionAppName.azurewebsites.net/api/meta_scraper_single?section=Spam" -ForegroundColor Cyan
