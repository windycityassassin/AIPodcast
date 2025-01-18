from dotenv import load_dotenv
from auto_podcast_creator import AutoPodcastCreator
import soundfile as sf
import os
import json

def main():
    # Load environment variables
    load_dotenv()
    
    # Create podcast creator
    creator = AutoPodcastCreator()
    
    # Test parameters
    topic = "The Future of Artificial Intelligence in Healthcare"
    duration_minutes = 5
    options = {
        "add_music": True,
        "music_volume": 0.1,
        "voice_type": "default",
        "accent": "American",
        "speed": 1.0,
        "style": "conversational"
    }
    
    try:
        # Generate podcast
        print("\n=== Starting Podcast Generation ===")
        result = creator.create_full_podcast(topic, duration_minutes, **options)
        
        # Save results
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save audio
        audio_file = os.path.join(output_dir, "test_podcast.wav")
        sf.write(audio_file, result["audio"], result["sample_rate"])
        print(f"\nAudio saved to: {audio_file}")
        
        # Save show notes
        notes_file = os.path.join(output_dir, "show_notes.md")
        show_notes_str = str(result["show_notes"])
        with open(notes_file, "w") as f:
            f.write(show_notes_str)
        print(f"Show notes saved to: {notes_file}")
        
        # Save research and fact check data
        metadata_file = os.path.join(output_dir, "metadata.json")
        metadata = {
            "title": result["title"],
            "description": result["description"],
            "keywords": result["keywords"],
            "research": result["research"],
            "fact_check": result["fact_check"]
        }
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved to: {metadata_file}")
        
        # Print summary
        print("\n=== Podcast Summary ===")
        print(f"Title: {result['title']}")
        print(f"Description: {result['description']}")
        print(f"Keywords: {', '.join(result['keywords'])}")
        print("\nSegments:")
        for segment in result["segments"]:
            print(f"- {segment['timestamp']}: {segment['title']}")
        
        print("\n=== Fact Check Summary ===")
        fact_check = result["fact_check"]
        print(f"Verified claims: {len(fact_check.get('verified_claims', []))}")
        print(f"Uncertain claims: {len(fact_check.get('uncertain_claims', []))}")
        print(f"Unverified claims: {len(fact_check.get('unverified_claims', []))}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise

if __name__ == "__main__":
    main()
