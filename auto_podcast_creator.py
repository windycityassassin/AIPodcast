import os
import numpy as np
import soundfile as sf
import traceback
import gradio as gr
from typing import Dict, List, Optional
from crew import PodcastCrew
from agents import (
    ResearchAgent,
    ContentAgent,
    FactCheckingAgent,
    ShowNotesAgent,
    AudioEnhancementAgent
)
import json
import requests
from pathlib import Path
from datetime import datetime
import torch
import sys
import soundfile as sf

# Add Kokoro to path
kokoro_path = os.path.join(os.path.dirname(__file__), 'Kokoro-82M')
sys.path.append(kokoro_path)

from models import build_model
from kokoro import generate

class AutoPodcastCreator:
    def __init__(self):
        """Initialize the podcast creator with CrewAI"""
        print("Initializing AutoPodcastCreator...")
        
        # Initialize CrewAI
        self.podcast_crew = PodcastCrew()
        
        try:
            # Initialize Kokoro model
            print("Loading Kokoro-82M model...")
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"Using device: {self.device}")
            
            model_path = os.path.join(kokoro_path, 'kokoro-v0_19.pth')
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            print(f"Loading model from: {model_path}")
            
            self.model = build_model(model_path, self.device)
            if self.model is None:
                raise RuntimeError("Failed to build Kokoro model")
            print("Model loaded successfully")
            
            # Load voice packs
            self.voicepacks = {}
            voices_dir = os.path.join(kokoro_path, 'voices')
            if not os.path.exists(voices_dir):
                raise FileNotFoundError(f"Voices directory not found: {voices_dir}")
            print(f"Loading voice packs from: {voices_dir}")
            
            voice_files = [f for f in os.listdir(voices_dir) if f.endswith('.pt')]
            if not voice_files:
                raise FileNotFoundError(f"No voice pack files found in {voices_dir}")
            
            for voice_file in voice_files:
                try:
                    voice_path = os.path.join(voices_dir, voice_file)
                    print(f"Loading voice pack: {voice_file}")
                    self.voicepacks[voice_file[:-3]] = torch.load(voice_path, weights_only=True).to(self.device)
                except Exception as e:
                    print(f"Error loading voice pack {voice_file}: {str(e)}")
            
            if not self.voicepacks:
                raise RuntimeError("No voice packs were loaded successfully")
            print(f"Loaded {len(self.voicepacks)} voice packs")
            
            # Set sample rate
            self.SAMPLE_RATE = 24000
            
            print("Initialization complete")
            
        except Exception as e:
            print(f"Error initializing AutoPodcastCreator: {str(e)}")
            traceback.print_exc()
            raise RuntimeError(f"Failed to initialize AutoPodcastCreator: {str(e)}")
    
    def get_voicepack(self, voice_type):
        """Get the appropriate voicepack based on selection"""
        voice_mapping = {
            "Default Mix (Bella & Sarah)": "af",
            "Bella (American Female)": "af_bella",
            "Nicole (American Female)": "af_nicole",
            "Sarah (American Female)": "af_sarah",
            "Sky (American Female)": "af_sky",
            "Adam (American Male)": "am_adam",
            "Michael (American Male)": "am_michael",
            "Emma (British Female)": "bf_emma",
            "Isabella (British Female)": "bf_isabella",
            "George (British Male)": "bm_george",
            "Lewis (British Male)": "bm_lewis"
        }
        
        voice_key = voice_mapping.get(voice_type)
        if voice_key not in self.voicepacks:
            print(f"Warning: Voice {voice_type} not found, using default")
            return self.voicepacks["af"]
        
        return self.voicepacks[voice_key]
    
    def generate_speech(self, text, voice_type, accent, speed):
        """Generate speech using Kokoro model"""
        try:
            print(f"\nGenerating speech:")
            print(f"Voice type: {voice_type}")
            print(f"Accent: {accent}")
            print(f"Speed: {speed}")
            print(f"Text length: {len(text)}")
            print(f"Text preview: {text[:100]}...")
            
            # Validate inputs
            if not text or len(text.strip()) == 0:
                raise ValueError("Empty text provided")
            
            if speed <= 0:
                raise ValueError("Speed must be positive")
            
            if accent not in ["American", "British"]:
                raise ValueError("Accent must be either 'American' or 'British'")
            
            # Get the appropriate voicepack
            voicepack = self.get_voicepack(voice_type)
            if voicepack is None:
                raise RuntimeError(f"Failed to get voicepack for voice type: {voice_type}")
            print(f"Using voicepack: {type(voicepack)}")
            
            # Generate audio using Kokoro
            print("Calling Kokoro generate function...")
            try:
                audio, phonemes = generate(
                    self.model, 
                    text, 
                    voicepack,
                    lang='a' if accent == "American" else 'b',  # 'a' for American English, 'b' for British English
                    speed=speed
                )
            except Exception as e:
                raise RuntimeError(f"Kokoro generation failed: {str(e)}")
            
            if audio is None:
                raise RuntimeError("No audio generated by Kokoro")
            
            print(f"Audio generated successfully. Type: {type(audio)}")
            
            # Convert to float32 numpy array
            try:
                audio = np.array(audio, dtype=np.float32)
            except Exception as e:
                raise RuntimeError(f"Failed to convert audio to numpy array: {str(e)}")
                
            print(f"Converted to numpy array. Shape: {audio.shape}, dtype: {audio.dtype}")
            
            # Validate audio output
            if audio.size == 0:
                raise RuntimeError("Generated audio is empty")
            
            if not np.isfinite(audio).all():
                raise RuntimeError("Generated audio contains invalid values (inf/nan)")
            
            return audio
            
        except Exception as e:
            print(f"Error in speech generation: {str(e)}")
            print(traceback.format_exc())
            return None
        
    def create_full_podcast(
            self,
            topic: str,
            duration_minutes: int,
            add_music: bool = False,
            music_volume: float = -20,
            voice_type: str = "default",
            accent: str = "American",
            speed: float = 1.0,
            style: str = "Conversational",
            progress_callback=None
        ):
        """Create a full podcast with audio for a given topic"""
        try:
            print(f"\nStarting podcast creation for topic: {topic}")
            
            # Get podcast content from CrewAI
            print("Getting content from CrewAI...")
            crew_result = self.podcast_crew.create_podcast(topic, duration_minutes, style, progress_callback)
            print(f"\nParsed CrewAI Result: {json.dumps(crew_result, indent=2)}")
            
            if progress_callback:
                progress_callback("Audio Generator", "Starting audio generation...")
            
            # Process each segment
            all_audio = []
            segments = crew_result.get("segments", [])
            print(f"CrewAI result structure: {crew_result.keys()}")
            print(f"Segments: {segments}")
            
            if not segments:
                raise Exception("No segments found in CrewAI output")
            
            for segment in segments:
                try:
                    # Generate speech for this segment
                    text = segment.get("content", "")
                    if not text:
                        print(f"Warning: Empty content in segment: {segment}")
                        continue
                    
                    print(f"\nProcessing segment: {segment.get('title', 'Untitled')}")
                    print(f"Content length: {len(text)}")
                    print(f"Content preview: {text[:100]}...")
                    
                    # Get audio parameters from segment enhancements
                    enhancements = segment.get("enhancements", {})
                    segment_speed = enhancements.get("speed", speed)
                    
                    # Generate speech
                    print(f"\nGenerating speech with parameters:")
                    print(f"Voice type: {voice_type}")
                    print(f"Accent: {accent}")
                    print(f"Speed: {segment_speed}")
                    
                    audio = self.generate_speech(text, voice_type, accent, segment_speed)
                    if audio is None:
                        print(f"Warning: Failed to generate audio for segment: {segment.get('title', 'Untitled')}")
                        continue
                    
                    print("Speech generated successfully")
                    
                    # Add background music if requested
                    if add_music and segment.get("music"):
                        music_info = segment["music"]
                        if isinstance(music_info, dict):
                            mood = music_info.get("mood")
                            volume = music_info.get("volume", music_volume)
                        else:
                            mood = music_info
                            volume = music_volume
                            
                        if mood:
                            print(f"\nAdding background music:")
                            print(f"Mood: {mood}")
                            print(f"Volume: {volume}")
                            
                            music_file = self.get_background_music(mood)
                            if music_file:
                                music = self.load_and_adjust_music(music_file, len(audio), volume)
                                audio = self.mix_audio(audio, music)
                                print("Music added successfully")
                            else:
                                print(f"Warning: Music file not found for mood: {mood}")
                    
                    # Add sound effects if specified
                    if segment.get("sound_effect"):
                        effect_type = segment["sound_effect"]
                        print(f"\nAdding sound effect: {effect_type}")
                        
                        effect = self.get_sound_effect(effect_type)
                        if effect is not None:
                            # TODO: Mix effect at the right timestamp
                            print("Sound effect added successfully")
                        else:
                            print(f"Warning: Sound effect not found: {effect_type}")
                    
                    all_audio.append(audio)
                    print(f"Segment {segment.get('title', 'Untitled')} processed successfully")
                    
                except Exception as e:
                    print(f"Error processing segment: {str(e)}")
                    traceback.print_exc()
            
            print(f"Found {len(all_audio)} segments to process")
            
            if not all_audio:
                raise Exception("No audio segments were generated successfully")
            
            # Combine all segments
            final_audio = np.concatenate(all_audio)
            
            # Save to file
            output_file = "output.wav"
            sf.write(output_file, final_audio, self.SAMPLE_RATE)
            
            return {
                "title": crew_result.get("title", "Untitled Podcast"),
                "description": crew_result.get("description", ""),
                "audio_file": output_file,
                "duration": len(final_audio) / self.SAMPLE_RATE,
                "segments": segments
            }
            
        except Exception as e:
            print(f"Error in create_full_podcast: {str(e)}")
            raise

    def get_background_music(self, mood: str) -> str:
        """Get appropriate background music file based on mood"""
        music_mapping = {
            "upbeat": "music/upbeat.wav",
            "calm": "music/calm.wav",
            "dramatic": "music/dramatic.wav",
            "tech": "music/tech.wav",
            "inspirational": "music/inspirational.wav"
        }
        return music_mapping.get(mood.lower())
    
    def get_sound_effect(self, effect_type: str) -> np.ndarray:
        """Get sound effect based on type"""
        try:
            effects_mapping = {
                "transition": "effects/transition.wav",
                "highlight": "effects/highlight.wav",
                "quote": "effects/quote.wav",
                "stats": "effects/stats.wav",
                "conclusion": "effects/conclusion.wav"
            }
            
            effect_path = effects_mapping.get(effect_type.lower())
            if effect_path and os.path.exists(effect_path):
                audio, _ = sf.read(effect_path)
                return audio
            return None
            
        except Exception as e:
            print(f"Error loading sound effect: {str(e)}")
            return None
    
    def load_and_adjust_music(self, music_file: str, target_length: int, volume: float) -> np.ndarray:
        """Load and adjust background music to match speech length"""
        try:
            if not os.path.exists(music_file):
                return np.zeros(target_length)
            
            music, _ = sf.read(music_file)
            
            # Loop music if needed
            if len(music) < target_length:
                repeats = target_length // len(music) + 1
                music = np.tile(music, repeats)
            
            # Trim to match speech length
            music = music[:target_length]
            
            # Apply volume adjustment
            music = music * volume
            
            return music
            
        except Exception as e:
            print(f"Error processing music: {str(e)}")
            return np.zeros(target_length)
    
    def mix_audio(self, speech: np.ndarray, music: np.ndarray) -> np.ndarray:
        """Mix speech and background music"""
        try:
            # Ensure both arrays are the same length
            min_length = min(len(speech), len(music))
            speech = speech[:min_length]
            music = music[:min_length]
            
            # Mix audio
            mixed = speech + music
            
            # Normalize to prevent clipping
            max_val = np.max(np.abs(mixed))
            if max_val > 1.0:
                mixed = mixed / max_val
            
            return mixed
            
        except Exception as e:
            print(f"Error mixing audio: {str(e)}")
            return speech

    def apply_audio_enhancements(self, audio: np.ndarray, enhancement: Dict) -> np.ndarray:
        """Apply audio enhancements based on the enhancement parameters"""
        try:
            # Apply pitch adjustment if specified
            if 'pitch' in enhancement:
                # For now, we'll skip pitch adjustment as it requires additional libraries
                pass

            # Apply volume adjustment
            if 'volume' in enhancement:
                audio = audio * float(enhancement['volume'])

            # Normalize audio
            max_val = np.max(np.abs(audio))
            if max_val > 1.0:
                audio = audio / max_val

            return audio

        except Exception as e:
            print(f"Error applying audio enhancements: {str(e)}")
            return audio

    def generate_podcast(self, topic: str, duration_minutes: int = 10, voice_type: str = "Default Mix (Bella & Sarah)", accent: str = "American", speed: float = 1.0, add_music: bool = True, music_volume: float = -20, style: str = "Conversational", progress_callback=None) -> Dict:
        """Generate a podcast for the given topic"""
        try:
            # Create podcast
            result = self.create_full_podcast(
                topic=topic,
                duration_minutes=duration_minutes,
                voice_type=voice_type,
                accent=accent,
                speed=speed,
                add_music=add_music,
                music_volume=music_volume,
                style=style,
                progress_callback=progress_callback
            )
            
            # The audio file has already been saved by create_full_podcast
            return {
                "title": result["title"],
                "description": result["description"],
                "audio_path": result["audio_file"],
                "duration": result["duration"],
                "segments": result["segments"]
            }
            
        except Exception as e:
            print(f"Error generating podcast: {str(e)}")
            traceback.print_exc()
            raise

