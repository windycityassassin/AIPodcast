from crewai import Task
from typing import Dict, List
import json

class PodcastCrewTasks:
    def research_task(self, topic: str, agent) -> Task:
        return Task(
            description=f"""Research the topic: {topic}
            1. Find reliable and up-to-date sources
            2. Gather key information, statistics, and expert opinions
            3. Identify current trends and developments
            4. Collect interesting examples and case studies
            
            Your final answer MUST be in JSON format with:
            {{
                "key_points": [list of main points],
                "facts": [list of verified facts],
                "statistics": [list of relevant statistics],
                "expert_opinions": [list of expert views],
                "trends": [list of current trends],
                "sources": [list of source URLs]
            }}
            """,
            agent=agent,
            expected_output="JSON object with research findings"
        )

    def content_creation_task(self, research_data: Dict, duration_minutes: int, agent) -> Task:
        return Task(
            description=f"""Create a {duration_minutes}-minute podcast script using this research:
            {json.dumps(research_data, indent=2)}
            
            Create multiple segments including:
            1. Engaging introduction
            2. Main discussion points
            3. Expert insights
            4. Case studies
            5. Future implications
            6. Conclusion
            
            Your final answer MUST be in JSON format with:
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
                        "music": {{
                            "mood": "upbeat|calm|dramatic|tech|inspirational",
                            "volume": "float between -30 and -10"
                        }},
                        "sound_effect": "transition|highlight|quote|stats|conclusion",
                        "content": "The actual text content to be spoken",
                        "enhancements": {{
                            "speed": "float between 0.8 and 1.2",
                            "emphasis": ["list of words to emphasize"],
                            "pauses": ["list of places to pause"]
                        }}
                    }}
                ]
            }}
            
            Important notes:
            1. Each segment should be 2-3 minutes long
            2. The content field MUST contain the actual text to be spoken
            3. Choose appropriate music mood and sound effects for each segment
            4. Specify audio enhancements to make the content more engaging
            """,
            agent=agent,
            expected_output="JSON object with podcast content"
        )

    def fact_checking_task(self, content: Dict, agent) -> Task:
        return Task(
            description=f"""Verify all facts in this content:
            {json.dumps(content, indent=2)}
            
            For each segment:
            1. Extract all factual claims
            2. Verify each claim against reliable sources
            3. Assign confidence scores
            4. Note any caveats or context
            
            Your final answer MUST be in JSON format with:
            {{
                "verified_claims": [
                    {{
                        "claim": "claim text",
                        "confidence": score (0-100),
                        "evidence": "supporting evidence",
                        "source": "source URL"
                    }}
                ],
                "uncertain_claims": [...],
                "unverified_claims": [...]
            }}
            """,
            agent=agent,
            expected_output="JSON object with fact-checking results"
        )

    def show_notes_task(self, content: Dict, fact_check: Dict, agent) -> Task:
        return Task(
            description=f"""Create comprehensive show notes using:
            Content: {json.dumps(content, indent=2)}
            Fact Check: {json.dumps(fact_check, indent=2)}
            
            Include:
            1. Episode title and description
            2. Chapter markers with timestamps
            3. Key points from each segment
            4. Expert quotes and insights
            5. Verified facts and statistics
            6. Source citations
            7. Further reading resources
            
            Your final answer MUST be in JSON format with:
            {{
                "title": "episode title",
                "description": "episode description",
                "chapters": [
                    {{
                        "timestamp": "MM:SS",
                        "title": "chapter title",
                        "summary": "chapter summary"
                    }}
                ],
                "key_points": ["point 1", "point 2", ...],
                "expert_quotes": ["quote 1", "quote 2", ...],
                "facts_and_stats": ["fact 1", "fact 2", ...],
                "sources": ["source 1", "source 2", ...],
                "further_reading": ["resource 1", "resource 2", ...]
            }}
            """,
            agent=agent,
            expected_output="JSON object with show notes"
        )

    def audio_enhancement_task(self, segment: Dict, agent) -> Task:
        return Task(
            description=f"""Optimize audio parameters for this segment:
            {json.dumps(segment, indent=2)}
            
            Determine:
            1. Voice characteristics (pitch, speed, emotion)
            2. Background music selection and volume
            3. Sound effect timing and type
            4. Audio transitions
            
            Your final answer MUST be in JSON format with:
            {{
                "voice": {{
                    "pitch": value,
                    "speed": value,
                    "emotion": "emotion type"
                }},
                "music": {{
                    "track": "track name",
                    "volume": value,
                    "fade_in": seconds,
                    "fade_out": seconds
                }},
                "effects": [
                    {{
                        "type": "effect type",
                        "timestamp": "MM:SS",
                        "duration": seconds
                    }}
                ]
            }}
            """,
            agent=agent,
            expected_output="JSON object with audio parameters"
        )
