"""
Meta Community Standards Scraper - Azure Function with Storage Version

This version saves scraped content to Azure Blob Storage while also returning
JSON responses via HTTP endpoints.
"""

import azure.functions as func
import requests
from bs4 import BeautifulSoup
import json
import re
import logging
import os
import validators
import traceback
from datetime import datetime
from typing import Dict, Any
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 9 * * 1", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def weekly_meta_scraper_timer(myTimer: func.TimerRequest) -> None:
    """
    Timer trigger function that runs weekly on Mondays at 9 AM UTC
    Cron expression: "0 0 9 * * 1" = second minute hour day month day-of-week
    """
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Weekly Meta Community Standards scraper started')
    
    try:
        # Get blob storage client
        blob_service_client = get_blob_service_client()
        
        # Create container name with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        container_name = f"meta-standards-weekly-{timestamp}"
        
        # Call the core scraping logic
        result = perform_scraping_operation(
            blob_service_client=blob_service_client,
            container_name=container_name,
            sections_param=None,  # Scrape all sections
            include_main=True,
            save_to_storage=True,
            response_format='summary'
        )
        
        logging.info(f'Weekly scraping completed successfully')
        logging.info(f'Total sections: {result["scraping_session"].get("total_sections", 0)}')
        logging.info(f'Successful sections: {result["scraping_session"].get("successful_sections", 0)}')
        logging.info(f'Success rate: {result["scraping_session"].get("success_rate", 0):.1f}%')
        logging.info(f'Container: {container_name}')
        
    except Exception as e:
        logging.error(f'Weekly scraping failed: {str(e)}')
        logging.error(traceback.format_exc())

def get_blob_service_client():
    """Get Azure Blob Storage client"""
    connection_string = os.environ.get('AzureWebJobsStorage')
    if not connection_string:
        raise ValueError("AzureWebJobsStorage connection string not found")
    return BlobServiceClient.from_connection_string(connection_string)

def save_to_blob_storage(blob_service_client: BlobServiceClient, container_name: str, 
                        blob_name: str, content: str, content_type: str = "application/json"):
    """Save content to Azure Blob Storage"""
    try:
        # Create container if it doesn't exist
        try:
            blob_service_client.create_container(container_name)
            logging.info(f"Created container: {container_name}")
        except Exception:
            # Container already exists
            pass
        
        # Upload blob
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        blob_client.upload_blob(
            content, 
            blob_type="BlockBlob", 
            content_settings={'content_type': content_type},
            overwrite=True
        )
        
        # Get blob URL
        blob_url = blob_client.url
        logging.info(f"Saved to blob: {blob_name}")
        return blob_url
        
    except Exception as e:
        logging.error(f"Error saving to blob storage: {str(e)}")
        raise

def perform_scraping_operation(blob_service_client, container_name, sections_param=None, 
                             include_main=True, save_to_storage=True, response_format='json'):
    """
    Core scraping operation that can be called from HTTP triggers or timer triggers
    """
    # Get all available sections
    all_sections = get_section_urls()
    
    # Determine which sections to scrape
    if sections_param:
        requested_sections = [s.strip() for s in sections_param.split(',')]
        section_urls = {name: url for name, url in all_sections.items() 
                       if name in requested_sections}
        if not section_urls:
            raise ValueError("No valid sections found in request")
    else:
        section_urls = all_sections
    
    # Setup session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Results structure
    results = {
        'scraping_session': {
            'timestamp': datetime.now().isoformat(),
            'total_sections': len(section_urls),
            'successful_sections': 0,
            'failed_sections': 0,
            'success_rate': 0.0,
            'include_main_page': include_main,
            'save_to_storage': save_to_storage,
            'container_name': container_name if save_to_storage else None
        },
        'storage_urls': {},
        'data': {}
    }
    
    # Scrape main page if requested
    if include_main:
        logging.info("Scraping main community standards page...")
        base_url = "https://transparency.meta.com/en-gb/policies/community-standards/"
        main_soup = get_page_content(base_url, session)
        main_content = extract_content_json(main_soup, "Main Page", base_url)
        results['data']['main_page'] = main_content
        
        # Save main page to storage if enabled
        if save_to_storage and blob_service_client:
            try:
                blob_name = f"main_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                blob_url = save_to_blob_storage(
                    blob_service_client,
                    container_name,
                    blob_name,
                    json.dumps(main_content, ensure_ascii=False, indent=2)
                )
                results['storage_urls']['main_page'] = blob_url
            except Exception as e:
                logging.error(f"Failed to save main page to storage: {str(e)}")
    
    # Scrape each section
    successful = 0
    results['data']['sections'] = {}
    
    for section_name, url in section_urls.items():
        logging.info(f"Scraping: {section_name}")
        
        soup = get_page_content(url, session)
        content = extract_content_json(soup, section_name, url)
        
        # Store the content
        results['data']['sections'][section_name] = content
        
        # Save to storage if enabled
        if save_to_storage and blob_service_client:
            try:
                # Create safe filename
                safe_filename = re.sub(r'[^\w\s-]', '', section_name)
                safe_filename = re.sub(r'[-\s]+', '_', safe_filename).strip('_')
                blob_name = f"sections/{safe_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                blob_url = save_to_blob_storage(
                    blob_service_client,
                    container_name,
                    blob_name,
                    json.dumps(content, ensure_ascii=False, indent=2)
                )
                results['storage_urls'][section_name] = blob_url
                logging.info(f"Saved {section_name} to blob storage")
            except Exception as e:
                logging.error(f"Failed to save {section_name} to storage: {str(e)}")
        
        # Track success/failure
        if content['metadata']['status'] == 'success' and content['statistics']['character_count'] > 200:
            logging.info(f"Successfully scraped {section_name}")
            successful += 1
        else:
            logging.warning(f"Failed to scrape {section_name}")
    
    # Save master summary to storage if enabled
    if save_to_storage and blob_service_client:
        try:
            summary_blob_name = f"master_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            summary_blob_url = save_to_blob_storage(
                blob_service_client,
                container_name,
                summary_blob_name,
                json.dumps(results, ensure_ascii=False, indent=2)
            )
            results['storage_urls']['master_summary'] = summary_blob_url
        except Exception as e:
            logging.error(f"Failed to save master summary to storage: {str(e)}")
    
    # Update final statistics
    results['scraping_session']['successful_sections'] = successful
    results['scraping_session']['failed_sections'] = len(section_urls) - successful
    results['scraping_session']['success_rate'] = (successful / len(section_urls)) * 100 if section_urls else 0
    
    return results

