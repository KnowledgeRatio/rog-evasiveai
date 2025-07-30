"""
Test script for the Azure Function Meta Scraper
Run this to test the function locally before deployment
"""

import requests
import json
import time

# Local development URL (when running 'func start')
BASE_URL = "http://localhost:7071/api"

def test_function_endpoints():
    """Test both function endpoints"""
    
    print("Testing Azure Function Meta Scraper")
    print("=" * 50)
    
    # Test 1: Single section scraper
    print("\n1. Testing single section scraper...")
    try:
        response = requests.get(f"{BASE_URL}/meta_scraper_single?section=Spam", timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Single section test passed")
            print(f"  Section: {data['data']['metadata']['section_name']}")
            print(f"  Status: {data['data']['metadata']['status']}")
            print(f"  Characters: {data['data']['statistics']['character_count']:,}")
        else:
            print(f"✗ Single section test failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Single section test error: {e}")
    
    # Test 2: Multiple sections with summary format
    print("\n2. Testing multiple sections (summary format)...")
    try:
        response = requests.get(f"{BASE_URL}/meta_scraper?sections=Spam,Misinformation&format=summary", timeout=120)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Multiple sections test passed")
            print(f"  Total sections: {data['session_info']['total_sections']}")
            print(f"  Successful: {data['session_info']['successful_sections']}")
            print(f"  Success rate: {data['session_info']['success_rate']:.1f}%")
            for section, stats in data['sections_summary'].items():
                print(f"  {section}: {stats['character_count']:,} chars, {stats['status']}")
        else:
            print(f"✗ Multiple sections test failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Multiple sections test error: {e}")
    
    # Test 3: Error handling - invalid section
    print("\n3. Testing error handling...")
    try:
        response = requests.get(f"{BASE_URL}/meta_scraper_single?section=InvalidSection")
        if response.status_code == 400:
            print(f"✓ Error handling test passed")
            print(f"  Correctly returned 400 for invalid section")
        else:
            print(f"✗ Error handling test failed: Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"✗ Error handling test error: {e}")
    
    print("\n" + "=" * 50)
    print("Testing completed!")
    print("\nTo run the function locally:")
    print("1. Open terminal in the project directory")
    print("2. Run: func start")
    print("3. Test endpoints at http://localhost:7071/api/")

def test_available_sections():
    """Test getting available sections"""
    try:
        response = requests.get(f"{BASE_URL}/meta_scraper_single?section=")
        if response.status_code == 400:
            data = response.json()
            if 'available_sections' in data:
                print("\nAvailable sections:")
                for i, section in enumerate(data['available_sections'], 1):
                    print(f"{i:2}. {section}")
    except Exception as e:
        print(f"Could not get available sections: {e}")

if __name__ == "__main__":
    print("Make sure to run 'func start' in another terminal first!")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    test_function_endpoints()
    test_available_sections()
