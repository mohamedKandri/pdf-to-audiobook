from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ Import ALL functions at the TOP (fixes scoping error)
from app.pdf_processor import extract_text_from_pdf, parse_dialogue_text
from app.tts_engine import convert_text_to_audio, convert_dialogue_to_audio

# Optional: ElevenLabs import (will fail gracefully if not installed)
try:
    from app.elevenlabs_engine import convert_with_elevenlabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("ℹ️ ElevenLabs not available (install with: pip install elevenlabs)")

app = FastAPI(
    title="PDF to Audiobook API",
    description="Convert PDF documents to audio books using Text-to-Speech",
    version="1.0.0"
)

# CORS Settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://mohamedKandri.github.io",
        "https://mohamedkand.github.io",
        "https://pdf-audiobook-api.onrender.com",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure paths
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "🎧 PDF to Audiobook API is running!",
        "version": "1.0.0",
        "docs": "/docs",
        "elevenlabs_available": ELEVENLABS_AVAILABLE
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "upload_dir": str(UPLOAD_DIR),
        "output_dir": str(OUTPUT_DIR),
        "upload_dir_exists": UPLOAD_DIR.exists(),
        "output_dir_exists": OUTPUT_DIR.exists()
    }


@app.post("/api/v1/convert")
async def convert_pdf_to_audio(
    file: UploadFile = File(...),
    voice: str = "en-gb-female",
    dialogue_mode: bool = False,
    premium: bool = False
):
    """
    Full pipeline: Upload PDF → Extract Text → Generate Audio → Return URL
    """
    # 1. Validate File
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # 2. Save PDF
    unique_pdf_name = f"{file.filename}"
    pdf_path = UPLOAD_DIR / unique_pdf_name
    
    try:
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save PDF: {str(e)}")
    
    # 3. Extract Text
    try:
        text = extract_text_from_pdf(str(pdf_path))
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="No text found in PDF (might be scanned/image-based)")
        
        print(f"📝 Extracted {len(text)} characters from PDF")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")
    
    # 4. Convert to Audio
    try:
        if dialogue_mode:
            # Parse dialogue and convert with multiple voices
            segments = parse_dialogue_text(text)
            print(f"🎭 Parsed {len(segments)} dialogue segments")
            
            audio_filename = convert_dialogue_to_audio(segments, OUTPUT_DIR)
            
        elif premium and ELEVENLABS_AVAILABLE and os.getenv("ELEVENLABS_API_KEY"):
            # Use ElevenLabs for premium voices
            try:
                voice_map = {
                    "en-gb-female": "relaxed_female",
                    "en-gb-male": "relaxed_male",
                    "en-us-female": "storyteller_female",
                    "en-us-male": "deep_male",
                }
                elevenlabs_voice = voice_map.get(voice, "relaxed_female")
                
                audio_filename = convert_with_elevenlabs(text, OUTPUT_DIR, elevenlabs_voice)
                print(f"✅ Converted with ElevenLabs voice: {elevenlabs_voice}")
                
            except Exception as e:
                print(f"⚠️ ElevenLabs failed, falling back to gTTS: {str(e)}")
                # Fall back to gTTS - function is already imported at top ✅
                audio_filename = convert_text_to_audio(text, OUTPUT_DIR, voice)
        else:
            # Use gTTS (free) - function is already imported at top ✅
            audio_filename = convert_text_to_audio(text, OUTPUT_DIR, voice)
            
    except Exception as e:
        print(f"❌ Audio conversion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio conversion failed: {str(e)}")
    
    # 5. Return Result
    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    audio_url = f"{backend_url}/api/v1/audio/{audio_filename}"
    
    return JSONResponse(
        status_code=200,
        content={
            "message": "✅ Conversion successful",
            "original_file": file.filename,
            "audio_filename": audio_filename,
            "audio_url": audio_url,
            "text_length": len(text),
            "dialogue_mode": dialogue_mode,
            "segments_count": len(segments) if dialogue_mode else 1,
            "voice_used": voice,
            "premium_used": premium and ELEVENLABS_AVAILABLE
        }
    )


@app.get("/api/v1/audio/{filename}")
async def get_audio(filename: str):
    """Serve the generated audio file"""
    audio_path = OUTPUT_DIR / filename
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=audio_path,
        filename=filename,
        media_type="audio/mpeg"
    )


@app.delete("/api/v1/audio/{filename}")
async def delete_audio(filename: str):
    """Delete a generated audio file (cleanup)"""
    audio_path = OUTPUT_DIR / filename
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        audio_path.unlink()
        return {"message": f"✅ Deleted {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )