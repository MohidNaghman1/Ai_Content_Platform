from ai_content_platform.app.config import settings
from ai_content_platform.app.modules.content.gemini_service import GeminiService

GEMINI_API_KEY = settings.GEMINI_API_KEY
gemini_service = GeminiService(api_key=GEMINI_API_KEY)
