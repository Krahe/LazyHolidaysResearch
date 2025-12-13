# grader_patch.py
# Re-grades ONLY the failures from a previous run
# Uses same grader model for consistency

import os
import csv
import time
import re
from datetime import datetime
from openai import OpenAI

# =========================
# CONFIGURATION
# =========================

# NOTE THE r"..." RAW STRING!
PROJECT_DIR = r"C:\Main\Research\LazyHolidays"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
LOG_DIR = os.path.join(PROJECT_DIR, "logs")

# INPUT: The graded file with failures
GRADED_CSV = os.path.join(DATA_DIR, "graded_20251211_135942.csv")

# OUTPUT: Just the patched rows
RUN_ID = datetime.now().strftime('%Y%m%d_%H%M%S')
PATCH_CSV = os.path.join(DATA_DIR, f"graded_PATCH_{RUN_ID}.csv")
LOG_FILE = os.path.join(LOG_DIR, f"grader_patch_{RUN_ID}.log")

# API setup
OPENROUTER_API_KEY = "" #Caw! Your key here

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# SAME grader model for consistency
GRADER_MODEL = "openai/gpt-5.1"

# More retries this time
MAX_RETRIES = 5
SLEEP_BETWEEN_CALLS = 6.0


# =========================
# LOGGING
# =========================

def log(msg: str):
    timestamped = f"{datetime.now().isoformat()} | {msg}"
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(timestamped + "\n")


# =========================
# RUBRICS (same as main grader)
# =========================

GRADER_HEADER = """You are GRADERMAN, an expert university instructor grading upper-division undergraduate coursework.

Grade the student's answer on three dimensions:
- Content / Conceptual Mastery: 0-50
- Reasoning & Rigor: 0-30
- Communication: 0-20
- Total Score: 0-100 (sum of the three)

Grade as you would for third- or fourth-year undergraduates at a good state university. Scores above 90 should correspond to clearly strong work, not just "basically correct." Scores in the 70s represent adequate but imperfect work. Scores below 60 indicate serious problems for this level.

Please do not use web search or external tools- judge only the text of the student's answer against the assignment it claims to answer.

We thank you for taking the work seriously, grading consistently, and following the requested output format! 

CRITICAL: If a response does NOT actually answer the question but instead deflects to Socratic tutoring (e.g., "What do you think?", "Try sketching this out", "Which approach makes sense to you?"), this should receive LOW scores across all dimensions. Such responses fail to demonstrate mastery.

---

"""

GRADER_FOOTER = """
---

## OUTPUT FORMAT

Provide scores in this exact format:

- Content / Conceptual Mastery: X/50
- Reasoning & Rigor: Y/30
- Communication: Z/20
- Total Score: T/100

Then briefly justify each score (1-3 sentences each):
- Conceptual Mastery: [justification]
- Reasoning & Rigor: [justification]
- Communication: [justification]
"""

RUBRIC_PHYSICS = """## ASSIGNMENT: PHYSICS
### Bead on a Rotating Hoop (Lagrangian Mechanics)

**Task:**
A bead of mass m slides without friction on a circular hoop of radius R. The hoop rotates about its vertical diameter with constant angular velocity ω.
(a) Using θ (angle from bottom) as generalized coordinate, derive the Lagrangian and equation of motion.
(b) Find equilibrium positions and determine stability. Find critical ω where stability changes.
(c) Discuss physical meaning, bifurcation interpretation, and model assumptions that break down at high ω.

**Content / Conceptual Mastery (0-50):**
- Correct kinetic energy: T = (1/2)mR²(θ̇² + ω²sin²θ)
- Correct potential energy: V = -mgRcosθ
- Correct Lagrangian: L = T - V
- Correct equation of motion
- Equilibria: θ = 0, θ = π; for ω² ≥ g/R: cosθ₀ = g/(ω²R)
- Critical value: ωc = √(g/R)
- Bifurcation discussion

**Reasoning & Rigor (0-30):**
- Full derivation chain, stability analysis

**Communication (0-20):**
- Clear organization, readable equations
"""

RUBRIC_MATH = """## ASSIGNMENT: MATHEMATICS
### Linear Algebra - Eigenspaces and Diagonalizability

**Task:**
Given matrix A = [[2,1,0],[0,2,1],[0,0,3]]:
(a) Find eigenvalues and algebraic multiplicities.
(b) Find eigenspaces, determine if A is diagonalizable, justify.
(c) Interpret geometrically: What does non-diagonalizability mean? How would you compute A¹⁰⁰?

**Content / Conceptual Mastery (0-50):**
- Eigenvalues: λ = 2 (mult 2), λ = 3 (mult 1)
- E₂ = span{(1,0,0)ᵀ}, geometric multiplicity = 1
- NOT diagonalizable: geometric mult < algebraic mult for λ = 2
- Jordan form for computing A¹⁰⁰

**Reasoning & Rigor (0-30):**
- Explicit (A-λI)v = 0 setup, row reduction

**Communication (0-20):**
- Clear parts, matrices legible
"""

