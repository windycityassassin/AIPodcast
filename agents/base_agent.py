from abc import ABC, abstractmethod
import os
import requests
from typing import Dict, List, Optional

class BaseAgent(ABC):
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("Deepseek API key is required")
    
    def deepseek_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """Get completion from Deepseek API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": 2000
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"Error in Deepseek API call: {str(e)}")
            return ""
    
    @abstractmethod
    def process(self, *args, **kwargs):
        """Process the agent's specific task"""
        pass
