"""
Test script to verify the Meta Community Standards scraper setup
"""

import sys
import importlib

def test_imports():
    """Test if all required packages are available"""
    required_packages = ['requests', 'bs4', 'json', 'time', 're', 'urllib']
    
    print("Testing package imports...")
    
    for package in required_packages:
        try:
            if package == 'bs4':
                import bs4
                print(f"✓ {package} (Beautiful Soup) - version {bs4.__version__}")
            elif package == 'urllib':
                import urllib.parse
                print(f"✓ {package}")
            else:
                module = importlib.import_module(package)
                if hasattr(module, '__version__'):
                    print(f"✓ {package} - version {module.__version__}")
                else:
                    print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package} - MISSING! Error: {e}")
            return False
    
    return True

def test_basic_functionality():
    """Test basic scraper functionality"""
    print("\nTesting basic functionality...")
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Test basic request
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Test with a simple page
        response = session.get('https://httpbin.org/html', timeout=10)
        if response.status_code == 200:
            print("✓ HTTP requests working")
        else:
            print(f"✗ HTTP request failed with status {response.status_code}")
            return False
        
        # Test Beautiful Soup parsing
        soup = BeautifulSoup(response.content, 'html.parser')
        if soup.find('h1'):
            print("✓ Beautiful Soup parsing working")
        else:
            print("✗ Beautiful Soup parsing failed")
            return False
        
        print("✓ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_meta_accessibility():
    """Test if Meta's community standards page is accessible"""
    print("\nTesting Meta site accessibility...")
    
    try:
        import requests
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        url = "https://transparency.meta.com/en-gb/policies/community-standards/"
        response = session.get(url, timeout=15)
        
        if response.status_code == 200:
            print(f"✓ Meta Community Standards page accessible (Status: {response.status_code})")
            print(f"  Content length: {len(response.content)} bytes")
            return True
        else:
            print(f"✗ Meta site returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Meta site accessibility test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("META COMMUNITY STANDARDS SCRAPER - SETUP TEST")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Package imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Basic functionality
    if test_basic_functionality():
        tests_passed += 1
    
    # Test 3: Meta site accessibility
    if test_meta_accessibility():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! Ready to run the scraper.")
        print("\nTo run the scraper:")
        print("  python simple_meta_scraper.py")
        print("  python meta_community_standards_scraper.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        if tests_passed == 0:
            print("\nTo install required packages:")
            print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()
