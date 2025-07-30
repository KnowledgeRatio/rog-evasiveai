"""
Test different URL patterns and approaches for Meta transparency site
"""

import requests
from urllib.parse import urljoin

def test_urls():
    test_urls = [
        "https://transparency.meta.com/",
        "https://transparency.meta.com/en-gb/",
        "https://transparency.meta.com/policies/",
        "https://transparency.meta.com/policies/community-standards/",
        "https://www.facebook.com/transparency/",
        "https://about.meta.com/policies/",
        "https://transparency.fb.com/",
        "https://transparency.facebook.com/"
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    })
    
    for url in test_urls:
        try:
            print(f"\nTesting: {url}")
            response = session.get(url, timeout=10, allow_redirects=True)
            print(f"Status: {response.status_code}")
            print(f"Final URL: {response.url}")
            
            if response.status_code == 200:
                print(f"Success! Content length: {len(response.content)}")
                # Check if it looks like the right page
                if "community standards" in response.text.lower():
                    print("✓ Found 'community standards' in content")
                if "transparency" in response.text.lower():
                    print("✓ Found 'transparency' in content")
            else:
                print(f"Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_urls()
