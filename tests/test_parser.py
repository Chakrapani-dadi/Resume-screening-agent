"""
test_parser.py
---------------
Tests for parser.py's text extraction. Uses the real sample resumes already
bundled in sample_resumes/, so these tests double as a check that the sample
data itself is readable.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import extract_text, load_all_resumes

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_resumes")


def test_extract_text_from_docx_returns_nonempty_string():
    docx_files = [f for f in os.listdir(SAMPLE_DIR) if f.endswith(".docx")]
    assert docx_files, "expected at least one sample .docx resume"
    text = extract_text(os.path.join(SAMPLE_DIR, docx_files[0]))
    assert isinstance(text, str)
    assert len(text.strip()) > 0


def test_extract_text_from_pdf_returns_nonempty_string():
    pdf_files = [f for f in os.listdir(SAMPLE_DIR) if f.endswith(".pdf")]
    assert pdf_files, "expected at least one sample .pdf resume"
    text = extract_text(os.path.join(SAMPLE_DIR, pdf_files[0]))
    assert isinstance(text, str)
    assert len(text.strip()) > 0


def test_extract_text_rejects_unsupported_extension():
    try:
        extract_text("resume.exe")
        assert False, "expected extract_text to raise ValueError for unsupported extension"
    except ValueError:
        pass


def test_load_all_resumes_finds_all_sample_files():
    resumes = load_all_resumes(SAMPLE_DIR)
    expected_count = len([f for f in os.listdir(SAMPLE_DIR) if f.endswith((".pdf", ".docx", ".txt"))])
    assert len(resumes) == expected_count
    assert all(isinstance(text, str) and len(text.strip()) > 0 for text in resumes.values())
