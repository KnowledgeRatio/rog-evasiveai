# Meta Community Standards Scraper

A comprehensive Python-based scraper for extracting and analyzing Meta's community standards policies from their transparency website. Available both as standalone scripts and as Azure Functions for serverless deployment.

## 🚀 Features

- **Multiple Output Formats**: JSON, plain text, and structured data
- **Azure Functions Support**: Serverless HTTP API endpoints
- **Comprehensive Coverage**: All 27+ Meta community standards sections
- **Structured Data**: Organized headings, paragraphs, lists, and links
- **Error Handling**: Robust error handling and retry mechanisms
- **Local & Cloud**: Run locally or deploy to Azure

## 📁 Project Structure

### Scripts
- `meta_scraper_json.py` - Original script with JSON output
- `meta_scraper_updated.py` - Enhanced version with better parsing
- `simple_meta_scraper.py` - Lightweight version
- `function_app.py` - **Azure Functions version (recommended)**

### Azure Functions
- `function_app.py` - Main Azure Function with HTTP endpoints
- `host.json` - Azure Functions host configuration
- `local.settings.json` - Local development settings
- `deploy.ps1` - PowerShell deployment script

### Documentation
- `AZURE_FUNCTION_README.md` - Detailed Azure Functions documentation
- `THIRD_PARTY_LICENSES.md` - License information for dependencies

### Testing & Utilities
- `test_azure_function.py` - Test script for Azure Functions
- `test_setup.py` - Environment testing
- `debug_requests.py` - Network debugging utilities

## 🔧 Quick Start

### Option 1: Azure Functions (Recommended)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run locally:**
   ```bash
   func start
   ```

3. **Test the endpoints:**
   ```bash
   # Get all sections
   curl "http://localhost:7071/api/meta_scraper"
   
   # Get specific sections
   curl "http://localhost:7071/api/meta_scraper?sections=Spam,Misinformation"
   
   # Get single section
   curl "http://localhost:7071/api/meta_scraper_single?section=Spam"
   ```

### Option 2: Standalone Script

```bash
python meta_scraper_json.py
```

## 🌐 Azure Functions API

### Endpoints

#### `/api/meta_scraper`
Scrape multiple sections with flexible options.

**Parameters:**
- `sections` (optional): Comma-separated section names
- `include_main` (optional): Include main page (default: true)
- `format` (optional): "json" or "summary" (default: json)

**Examples:**
```
GET /api/meta_scraper
GET /api/meta_scraper?sections=Spam,Misinformation&format=summary
GET /api/meta_scraper?include_main=false
```

#### `/api/meta_scraper_single`
Scrape a single section.

**Parameters:**
- `section` (required): Section name to scrape
- `url` (optional): Custom URL to scrape

**Examples:**
```
GET /api/meta_scraper_single?section=Spam
GET /api/meta_scraper_single?section=Custom&url=https://example.com/policy
```

## 📋 Available Sections

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

## 🚀 Deploy to Azure

### Prerequisites
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- Azure subscription

### Quick Deploy
```powershell
# Login to Azure
az login

# Run deployment script
.\deploy.ps1
```

### Manual Deployment
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

## 📊 Response Format

### Full JSON Response
```json
{
  "scraping_session": {
    "timestamp": "2025-07-30T10:30:00",
    "total_sections": 5,
    "successful_sections": 4,
    "failed_sections": 1,
    "success_rate": 80.0
  },
  "data": {
    "sections": {
      "Spam": {
        "metadata": {
          "section_name": "Spam",
          "url": "https://...",
          "scraped_at": "2025-07-30T10:30:00",
          "status": "success"
        },
        "content": {
          "title": "Spam",
          "raw_text": "...",
          "structured_content": {
            "headings": [...],
            "paragraphs": [...],
            "lists": [...],
            "links": [...]
          }
        },
        "statistics": {
          "character_count": 8500,
          "word_count": 1200,
          "paragraph_count": 25,
          "heading_count": 5
        }
      }
    }
  }
}
```

## 🔍 Testing

Run the test suite:
```bash
# Test Azure Functions locally
python test_azure_function.py

# Test environment setup
python test_setup.py
```