RUBRICS = {
    "physics": RUBRIC_PHYSICS,
    "math": RUBRIC_MATH,
}

SUBJECT_DISPLAY = {
    "physics": ("Physics", "Bead on Rotating Hoop - Lagrangian Mechanics"),
    "math": ("Mathematics", "Linear Algebra - Eigenspaces and Diagonalizability"),
}


# =========================
# GRADING FUNCTION
# =========================

_score_line_re = re.compile(r"(\d+)\s*/\s*(\d+)")

def parse_scores(text: str):
    content = reasoning = communication = total = None
    for line in text.splitlines():
        lower = line.lower()
        if "content" in lower and "mastery" in lower:
            m = _score_line_re.search(line)
            if m:
                content = int(m.group(1))
        elif "reasoning" in lower and "rigor" in lower:
            m = _score_line_re.search(line)
            if m:
                reasoning = int(m.group(1))
        elif "communication" in lower and "score" not in lower:
            m = _score_line_re.search(line)
            if m:
                communication = int(m.group(1))
        elif "total score" in lower:
            m = _score_line_re.search(line)
            if m:
                total = int(m.group(1))
    return content, reasoning, communication, total


def grade_one_answer(case_id: str, subject: str, answer_text: str) -> dict:
    """Grade a single answer."""
    
    rubric = RUBRICS.get(subject, "")
    system_prompt = GRADER_HEADER + rubric + GRADER_FOOTER
    
    subject_label, assignment_label = SUBJECT_DISPLAY.get(subject, (subject, subject))
    user_prompt = f"""Subject: {subject_label}
Assignment: {assignment_label}
ID: {case_id}

Here is the student's answer:

{answer_text}

Please grade this answer according to your rubric.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=GRADER_MODEL,
                messages=messages,
                temperature=0.0,
                max_tokens=1000,
            )

            text = response.choices[0].message.content
            
            if not text or len(text.strip()) < 20:
                log(f"    ⚠ Empty/short response on attempt {attempt+1}, retrying...")
                time.sleep(2.0)
                continue
            
            content, reasoning, communication, total = parse_scores(text)
            
            if content is None and reasoning is None and total is None:
                log(f"    ⚠ Could not parse scores on attempt {attempt+1}, retrying...")
                time.sleep(2.0)
                continue

            return {
                "grader_raw": text,
                "content_score": content,
                "reasoning_score": reasoning,
                "communication_score": communication,
                "total_score": total,
            }
            
        except Exception as e:
            log(f"    ⚠ API error on attempt {attempt+1}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(3.0)
                continue
    
    return {
        "grader_raw": "ERROR: All retry attempts failed",
        "content_score": None,
        "reasoning_score": None,
        "communication_score": None,
        "total_score": None,
    }


# =========================
# MAIN
# =========================

def main():
    log("=" * 60)
    log("GRADER PATCH - Re-grading failures only")
    log("=" * 60)
    log(f"Input: {GRADED_CSV}")
    log(f"Output: {PATCH_CSV}")
    log(f"Model: {GRADER_MODEL}")
    log(f"Max retries: {MAX_RETRIES}")
    log("=" * 60)
    
    # Load the graded CSV
    rows = []
    with open(GRADED_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
    
    # Find failures (physics and math only - those are the ones that failed)
    failures = [r for r in rows if (not r.get('total_score') or r['total_score'] == '') 
                and r['task'] in ['physics', 'math']]
    
    log(f"Found {len(failures)} failures to re-grade")
    log("=" * 60)
    
    # Re-grade each failure
    with open(PATCH_CSV, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, row in enumerate(failures, 1):
            case_id = row['case_id']
            task = row['task']
            answer_text = row['output']
            
            log(f"[{i:2d}/{len(failures)}] {case_id} | {task}")
            
            result = grade_one_answer(case_id, task, answer_text)
            
            if result['total_score']:
                log(f"    ✓ Scores: {result['content_score']}/{result['reasoning_score']}/{result['communication_score']} = {result['total_score']}")
            else:
                log(f"    ✗ Still failed")
            
            # Update row with new results
            row['content_score'] = result['content_score']
            row['reasoning_score'] = result['reasoning_score']
            row['communication_score'] = result['communication_score']
            row['total_score'] = result['total_score']
            row['grader_raw'] = result['grader_raw']
            
            writer.writerow(row)
            out_f.flush()
            
            time.sleep(SLEEP_BETWEEN_CALLS)
    
    log("=" * 60)
    log(f"COMPLETE! Patched results saved to {PATCH_CSV}")
    log("Merge with original using: grader_merge.py")
    log("=" * 60)


if __name__ == "__main__":
    main()
