from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
from typing import List, Dict
from .base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    """Agent responsible for gathering and analyzing information"""
    
    def process(self, query: str, num_results: int = 5) -> List[Dict]:
        """Research a topic and return analyzed information"""
        # 1. Search for information
        results = self.search_topic(query, num_results)
        
        # 2. Extract and analyze content
        analyzed_data = []
        for result in results:
            content = self.extract_content(result['link'])
            if content:
                analysis = self.analyze_content(content, query)
                if analysis:
                    analyzed_data.append({
                        'source': result['link'],
                        'title': result['title'],
                        'analysis': analysis
                    })
        
        return analyzed_data
    
    def search_topic(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search DuckDuckGo for relevant information"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
            return results
        except Exception as e:
            print(f"Error in DuckDuckGo search: {str(e)}")
            return []

    def extract_content(self, url: str) -> str:
        """Extract main content from a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            return ' '.join(soup.stripped_strings)[:5000]
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return ""

    def analyze_content(self, content: str, topic: str) -> Dict:
        """Analyze content using AI"""
        try:
            prompt = f"""
            Analyze this content about "{topic}" and extract key information.
            Content: {content}
            
            Provide a JSON response with:
            {{
                "key_points": [main points],
                "facts": [verified facts],
                "statistics": [relevant statistics],
                "expert_opinions": [expert views],
                "trends": [current trends]
            }}
            """
            
            response = self.deepseek_completion(prompt)
            return eval(response)  # Convert string to dict
        except Exception as e:
            print(f"Error in content analysis: {str(e)}")
            return {}