## 📄 License & Attribution

This project uses several open-source libraries. See `THIRD_PARTY_LICENSES.md` for complete license information and attributions.

### Key Dependencies
- **Beautiful Soup** (MIT License) - HTML parsing
- **Requests** (Apache 2.0) - HTTP requests  
- **Azure Functions** (MIT License) - Serverless framework

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## ⚠️ Important Notes

- **Rate Limiting**: Be respectful of Meta's servers
- **Terms of Service**: Ensure compliance with Meta's terms
- **Data Usage**: Review Meta's data usage policies
- **Timeout**: Azure Functions have a 10-minute timeout limit

## 🔧 Troubleshooting

### Common Issues
1. **403 Errors**: Update User-Agent string
2. **Timeout Issues**: Reduce number of sections per request
3. **Memory Issues**: Use summary format for large datasets
4. **Cold Start**: Azure Functions may have initial delays

### Getting Help
- Check Azure Function logs
- Verify target URLs are accessible
- Monitor for rate limiting
- Review error messages in responses

## 📈 Monitoring

When deployed to Azure:
- Use Application Insights for monitoring
- Track success rates and performance
- Set up alerts for failures
- Monitor function execution times

---

**⭐ If this project helps you, please consider giving it a star!**

### Step 2: Download This Tool
1. Download all files from this repository to a folder on your computer
2. Remember where you saved them!

### Step 3: Install Required Components
1. Open Command Prompt (Windows) or Terminal (Mac/Linux)
2. Navigate to the folder where you saved the files
3. Type: `pip install -r requirements.txt`
4. Press Enter and wait for it to finish

### Step 4: Run the Scraper
1. In the same Command Prompt/Terminal, type: `python meta_scraper_updated.py`
2. Press Enter
3. Wait for it to finish (takes about 2-3 minutes)
4. You'll see progress updates as it downloads each section

## What You'll Find in Your Results

After the scraper finishes, you'll have a new folder called `meta_standards_output` with these files:

### 📊 Summary Files
- **`summary.txt`** - Your main report! Shows what was downloaded successfully
- **`meta_standards_summary.json`** - Technical version (you can ignore this)

### 📄 Content Files
- **`00_main_page.txt`** - Meta's main Community Standards page
- **`01_Coordinating_Harm_and_Promoting_Crime.txt`** - First policy section
- **`02_Dangerous_Organisations_and_Individuals.txt`** - Second policy section
- ...and so on through **`27_User_Requests.txt`**

### 🔍 How to Read Your Results

1. **Start with `summary.txt`** - This tells you:
   - How many sections were downloaded successfully
   - Which sections (if any) failed to download
   - Success rate percentage

2. **Browse the numbered files** - Each contains:
   - The full text of one policy section
   - The official title from Meta's website
   - The web address where it came from
   - How many characters of content were captured

### 📈 Understanding the Summary Report

When you open `summary.txt`, you'll see something like:

```
META COMMUNITY STANDARDS SCRAPING SUMMARY
============================================================

Total sections attempted: 27
Successfully scraped: 27
Failed: 0
Success rate: 100.0%

SUCCESSFUL SECTIONS:
------------------------------
✓ Coordinating Harm and Promoting Crime (13,344 chars)
✓ Dangerous Organisations and Individuals (24,009 chars)
...
```

- **Total sections attempted**: How many policy sections the tool tried to download
- **Successfully scraped**: How many actually worked
- **Success rate**: Percentage that worked (100% is perfect!)
- **Character count**: Shows how much content was captured (more = better)

## Complete List of Policy Sections Downloaded

The tool downloads all 27 sections of Meta's Community Standards:

