"""
Meta Community Standards Scraper - JSON Output Version

This version saves all content as structured JSON files in a separate directory.
Each section gets its own JSON file plus a master summary file.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
from urllib.parse import urljoin
from datetime import datetime

def get_page_content(url, session):
    """Fetch page content with error handling"""
    try:
        print(f"Fetching: {url}")
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            print(f"HTTP {response.status_code} for {url}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_content_json(soup, section_name, url):
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

def main():
    # Correct URLs based on the actual Meta site structure
    section_urls = {
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
    
    # Setup session with minimal headers that work
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = "https://transparency.meta.com/en-gb/policies/community-standards/"
    
    # Create output directory
    output_dir = "meta_standards_json"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # First, scrape the main page
    print("Scraping main community standards page...")
    main_soup = get_page_content(base_url, session)
    
    # Process main page
    main_content = extract_content_json(main_soup, "Main Page", base_url)
    
    # Save main page JSON
    main_filename = os.path.join(output_dir, "00_main_page.json")
    with open(main_filename, 'w', encoding='utf-8') as f:
        json.dump(main_content, f, indent=2, ensure_ascii=False)
    print(f"Saved main page to {main_filename}")
    
    # Results for summary
    results = {
        'scraping_session': {
            'timestamp': datetime.now().isoformat(),
            'total_sections': len(section_urls),
            'successful_sections': 0,
            'failed_sections': 0,
            'success_rate': 0.0
        },
        'main_page': {
            'filename': '00_main_page.json',
            'status': main_content['metadata']['status'],
            'character_count': main_content['statistics']['character_count']
        },
        'sections': {}
    }
    
    # Scrape each section
    successful = 0
    for i, (section_name, url) in enumerate(section_urls.items(), 1):
        print(f"\n--- Scraping: {section_name} ---")
        
        soup = get_page_content(url, session)
        content = extract_content_json(soup, section_name, url)
        
        # Create safe filename
        safe_filename = re.sub(r'[^\w\s-]', '', section_name)
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename).strip('_')
        filename = f"{i:02d}_{safe_filename}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Save individual JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        # Update results
        if content['metadata']['status'] == 'success' and content['statistics']['character_count'] > 200:
            print(f"✓ Successfully scraped {section_name}")
            successful += 1
            status = 'success'
        else:
            print(f"✗ Failed to scrape {section_name}")
            status = 'failed'
        
        results['sections'][section_name] = {
            'filename': filename,
            'status': status,
            'character_count': content['statistics']['character_count'],
            'word_count': content['statistics']['word_count'],
            'paragraph_count': content['statistics']['paragraph_count'],
            'heading_count': content['statistics']['heading_count']
        }
        
        print(f"Saved {section_name} to {filepath}")
        time.sleep(2)  # Delay between sections
    
    # Update final statistics
    results['scraping_session']['successful_sections'] = successful
    results['scraping_session']['failed_sections'] = len(section_urls) - successful
    results['scraping_session']['success_rate'] = (successful / len(section_urls)) * 100
    
    # Save master summary JSON
    summary_filename = os.path.join(output_dir, "master_summary.json")
    with open(summary_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Create human-readable summary
    summary_text_filename = os.path.join(output_dir, "summary_report.txt")
    with open(summary_text_filename, 'w', encoding='utf-8') as f:
        f.write("META COMMUNITY STANDARDS JSON SCRAPING REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Scraping completed: {results['scraping_session']['timestamp']}\n")
        f.write(f"Total sections attempted: {results['scraping_session']['total_sections']}\n")
        f.write(f"Successfully scraped: {results['scraping_session']['successful_sections']}\n")
        f.write(f"Failed: {results['scraping_session']['failed_sections']}\n")
        f.write(f"Success rate: {results['scraping_session']['success_rate']:.1f}%\n\n")
        
        f.write("MAIN PAGE:\n")
        f.write("-" * 30 + "\n")
        f.write(f"File: {results['main_page']['filename']}\n")
        f.write(f"Status: {results['main_page']['status']}\n")
        f.write(f"Characters: {results['main_page']['character_count']:,}\n\n")
        
        f.write("SUCCESSFUL SECTIONS:\n")
        f.write("-" * 30 + "\n")
        for section_name, info in results['sections'].items():
            if info['status'] == 'success':
                f.write(f"✓ {section_name}\n")
                f.write(f"  File: {info['filename']}\n")
                f.write(f"  Characters: {info['character_count']:,}\n")
                f.write(f"  Words: {info['word_count']:,}\n")
                f.write(f"  Paragraphs: {info['paragraph_count']}\n")
                f.write(f"  Headings: {info['heading_count']}\n\n")
        
        f.write("FAILED SECTIONS:\n")
        f.write("-" * 30 + "\n")
        for section_name, info in results['sections'].items():
            if info['status'] == 'failed':
                f.write(f"✗ {section_name}\n")
                f.write(f"  File: {info['filename']}\n")
                f.write(f"  Characters: {info['character_count']:,}\n\n")
        
        f.write("FILE STRUCTURE:\n")
        f.write("-" * 30 + "\n")
        f.write("JSON files are structured with:\n")
        f.write("- metadata: Section info, URL, scraping timestamp, status\n")
        f.write("- content: Title, raw text, structured content (headings, paragraphs, lists, links)\n")
        f.write("- statistics: Character count, word count, paragraph count, heading count\n")
    
    print(f"\n=== JSON SCRAPING SUMMARY ===")
    print(f"Total sections attempted: {len(section_urls)}")
    print(f"Successfully scraped: {successful}")
    print(f"Failed: {len(section_urls) - successful}")
    print(f"Success rate: {(successful/len(section_urls)*100):.1f}%")
    print(f"Results saved to {output_dir}/ directory")
    print(f"- Master summary: {output_dir}/master_summary.json")
    print(f"- Text summary: {output_dir}/summary_report.txt")
    print(f"- Individual JSON files: {output_dir}/01_*.json to {len(section_urls):02d}_*.json")
    print(f"- Main page: {output_dir}/00_main_page.json")

if __name__ == "__main__":
    main()
