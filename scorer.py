"""
scorer.py
---------
Turns "job description text" + "resume text" into a similarity score (0-1)
and a short human-readable reason.

How the scoring works (this is the core idea of the whole agent):

1. EMBEDDING: We send text to Google's Gemini embedding model. It returns a
   list of numbers (a "vector") that represents the MEANING of that text.
   Texts about similar topics end up with similar vectors.

2. COSINE SIMILARITY: We compare two vectors (JD vector vs resume vector)
   using cosine similarity - a standard math formula that outputs a number
   from -1 to 1 (in practice ~0 to 1 for real text) measuring how close in
   "meaning-space" two vectors are. 1.0 = identical meaning, 0 = unrelated.

   This is NOT keyword matching. A resume that says "led backend systems"
   can score well against a JD asking for "server-side engineering
   experience" even though the exact words differ - because their MEANING
   is similar.

3. REASONING: For the top candidates only (to save API cost/time), we ask
   the LLM one direct question: "why does this resume match or not match?"
   This gives a human-readable explanation alongside the raw number.
"""

import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # loads GEMINI_API_KEY from .env before the client is created

client = genai.Client()  # reads GEMINI_API_KEY from environment

EMBEDDING_MODEL = "gemini-embedding-001"
CHAT_MODEL = "gemini-3.6-flash"


def get_embedding(text: str) -> np.ndarray:
    """Converts text into a numeric vector representing its meaning."""
    # Embedding models have input limits; trim very long resumes defensively.
    text = text.replace("\n", " ").strip()[:8000]
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )
    return np.array(response.embeddings[0].values)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Standard cosine similarity formula:
        similarity = (A . B) / (||A|| * ||B||)
    Returns a value from -1 to 1. For text embeddings, real-world scores
    typically land between 0.1 (unrelated) and 0.9 (near-identical).
    """
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))


def score_resume(jd_embedding: np.ndarray, resume_text: str) -> dict:
    """
    Scores a single resume against a job description embedding.
    Returns {"score": float, "embedding": np.ndarray} so the embedding
    can be reused later if needed (e.g. for reasoning) without recomputing.
    """
    resume_embedding = get_embedding(resume_text)
    score = cosine_similarity(jd_embedding, resume_embedding)
    return {"score": round(score, 4)}


def generate_reasoning(jd_text: str, resume_text: str, candidate_name: str) -> str:
    """
    Asks the LLM to explain, in plain English, why this resume is (or isn't)
    a good match. Used only for top candidates to keep API calls low.
    """
    prompt = f"""You are a recruiting assistant. Compare this resume against
the job description and explain the match in 1-2 short sentences.
Mention specific skills that matched and any obvious gaps.

JOB DESCRIPTION:
{jd_text}

RESUME ({candidate_name}):
{resume_text[:3000]}

Respond with ONLY the 1-2 sentence explanation, no preamble."""

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3),
    )
    return response.text.strip()
