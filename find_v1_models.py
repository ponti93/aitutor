import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def find_v1_models():
    """Find models that work with API v1"""
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        print("🔍 Finding models that work with API v1...")
        models = genai.list_models()
        
        # Common v1 model names
        v1_model_patterns = ['gemini-pro', 'models/gemini-pro']
        
        working_models = []
        
        for model in models:
            model_name = model.name
            # Check if it's a v1 model
            if any(pattern in model_name for pattern in v1_model_patterns):
                if 'generateContent' in model.supported_generation_methods:
                    working_models.append(model)
                    print(f"✅ Found working v1 model: {model_name}")
                    print(f"   Display Name: {model.display_name}")
                    print(f"   Supported Methods: {model.supported_generation_methods}")
                    print("-" * 80)
        
        if not working_models:
            print("❌ No working v1 models found. Available models:")
            for model in models:
                print(f"📋 Model: {model.name}")
                print(f"   Supported Methods: {model.supported_generation_methods}")
                print("-" * 80)
        
        return working_models
        
    except Exception as e:
        print(f"❌ Error finding models: {str(e)}")

def test_v1_model(model_name):
    """Test a specific model with v1 API"""
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        print(f"🔧 Testing v1 model: {model_name}")
        
        # Try to create the model
        model = genai.GenerativeModel(model_name)
        
        # Test a simple prompt
        response = model.generate_content("Hello, are you working with v1 API?")
        
        print(f"✅ v1 Model connection successful!")
        print(f"📝 Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ v1 Model connection failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("🤖 Gemini AI v1 Model Finder")
    print("=" * 50)
    
    working_models = find_v1_models()
    
    if working_models:
        print("\n🧪 Testing the first working model...")
        test_v1_model(working_models[0].name)