def create_gradio_interface():
    creator = AutoPodcastCreator()
    
    def generate_podcast_ui(topic, duration_minutes, style, voice_type, accent, speed, add_music=True, music_volume=-20, progress=gr.Progress()):
        try:
            print(f"\nGenerating podcast for topic: {topic}")
            print(f"Style: {style}, Duration: {duration_minutes} minutes")
            print(f"Voice: {voice_type}, Accent: {accent}, Speed: {speed}")
            
            # Initialize agent status
            status_updates = []
            
            def update_status(agent_name, status):
                timestamp = datetime.now().strftime("%H:%M:%S")
                status_updates.append(f"[{timestamp}] {agent_name}: {status}")
                return "\n".join(status_updates)
            
            progress(0, desc="Starting research...")
            
            # Generate podcast
            result = creator.generate_podcast(
                topic=topic,
                duration_minutes=duration_minutes,
                voice_type=voice_type,
                accent=accent,
                speed=speed,
                add_music=add_music,
                music_volume=music_volume,
                style=style,
                progress_callback=update_status
            )
            
            progress(0.5, desc="Processing audio...")
            
            # Format the script for display
            script = "# Generated Podcast Script\n\n"
            for segment in result["segments"]:
                script += f"## {segment.get('title', '')}\n\n{segment.get('content', '')[:200]}...\n\n"
            
            progress(1.0, desc="Done!")
            
            # Return the results
            return (
                result["audio_path"],  # Audio file path
                script,  # Full script preview
                f"# {result['title']}\n\n{result['description']}",  # Episode info
                "\n".join([  # Show notes
                    "## Segments",
                    *[f"- {s.get('title', 'Untitled')}" for s in result["segments"]]
                ]),
                "✅ Podcast generated successfully!",  # Status
                "\n".join(status_updates)  # Agent status updates
            )
            
        except Exception as e:
            error_msg = f"Error generating podcast: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            return None, "", error_msg, "", "❌ Generation failed", "Error occurred during generation"
    
    # Create a nice-looking interface with orange theme
    theme = gr.themes.Base(
        primary_hue=gr.themes.colors.orange,
        secondary_hue=gr.themes.colors.orange,
        neutral_hue=gr.themes.colors.gray,
    )
    
    with gr.Blocks(title="AI Podcast Creator", theme=theme) as interface:
        gr.Markdown(
            """
            # 🎙️ AI Podcast Creator Pro
            Generate professional, engaging podcasts on any topic using advanced AI technology.
            """
        )
        
        with gr.Tabs():
            with gr.TabItem("🎯 Generate Podcast"):
                with gr.Row():
                    # Left column - Input options
                    with gr.Column(scale=1):
                        gr.Markdown("### 📝 Podcast Configuration")
                        
                        topic_input = gr.Textbox(
                            label="Topic",
                            placeholder="Enter the topic for your podcast...",
                            lines=3
                        )
                        
                        with gr.Row():
                            duration_slider = gr.Slider(
                                minimum=5,
                                maximum=30,
                                value=10,
                                step=5,
                                label="Duration (minutes)"
                            )
                            
                            style_dropdown = gr.Dropdown(
                                choices=[
                                    "Conversational",
                                    "Educational",
                                    "Professional",
                                    "Entertainment"
                                ],
                                value="Conversational",
                                label="Style"
                            )
                        
                        gr.Markdown("### 🎤 Voice Configuration")
                        
                        with gr.Row():
                            voice_dropdown = gr.Dropdown(
                                choices=[
                                    "Default Mix (Bella & Sarah)",
                                    "Bella (American Female)",
                                    "Nicole (American Female)",
                                    "Sarah (American Female)",
                                    "Sky (American Female)",
                                    "Adam (American Male)",
                                    "Michael (American Male)",
                                    "Emma (British Female)",
                                    "Isabella (British Female)",
                                    "George (British Male)",
                                    "Lewis (British Male)"
                                ],
                                value="Default Mix (Bella & Sarah)",
                                label="Voice"
                            )
                            
                            accent_dropdown = gr.Dropdown(
                                choices=[
                                    "American",
                                    "British"
                                ],
                                value="American",
                                label="Accent"
                            )
                        
                        with gr.Row():
                            speed_slider = gr.Slider(
                                minimum=0.5,
                                maximum=2.0,
                                value=1.0,
                                step=0.1,
                                label="Speaking Speed"
                            )
                        
                        gr.Markdown("### 🎵 Music Configuration")
                        
                        with gr.Row():
                            add_music = gr.Checkbox(
                                label="Add Background Music",
                                value=True
                            )
                            music_volume = gr.Slider(
                                minimum=-40,
                                maximum=0,
                                value=-20,
                                step=1,
                                label="Music Volume (dB)"
                            )
                        
                        generate_btn = gr.Button(
                            "🎙️ Generate Podcast",
                            variant="primary",
                            size="lg"
                        )
                        
                        status_text = gr.Markdown("Ready to generate your podcast!")
                    
                    # Right column - Output display
                    with gr.Column(scale=2):
                        gr.Markdown("### 🎧 Generated Podcast")
                        
                        # Tabs for different outputs
                        with gr.Tabs():
                            with gr.TabItem("🔊 Audio"):
                                audio_output = gr.Audio(
                                    label="Generated Audio",
                                    show_download_button=True
                                )
                            
                            with gr.TabItem("📜 Script Preview"):
                                script_output = gr.Markdown()
                            
                            with gr.TabItem("ℹ️ Episode Info"):
                                info_output = gr.Markdown()
                            
                            with gr.TabItem("📝 Show Notes"):
                                notes_output = gr.Markdown()
                                
                            with gr.TabItem("🤖 Agent Status"):
                                agent_status_output = gr.Markdown()
            
            with gr.TabItem("ℹ️ Help & Tips"):
                gr.Markdown(
                    """
                    ### 🎯 Tips for Better Results
                    
                    1. **Topic Selection**
                       - Be specific but not too narrow
                       - Include key aspects you want covered
                       - Consider your target audience
                    
                    2. **Voice Settings**
                       - Default Mix provides a dynamic experience
                       - Single voices work well for specific styles
                       - Adjust speed for better engagement
                    
                    3. **Style Guidelines**
                       - Conversational: Casual, friendly tone
                       - Educational: Clear, structured content
                       - Professional: Formal, business-focused
                       - Entertainment: Engaging, dynamic style
                    
                    4. **Music Tips**
                       - Enable for better engagement
                       - Adjust volume based on content
                       - -20dB is a good starting point
                    """
                )
        
        # Connect the generate button
        generate_btn.click(
            fn=generate_podcast_ui,
            inputs=[
                topic_input,
                duration_slider,
                style_dropdown,
                voice_dropdown,
                accent_dropdown,
                speed_slider,
                add_music,
                music_volume
            ],
            outputs=[
                audio_output,
                script_output,
                info_output,
                notes_output,
                status_text,
                agent_status_output
            ]
        )
    
    return interface

if __name__ == "__main__":
    try:
        print("Starting AI Podcast Creator...")
        interface = create_gradio_interface()
        print("Launching web interface...")
        interface.launch(share=True)  # share=True creates a public URL
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
