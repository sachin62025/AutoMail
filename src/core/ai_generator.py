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
        # --- FIX: Updated model to a stable one ---
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')

    def generate_email(self, user_prompt: str, context_text: str = "") -> Dict[str, str]:
        """
        Generates an email subject and body based on a single user prompt and optional context.

        Args:
            user_prompt (str): The user's natural language request for the email.
            context_text (str): Optional text content from a resume or other document.

        Returns:
            Dict[str, str]: A dictionary with 'subject' and 'body' keys.
        """
        # --- NEW: A much more robust prompt that lets the AI figure out the details ---
        context_section = ""
        if context_text:
            context_section = f"""
            **Additional Context (e.g., User's Resume/Info):**
            "{context_text}"
            
            Use this context to personalize the email (e.g., mention specific skills, experience, or contact info if relevant).
            """

        prompt = f"""
        You are an expert email writing assistant. Analyze the following user request and generate a professional email subject and body.

        **User Request:**
        "{user_prompt}"

        {context_section}

        **Your Task:**
        1. **Analyze & Synthesize**: From the user's request and provided context (if any), deduce the tone, recipient, sender, and primary goal. Do NOT just copy-paste lists from the resume. Select the most relevant skills and experiences that align with the specific goal of the email.
        2. **Drafting**: Write a compelling, natural-sounding, and ready-to-send subject and email body.
        3. **Formatting**: 
           - The body MUST be formatted in clean HTML.
           - Use `<p>` for paragraphs.
           - **CRITICAL**: Format the signature block professionally. Put the Name, Phone, Email, and Links on **separate lines** using `<br>`. Do not clump them together.
           - Example Signature:
             <p>Sincerely,<br>
             [Name]<br>
             [Phone]<br>
             [Email]<br>
             [Link 1] | [Link 2]</p>
        4. **Output**: Return your response as a single, minified JSON object with two keys: "subject" and "body".
        5. Do not include any text, markdown, or code block formatting like ```json before or after the JSON object itself. Just the raw JSON.

        **Example JSON Output:**
        {{"subject": "Inquiry Regarding AI/ML Internship Opportunities", "body": "<p>Dear Hiring Manager,</p><p>I hope you're doing well...</p><p>Sincerely,<br>John Doe<br>555-0123<br>john@example.com</p>"}}
        """

        try:
            response = self.model.generate_content(prompt)
            # Clean up the response to ensure it's valid JSON
            cleaned_response = response.text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            cleaned_response = cleaned_response.strip()
            
            # Parse the JSON string into a Python dictionary
            email_content = json.loads(cleaned_response)
            
            if "subject" not in email_content or "body" not in email_content:
                raise ValueError("AI response did not contain 'subject' or 'body' keys.")
                
            return email_content

        except json.JSONDecodeError:
            raise RuntimeError(f"Failed to decode the AI's JSON response. The response was: {cleaned_response}")
        except Exception as e:
            raise RuntimeError(f"An error occurred with the Gemini API: {e}")