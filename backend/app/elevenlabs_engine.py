from pathlib import Path
import uuid
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def convert_with_elevenlabs(text: str, output_dir: Path, voice_id: str = "relaxed_female") -> str:
    """
    Convert text to speech using ElevenLabs premium voices.
    Much more natural and relaxing than gTTS.
    """
    try:
        from elevenlabs import generate, save
        
        # Voice IDs - relaxing, natural voices
        VOICES = {
            "relaxed_female": "EXAVITQu4vr4xnSDxMaL",  # Bella - calm, warm
            "relaxed_male": "21m00Tcm4TlvDq8ikWAM",    # Rachel - professional
            "storyteller_female": "MF3mGyEYCl7XYWbV9V6O",  # Elli - narrative
            "deep_male": "AZnzlk1XvdvUeBnXmlld",      # Domi - deep, calm
            "soft_female": "2EiwWnXFnvU5JabPnv8n",     # Sarah - soft, gentle
        }
        
        audio_filename = f"{uuid.uuid4().hex}.mp3"
        audio_path = output_dir / audio_filename
        
        # Generate audio
        audio = generate(
            text=text,
            voice=VOICES.get(voice_id, VOICES["relaxed_female"]),
            model="eleven_monolingual_v1",
            stability=0.5,
            similarity_boost=0.75
        )
        
        save(audio, str(audio_path))
        return audio_filename
        
    except Exception as e:
        print(f"⚠️ ElevenLabs error: {str(e)}")
        raise Exception(f"ElevenLabs conversion failed: {str(e)}")