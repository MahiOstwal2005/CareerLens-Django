import os
import PyPDF2
import docx
import urllib.request
import re

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
        elif ext in ['.txt', '.html']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
                if ext == '.html':
                    # Simple regex to strip HTML tags
                    text = re.sub('<[^<]+>', ' ', text)
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text.strip()

def extract_text_from_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        # Strip script/style tags and then html tags
        html = re.sub(r'<script.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style.*?</style>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub('<[^<]+>', ' ', html)
        return text.strip()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return ""
