
# gemini_service.py
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_response(self, text: str) -> str:
        try:
            prompt = f"You are a friendly and supportive mental wellness assistant named MindEase. Respond to the following user message with empathy and support: \"{text}\""
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "I'm having a little trouble thinking right now. Could you try again?"
