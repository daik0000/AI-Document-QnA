import pdfplumber
from docx import Document as DocxDocument
from fastapi import HTTPException, status

def extract_text_from_pdf(file_path: str) -> str:
    try:
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text: # Check if page_text is not None
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text from PDF: {str(e)}"
        )

def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = DocxDocument(file_path)
        text_parts = [para.text for para in doc.paragraphs if para.text]  # Only include non-empty paragraphs
        return "\n".join(text_parts)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text from DOCX: {str(e)}"
        )

def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text from TXT: {str(e)}"
        )

def extract_text(file_path: str, file_type: str) -> str:
    extractors = {
        "pdf": extract_text_from_pdf,
        "docx": extract_text_from_docx,
        "txt": extract_text_from_txt,
    }

    extractor = extractors.get(file_type.lower())

    if extractor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type for text extraction: {file_type}"
        )

    text = extractor(file_path)
    if not text or not text.strip():  # Check if text is empty or only whitespace
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"No text could be extracted from the file: {file_path}"
        )

    return text