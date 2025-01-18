from typing import Dict, List
from .base_agent import BaseAgent

class FactCheckingAgent(BaseAgent):
    """Agent responsible for verifying facts and sources"""
    
    def process(self, content: Dict) -> Dict:
        """Verify facts and add confidence scores"""
        try:
            # Extract all factual claims
            facts = []
            for segment in content['segments']:
                prompt = f"""
                Extract factual claims from this content and rate confidence:
                {segment['content']}
                
                For each claim, provide:
                1. The claim
                2. Confidence score (0-100)
                3. Supporting evidence
                4. Potential caveats
                
                Format as JSON:
                {{
                    "claims": [
                        {{
                            "statement": "claim text",
                            "confidence": confidence_score,
                            "evidence": "supporting evidence",
                            "caveats": "potential limitations"
                        }}
                    ]
                }}
                """
                
                response = self.deepseek_completion(prompt)
                segment_facts = eval(response)
                facts.extend(segment_facts['claims'])
            
            # Add fact-checking results to content
            content['fact_check'] = {
                'verified_claims': [f for f in facts if f['confidence'] >= 80],
                'uncertain_claims': [f for f in facts if 50 <= f['confidence'] < 80],
                'unverified_claims': [f for f in facts if f['confidence'] < 50]
            }
            
            return content
            
        except Exception as e:
            print(f"Error in fact checking: {str(e)}")
            return content
