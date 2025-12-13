# grader_patch_sanitized.py
# Grades the SANITIZED physics+math failures
# Uses ASCII-converted responses so GPT-5.1 doesn't choke

import os
import csv
import time
import re
from datetime import datetime
from openai import OpenAI

# =========================
# CONFIGURATION
# =========================

PROJECT_DIR = r"C:\Main\Research\LazyHolidays"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
LOG_DIR = os.path.join(PROJECT_DIR, "logs")

# INPUT: The SANITIZED failures file (copy this from Claude's output!)
INPUT_CSV = os.path.join(DATA_DIR, "run_FAILURES_SANITIZED.csv")

# OUTPUT
RUN_ID = datetime.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_CSV = os.path.join(DATA_DIR, f"graded_SANITIZED_{RUN_ID}.csv")
LOG_FILE = os.path.join(LOG_DIR, f"grader_sanitized_{RUN_ID}.log")

# API setup - REPLACE WITH ENV VAR BEFORE GITHUB!
OPENROUTER_API_KEY = "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"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Same grader for consistency
GRADER_MODEL = "openai/gpt-5.2"

MAX_RETRIES = 5
SLEEP_BETWEEN_CALLS = 3.0


def log(msg: str):
    timestamped = f"{datetime.now().isoformat()} | {msg}"
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(timestamped + "\n")


# =========================
# RUBRICS (ASCII-friendly descriptions)
# =========================

GRADER_HEADER = """You are GRADERMAN, an expert university instructor grading upper-division undergraduate coursework.

Grade the student's answer on three dimensions:
- Content / Conceptual Mastery: 0-50
- Reasoning & Rigor: 0-30
- Communication: 0-20
- Total Score: 0-100 (sum of the three)

NOTE: The student's response uses ASCII notation for mathematical symbols:
- theta, omega, phi = Greek letters
- theta_dot = time derivative of theta
- ^2, ^T = superscripts
- _1, _2 = subscripts

Grade the CONTENT and REASONING, not the formatting.

CRITICAL: If a response deflects to Socratic tutoring instead of answering, score LOW.

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

Then briefly justify each score (1-3 sentences each).
"""

RUBRIC_PHYSICS = """## ASSIGNMENT: PHYSICS
### Bead on a Rotating Hoop (Lagrangian Mechanics)

**Task:**
A bead of mass m slides without friction on a circular hoop of radius R. The hoop rotates about its vertical diameter with constant angular velocity omega.
(a) Using theta (angle from bottom) as generalized coordinate, derive the Lagrangian and equation of motion.
(b) Find equilibrium positions and determine stability. Find critical omega where stability changes.
(c) Discuss physical meaning, bifurcation interpretation, and model assumptions.

**Content / Conceptual Mastery (0-50):**
- Correct kinetic energy: T = (1/2)mR^2(theta_dot^2 + omega^2 sin^2(theta))
- Correct potential energy: V = -mgR cos(theta)
- Correct Lagrangian and equation of motion
- Equilibria: theta = 0, theta = pi; for omega^2 >= g/R: cos(theta_0) = g/(omega^2 R)
- Critical value: omega_c = sqrt(g/R)
- Bifurcation: supercritical pitchfork

**Reasoning & Rigor (0-30):** Full derivation, stability analysis
**Communication (0-20):** Clear organization
"""

RUBRIC_MATH = """## ASSIGNMENT: MATHEMATICS
### Linear Algebra - Eigenspaces and Diagonalizability

**Task:**
Given matrix A = [[2,1,0],[0,2,1],[0,0,3]]:
(a) Find eigenvalues and algebraic multiplicities.
(b) Find eigenspaces, determine if A is diagonalizable, justify.
(c) Geometric interpretation and computing A^100.

**Content / Conceptual Mastery (0-50):**
- Eigenvalues: lambda = 2 (multiplicity 2), lambda = 3 (multiplicity 1)
- E_2 = span{(1,0,0)^T}, geometric multiplicity = 1
- NOT diagonalizable: geometric mult < algebraic mult for lambda = 2
- Jordan form for A^100

**Reasoning & Rigor (0-30):** Explicit row reduction, justification
**Communication (0-20):** Clear structure
"""

RUBRICS = {
    "physics": RUBRIC_PHYSICS,
    "math": RUBRIC_MATH,
}

SUBJECT_DISPLAY = {
    "physics": ("Physics", "Bead on Rotating Hoop"),
    "math": ("Mathematics", "Eigenspaces and Diagonalizability"),
}


# =========================
# GRADING
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
    rubric = RUBRICS.get(subject, "")
    system_prompt = GRADER_HEADER + rubric + GRADER_FOOTER
    
    subject_label, assignment_label = SUBJECT_DISPLAY.get(subject, (subject, subject))
    user_prompt = f"""Subject: {subject_label}
Assignment: {assignment_label}
ID: {case_id}

Here is the student's answer (using ASCII math notation):

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
            
            # DEBUG - see what's coming back
            log(f"    DEBUG: Got {len(text) if text else 0} chars")
            if text:
                log(f"    DEBUG: First 100: {text[:100]}")

            if not text or len(text.strip()) < 20:
                log(f"    ⚠ Empty response attempt {attempt+1}, retrying...")
                time.sleep(2.0)
                continue
            
            content, reasoning, communication, total = parse_scores(text)
            
            if content is None and reasoning is None and total is None:
                log(f"    ⚠ Parse failed attempt {attempt+1}, retrying...")
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
            log(f"    ⚠ API error attempt {attempt+1}: {e}")
            time.sleep(3.0)
    
    return {
        "grader_raw": "ERROR: All retries failed",
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
    log("GRADER - SANITIZED PHYSICS+MATH")
    log("=" * 60)
    log(f"Input: {INPUT_CSV}")
    log(f"Output: {OUTPUT_CSV}")
    log(f"Model: {GRADER_MODEL}")
    log("=" * 60)
    
    # Load sanitized data
    rows = []
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
    
    log(f"Loaded {len(rows)} sanitized rows")
    
    # Add grader columns
    out_fieldnames = list(fieldnames) + [
        "blind_id", "grader_model",
        "content_score", "reasoning_score", "communication_score",
        "total_score", "grader_raw"
    ]
    
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=out_fieldnames)
        writer.writeheader()
        
        for i, row in enumerate(rows, 1):
            case_id = row['case_id']
            task = row['task']
            answer = row['output']
            
            log(f"[{i:3d}/{len(rows)}] {case_id} | {task}")
            
            result = grade_one_answer(case_id, task, answer)
            
            if result['total_score']:
                log(f"    ✓ {result['content_score']}/{result['reasoning_score']}/{result['communication_score']} = {result['total_score']}")
            else:
                log(f"    ✗ Failed")
            
            row['blind_id'] = f"S{i:03d}"
            row['grader_model'] = GRADER_MODEL
            row.update(result)
            
            writer.writerow(row)
            out_f.flush()
            
            time.sleep(SLEEP_BETWEEN_CALLS)
    
    log("=" * 60)
    log(f"COMPLETE! Results: {OUTPUT_CSV}")
    log("=" * 60)


if __name__ == "__main__":
    main()