from typing import Dict, List
from .base_agent import BaseAgent

class ContentAgent(BaseAgent):
    """Agent responsible for generating podcast content"""
    
    def process(self, research_data: List[Dict], duration_minutes: int, style: str) -> Dict:
        """Generate podcast content from research data"""
        try:
            segments_per_minute = 2
            num_segments = max(3, duration_minutes * segments_per_minute)
            
            prompt = f"""
            Create a {duration_minutes}-minute podcast script in {style} style using this research:
            {research_data}
            
            Create {num_segments} segments including:
            1. Engaging introduction
            2. Main discussion points
            3. Expert insights
            4. Case studies
            5. Future implications
            6. Conclusion
            
            For each segment, specify:
            - Timestamp (MM:SS)
            - Speaker (Host/Guest/Expert)
            - Tone (excited/serious/curious)
            - Background music mood
            - Sound effect for transition
            
            Provide a JSON response with:
            {{
                "title": "podcast title",
                "description": "episode description",
                "keywords": ["relevant", "keywords"],
                "segments": [
                    {{
                        "timestamp": "MM:SS",
                        "title": "segment title",
                        "speaker": "speaker role",
                        "tone": "emotional tone",
                        "music": "music mood",
                        "sound_effect": "effect type",
                        "content": "segment content"
                    }}
                ],
                "chapter_markers": [
                    {{
                        "time": "MM:SS",
                        "title": "chapter title",
                        "description": "brief description"
                    }}
                ]
            }}
            """
            
            response = self.deepseek_completion(prompt)
            return eval(response)  # Convert string to dict
            
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            raise
