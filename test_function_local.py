"""
Local test script for Meta Community Standards Azure Function
Tests the function endpoints without requiring deployment
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from azure.storage.blob import BlobServiceClient

def test_function_endpoint(base_url, endpoint, params=None, timeout=300):
    """Test a specific function endpoint"""
    url = f"{base_url}/api/{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing endpoint: {endpoint}")
    print(f"URL: {url}")
    if params:
        print(f"Parameters: {params}")
    print(f"{'='*60}")
    
    try:
        print("Sending request...")
        start_time = time.time()
        
        response = requests.get(url, params=params, timeout=timeout)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Response received in {duration:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✓ Response is valid JSON")
                
                # Print summary information
                if 'scraping_session' in data:
                    session_info = data['scraping_session']
                    print(f"  Total sections: {session_info.get('total_sections', 'Unknown')}")
                    print(f"  Successful: {session_info.get('successful_sections', 'Unknown')}")
                    print(f"  Failed: {session_info.get('failed_sections', 'Unknown')}")
                    print(f"  Success rate: {session_info.get('success_rate', 'Unknown')}%")
                    
                    if session_info.get('save_to_storage'):
                        print(f"  Storage container: {session_info.get('container_name', 'Unknown')}")
                        storage_urls = data.get('storage_urls', {})
                        print(f"  Files saved to storage: {len(storage_urls)}")
                
                return True, data
                
            except json.JSONDecodeError:
                print("✗ Response is not valid JSON")
                print(f"Response content: {response.text[:500]}...")
                return False, response.text
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except requests.Timeout:
        print(f"✗ Request timed out after {timeout} seconds")
        return False, None
    except requests.RequestException as e:
        print(f"✗ Request failed: {e}")
        return False, None

def test_blob_storage_access():
    """Test if we can access blob storage locally"""
    print(f"\n{'='*60}")
    print("Testing Azure Blob Storage Access")
    print(f"{'='*60}")
    
    try:
        # Try to connect to development storage
        connection_string = "UseDevelopmentStorage=true"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Try to list containers (this will test connection)
        containers = list(blob_service_client.list_containers())
        print(f"✓ Connected to development storage")
        print(f"  Found {len(containers)} containers")
        
        return True
    except Exception as e:
        print(f"✗ Failed to connect to development storage: {e}")
        print("Note: Make sure Azure Storage Emulator/Azurite is running")
        return False

def main():
    print("META COMMUNITY STANDARDS AZURE FUNCTION - LOCAL TESTING")
    print("=" * 80)
    
    # Configuration
    base_url = "http://localhost:7071"  # Default Azure Functions local URL
    
    print(f"Function app base URL: {base_url}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Test storage access first
    storage_ok = test_blob_storage_access()
    
    print(f"\n{'='*60}")
    print("Available Test Scenarios")
    print(f"{'='*60}")
    print("1. Test single section scraping (fast)")
    print("2. Test multiple specific sections")
    print("3. Test all sections with storage (slow)")
    print("4. Test summary format response")
    print("5. Test all sections without storage")
    print("6. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                # Test single section
                params = {
                    'section': 'Spam',
                    'save_to_storage': 'true' if storage_ok else 'false'
                }
                success, data = test_function_endpoint(base_url, "meta_scraper_single", params, 60)
                
            elif choice == '2':
                # Test specific sections
                params = {
                    'sections': 'Spam,Misinformation,Cybersecurity',
                    'format': 'summary',
                    'save_to_storage': 'true' if storage_ok else 'false'
                }
                success, data = test_function_endpoint(base_url, "meta_scraper_storage", params, 120)
                
            elif choice == '3':
                # Test all sections with storage (this will take a long time!)
                print("WARNING: This will scrape ALL sections and may take 5-10 minutes!")
                confirm = input("Are you sure? (y/N): ").strip().lower()
                if confirm == 'y':
                    params = {
                        'save_to_storage': 'true' if storage_ok else 'false',
                        'format': 'summary'
                    }
                    success, data = test_function_endpoint(base_url, "meta_scraper_storage", params, 600)
                else:
                    print("Test cancelled")
                    continue
                    
            elif choice == '4':
                # Test summary format
                params = {
                    'sections': 'Spam,Misinformation',
                    'format': 'summary',
                    'save_to_storage': 'false'
                }
                success, data = test_function_endpoint(base_url, "meta_scraper_storage", params, 120)
                
            elif choice == '5':
                # Test all sections without storage
                print("WARNING: This will scrape ALL sections without storage (faster but still takes time)")
                confirm = input("Continue? (y/N): ").strip().lower()
                if confirm == 'y':
                    params = {
                        'save_to_storage': 'false',
                        'format': 'summary'
                    }
                    success, data = test_function_endpoint(base_url, "meta_scraper_storage", params, 600)
                else:
                    print("Test cancelled")
                    continue
                    
            elif choice == '6':
                print("Exiting...")
                break
                
            else:
                print("Invalid choice. Please enter 1-6.")
                continue
                
            # Ask if user wants to save the response
            if success and data:
                save_response = input("\nSave response to file? (y/N): ").strip().lower()
                if save_response == 'y':
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"test_response_{choice}_{timestamp}.json"
                    filepath = os.path.join(os.getcwd(), filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    print(f"Response saved to: {filepath}")
                    
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            break
        except Exception as e:
            print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()
