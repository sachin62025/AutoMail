import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file
load_dotenv()

# Configure API key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# The model you want to check
model_to_check = 'models/gemini-2.0-flash-thinking-exp-01-21'
# 'models/gemini-2.0-flash-thinking-exp-01-21'
# List all available models
available_models = list(genai.list_models())

# Check if model exists
found = False
for model in available_models:
    # model.name has the full identifier, e.g., 'models/gemini-2.0-flash-thinking-exp-01-21'
    if model_to_check in model.name:
        found = True
        print(f"Model '{model_to_check}' is available: {model.name}")
        break

if not found:
    print(f"Model '{model_to_check}' is NOT available in your API.")
