import google.generativeai as genai

# Set your Gemini API Key
GEMINI_API_KEY = 'AIzaSyDT5161mUjmkK8ywECD26_ZR3YaSjC-X4U'  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# List all available models
try:
    models = genai.list_models()
    print("Available Models:")
    for model in models:
        print(f"- Name: {model.name}")
        print(f"  Description: {model.description}")
        print(f"  Supported Methods: {model.supported_generation_methods}")
        print()
except Exception as e:
    print(f"Error: {e}")