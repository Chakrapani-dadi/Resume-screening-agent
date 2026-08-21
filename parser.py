"""
parser.py
---------
Extracts raw text from a resume file, regardless of format (PDF, DOCX, TXT).

Why this file exists on its own:
Every resume format stores text differently under the hood. This module's
only job is: "give me a file path, get back plain text." Everything else
(scoring, ranking) doesn't need to know or care what format the file was.
"""

import os
import pdfplumber
from docx import Document


def extract_text(file_path: str) -> str:
    """
    Reads a resume file and returns its plain text content.
    Supports .pdf, .docx, and .txt files.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_from_pdf(file_path)
    elif ext == ".docx":
        return _extract_from_docx(file_path)
    elif ext == ".txt":
        return _extract_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext} (use .pdf, .docx, or .txt)")


def _extract_from_pdf(file_path: str) -> str:
    text_chunks = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
    return "\n".join(text_chunks)


def _extract_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _extract_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_all_resumes(folder_path: str) -> dict:
    """
    Reads every supported resume file in a folder.
    Returns {filename: extracted_text}.
    """
    resumes = {}
    for filename in sorted(os.listdir(folder_path)):
        ext = os.path.splitext(filename)[1].lower()
        if ext in (".pdf", ".docx", ".txt"):
            file_path = os.path.join(folder_path, filename)
            try:
                resumes[filename] = extract_text(file_path)
            except Exception as e:
                print(f"⚠️  Skipping {filename}: {e}")
    return resumes
