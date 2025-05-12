from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
import numpy as np
import io
import base64
import speech_recognition as sr
from elevenlabs import generate, set_api_key, voices
import logging
import tempfile
import traceback
import random

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Set ElevenLabs API key
ELEVENLABS_API_KEY = "use yours"
set_api_key(ELEVENLABS_API_KEY)

# Zoro-style responses
GREETINGS = [
    "Hmph, what do you want?",
    "You better have a good reason for interrupting my training.",
    "Is there a strong opponent nearby?",
    "Make it quick, I've got training to do.",
    "Yeah, I'm here. What's the situation?"
]

HELP_RESPONSES = [
    "Need help? Heh, you came to the right swordsman.",
    "What kind of trouble are you in? I'll cut through it.",
    "If it's about directions, I... uh... might not be the best person to ask.",
    "Tell me what's wrong. I'll handle it with my three-sword style!"
]

CONFUSION = [
    "Huh? Speak clearly, I can't understand what you're saying.",
    "You're making less sense than that stupid cook.",
    "Are you lost? Because I'm definitely not... the buildings just keep moving.",
    "What are you mumbling about?",
    "Speak up! I can barely hear you over the sound of my training.",
    "Your voice is weaker than a Marine recruit's sword skills."
]

ACKNOWLEDGMENTS = [
    "I see...",
    "Interesting...",
    "Hmph, is that so?",
    "Whatever..."
]

COMBAT_RESPONSES = [
    "Sounds like a challenge. I'm in!",
    "Finally, something worth drawing my swords for!",
    "Heh, this might be fun.",
    "Three-sword style should be enough for this."
]

DIRECTION_RESPONSES = [
    "I know exactly where to go! The buildings just keep moving...",
    "Follow me! Though the streets seem to have changed again...",
    "It's this way! ...probably.",
    "The destination keeps moving, but I'll get us there!"
]

def generate_zoro_response(text):
    """Generate a Zoro-style response based on the input text."""
    text_lower = text.lower()
    
    # Check for different types of input and generate appropriate responses
    if any(word in text_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        response = random.choice(GREETINGS)
    elif any(word in text_lower for word in ['help', 'assist', 'support', 'need you']):
        response = random.choice(HELP_RESPONSES)
    elif any(word in text_lower for word in ['fight', 'battle', 'strong', 'challenge', 'sword']):
        response = random.choice(COMBAT_RESPONSES)
    elif any(word in text_lower for word in ['where', 'direction', 'lost', 'way']):
        response = random.choice(DIRECTION_RESPONSES)
    elif '?' in text:
        # For questions, combine an acknowledgment with a relevant response
        response = f"{random.choice(ACKNOWLEDGMENTS)} {random.choice(COMBAT_RESPONSES)}"
    else:
        # For statements, give a general response
        responses = ACKNOWLEDGMENTS + [
            "That's nothing compared to becoming the world's greatest swordsman.",
            "As long as it doesn't interfere with my training.",
            "Luffy would probably find that interesting.",
            "Sounds like something that cook would care about."
        ]
        response = random.choice(responses)
    
    return response

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_data = []
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received data length: {len(data) if data != 'DONE' else 'DONE'}")
                
                if data == "DONE":
                    logger.info("Received DONE signal, processing audio...")
                    if not audio_data:
                        logger.warning("No audio data received")
                        await websocket.send_json({
                            "type": "error",
                            "message": random.choice(CONFUSION)
                        })
                        continue

                    try:
                        # Convert base64 to audio data
                        logger.debug("Converting base64 to audio data...")
                        audio_bytes = base64.b64decode(audio_data[0])
                        
                        # Save to temporary WAV file
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                            temp_wav_path = temp_wav.name
                            temp_wav.write(audio_bytes)
                            logger.debug(f"Saved audio to temporary file: {temp_wav_path}")
                        
                        try:
                            # Transcribe with SpeechRecognition
                            logger.info("Starting transcription...")
                            with sr.AudioFile(temp_wav_path) as source:
                                audio = recognizer.record(source)
                                transcription = recognizer.recognize_google(audio)
                                logger.info(f"Transcription result: {transcription}")
                            
                            if not transcription:
                                raise ValueError("No transcription produced")
                            
                            # Generate Zoro-style response
                            response_text = generate_zoro_response(transcription)
                            logger.info(f"Generated response: {response_text}")
                            
                            # Get available voices
                            logger.info("Getting ElevenLabs voices...")
                            available_voices = voices()
                            if not available_voices:
                                raise ValueError("No ElevenLabs voices available")
                            
                            voice_id = available_voices[0].voice_id
                            logger.info(f"Using voice ID: {voice_id}")
                            
                            # Generate response using ElevenLabs
                            logger.info("Generating voice response...")
                            audio = generate(
                                text=response_text,
                                voice=voice_id,
                                model="eleven_monolingual_v1"
                            )
                            
                            # Convert audio to base64
                            audio_base64 = base64.b64encode(audio).decode('utf-8')
                            logger.debug("Audio response generated and converted to base64")
                            
                            # Send response
                            logger.info("Sending response to client...")
                            await websocket.send_json({
                                "type": "transcription",
                                "text": response_text,
                                "audio": audio_base64
                            })
                            logger.info("Response sent successfully")
                            
                        except sr.UnknownValueError:
                            error_response = random.choice(CONFUSION)
                            logger.error("Speech Recognition could not understand audio")
                            await websocket.send_json({
                                "type": "error",
                                "message": error_response
                            })
                        except sr.RequestError as e:
                            logger.error(f"Could not request results from Speech Recognition service: {str(e)}")
                            await websocket.send_json({
                                "type": "error",
                                "message": "Tch... something's interfering with my communication. Speak up!"
                            })
                        except Exception as e:
                            logger.error(f"Error during transcription/response: {str(e)}")
                            logger.error(traceback.format_exc())
                            await websocket.send_json({
                                "type": "error",
                                "message": "Hmph... something's not right here."
                            })
                        finally:
                            # Clean up temporary file
                            try:
                                os.unlink(temp_wav_path)
                                logger.debug("Temporary file cleaned up")
                            except Exception as e:
                                logger.error(f"Error cleaning up temp file: {str(e)}")
                        
                    except Exception as e:
                        logger.error(f"Error processing audio data: {str(e)}")
                        logger.error(traceback.format_exc())
                        await websocket.send_json({
                            "type": "error",
                            "message": "Something's interfering with my focus..."
                        })
                    
                    # Clear audio data
                    audio_data = []
                else:
                    # Accumulate audio data
                    audio_data.append(data)
                    logger.debug(f"Accumulated audio chunk. Total chunks: {len(audio_data)}")
                    
            except Exception as e:
                logger.error(f"Error in websocket loop: {str(e)}")
                logger.error(traceback.format_exc())
                await websocket.send_json({
                    "type": "error",
                    "message": "Tch... something went wrong."
                })
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("Closing WebSocket connection")
        await websocket.close() 
