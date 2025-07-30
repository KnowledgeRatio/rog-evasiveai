# Azure Function with Storage Documentation

## Storage-Enabled Azure Function

The `function_app_with_storage.py` version adds Azure Blob Storage capabilities to persist scraped data while maintaining all original functionality.

## New Features

### 🗄️ **Azure Blob Storage Integration**
- Saves all scraped content as JSON files in Azure Blob Storage
- Automatic container creation
- Timestamped file naming
- Organized folder structure

### 📁 **Storage Structure**
```
Container: meta-standards/
├── main_page_YYYYMMDD_HHMMSS.json
├── sections/
│   ├── Spam_YYYYMMDD_HHMMSS.json
│   ├── Misinformation_YYYYMMDD_HHMMSS.json
│   └── ...
├── single_sections/
│   └── Custom_Section_YYYYMMDD_HHMMSS.json
└── master_summary_YYYYMMDD_HHMMSS.json
```

## New Endpoints

### 1. Storage-Enabled Scraper (`/api/meta_scraper_storage`)

**Query Parameters:**
- `sections` (optional): Comma-separated section names
- `include_main` (optional): Include main page (default: true)
- `format` (optional): "json" or "summary" (default: json)
- `save_to_storage` (optional): Save to blob storage (default: true)
- `container_name` (optional): Container name (default: meta-standards)

**Examples:**
```
GET /api/meta_scraper_storage
GET /api/meta_scraper_storage?sections=Spam,Misinformation&container_name=my-policies
GET /api/meta_scraper_storage?save_to_storage=false
```

### 2. Enhanced Single Section (`/api/meta_scraper_single`)

**New Parameters:**
- `save_to_storage` (optional): Save to blob storage (default: false)
- `container_name` (optional): Container name (default: meta-standards)

**Examples:**
```
GET /api/meta_scraper_single?section=Spam&save_to_storage=true
GET /api/meta_scraper_single?section=Spam&save_to_storage=true&container_name=spam-policies
```

## Response Format with Storage

### Storage-Enabled Response
```json
{
  "scraping_session": {
    "timestamp": "2025-07-30T10:30:00",
    "total_sections": 2,
    "successful_sections": 2,
    "failed_sections": 0,
    "success_rate": 100.0,
    "save_to_storage": true,
    "container_name": "meta-standards"
  },
  "storage_urls": {
    "main_page": "https://yourstorageaccount.blob.core.windows.net/meta-standards/main_page_20250730_103000.json",
    "Spam": "https://yourstorageaccount.blob.core.windows.net/meta-standards/sections/Spam_20250730_103001.json",
    "Misinformation": "https://yourstorageaccount.blob.core.windows.net/meta-standards/sections/Misinformation_20250730_103002.json",
    "master_summary": "https://yourstorageaccount.blob.core.windows.net/meta-standards/master_summary_20250730_103003.json"
  },
  "data": {
    // ... full scraped data as before
  }
}
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Storage

**For Local Development:**
- Install [Azurite](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite) for local storage emulation
- Or update `local.settings.json` with real Azure Storage connection string

**For Azure Deployment:**
- The function automatically uses the storage account created during deployment
- No additional configuration needed

### 3. Deploy with Storage

```powershell
# Use the updated deployment script
.\deploy_with_storage.ps1
```

Or manually:
```powershell
# Create storage account (if not already done)
az storage account create --name metascraperstorage --location "East US" --resource-group rg-meta-scraper --sku Standard_LRS

# Deploy function (will use the same storage account)
func azure functionapp publish meta-scraper-function
```

## Storage Benefits

### ✅ **Advantages**
- **Persistence**: Data survives function restarts and redeployments
- **Scalability**: Can handle large datasets without memory limits
- **Accessibility**: Files accessible via Azure Storage APIs, Azure Portal, or direct URLs
- **Backup**: Automatic geo-replication if configured
- **Cost-Effective**: Pay only for storage used
- **Integration**: Easy integration with other Azure services

### 📊 **Use Cases**
- **Data Archiving**: Keep historical snapshots of policy changes
- **Batch Processing**: Process large datasets in chunks
- **Data Analytics**: Feed data to other analytics tools
- **API Integration**: Other systems can access stored files directly
- **Compliance**: Meet data retention requirements

## Storage Management

### Access Stored Files
1. **Azure Portal**: Navigate to Storage Account → Containers → meta-standards
2. **Storage Explorer**: Use Azure Storage Explorer desktop app
3. **Azure CLI**: `az storage blob list --container-name meta-standards`
4. **Direct URLs**: Use the URLs returned in the response

### File Cleanup
```powershell
# Delete old files (example: files older than 30 days)
az storage blob delete-batch --source meta-standards --pattern "*/????????_??????.json" --account-name metascraperstorage
```

## Environment Variables

### Required Settings
- `AzureWebJobsStorage`: Connection string for storage account (automatically set)

### Optional Settings
- `AZURE_STORAGE_CONNECTION_STRING`: Alternative storage connection (if different from function storage)
- `DEFAULT_CONTAINER_NAME`: Override default container name
- `STORAGE_RETENTION_DAYS`: Automatic cleanup after X days (if implemented)

## Error Handling

The function handles storage errors gracefully:
- **Storage Unavailable**: Returns data without storage URLs
- **Permission Issues**: Logs error and continues with API response
- **Container Creation**: Automatically creates containers if they don't exist
- **Blob Conflicts**: Overwrites existing files with same name

## Monitoring Storage Usage

### Azure Monitor Queries
```kusto
// Function execution with storage operations
FunctionAppLogs
| where Message contains "Saved to blob"
| summarize count() by bin(TimeGenerated, 1h)

// Storage operation failures
FunctionAppLogs
| where Message contains "Failed to save" and Message contains "storage"
| project TimeGenerated, Message
```

### Storage Metrics
- Monitor blob storage usage in Azure Portal
- Set up alerts for storage costs
- Track blob creation/deletion rates

## Backward Compatibility

The original endpoints (`/api/meta_scraper` and `/api/meta_scraper_single`) remain unchanged and don't save to storage by default, ensuring existing integrations continue to work.
