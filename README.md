# AI Podcast Creator

An AI-powered podcast creation tool that generates engaging audio content using CrewAI for content generation and Kokoro-82M for text-to-speech synthesis.

## Features

- Automated podcast content generation using CrewAI
- High-quality text-to-speech using Kokoro-82M
- Multiple voice options with different accents
- Background music and sound effects
- User-friendly web interface using Gradio

## Project Structure

```
voice/
├── crew/                   # CrewAI components
│   ├── agents.py          # AI agent definitions
│   ├── llm.py            # Language model setup
│   ├── podcast_crew.py   # Main podcast crew logic
│   └── tasks.py          # Task definitions
├── effects/               # Sound effects directory
├── music/                # Background music directory
├── auto_podcast_creator.py # Main podcast creation logic
├── gradio_app.py         # Web interface
└── requirements.txt      # Project dependencies
```

## Prerequisites

- Python 3.11+
- espeak-ng (for text-to-speech)
- OpenAI API key (for content generation)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/voice.git
   cd voice
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install espeak-ng:
   ```bash
   # On macOS
   brew install espeak-ng
   
   # On Ubuntu/Debian
   sudo apt-get install espeak-ng
   ```

5. Download Kokoro-82M model:
   ```bash
   # Download instructions for Kokoro-82M model files
   ```

6. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Usage

1. Start the web interface:
   ```bash
   python gradio_app.py
   ```

2. Open your browser and navigate to `http://localhost:7860`

3. Enter your podcast topic and adjust settings as needed

## Project Organization

- `crew/`: Contains all CrewAI-related components
- `effects/`: Sound effects for podcast transitions and highlights
- `music/`: Background music tracks
- `auto_podcast_creator.py`: Core podcast generation logic
- `gradio_app.py`: Web interface implementation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [Kokoro-82M](https://github.com/voicepaw/kokoro)
