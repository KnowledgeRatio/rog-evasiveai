"""
Meta Community Standards Scraper - Azure Function Version

This version is adapted to run as an Azure Function, returning JSON data
instead of saving to local files.
"""

import azure.functions as func
import requests
from bs4 import BeautifulSoup
import json
import re
import logging
from datetime import datetime
from typing import Dict, Any

app = func.FunctionApp()

def get_page_content(url: str, session: requests.Session) -> BeautifulSoup:
    """Fetch page content with error handling"""
    try:
        logging.info(f"Fetching: {url}")
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
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

@app.route(route="meta_scraper", auth_level=func.AuthLevel.FUNCTION)
def meta_scraper_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to scrape Meta Community Standards.
    
    Query parameters:
    - sections: comma-separated list of section names to scrape (optional, default: all)
    - include_main: whether to include main page (default: true)
    - format: response format (json or summary, default: json)
    """
    logging.info('Meta scraper function triggered.')
    
    try:
        # Parse query parameters
        sections_param = req.params.get('sections')
        include_main = req.params.get('include_main', 'true').lower() == 'true'
        response_format = req.params.get('format', 'json').lower()
        
        # Get all available sections
        all_sections = get_section_urls()
        
        # Determine which sections to scrape
        if sections_param:
            requested_sections = [s.strip() for s in sections_param.split(',')]
            section_urls = {name: url for name, url in all_sections.items() 
                           if name in requested_sections}
            if not section_urls:
                return func.HttpResponse(
                    json.dumps({"error": "No valid sections found in request"}),
                    status_code=400,
                    mimetype="application/json"
                )
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
                'include_main_page': include_main
            },
            'data': {}
        }
        
        # Scrape main page if requested
        if include_main:
            logging.info("Scraping main community standards page...")
            base_url = "https://transparency.meta.com/en-gb/policies/community-standards/"
            main_soup = get_page_content(base_url, session)
            main_content = extract_content_json(main_soup, "Main Page", base_url)
            results['data']['main_page'] = main_content
        
        # Scrape each section
        successful = 0
        results['data']['sections'] = {}
        
        for section_name, url in section_urls.items():
            logging.info(f"Scraping: {section_name}")
            
            soup = get_page_content(url, session)
            content = extract_content_json(soup, section_name, url)
            
            # Store the content
            results['data']['sections'][section_name] = content
            
            # Track success/failure
            if content['metadata']['status'] == 'success' and content['statistics']['character_count'] > 200:
                logging.info(f"Successfully scraped {section_name}")
                successful += 1
            else:
                logging.warning(f"Failed to scrape {section_name}")
        
        # Update final statistics
        results['scraping_session']['successful_sections'] = successful
        results['scraping_session']['failed_sections'] = len(section_urls) - successful
        results['scraping_session']['success_rate'] = (successful / len(section_urls)) * 100 if section_urls else 0
        
        # Format response based on requested format
        if response_format == 'summary':
            # Return summary only
            summary = {
                'session_info': results['scraping_session'],
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
        logging.error(f"Error in meta_scraper_function: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="meta_scraper_single", auth_level=func.AuthLevel.FUNCTION)
def meta_scraper_single_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to scrape a single Meta Community Standards section.
    
    Query parameters:
    - section: section name to scrape (required)
    - url: custom URL to scrape (optional, overrides predefined URLs)
    """
    logging.info('Meta single scraper function triggered.')
    
    try:
        # Parse query parameters
        section_name = req.params.get('section')
        custom_url = req.params.get('url')
        
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
        
        # Scrape the section
        logging.info(f"Scraping: {section_name} from {url}")
        soup = get_page_content(url, session)
        content = extract_content_json(soup, section_name, url)
        
        # Add session metadata
        response_data = {
            'scraping_session': {
                'timestamp': datetime.now().isoformat(),
                'section_name': section_name,
                'url': url,
                'status': content['metadata']['status']
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
