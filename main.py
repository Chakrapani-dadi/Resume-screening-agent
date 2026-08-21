"""
main.py
-------
The pipeline. This is the "loop" every agent needs:

    Input -> Fetch data -> Send to AI model -> Receive answer -> Output

Run with:  python main.py
"""

import os
import json
import csv
from dotenv import load_dotenv

from parser import load_all_resumes
from scorer import get_embedding, score_resume, generate_reasoning

load_dotenv()  # loads GEMINI_API_KEY from .env

JD_PATH = "job_description.txt"
RESUME_FOLDER = "sample_resumes"
OUTPUT_JSON = "output/ranked_candidates.json"
OUTPUT_CSV = "output/ranked_candidates.csv"
TOP_N_FOR_REASONING = 5  # only ask the LLM for reasoning on the top N matches


def main():
    print("📄 Loading job description...")
    with open(JD_PATH, "r", encoding="utf-8") as f:
        jd_text = f.read()

    print("📁 Loading resumes...")
    resumes = load_all_resumes(RESUME_FOLDER)
    print(f"   Found {len(resumes)} resumes.")

    print("🧠 Embedding job description...")
    jd_embedding = get_embedding(jd_text)

    print("🔍 Scoring each resume against the job description...")
    results = []
    for filename, resume_text in resumes.items():
        if not resume_text.strip():
            print(f"⚠️  {filename} appears empty, skipping.")
            continue
        scored = score_resume(jd_embedding, resume_text)
        results.append({
            "filename": filename,
            "score": scored["score"],
            "resume_text": resume_text,
        })

    # Rank: highest similarity first
    results.sort(key=lambda r: r["score"], reverse=True)

    print(f"💬 Generating reasoning for top {TOP_N_FOR_REASONING} candidates...")
    for i, r in enumerate(results):
        if i < TOP_N_FOR_REASONING:
            r["reasoning"] = generate_reasoning(jd_text, r["resume_text"], r["filename"])
        else:
            r["reasoning"] = "(reasoning skipped past top candidates to save API calls)"
        r["rank"] = i + 1
        del r["resume_text"]  # don't clutter the output file with full text

    os.makedirs("output", exist_ok=True)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rank", "filename", "score", "reasoning"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Done. Ranked {len(results)} candidates.")
    print(f"   JSON: {OUTPUT_JSON}")
    print(f"   CSV:  {OUTPUT_CSV}\n")

    print("Top 3 candidates:")
    for r in results[:3]:
        print(f"  #{r['rank']} {r['filename']} — score {r['score']}")
        print(f"      {r['reasoning']}")


if __name__ == "__main__":
    main()
