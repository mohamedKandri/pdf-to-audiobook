from gtts import gTTS
from pathlib import Path
import uuid

def convert_text_to_audio(text: str, output_dir: Path) -> str:
    """
    Converts text to audio using Google TTS.
    Returns the filename of the generated audio.
    """
    try:
        # Generate unique filename
        audio_filename = f"{uuid.uuid4().hex}.mp3"
        audio_path = output_dir / audio_filename
        
        # Limit text length for MVP (gTTS has limits)
        # For long books, you'd need to chunk this (advanced)
        max_chars = 5000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."  # Truncate for demo
        
        # Generate Audio
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(str(audio_path))
        
        return audio_filename
    except Exception as e:
        raise Exception(f"Failed to convert to audio: {str(e)}")