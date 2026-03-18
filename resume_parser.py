import pdfplumber
from typing import Optional

def extract_text_from_pdf(uploaded_file) -> Optional[str]:
    """
    Extracts text from an uploaded PDF file using pdfplumber.
    Much more accurate than PyPDF2, handles multi-column layouts.
    """
    if uploaded_file is None:
        return None

    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join(
                page.extract_text() for page in pdf.pages if page.extract_text()
            )
        return text.strip() or None
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
