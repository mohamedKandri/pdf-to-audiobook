from gtts import gTTS
from pathlib import Path
import uuid
import os
import time

def convert_text_to_audio(text: str, output_dir: Path, voice: str = "en-us-female") -> str:
    """
    Converts text to audio with voice selection (gTTS - free).
    Handles large texts by chunking.
    """
    try:
        # Generate unique filename
        audio_filename = f"{uuid.uuid4().hex}.mp3"
        audio_path = output_dir / audio_filename
        
        # gTTS limit is 5000 chars, but we'll use 4500 to be safe
        max_chars = 4500
        
        if len(text) <= max_chars:
            # Single chunk - fast path
            lang, tld = get_voice_settings(voice)
            tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
            tts.save(str(audio_path))
        else:
            # Multiple chunks - concatenate
            audio_filename = convert_text_to_audio_chunked(text, output_dir, voice)
        
        return audio_filename
        
    except Exception as e:
        raise Exception(f"Failed to convert to audio: {str(e)}")


def get_voice_settings(voice: str) -> tuple:
    """Map voice name to language code and TLD"""
    voice_map = {
        "en-us-female": ("en", "com"),
        "en-us-male": ("en", "com"),
        "en-gb-female": ("en", "co.uk"),
        "en-gb-male": ("en", "co.uk"),
        "en-au-female": ("en", "com.au"),
        "en-in-male": ("en", "co.in"),
    }
    return voice_map.get(voice, ("en", "com"))


def convert_text_to_audio_chunked(text: str, output_dir: Path, voice: str) -> str:
    """Convert long text by splitting into chunks and concatenating"""
    try:
        from pydub import AudioSegment
        
        # Split text into chunks (respect word boundaries)
        chunks = split_text_into_chunks(text, max_chars=4500)
        print(f"📝 Split text into {len(chunks)} chunks")
        
        combined = AudioSegment.empty()
        temp_files = []
        lang, tld = get_voice_settings(voice)
        
        for i, chunk_text in enumerate(chunks):
            print(f"🎙️ Converting chunk {i+1}/{len(chunks)}...")
            
            # Generate audio for this chunk
            chunk_filename = f"chunk_{uuid.uuid4().hex}.mp3"
            chunk_path = output_dir / chunk_filename
            
            tts = gTTS(text=chunk_text, lang=lang, tld=tld, slow=False)
            tts.save(str(chunk_path))
            temp_files.append(chunk_path)
            
            # Load and append
            chunk_audio = AudioSegment.from_mp3(str(chunk_path))
            
            # Add small pause between chunks (50ms)
            if i > 0:
                combined += AudioSegment.silent(duration=50)
            
            combined += chunk_audio
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        # Save combined audio
        final_filename = f"{uuid.uuid4().hex}.mp3"
        final_path = output_dir / final_filename
        combined.export(str(final_path), format="mp3", bitrate="128k")
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                temp_file.unlink()
            except:
                pass
        
        print(f"✅ Chunked conversion complete: {final_filename}")
        return final_filename
        
    except ImportError:
        # pydub not available - truncate text
        print("⚠️ pydub not available, truncating to 4500 chars")
        lang, tld = get_voice_settings(voice)
        audio_filename = f"{uuid.uuid4().hex}.mp3"
        audio_path = output_dir / audio_filename
        tts = gTTS(text=text[:4500], lang=lang, tld=tld, slow=False)
        tts.save(str(audio_path))
        return audio_filename
    except Exception as e:
        raise Exception(f"Chunked conversion failed: {str(e)}")


def split_text_into_chunks(text: str, max_chars: int = 4500) -> list:
    """Split text into chunks at sentence/word boundaries"""
    chunks = []
    
    while len(text) > max_chars:
        # Try to split at sentence boundary
        split_point = text.rfind('. ', 0, max_chars)
        if split_point == -1:
            # Try paragraph boundary
            split_point = text.rfind('\n', 0, max_chars)
        if split_point == -1:
            # Try word boundary
            split_point = text.rfind(' ', 0, max_chars)
        if split_point == -1:
            # Just split at max_chars
            split_point = max_chars
        
        chunks.append(text[:split_point + 1].strip())
        text = text[split_point + 1:].strip()
    
    # Add remaining text
    if text.strip():
        chunks.append(text.strip())
    
    return chunks


def convert_dialogue_to_audio(segments: list, output_dir: Path) -> str:
    """
    Converts dialogue segments to audio with different voices, then concatenates them.
    Handles large segments with chunking.
    """
    try:
        from pydub import AudioSegment
        
        combined = AudioSegment.empty()
        temp_files = []
        
        for i, (voice, text) in enumerate(segments):
            print(f"🎭 Converting segment {i+1}/{len(segments)} with voice: {voice}")
            
            # For each segment, use chunking if needed
            if len(text) > 4500:
                segment_filename = convert_text_to_audio_chunked(text, output_dir, voice)
            else:
                segment_filename = convert_text_to_audio(text, output_dir, voice)
            
            segment_path = output_dir / segment_filename
            temp_files.append(segment_path)
            
            # Load and append
            segment_audio = AudioSegment.from_mp3(str(segment_path))
            
            # Add small pause between dialogue segments (150ms)
            if i > 0:
                combined += AudioSegment.silent(duration=150)
            
            combined += segment_audio
        
        # Save combined audio
        final_filename = f"{uuid.uuid4().hex}.mp3"
        final_path = output_dir / final_filename
        combined.export(str(final_path), format="mp3", bitrate="128k")
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                temp_file.unlink()
            except:
                pass
        
        print(f"✅ Dialogue conversion complete: {final_filename}")
        return final_filename
        
    except ImportError:
        print("⚠️ pydub not available, using single voice")
        full_text = " ".join([text for _, text in segments])
        return convert_text_to_audio(full_text, output_dir, segments[0][0])
    except Exception as e:
        raise Exception(f"Failed to convert dialogue: {str(e)}")