import requests
import os

class OllamaService:
    def __init__(self):
        self.base_url = os.getenv('OLLAMA_HOST', 'http://ollama:11434')
    
    async def generate_response(self, prompt: str, model: str = "llama2"):
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            print(f"Error calling Ollama: {str(e)}")
            return None 