import os
from dotenv import load_dotenv
from src.core.ai_generator import GeminiEmailGenerator

# Mock resume context
resume_text = """
Name: John Doe
Email: john.doe@example.com
Phone: +1-555-0123
LinkedIn: linkedin.com/in/johndoe
Skills: Python, Machine Learning, FastAPI
Experience: AI Intern at Tech Corp (2023)
"""

def test_prompt():
    print("Testing AI Generator with Context...")
    try:
        generator = GeminiEmailGenerator()
        response = generator.generate_email(
            user_prompt="Write an email applying for a Senior ML Engineer role.",
            context_text=resume_text
        )
        print("\n[SUCCESS] Generation Successful!")
        print(f"Subject: {response['subject']}")
        print("Body Preview:")
        print(response['body'][:500] + "...")
        
        # Check for signature formatting
        if "<br>" in response['body'] and "John Doe" in response['body']:
            print("\n[PASS] Signature formatting check passed (contains <br> and Name).")
        else:
            print("\n[WARN] Signature formatting check warning: Might not be formatted correctly.")
            
    except Exception as e:
        print(f"\n[FAIL] Test Failed: {e}")

if __name__ == "__main__":
    test_prompt()
