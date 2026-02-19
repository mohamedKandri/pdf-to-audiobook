import pdfplumber
import re
from pathlib import Path

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file.
    Returns clean text string.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
        
        # Basic cleaning
        text = text.replace("\n", " ")
        text = text.replace("- ", "")  # Fix hyphenated words
        text = " ".join(text.split())  # Remove extra spaces
        
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text: {str(e)}")


def parse_dialogue_text(text: str) -> list:
    """
    Parses text with [VOICE] tags and returns list of (voice, text) tuples.
    
    Supported tags:
    - [NARRATOR] or [FEMALE] → Female voice (default)
    - [MALE] → Male voice
    - [UK-MALE] → British male voice
    - [UK-FEMALE] → British female voice
    
    Example input:
    "[NARRATOR] Once upon a time [MALE] 'Hello!' he said [FEMALE] 'Hi!' she replied"
    
    Returns:
    [("en-us-female", "Once upon a time"), ("en-us-male", "'Hello!' he said"), ...]
    """
    segments = []
    current_voice = "en-us-female"  # Default voice
    
    # Split by voice tags
    pattern = r'\[(NARRATOR|MALE|FEMALE|UK-MALE|UK-FEMALE)\]'
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    
    voice_map = {
        "NARRATOR": "en-us-female",
        "FEMALE": "en-us-female",
        "MALE": "en-us-male",
        "UK-MALE": "en-gb-male",
        "UK-FEMALE": "en-gb-female",
    }
    
    for i, part in enumerate(parts):
        if not part:
            continue
            
        part_upper = part.upper().strip()
        
        if part_upper in voice_map:
            # This is a voice tag - update current voice
            current_voice = voice_map[part_upper]
        elif part.strip():
            # This is actual text - add segment with current voice
            segments.append((current_voice, part.strip()))
    
    # If no tags found, return entire text with default voice
    return segments if segments else [("en-us-female", text)]

def parse_dialogue_text(text: str) -> list:
    """
    Parses text with [VOICE] tags (case-insensitive).
    """
    segments = []
    current_voice = "en-gb-female"  # Default to British female (calmer)
    
    # Split by voice tags (case-insensitive)
    pattern = r'\[(NARRATOR|MALE|FEMALE|UK-MALE|UK-FEMALE|BRITISH-MALE|BRITISH-FEMALE)\]'
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    
    voice_map = {
        "NARRATOR": "en-gb-female",
        "FEMALE": "en-gb-female",
        "BRITISH-FEMALE": "en-gb-female",
        "MALE": "en-gb-male",
        "UK-MALE": "en-gb-male",
        "BRITISH-MALE": "en-gb-male",
        "UK-FEMALE": "en-gb-female",
    }
    
    for i, part in enumerate(parts):
        if not part:
            continue
        
        part_upper = part.upper().strip()
        
        if part_upper in voice_map:
            current_voice = voice_map[part_upper]
        elif part.strip():
            segments.append((current_voice, part.strip()))
    
    return segments if segments else [("en-gb-female", text)]