import pdfplumber
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