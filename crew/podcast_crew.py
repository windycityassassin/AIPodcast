from crewai import Crew
from typing import Dict, List, Callable, Optional
import json
from .agents import PodcastCrewAgents
from .tasks import PodcastCrewTasks
import re
import ast

class PodcastCrew:
    def __init__(self):
        # Initialize agents
        self.agents = PodcastCrewAgents()
        self.tasks = PodcastCrewTasks()
        
    def parse_crew_output(self, result_str: str, stage: str) -> dict:
        """Parse CrewAI output into a JSON object"""
        print(f"\nParsing {stage} output...")
        print(f"Raw result: {result_str}")
        
        try:
            # First try using ast.literal_eval since CrewAI returns Python dict strings
            try:
                # Find the dictionary content
                dict_start = result_str.find('{')
                dict_end = result_str.rfind('}') + 1
                if dict_start == -1 or dict_end == 0:
                    raise ValueError(f"No dictionary content found in {stage} result")
                
                dict_str = result_str[dict_start:dict_end]
                print(f"\nExtracted dictionary string: {dict_str}")
                
                # Parse using ast.literal_eval which can handle Python literals
                result = ast.literal_eval(dict_str)
                print(f"\nParsed result: {result}")
                
                # Convert Python types to JSON-compatible types
                def convert_to_json_types(obj):
                    if isinstance(obj, dict):
                        return {str(k): convert_to_json_types(v) for k, v in obj.items()}
                    elif isinstance(obj, (list, tuple)):
                        return [convert_to_json_types(x) for x in obj]
                    elif isinstance(obj, (int, float, str, bool, type(None))):
                        return obj
                    else:
                        return str(obj)
                
                return convert_to_json_types(result)
                
            except (ValueError, SyntaxError) as e:
                print(f"\nFailed to parse with ast.literal_eval: {e}")
                print("Falling back to JSON parsing...")
                
                # Find the JSON content
                json_start = result_str.find('{')
                json_end = result_str.rfind('}') + 1
                if json_start == -1 or json_end == 0:
                    raise ValueError(f"No JSON content found in {stage} result")
                
                json_str = result_str[json_start:json_end]
                print(f"\nExtracted JSON string: {json_str}")
                
                # Clean up the JSON string
                json_str = json_str.replace("'", '"')  # Replace single quotes with double quotes
                json_str = json_str.replace('None', 'null')  # Replace Python None with JSON null
                json_str = json_str.replace('True', 'true')  # Replace Python True with JSON true
                json_str = json_str.replace('False', 'false')  # Replace Python False with JSON false
                print(f"\nAfter basic replacements: {json_str}")
                
                # Add quotes around unquoted property names
                json_str = re.sub(r'(\{|\,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1 "\2":', json_str)
                print(f"\nAfter property name quoting: {json_str}")
                
                # Fix common JSON formatting issues
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)  # Remove trailing commas
                json_str = re.sub(r'"\s*\+\s*"', '', json_str)  # Remove string concatenation
                json_str = re.sub(r'\s+', ' ', json_str)  # Normalize whitespace
                
                # Additional cleanup for CrewAI output
                json_str = re.sub(r'(["\d])\s+(["\w{[])', r'\1,\2', json_str)  # Add missing commas
                json_str = re.sub(r'}\s*{', '},{', json_str)  # Add commas between objects
                json_str = re.sub(r']\s*{', '],{', json_str)  # Add commas between array and object
                json_str = re.sub(r'}\s*\[', '},\[', json_str)  # Add commas between object and array
                json_str = re.sub(r']\s*\[', '],\[', json_str)  # Add commas between arrays
                
                # Remove any remaining invalid characters
                json_str = re.sub(r'[^\x20-\x7E]', '', json_str)  # Remove non-printable characters
                
                print(f"\nFinal JSON string: {json_str}")
                print("\nCharacter by character:")
                for i, c in enumerate(json_str):
                    print(f"[{i}] {c!r}")
                
                return json.loads(json_str)
                
        except Exception as e:
            print(f"\nError parsing {stage} output: {e}")
            print(f"Raw output: {result_str}")
            raise

    def create_podcast(self, topic: str, duration_minutes: int, style: str = "Conversational", progress_callback: Optional[Callable[[str, str], None]] = None) -> Dict:
        """Create a full podcast with research, content, and enhancements"""
        try:
            # Initialize agents with style
            researcher = self.agents.get_research_agent()
            content_creator = self.agents.get_content_agent(style)
            fact_checker = self.agents.get_fact_checking_agent()
            show_notes_agent = self.agents.get_show_notes_agent()
            audio_agent = self.agents.get_audio_enhancement_agent()
            
            if progress_callback:
                progress_callback("Research Agent", "Starting research phase...")
            
            # 1. Research
            research_task = self.tasks.research_task(topic, researcher)
            research_crew = Crew(
                agents=[researcher],
                tasks=[research_task],
                verbose=True
            )
            print("\nResearching topic...")
            research_result = research_crew.kickoff()
            research_data = self.parse_crew_output(str(research_result), "research")
            
            if progress_callback:
                progress_callback("Content Creator", "Creating podcast content...")
            
            # 2. Content creation
            content_task = self.tasks.content_creation_task(research_data, duration_minutes, content_creator)
            content_crew = Crew(
                agents=[content_creator],
                tasks=[content_task],
                verbose=True
            )
            print("\nCreating content...")
            content_result = content_crew.kickoff()
            content_data = self.parse_crew_output(str(content_result), "content")
            
            # Process segments to ensure they have content
            segments = content_data.get("segments", [])
            for segment in segments:
                # Use the script as content if not present
                if "content" not in segment:
                    segment["content"] = segment.get("script", "")
                # Combine speaker's lines if present
                if "lines" in segment:
                    segment["content"] = "\n".join(
                        f"{line.get('speaker', 'Speaker')}: {line.get('text', '')}"
                        for line in segment["lines"]
                    )
            content_data["segments"] = segments
            
            if progress_callback:
                progress_callback("Fact Checker", "Verifying facts...")
            
            # 3. Fact checking
            fact_check_task = self.tasks.fact_checking_task(content_data, fact_checker)
            fact_check_crew = Crew(
                agents=[fact_checker],
                tasks=[fact_check_task],
                verbose=True
            )
            print("\nVerifying facts...")
            fact_check_result = fact_check_crew.kickoff()
            fact_check_data = self.parse_crew_output(str(fact_check_result), "fact check")
            
            if progress_callback:
                progress_callback("Show Notes Agent", "Creating show notes...")
            
            # 4. Show notes
            show_notes_task = self.tasks.show_notes_task(content_data, fact_check_data, show_notes_agent)
            show_notes_crew = Crew(
                agents=[show_notes_agent],
                tasks=[show_notes_task],
                verbose=True
            )
            print("\nCreating show notes...")
            show_notes_result = show_notes_crew.kickoff()
            show_notes = self.parse_crew_output(str(show_notes_result), "show notes")
            
            if progress_callback:
                progress_callback("Audio Enhancement Agent", "Optimizing audio parameters...")
            
            # 5. Audio enhancement for each segment
            print("\nOptimizing audio parameters...")
            audio_enhancements = []
            for segment in segments:
                audio_task = self.tasks.audio_enhancement_task(segment, audio_agent)
                audio_crew = Crew(
                    agents=[audio_agent],
                    tasks=[audio_task],
                    verbose=True
                )
                enhancement_result = audio_crew.kickoff()
                enhancement = self.parse_crew_output(str(enhancement_result), "audio enhancement")
                # Add enhancements to segment
                segment["enhancements"] = enhancement
                audio_enhancements.append(enhancement)
            
            if progress_callback:
                progress_callback("System", "Compiling final results...")
            
            # Combine all results
            return {
                "title": content_data.get("title", "Untitled Podcast"),
                "description": content_data.get("description", ""),
                "keywords": content_data.get("keywords", []),
                "segments": segments,  # Now includes content and enhancements
                "research": research_data,
                "fact_check": fact_check_data,
                "show_notes": show_notes
            }
            
        except Exception as e:
            print(f"Error in create_podcast: {str(e)}")
            raise
