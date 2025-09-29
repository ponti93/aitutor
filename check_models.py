import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_available_models():
    """Check available models for the current API key"""
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # List available models
        print("🔍 Checking available models...")
        models = genai.list_models()
        
        print(f"\n✅ Found {len(list(models))} available models:")
        print("-" * 80)
        
        for model in models:
            print(f"📋 Model: {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description}")
            print(f"   Supported Methods: {model.supported_generation_methods}")
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Error checking models: {str(e)}")

def test_model_connection():
    """Test connection with the current model configuration"""
    api_key = os.environ.get('GEMINI_API_KEY')
    model_name = os.environ.get('GEMINI_MODEL', 'gemini-1.0-pro')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        print(f"🔧 Testing connection with model: {model_name}")
        
        # Try to create the model
        model = genai.GenerativeModel(model_name)
        
        # Test a simple prompt
        response = model.generate_content("Hello, are you working?")
        
        print(f"✅ Model connection successful!")
        print(f"📝 Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Model connection failed: {str(e)}")

if __name__ == '__main__':
    print("🤖 Gemini AI Model Checker")
    print("=" * 50)
    
    check_available_models()
    print("\n" + "=" * 50)
    test_model_connection()
