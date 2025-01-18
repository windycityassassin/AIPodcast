from crewai import LLM
import os

def get_llm():
    """Create and configure the DeepSeek LLM for use with CrewAI"""
    if not os.getenv('DEEPSEEK_API_KEY'):
        raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        
    return LLM(
        model="deepseek-chat",
        api_key=os.getenv('DEEPSEEK_API_KEY'),
        api_base="https://api.deepseek.com/v1",
        temperature=0.7,
        max_tokens=4096
    )
