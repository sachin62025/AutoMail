# src/core/ai_generator.py

import os
import json
import google.generativeai as genai
from typing import Dict
from dotenv import load_dotenv
class GeminiEmailGenerator:
    """
    A class to handle email content generation using the Gemini API.
    """
    def __init__(self):
        """
        Initializes the Gemini model.
        """
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        # --- FIX: Updated model to a current and powerful one ---
        self.model = genai.GenerativeModel('models/gemini-2.0-flash-thinking-exp')

    def generate_email(self, user_prompt: str) -> Dict[str, str]:
        """
        Generates an email subject and body based on a single user prompt.

        Args:
            user_prompt (str): The user's natural language request for the email.

        Returns:
            Dict[str, str]: A dictionary with 'subject' and 'body' keys.
        """
        # --- NEW: A much more robust prompt that lets the AI figure out the details ---
        prompt = f"""
        You are an expert email writing assistant. Analyze the following user request and generate a professional email subject and body.

        **User Request:**
        "{user_prompt}"

        **Your Task:**
        1. From the user's request, deduce the tone, recipient, sender, and primary goal.
        2. Write a compelling, ready-to-send subject and a complete email body.
        3. The body MUST be formatted in clean HTML, using `<p>` for paragraphs and `<br>` for line breaks where appropriate (e.g., in signatures).
        4. **Crucially, you must return your response as a single, minified JSON object** with two keys: "subject" and "body".
        5. Do not include any text, markdown, or code block formatting like ```json before or after the JSON object itself. Just the raw JSON.

        **Example JSON Output:**
        {{"subject": "Inquiry Regarding AI/ML Internship Opportunities", "body": "<p>Dear Hiring Manager,</p><p>I hope you're doing well...</p>"}}
        """

        try:
            response = self.model.generate_content(prompt)
            # Clean up the response to ensure it's valid JSON
            cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
            
            # Parse the JSON string into a Python dictionary
            email_content = json.loads(cleaned_response)
            
            if "subject" not in email_content or "body" not in email_content:
                raise ValueError("AI response did not contain 'subject' or 'body' keys.")
                
            return email_content

        except json.JSONDecodeError:
            raise RuntimeError(f"Failed to decode the AI's JSON response. The response was: {cleaned_response}")
        except Exception as e:
            raise RuntimeError(f"An error occurred with the Gemini API: {e}")