import os
import PyPDF2
import docx

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    try:
        if ext == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    if page.extract_text():
                        text += page.extract_text() + " "
        elif ext == '.docx':
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + " "
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text.strip()
