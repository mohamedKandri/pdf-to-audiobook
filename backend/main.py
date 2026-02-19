from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import os

# Import our new modules
from app.pdf_processor import extract_text_from_pdf
from app.tts_engine import convert_text_to_audio

app = FastAPI(
    title="PDF to Audiobook API",
    version="0.2.0"
)

# CORS Settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    return {"message": "🎧 PDF to Audiobook API is running!", "version": "0.2.0"}


@app.post("/api/v1/convert")
async def convert_pdf_to_audio(file: UploadFile = File(...)):
    """
    Full pipeline: Upload PDF -> Extract Text -> Generate Audio -> Return URL
    """
    # 1. Validate File
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # 2. Save PDF
    file_extension = Path(file.filename).suffix
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
            raise HTTPException(status_code=400, detail="No text found in PDF (might be scanned)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # 4. Convert to Audio
    try:
        audio_filename = convert_text_to_audio(text, OUTPUT_DIR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # 5. Return Result
    audio_url = f"http://127.0.0.1:8000/api/v1/audio/{audio_filename}"
    
    return JSONResponse(
        status_code=200,
        content={
            "message": "✅ Conversion successful",
            "original_file": file.filename,
            "audio_filename": audio_filename,
            "audio_url": audio_url,
            "text_length": len(text)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)