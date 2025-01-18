from typing import Dict
from .base_agent import BaseAgent

class ShowNotesAgent(BaseAgent):
    """Agent responsible for creating comprehensive show notes"""
    
    def process(self, content: Dict) -> str:
        """Generate detailed show notes with citations"""
        try:
            prompt = f"""
            Create professional podcast show notes using:
            Content: {content}
            
            Include:
            1. Episode title and description
            2. Chapter markers with timestamps
            3. Key points from each segment
            4. Expert quotes and insights
            5. Verified facts and statistics
            6. Source citations
            7. Further reading resources
            8. Call to action
            
            Format in clean Markdown with proper headings, lists, and links.
            Make it easy to read and reference.
            """
            
            return self.deepseek_completion(prompt)
            
        except Exception as e:
            print(f"Error generating show notes: {str(e)}")
            return ""
