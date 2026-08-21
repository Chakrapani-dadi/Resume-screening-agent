# Resume Screening Agent

Ranks a folder of resumes (PDF/DOCX/TXT) against a job description using
semantic similarity, and outputs a scored, ordered shortlist with reasoning.

## What it does

1. Reads a job description (`job_description.txt`).
2. Reads every resume in `sample_resumes/`.
3. Converts the JD and each resume into a numeric "meaning vector"
   (embedding) using Google's Gemini embedding model.
4. Computes **cosine similarity** between each resume's vector and the JD's
   vector — a score from 0 to 1 showing how close their *meaning* is (not
   just keyword overlap).
5. Ranks resumes by score, and asks the LLM for a short plain-English
   explanation for the top matches.
6. Writes results to `output/ranked_candidates.json` and `.csv`.

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Add your Gemini API key**
```bash
cp .env.example .env
# then edit .env and paste your key:
# GEMINI_API_KEY=...
```
Get a free key at https://aistudio.google.com/apikey

**3. Run the agent**
```bash
python main.py
```

That's it. Sample resumes are already included in `sample_resumes/`
(11 resumes, mix of `.pdf` and `.docx`) and a sample job description is in
`job_description.txt`.

To regenerate the sample resumes yourself (optional):
```bash
python generate_samples.py
```

## Project structure

```
resume-screener/
├── main.py               # orchestrates the full pipeline
├── parser.py               # extracts text from PDF/DOCX/TXT resumes
├── scorer.py                 # embeddings + cosine similarity + LLM reasoning
├── generate_samples.py         # (optional) generates sample resume files
├── job_description.txt
├── sample_resumes/               # 11 sample resumes, mixed formats
├── output/
│   ├── ranked_candidates.json
│   └── ranked_candidates.csv
├── requirements.txt
└── .env.example
```

## How the scoring works

This agent uses **embeddings + cosine similarity**, not keyword matching:

- Gemini's embedding model turns text into a list of numbers representing
  its *meaning*.
- Two texts about similar topics end up with similar vectors, even if they
  use different words. E.g. a resume saying "led backend systems" scores
  well against a JD asking for "server-side engineering experience"
  because the *meaning* overlaps, not the exact words.
- Cosine similarity measures the angle between two vectors: `1.0` = same
  meaning, `0.0` = unrelated. In practice, resume-vs-JD scores usually land
  between ~0.15 (irrelevant) and ~0.55 (strong match) — embedding
  similarity scores compress toward the middle of the range compared to
  raw human intuition, so relative ranking matters more than the absolute
  number.
- For the **top 5** candidates only, the agent makes one additional LLM
  call asking it to explain *why* the resume matches — this keeps API
  costs low while still giving human-readable reasoning for the
  candidates a recruiter would actually look at.

## Sample output

See `output/ranked_candidates.json` and `output/ranked_candidates.csv`
after running. Example row:

```json
{
  "filename": "priya_sharma.docx",
  "score": 0.51,
  "rank": 1,
  "reasoning": "Strong match: extensive Python/FastAPI backend experience, PostgreSQL optimization, Docker/Kubernetes, and AWS CI/CD — directly aligned with the JD's core requirements."
}
```

## Tradeoffs & what I'd improve with more time

- **No skill/experience extraction layer.** The agent scores whole-resume
  text against the whole JD rather than first extracting structured fields
  (years of experience, specific skills list) and scoring those separately.
  A structured extraction pass first would make scoring more precise and
  auditable, at the cost of more LLM calls and complexity.
- **Reasoning is only generated for the top 5.** This was a deliberate
  cost/time tradeoff for the 12-hour window — every candidate could get a
  reasoning string, but that multiplies API calls linearly with resume
  count.
- **No de-duplication or resume-quality checks.** A truncated or corrupted
  PDF still gets scored; it would help to flag resumes where extracted
  text is suspiciously short.
- **Cosine similarity alone can be gamed by keyword-stuffed resumes** since
  it operates on meaning density, not verified claims. In production, this
  would be paired with the reasoning step (already present) and ideally
  human review before any hiring decision.
- **Single embedding per resume.** Long resumes get truncated to fit
  input limits, which can lose information at the bottom of dense resumes.
  Chunking + averaging embeddings would fix this with more engineering time.
