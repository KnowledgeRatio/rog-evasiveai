# Meta Community Standards Scraper - Azure Function

This is an Azure Function version of the Meta Community Standards scraper that provides HTTP endpoints to scrape Meta's community standards pages and return structured JSON data.

## Features

- **HTTP Triggered Functions**: RESTful API endpoints for scraping
- **Flexible Scraping**: Scrape all sections or specific ones
- **Structured JSON Output**: Well-formatted data with metadata and statistics
- **Two Endpoints**:
  - `meta_scraper`: Scrape multiple sections
  - `meta_scraper_single`: Scrape a single section
- **Multiple Response Formats**: Full data or summary only
- **Error Handling**: Comprehensive error handling and logging

## Endpoints

### 1. Full Scraper (`/api/meta_scraper`)

Scrapes multiple sections of Meta's community standards.

**Query Parameters:**
- `sections` (optional): Comma-separated list of section names to scrape
- `include_main` (optional): Include main page (default: true)
- `format` (optional): Response format - "json" or "summary" (default: json)

**Examples:**
```
GET /api/meta_scraper
GET /api/meta_scraper?sections=Spam,Misinformation
GET /api/meta_scraper?format=summary
GET /api/meta_scraper?sections=Spam&include_main=false
```

### 2. Single Section Scraper (`/api/meta_scraper_single`)

Scrapes a single section.

**Query Parameters:**
- `section` (required): Section name to scrape
- `url` (optional): Custom URL to scrape (overrides predefined URLs)

**Examples:**
```
GET /api/meta_scraper_single?section=Spam
GET /api/meta_scraper_single?section=Custom&url=https://example.com/policy
```

## Available Sections

- Coordinating Harm and Promoting Crime
- Dangerous Organisations and Individuals
- Fraud, Scams and Deceptive Practices
- Restricted Goods and Services
- Violence and Incitement
- Adult Sexual Exploitation
- Bullying and Harassment
- Child Sexual Exploitation, Abuse and Nudity
- Human Exploitation
- Suicide, Self-Injury and Eating Disorders
- Adult Nudity and Sexual Activity
- Adult Sexual Solicitation and Sexually Explicit Language
- Hateful Conduct
- Privacy Violations
- Violent and Graphic Content
- Account Integrity
- Authentic Identity Representation
- Cybersecurity
- Inauthentic Behavior
- Memorialisation
- Misinformation
- Spam
- Third-Party Intellectual Property Infringement
- Using Meta Intellectual Property and Licences
- Additional Protection of Minors
- Locally Illegal Content, Products or Services
- User Requests

## Response Format

### Full Response Structure
```json
{
  "scraping_session": {
    "timestamp": "2025-07-30T10:30:00",
    "total_sections": 5,
    "successful_sections": 4,
    "failed_sections": 1,
    "success_rate": 80.0,
    "include_main_page": true
  },
  "data": {
    "main_page": {
      "metadata": {
        "section_name": "Main Page",
        "url": "https://...",
        "scraped_at": "2025-07-30T10:30:00",
        "status": "success"
      },
      "content": {
        "title": "Community Standards",
        "raw_text": "...",
        "structured_content": {
          "headings": [...],
          "paragraphs": [...],
          "lists": [...],
          "links": [...]
        }
      },
      "statistics": {
        "character_count": 12345,
        "word_count": 2000,
        "paragraph_count": 50,
        "heading_count": 10
      }
    },
    "sections": {
      "Spam": { ... },
      "Misinformation": { ... }
    }
  }
}
```

### Summary Response Structure
```json
{
  "session_info": {
    "timestamp": "2025-07-30T10:30:00",
    "total_sections": 5,
    "successful_sections": 4,
    "failed_sections": 1,
    "success_rate": 80.0
  },
  "main_page_summary": {
    "status": "success",
    "character_count": 12345,
    "word_count": 2000
  },
  "sections_summary": {
    "Spam": {
      "status": "success",
      "character_count": 8500,
      "word_count": 1200,
      "paragraph_count": 25,
      "heading_count": 5
    }
  }
}
```

## Deployment

### Prerequisites
1. [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
3. Azure subscription

### Local Development
```powershell
# Install dependencies
pip install -r requirements.txt

# Run locally
func start
```

### Deploy to Azure
```powershell
# Login to Azure
az login

# Run deployment script
.\deploy.ps1
```

Or manually:
```powershell
# Create resource group
az group create --name rg-meta-scraper --location "East US"

# Create storage account
az storage account create --name metascraperstorage --location "East US" --resource-group rg-meta-scraper --sku Standard_LRS

# Create function app
az functionapp create --resource-group rg-meta-scraper --consumption-plan-location "East US" --runtime python --runtime-version 3.11 --functions-version 4 --name meta-scraper-function --storage-account metascraperstorage --os-type Linux

# Deploy
func azure functionapp publish meta-scraper-function
```

## Configuration

### Environment Variables
Set these in Azure Function App settings:
- `FUNCTIONS_WORKER_RUNTIME`: `python`
- Add custom variables as needed for URLs or timeouts

### Timeout Settings
The function timeout is set to 10 minutes in `host.json`. Adjust as needed for your scraping requirements.

## Error Handling

The function includes comprehensive error handling:
- HTTP request failures
- Parsing errors
- Timeout handling
- Invalid parameters
- Missing sections

All errors are logged and returned in a structured format.

## Monitoring

Use Azure Application Insights for monitoring:
- Function execution metrics
- Error rates and details
- Performance analytics
- Custom logging events

## Security

- Functions use `AuthLevel.FUNCTION` requiring function keys
- No sensitive data is stored in the function
- All external requests use proper user agents
- Input validation on all parameters

## Limitations

- Azure Functions have execution time limits (10 minutes default)
- Memory limitations may affect large scraping operations
- Cold start delays for infrequently used functions
- Rate limiting may be needed for high-frequency usage

## Support

For issues or questions:
1. Check Azure Function logs
2. Verify the target URLs are accessible
3. Ensure proper authentication headers if required
4. Monitor for rate limiting from target sites
