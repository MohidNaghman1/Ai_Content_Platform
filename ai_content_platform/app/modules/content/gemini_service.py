
from google import genai
import asyncio

class GeminiService:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

        

    async def generate_streaming_text(
        self,
        prompt: str,
        model: str = "models/gemini-2.5-flash"
    ):
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            if hasattr(response, "text") and response.text:
                # Simulate async streaming by yielding chunks with a small delay
                for chunk in response.text.split('.'):
                    chunk = chunk.strip()
                    if chunk:
                        await asyncio.sleep(0.02)  # Simulate network/streaming delay
                        yield chunk + '.'
            else:
                raise ValueError("Invalid response from Gemini API.")
        except Exception as e:
            raise RuntimeError(f"GeminiService streaming error: {str(e)}")
        

    async def generate_text(self, prompt: str, model: str = "models/gemini-2.5-flash"):
        """
        Non-streaming LLM call for summary generation.
        """
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            if hasattr(response, "text") and response.text:
                return response.text
            else:
                raise ValueError("Invalid response from Gemini API.")
        except Exception as e:
            raise RuntimeError(f"GeminiService error: {str(e)}")