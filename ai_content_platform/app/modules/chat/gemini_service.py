import os
from ai_content_platform.app.modules.content.gemini_service import GeminiService

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
gemini_service = GeminiService(api_key=GEMINI_API_KEY)