1. **Coordinating Harm and Promoting Crime** - Rules about planning illegal activities
2. **Dangerous Organisations and Individuals** - Policies on terrorists, criminals, etc.
3. **Fraud, Scams and Deceptive Practices** - Rules against scams and fake schemes
4. **Restricted Goods and Services** - What you can't sell on Meta platforms
5. **Violence and Incitement** - Rules about violent content and threats
6. **Adult Sexual Exploitation** - Policies protecting adults from sexual exploitation
7. **Bullying and Harassment** - Rules against bullying and harassment
8. **Child Sexual Exploitation, Abuse and Nudity** - Strong protections for children
9. **Human Exploitation** - Rules against human trafficking and exploitation
10. **Suicide, Self-Injury and Eating Disorders** - Mental health protection policies
11. **Adult Nudity and Sexual Activity** - Rules about adult content
12. **Adult Sexual Solicitation and Sexually Explicit Language** - Sexual conduct rules
13. **Hateful Conduct** - Policies against hate speech and discrimination
14. **Privacy Violations** - Rules protecting people's privacy
15. **Violent and Graphic Content** - Policies on disturbing visual content
16. **Account Integrity** - Rules about authentic accounts
17. **Authentic Identity Representation** - Requirements for real identity
18. **Cybersecurity** - Protection against hacking and cyber threats
19. **Inauthentic Behavior** - Rules against fake engagement and manipulation
20. **Memorialisation** - Policies for accounts of deceased users
21. **Misinformation** - Rules against false information
22. **Spam** - Policies against unwanted content and messages
23. **Third-Party Intellectual Property Infringement** - Copyright protection rules
24. **Using Meta Intellectual Property and Licences** - Rules about using Meta's content
25. **Additional Protection of Minors** - Extra safety measures for young users
26. **Locally Illegal Content, Products or Services** - Country-specific legal requirements
27. **User Requests** - How Meta handles user reports and requests

## Troubleshooting (If Something Goes Wrong)

### ❌ "Python is not recognized" Error
**Problem**: Python isn't installed properly
**Solution**: 
1. Reinstall Python from python.org
2. Make sure to check "Add Python to PATH" during installation
3. Restart your computer

### ❌ "pip is not recognized" Error  
**Problem**: Python package manager isn't working
**Solution**: Try `python -m pip install -r requirements.txt` instead

### ❌ Some Sections Show "Failed to scrape"
**Problem**: Meta might have changed their website
**Solution**: This is normal - the tool will get most sections even if a few fail

### ❌ Very Slow or Stuck
**Problem**: The tool waits 2 seconds between downloads to be respectful
**Solution**: This is normal! Just wait - it takes 2-3 minutes total

### ❌ Empty or Very Short Files
**Problem**: Meta's website might be temporarily down or changed
**Solution**: Try running the tool again later

## For Advanced Users

### Technical Details
- Uses `requests` library for web downloads
- Uses `BeautifulSoup` for reading website content  
- Waits 2 seconds between downloads to be respectful to Meta's servers
- Saves content in both JSON (for programs) and TXT (for humans) formats

### Customizing the Tool
You can modify `meta_scraper_updated.py` to:
- Change which sections to download
- Adjust the delay time between downloads
- Modify the output format
- Add new sections if Meta creates them

## Files in This Project

- **`meta_scraper_updated.py`** - The main tool (this is what you run)
- **`requirements.txt`** - List of components Python needs to install
- **`README.md`** - This instruction file
- **Other files** - Various versions and test files (you can ignore these)

## Legal and Ethical Use

✅ **This tool is designed for:**
- Educational research
- Policy analysis  
- Academic study
- Personal reference

✅ **Important notes:**
- Only downloads publicly available information
- Respects Meta's servers with reasonable delays
- Downloads from Meta's official transparency pages
- Does not bypass any security or access controls

⚠️ **Please use responsibly:**
- Don't run this tool excessively (once per day maximum)
- Respect the content and don't redistribute without permission
- Check Meta's terms of service for any restrictions
- Use the downloaded content ethically and legally

## Support and Issues

If you encounter problems:

1. **Check the troubleshooting section above first**
2. **Make sure you have a stable internet connection**
3. **Try running the tool again (sometimes temporary network issues occur)**
4. **Check that you're using Python 3.8 or newer**

The tool is designed to be robust and handle most common issues automatically.

---

**Last Updated**: July 2025  
**Tool Version**: 2.0 (Individual file output with 100% success rate)  
**Tested On**: Windows 10/11, macOS, Linux
