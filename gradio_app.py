import gradio as gr
from auto_podcast_creator import AutoPodcastCreator
from datetime import datetime
import traceback

def create_interface():
    def generate_podcast(topic, duration_minutes=10, voice_type="Default Mix (Bella & Sarah)", accent="American", speed=1.0, add_music=True, music_volume=-20, style="Conversational"):
        try:
            print(f"\nGenerating podcast for topic: {topic}\n")
            print(f"\nStyle: {style}, Duration: {duration_minutes} minutes")
            print(f"Voice: {voice_type}, Accent: {accent}, Speed: {speed}\n")
            
            creator = AutoPodcastCreator()
            result = creator.generate_podcast(
                topic=topic,
                duration_minutes=duration_minutes,
                voice_type=voice_type,
                accent=accent,
                speed=speed,
                add_music=add_music,
                music_volume=music_volume
            )
            
            return {
                "title": result["title"],
                "description": result["description"],
                "audio": result["audio_path"],
                "segments": [
                    f"{segment.get('title', 'Untitled')}: {segment.get('content', '')[:100]}..."
                    for segment in result["segments"]
                ]
            }
            
        except Exception as e:
            print(f"Error: {str(e)}")
            traceback.print_exc()
            raise gr.Error(str(e))

    with gr.Blocks() as demo:
        gr.Markdown("""# 🎙️ AI Podcast Creator Pro
        Generate professional, engaging podcasts on any topic using advanced AI technology.
        """)
        
        with gr.Tabs():
            with gr.TabItem("🎯 Generate Podcast"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📝 Podcast Configuration")
                        
                        topic = gr.Textbox(label="Topic", placeholder="Enter a topic for your podcast")
                        duration = gr.Slider(minimum=1, maximum=30, value=10, label="Duration (minutes)")
                        
                        with gr.Row():
                            style = gr.Dropdown(
                                choices=["Conversational", "Educational", "Professional", "Entertainment"],
                                value="Conversational",
                                label="Style"
                            )
                        
                        gr.Markdown("### 🎤 Voice Configuration")
                        
                        with gr.Row():
                            voice = gr.Dropdown(
                                choices=["Default Mix (Bella & Sarah)", "Bella (American Female)", "Nicole (American Female)", "Sarah (American Female)", "Sky (American Female)", "Adam (American Male)", "Michael (American Male)", "Emma (British Female)", "Isabella (British Female)", "George (British Male)", "Lewis (British Male)"],
                                value="Default Mix (Bella & Sarah)",
                                label="Voice Type"
                            )
                            
                            accent = gr.Dropdown(
                                choices=["American", "British"],
                                value="American",
                                label="Accent"
                            )
                        
                        with gr.Row():
                            speed = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, label="Speech Speed")
                        
                        gr.Markdown("### 🎵 Music Configuration")
                        
                        with gr.Row():
                            add_music = gr.Checkbox(value=True, label="Add Background Music")
                            music_volume = gr.Slider(minimum=-40, maximum=0, value=-20, label="Music Volume (dB)")
                        
                        generate_btn = gr.Button("🎙️ Generate Podcast")
                    
                    with gr.Column():
                        title = gr.Textbox(label="Title")
                        description = gr.Textbox(label="Description")
                        audio = gr.Audio(label="Generated Podcast")
                        segments = gr.JSON(label="Segments")
            
            with gr.TabItem("ℹ️ Help & Tips"):
                gr.Markdown(
                    """
                    ### 🎯 How to Get the Best Results
                    
                    1. **Topic Selection**
                       - Be specific with your topic
                       - Include key points you want to cover
                       - Consider your target audience
                    
                    2. **Duration**
                       - 5-10 minutes: Perfect for quick overviews
                       - 10-20 minutes: Ideal for detailed explanations
                       - 20-30 minutes: Best for comprehensive topics
                    
                    3. **Style Options**
                       - Conversational: Casual, friendly tone
                       - Educational: Clear, instructional approach
                       - Professional: Formal, business-oriented
                       - Technical: Detailed, specialized content
                       - Entertainment: Engaging, dynamic style
                    
                    4. **Voice Options**
                       - Multiple American and British voices available
                       - Adjust speaking speed for perfect pacing
                       - Mix different voices for variety
                    
                    5. **Background Music**
                       - Adds atmosphere to your podcast
                       - Adjust volume to maintain clarity
                    """
                )
        
        generate_btn.click(
            fn=generate_podcast,
            inputs=[topic, duration, voice, accent, speed, add_music, music_volume, style],
            outputs=[
                gr.JSON({
                    "title": title,
                    "description": description,
                    "audio": audio,
                    "segments": segments
                })
            ]
        )
    
    return demo

if __name__ == "__main__":
    interface = create_interface()
    interface.launch()
