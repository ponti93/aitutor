import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://127.0.0.1:5000"

def test_download_endpoint():
    """Test the download document endpoint"""
    print("🧪 Testing Download Endpoint...")
    
    # First, we need to login and get a document ID
    # For now, let's just test if the endpoint exists
    try:
        response = requests.get(f"{BASE_URL}/download_document/1")
        print(f"📥 Download endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Download endpoint is working!")
        else:
            print(f"❌ Download endpoint returned: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Download endpoint test failed: {str(e)}")

def test_delete_endpoint():
    """Test the delete document endpoint"""
    print("\n🧪 Testing Delete Endpoint...")
    
    try:
        response = requests.delete(f"{BASE_URL}/delete_document/1")
        print(f"🗑️ Delete endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Delete endpoint is working!")
        else:
            print(f"❌ Delete endpoint returned: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Delete endpoint test failed: {str(e)}")

def check_app_status():
    """Check if the application is running"""
    print("🔍 Checking Application Status...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"🏠 App status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Application is running!")
        else:
            print(f"❌ Application returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Application is not accessible: {str(e)}")
        print("💡 Make sure the Flask app is running on http://127.0.0.1:5000")

if __name__ == '__main__':
    print("🚀 Testing AI Tutor Library Features")
    print("=" * 50)
    
    check_app_status()
    test_download_endpoint()
    test_delete_endpoint()
    
    print("\n📋 Summary:")
    print("- Download button should now work directly via the link")
    print("- Delete button should show confirmation modal")
    print("- Processing status badges should display document status")
    print("- All old View/Analyze buttons have been removed")
