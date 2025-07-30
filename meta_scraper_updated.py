"""
Updated Meta Community Standards Scraper with correct URLs

This version uses the actual URLs found on the Meta Community Standards page.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
from urllib.parse import urljoin

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

def extract_content(soup, section_name):
    """Extract content from a page"""
    content = {
        'section_name': section_name,
        'title': '',
        'content': '',
        'url': ''
    }
    
    if not soup:
        return content
    
    # Extract title
    title = soup.find('h1')
    if title:
        content['title'] = title.get_text(strip=True)
    
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
        
        # Get text content
        content['content'] = main_content.get_text(separator='\n', strip=True)
    
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
    
    # First, scrape the main page
    print("Scraping main community standards page...")
    main_soup = get_page_content(base_url, session)
    
    results = {
        'main_page': extract_content(main_soup, "Main Page"),
        'sections': {}
    }
    results['main_page']['url'] = base_url
    
    # Scrape each section
    successful = 0
    for section_name, url in section_urls.items():
        print(f"\n--- Scraping: {section_name} ---")
        
        soup = get_page_content(url, session)
        if soup:
            content = extract_content(soup, section_name)
            content['url'] = url
            
            # Check if we got meaningful content
            if len(content['content']) > 200:  # Arbitrary threshold
                results['sections'][section_name] = content
                print(f"✓ Successfully scraped {section_name}")
                successful += 1
            else:
                print(f"Got content but it seems too short for {section_name}")
                results['sections'][section_name] = {
                    'section_name': section_name,
                    'title': content['title'],
                    'content': 'Content too short or empty',
                    'url': url
                }
        else:
            results['sections'][section_name] = {
                'section_name': section_name,
                'title': '',
                'content': 'Failed to scrape content',
                'url': url
            }
            print(f"✗ Failed to scrape {section_name}")
        
        time.sleep(2)  # Delay between sections
    
    # Create output directory
    import os
    output_dir = "meta_standards_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save main summary file
    with open(os.path.join(output_dir, 'meta_standards_summary.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Save main page to separate file
    main = results['main_page']
    main_filename = os.path.join(output_dir, "00_main_page.txt")
    with open(main_filename, 'w', encoding='utf-8') as f:
        f.write(f"META COMMUNITY STANDARDS - MAIN PAGE\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Title: {main['title']}\n")
        f.write(f"URL: {main['url']}\n")
        f.write(f"Content Length: {len(main['content'])} characters\n\n")
        f.write("FULL CONTENT:\n")
        f.write("-" * 50 + "\n")
        f.write(main['content'])
    
    # Save each section to separate files
    for i, (section_name, content) in enumerate(results['sections'].items(), 1):
        # Create safe filename
        safe_filename = re.sub(r'[^\w\s-]', '', section_name)
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename).strip('_')
        filename = os.path.join(output_dir, f"{i:02d}_{safe_filename}.txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"META COMMUNITY STANDARDS - {section_name.upper()}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Section: {section_name}\n")
            f.write(f"Title: {content['title']}\n")
            f.write(f"URL: {content['url']}\n")
            f.write(f"Content Length: {len(content['content'])} characters\n\n")
            
            if content['content'] and content['content'] not in ['Failed to scrape content', 'Content too short or empty']:
                f.write("FULL CONTENT:\n")
                f.write("-" * 50 + "\n")
                f.write(content['content'])
            else:
                f.write(f"STATUS: {content['content']}\n")
        
        print(f"Saved {section_name} to {filename}")
    
    # Create summary file
    summary_filename = os.path.join(output_dir, "summary.txt")
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write("META COMMUNITY STANDARDS SCRAPING SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total sections attempted: {len(section_urls)}\n")
        f.write(f"Successfully scraped: {successful}\n")
        f.write(f"Failed: {len(section_urls) - successful}\n")
        f.write(f"Success rate: {(successful/len(section_urls)*100):.1f}%\n\n")
        
        f.write("SUCCESSFUL SECTIONS:\n")
        f.write("-" * 30 + "\n")
        for section_name, content in results['sections'].items():
            if content['content'] not in ['Failed to scrape content', 'Content too short or empty']:
                f.write(f"✓ {section_name} ({len(content['content'])} chars)\n")
        
        f.write("\nFAILED SECTIONS:\n")
        f.write("-" * 30 + "\n")
        for section_name, content in results['sections'].items():
            if content['content'] in ['Failed to scrape content', 'Content too short or empty']:
                f.write(f"✗ {section_name} - {content['content']}\n")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total sections attempted: {len(section_urls)}")
    print(f"Successfully scraped: {successful}")
    print(f"Failed: {len(section_urls) - successful}")
    print(f"Success rate: {(successful/len(section_urls)*100):.1f}%")
    print(f"Results saved to {output_dir}/ directory")
    print(f"- Main summary: {output_dir}/meta_standards_summary.json")
    print(f"- Text summary: {output_dir}/summary.txt")
    print(f"- Individual files: {output_dir}/01_*.txt to {len(section_urls):02d}_*.txt")

if __name__ == "__main__":
    main()
