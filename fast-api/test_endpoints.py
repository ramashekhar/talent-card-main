import requests
import sys

def test_endpoints():
    base_url = "http://localhost:8000"
    
    print("Testing FastAPI endpoints...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Message: {response.json().get('message', 'N/A')}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test HTML employee page
    try:
        response = requests.get(f"{base_url}/employee/101")
        print(f"✅ HTML employee page: {response.status_code}")
        print(f"   Content type: {response.headers.get('content-type')}")
        print(f"   Contains employee name: {'John Doe' in response.text}")
    except Exception as e:
        print(f"❌ HTML employee page failed: {e}")
    
    # Test PDF generation (expect it to fail locally without wkhtmltopdf)
    try:
        response = requests.get(f"{base_url}/employee/101?format=pdf")
        if response.status_code == 500:
            print(f"⚠️  PDF generation failed as expected: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'N/A')}")
        else:
            print(f"✅ PDF generation worked: {response.status_code}")
            print(f"   Content type: {response.headers.get('content-type')}")
    except Exception as e:
        print(f"❌ PDF test failed: {e}")
    
    return True

if __name__ == "__main__":
    test_endpoints()