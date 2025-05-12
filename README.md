# Zoro VoiceBot 🗡️

A voice-interactive chatbot that embodies Roronoa Zoro from One Piece, complete with his personality, speech patterns, and (questionable) sense of direction.

## Features 🌟

- **Real-time Voice Interaction**: Speak with Zoro using your microphone
- **Character-Authentic Responses**: Get responses that match Zoro's personality
- **Voice Synthesis**: Hear Zoro's responses through ElevenLabs voice synthesis
- **Beautiful UI**: Themed interface with Zoro's image and sword decorations
- **Response Categories**:
  - Greetings and acknowledgments
  - Combat-related responses
  - Direction-related confusion
  - Help and assistance
  - Training references
  - Error messages in Zoro's style

## Prerequisites 🔧

- Python 3.9+
- Modern web browser with microphone support
- Internet connection (for speech recognition and voice synthesis)

## Installation 🛠️

1. Clone the repository:
```bash
git clone <repository-url>
cd voicebot
```

2. Install the required dependencies:
```bash
pip3 install uvicorn fastapi jinja2 python-multipart SpeechRecognition elevenlabs
```

3. Set up your ElevenLabs API key:
- Sign up at [ElevenLabs](https://elevenlabs.io)
- Replace the API key in `main.py` with your own:
```python
ELEVENLABS_API_KEY = "your-api-key-here"
```

## Running the Application 🚀

1. Start the FastAPI server:
```bash
python3 -m uvicorn main:app --reload
```

2. Open your browser and navigate to:
```
http://127.0.0.1:8000
```

## Usage 💬

1. Click the "Start Recording" button to begin speaking
2. Speak your message clearly into the microphone
3. Click "Stop" when you're done
4. Wait for Zoro's response (both text and voice)

## Response Types 🗣️

- **Greetings**: "Hello", "Hi", "Hey"
- **Help Requests**: "Help", "I need assistance"
- **Combat**: Anything related to fighting or swords
- **Directions**: Questions about locations or paths
- **General**: Any other conversation

## Project Structure 📁

```
voicebot/
├── main.py              # FastAPI backend server
├── static/             
│   └── images/         
│       └── zorro.png    # Zoro's image
├── templates/
│   └── index.html       # Frontend UI template
└── README.md            # This file
```

## Technical Details 🔍

- **Backend**: FastAPI with WebSocket support
- **Speech Recognition**: Google Speech Recognition API
- **Voice Synthesis**: ElevenLabs API
- **Frontend**: HTML, CSS, JavaScript with WebSocket
- **Audio Processing**: Web Audio API

## Error Handling 🚨

The bot handles various scenarios with Zoro-style responses:
- Inaudible voice
- Connection issues
- Speech recognition failures
- Server errors

## Contributing 🤝

Feel free to submit issues and enhancement requests!

## License 📄

[Your chosen license]

## Acknowledgments 🙏

- One Piece created by Eiichiro Oda
- ElevenLabs for voice synthesis
- Google Speech Recognition for speech-to-text 