def get_page_content(url: str, session: requests.Session) -> BeautifulSoup:
    """Fetch page content with error handling"""
    try:
        logging.info(f"Fetching: {url}")
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'lxml')
        else:
            logging.warning(f"HTTP {response.status_code} for {url}")
            return None
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def extract_content_json(soup: BeautifulSoup, section_name: str, url: str) -> Dict[str, Any]:
    """Extract content from a page and structure as JSON"""
    content = {
        'metadata': {
            'section_name': section_name,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'status': 'success'
        },
        'content': {
            'title': '',
            'raw_text': '',
            'structured_content': {
                'headings': [],
                'paragraphs': [],
                'lists': [],
                'links': []
            }
        },
        'statistics': {
            'character_count': 0,
            'word_count': 0,
            'paragraph_count': 0,
            'heading_count': 0
        }
    }
    
    if not soup:
        content['metadata']['status'] = 'failed'
        content['metadata']['error'] = 'Failed to fetch page'
        return content
    
    # Extract title
    title = soup.find('h1')
    if title:
        content['content']['title'] = title.get_text(strip=True)
    
    # Extract main content - try different selectors
    main_selectors = [
        'main',
        'article',
        '[role="main"]',
        '.content',
        '.policy-content',
        '.main-content'
    ]
    
    main_content = None
    for selector in main_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    if not main_content:
        # Fallback to body
        main_content = soup.find('body')
    
    if main_content:
        # Remove navigation, header, footer
        for element in main_content.find_all(['nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Extract structured content
        # Headings
        for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            content['content']['structured_content']['headings'].append({
                'level': int(heading.name[1]),
                'text': heading.get_text(strip=True),
                'tag': heading.name
            })
        
        # Paragraphs
        for para in main_content.find_all('p'):
            para_text = para.get_text(strip=True)
            if para_text:  # Only add non-empty paragraphs
                content['content']['structured_content']['paragraphs'].append(para_text)
        
        # Lists
        for list_elem in main_content.find_all(['ul', 'ol']):
            list_items = []
            for li in list_elem.find_all('li'):
                li_text = li.get_text(strip=True)
                if li_text:
                    list_items.append(li_text)
            if list_items:
                content['content']['structured_content']['lists'].append({
                    'type': list_elem.name,
                    'items': list_items
                })
        
        # Links
        for link in main_content.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            if link_text and link['href']:
                content['content']['structured_content']['links'].append({
                    'text': link_text,
                    'url': link['href']
                })
        
        # Get raw text content
        raw_text = main_content.get_text(separator='\n', strip=True)
        content['content']['raw_text'] = raw_text
        
        # Calculate statistics
        content['statistics']['character_count'] = len(raw_text)
        content['statistics']['word_count'] = len(raw_text.split())
        content['statistics']['paragraph_count'] = len(content['content']['structured_content']['paragraphs'])
        content['statistics']['heading_count'] = len(content['content']['structured_content']['headings'])
    
    return content

def get_section_urls() -> Dict[str, str]:
    """Get the predefined section URLs"""
    return {
        "Coordinating Harm and Promoting Crime": "https://transparency.meta.com/en-gb/policies/community-standards/coordinating-harm-publicizing-crime/",
        "Dangerous Organisations and Individuals": "https://transparency.meta.com/en-gb/policies/community-standards/dangerous-individuals-organizations/",
        "Fraud, Scams and Deceptive Practices": "https://transparency.meta.com/en-gb/policies/community-standards/fraud-scams/",
        "Restricted Goods and Services": "https://transparency.meta.com/en-gb/policies/community-standards/regulated-goods/",
        "Violence and Incitement": "https://transparency.meta.com/en-gb/policies/community-standards/violence-incitement/",
        "Adult Sexual Exploitation": "https://transparency.meta.com/en-gb/policies/community-standards/sexual-exploitation-adults/",
        "Bullying and Harassment": "https://transparency.meta.com/en-gb/policies/community-standards/bullying-harassment/",
        "Child Sexual Exploitation, Abuse and Nudity": "https://transparency.meta.com/en-gb/policies/community-standards/child-sexual-exploitation-abuse-nudity/",
        "Human Exploitation": "https://transparency.meta.com/en-gb/policies/community-standards/human-exploitation/",
        "Suicide, Self-Injury and Eating Disorders": "https://transparency.meta.com/en-gb/policies/community-standards/suicide-self-injury/",
        "Adult Nudity and Sexual Activity": "https://transparency.meta.com/en-gb/policies/community-standards/adult-nudity-sexual-activity/",
        "Adult Sexual Solicitation and Sexually Explicit Language": "https://transparency.meta.com/en-gb/policies/community-standards/sexual-solicitation/",
        "Hateful Conduct": "https://transparency.meta.com/en-gb/policies/community-standards/hate-speech/",
        "Privacy Violations": "https://transparency.meta.com/en-gb/policies/community-standards/privacy-violations-image-privacy-rights/",
        "Violent and Graphic Content": "https://transparency.meta.com/en-gb/policies/community-standards/violent-graphic-content/",
        "Account Integrity": "https://transparency.meta.com/en-gb/policies/community-standards/account-integrity",
        "Authentic Identity Representation": "https://transparency.meta.com/en-gb/policies/community-standards/authentic-identity-representation",
        "Cybersecurity": "https://transparency.meta.com/en-gb/policies/community-standards/cybersecurity/",
        "Inauthentic Behavior": "https://transparency.meta.com/en-gb/policies/community-standards/inauthentic-behavior/",
        "Memorialisation": "https://transparency.meta.com/en-gb/policies/community-standards/memorialization/",
        "Misinformation": "https://transparency.meta.com/en-gb/policies/community-standards/misinformation/",
        "Spam": "https://transparency.meta.com/en-gb/policies/community-standards/spam/",
        "Third-Party Intellectual Property Infringement": "https://transparency.meta.com/en-gb/policies/community-standards/intellectual-property/",
        "Using Meta Intellectual Property and Licences": "https://transparency.meta.com/en-gb/policies/community-standards/meta-intellectual-property",
        "Additional Protection of Minors": "https://transparency.meta.com/en-gb/policies/community-standards/additional-protection-minors/",
        "Locally Illegal Content, Products or Services": "https://transparency.meta.com/en-gb/policies/community-standards/locally-illegal-products-services",
        "User Requests": "https://transparency.meta.com/en-gb/policies/community-standards/user-requests/"
    }

@app.route(route="meta_scraper_storage", auth_level=func.AuthLevel.FUNCTION)
def meta_scraper_storage_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to scrape Meta Community Standards and save to storage.
    
    Query parameters:
    - sections: comma-separated list of section names to scrape (optional, default: all)
    - include_main: whether to include main page (default: true)
    - format: response format (json or summary, default: json)
    - save_to_storage: whether to save files to blob storage (default: true)
    - container_name: blob container name (default: meta-standards)
    """
    logging.info('Meta scraper with storage function triggered.')
    
    try:
        # Parse query parameters
        sections_param = req.params.get('sections')
        include_main = req.params.get('include_main', 'true').lower() == 'true'
        response_format = req.params.get('format', 'json').lower()
        save_to_storage = req.params.get('save_to_storage', 'true').lower() == 'true'
        container_name = req.params.get('container_name', 'meta-standards')
        
        # Initialize blob service client if saving to storage
        blob_service_client = None
        if save_to_storage:
            try:
                blob_service_client = get_blob_service_client()
            except Exception as e:
                logging.error(f"Failed to initialize blob storage: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": f"Storage initialization failed: {str(e)}"}),
                    status_code=500,
                    mimetype="application/json"
                )
        
        # Perform the scraping operation
        results = perform_scraping_operation(
            blob_service_client=blob_service_client,
            container_name=container_name,
            sections_param=sections_param,
            include_main=include_main,
            save_to_storage=save_to_storage,
            response_format=response_format
        )
        
        # Format response based on requested format
        if response_format == 'summary':
            # Return summary only
            summary = {
                'session_info': results['scraping_session'],
                'storage_urls': results['storage_urls'],
                'sections_summary': {}
            }
            
            if include_main and 'main_page' in results['data']:
                summary['main_page_summary'] = {
                    'status': results['data']['main_page']['metadata']['status'],
                    'character_count': results['data']['main_page']['statistics']['character_count'],
                    'word_count': results['data']['main_page']['statistics']['word_count']
                }
            
            for section_name, content in results['data'].get('sections', {}).items():
                summary['sections_summary'][section_name] = {
                    'status': content['metadata']['status'],
                    'character_count': content['statistics']['character_count'],
                    'word_count': content['statistics']['word_count'],
                    'paragraph_count': content['statistics']['paragraph_count'],
                    'heading_count': content['statistics']['heading_count']
                }
            
            response_data = summary
        else:
            # Return full data
            response_data = results
        
        logging.info(f"Scraping completed. Success rate: {results['scraping_session']['success_rate']:.1f}%")
        
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in meta_scraper_storage_function: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

# Keep the original functions for backward compatibility
@app.route(route="meta_scraper", auth_level=func.AuthLevel.FUNCTION)
def meta_scraper_function(req: func.HttpRequest) -> func.HttpResponse:
    """Original function without storage - for backward compatibility"""
    # Redirect to storage function with save_to_storage=false
    from urllib.parse import urlencode, parse_qs
    
    params = dict(req.params)
    params['save_to_storage'] = 'false'
    
    # Create a new request-like object
    class MockRequest:
        def __init__(self, params):
            self.params = params
    
    mock_req = MockRequest(params)
    return meta_scraper_storage_function(mock_req)

@app.route(route="meta_scraper_single", auth_level=func.AuthLevel.FUNCTION)
def meta_scraper_single_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to scrape a single Meta Community Standards section and optionally save to storage.
    
    Query parameters:
    - section: section name to scrape (required)
    - url: custom URL to scrape (optional, overrides predefined URLs)
    - save_to_storage: whether to save file to blob storage (default: false)
    - container_name: blob container name (default: meta-standards)
    """
    logging.info('Meta single scraper function triggered.')
    
    try:
        # Parse query parameters
        section_name = req.params.get('section')
        custom_url = req.params.get('url')
        save_to_storage = req.params.get('save_to_storage', 'false').lower() == 'true'
        container_name = req.params.get('container_name', 'meta-standards')
        
        if not section_name:
            return func.HttpResponse(
                json.dumps({"error": "Section parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Determine URL to scrape
        if custom_url:
            url = custom_url
        else:
            all_sections = get_section_urls()
            if section_name not in all_sections:
                available_sections = list(all_sections.keys())
                return func.HttpResponse(
                    json.dumps({
                        "error": f"Section '{section_name}' not found",
                        "available_sections": available_sections
                    }),
                    status_code=400,
                    mimetype="application/json"
                )
            url = all_sections[section_name]
        
        # Setup session
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Initialize blob service client if saving to storage
        blob_service_client = None
        storage_url = None
        if save_to_storage:
            try:
                blob_service_client = get_blob_service_client()
            except Exception as e:
                logging.error(f"Failed to initialize blob storage: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": f"Storage initialization failed: {str(e)}"}),
                    status_code=500,
                    mimetype="application/json"
                )
        
        # Scrape the section
        logging.info(f"Scraping: {section_name} from {url}")
        soup = get_page_content(url, session)
        content = extract_content_json(soup, section_name, url)
        
        # Save to storage if enabled
        if save_to_storage and blob_service_client:
            try:
                # Create safe filename
                safe_filename = re.sub(r'[^\w\s-]', '', section_name)
                safe_filename = re.sub(r'[-\s]+', '_', safe_filename).strip('_')
                blob_name = f"single_sections/{safe_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                storage_url = save_to_blob_storage(
                    blob_service_client,
                    container_name,
                    blob_name,
                    json.dumps(content, ensure_ascii=False, indent=2)
                )
                logging.info(f"Saved {section_name} to blob storage")
            except Exception as e:
                logging.error(f"Failed to save {section_name} to storage: {str(e)}")
        
        # Add session metadata
        response_data = {
            'scraping_session': {
                'timestamp': datetime.now().isoformat(),
                'section_name': section_name,
                'url': url,
                'status': content['metadata']['status'],
                'save_to_storage': save_to_storage,
                'container_name': container_name if save_to_storage else None,
                'storage_url': storage_url
            },
            'data': content
        }
        
        status_code = 200 if content['metadata']['status'] == 'success' else 500
        
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False, indent=2),
            status_code=status_code,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in meta_scraper_single_function: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
