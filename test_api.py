import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    print("Testing Root Endpoint...")
    try:
        response = requests.get(BASE_URL + "/")
        if response.status_code == 200:
            print("✅ Root endpoint is accessible.")
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")

def test_ai_generation():
    print("\nTesting AI Generation Endpoint...")
    payload = {
        "prompt": "Write a short email to my boss asking for a leave on Friday."
    }
    try:
        response = requests.post(BASE_URL + "/api/generate-email", json=payload)
        if response.status_code == 200:
            data = response.json()
            if "subject" in data and "body" in data:
                print("✅ AI Generation successful.")
                print(f"   Subject: {data['subject']}")
            else:
                print("❌ AI Generation response missing keys.")
        else:
            print(f"❌ AI Generation failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ AI Generation test failed: {e}")

if __name__ == "__main__":
    print("⚠️ Make sure the server is running (uvicorn src.main:app --reload) before running this test.\n")
    test_root()
    test_ai_generation() # Uncomment if you have a valid API key set in .env
