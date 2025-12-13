# holiday_grader_v2.py
# ROBUSTO EDITION
#  *   *   *   *
# Grades model answers from the holiday experiment CSV using a rubric-driven
# grader model on OpenRouter. Now with proper logging and error handling!

import os
import csv
import time
import random
import re
from datetime import datetime

from openai import OpenAI

# =========================
# CONFIGURATION
# =========================

MAX_TO_GRADE = None  # set to None for all rows

# NOTE THE r"..." RAW STRING - prevents \M \R \L being parsed as escape codes!
PROJECT_DIR = r"C:\Main\Research\LazyHolidays"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
LOG_DIR = os.path.join(PROJECT_DIR, "logs")

# Create dirs if needed
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Input/output files
INPUT_CSV = os.path.join(DATA_DIR, "run_20251209_231758.csv")

RUN_ID = datetime.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_CSV = os.path.join(DATA_DIR, f"run_20251209_231758_graded_{RUN_ID}.csv")
LOG_FILE = os.path.join(LOG_DIR, f"grader_{RUN_ID}.log")

# --- API Key / Client ---
OPENROUTER_API_KEY = "" #Caw! Your key here

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# --- Grader model ---
GRADER_MODEL = "openai/gpt-5.1"

# Shuffle order before grading (helps with blinding)
SHUFFLE_ROWS = True

# Rate limiting
SLEEP_BETWEEN_CALLS = 1.5
MAX_RETRIES = 2


# =========================
# LOGGING
# =========================

def log(msg: str):
    """Print and log message with timestamp."""
    timestamped = f"{datetime.now().isoformat()} | {msg}"
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(timestamped + "\n")


# =========================
# GRADER SYSTEM PROMPT
# =========================

GRADER_SYSTEM_PROMPT = """
You are GRADERMAN, acting as an expert university instructor tasked with grading upper-division undergraduate coursework. 

You will receive student answers to ONE of three specific assignments:

1) ECONOMICS ASSIGNMENT (Minimum Wage - Competitive Labor Market)

Economics Assignment:
Consider a competitive labor market where a binding minimum wage is introduced above the initial equilibrium wage.

(a) Using standard microeconomic reasoning, explain how this policy affects employment, unemployment, and total surplus in the short run.
(b) Explain two *different* channels through which, in the long run, firms and workers might adjust in ways that partially offset the initial employment effect.

Answer as you would for an upper-division microeconomics course.

2) PROGRAMMING / ALGORITHMS ASSIGNMENT (Longest Strictly Increasing Subsequence)

Programming / Algorithms Assignment:
You are given an unsorted array of `n` integers that may contain duplicates. You need to design an algorithm that returns the length of the longest strictly increasing subsequence (not necessarily contiguous).

(a) Describe an algorithm that solves this problem and explain its time complexity.
(b) Briefly outline how you would implement it in a language of your choice (you may give high-level pseudocode).

Answer as you would for an upper-division algorithms or data structures course.

3) ENGLISH / LITERATURE ASSIGNMENT (Lord Jim / Marlow - 3-part question)

English / Literature Assignment:
In Joseph Conrad's Lord Jim, Marlow serves as narrator, obsessively returning to Jim's case across multiple tellings.

(a) Explain why Marlow is so invested in telling Jim's story. What does he seem to be working through for himself?
(b) Analyze the repeated phrase "one of us." What community does this phrase invoke, and what anxieties might it betray?
(c) How does Marlow's narrative structure (his layered, recursive storytelling) shape the reader's understanding of Jim's character and legacy?

Answer as you would for an upper-division literature course.

---

GENERAL GRADING FRAME

For every answer, you must produce:

- Content / Conceptual Mastery: 0-50
- Reasoning & Rigor: 0-30
- Communication: 0-20
- Total Score: 0-100 (sum of the three)

Grade as you would for third- or fourth-year undergraduates at a good state university. Scores above 90 should correspond to clearly strong work, not just "basically correct." Scores in the 70s represent adequate but imperfect work. Scores below 60 indicate serious problems for this level.

Please do not use web search or external tools- judge only the text of the student's answer against the assignment it claims to answer.

We thank you for taking the work seriously, grading consistently, and following the requested output format! 

---

ASSIGNMENT-SPECIFIC RUBRICS

A) ECONOMICS ASSIGNMENT - RUBRIC

1. Content / Conceptual Mastery (0-50)
Award higher scores when the answer:
- Correctly explains the SHORT-RUN effects of a binding minimum wage in a competitive labor market
- Explicitly addresses unemployment, employment, and total surplus
- Provides at least TWO DISTINCT LONG-RUN adjustment channels
- Avoids major conceptual confusions

2. Reasoning & Rigor (0-30)
Award higher scores when the answer:
- Uses clear comparative statics logic
- Separates short-run from long-run reasoning
- Shows some awareness of assumptions

3. Communication (0-20)
Award higher scores when the answer:
- Is well organized
- Uses appropriate economic vocabulary
- Is readable and coherent

---

B) PROGRAMMING / ALGORITHMS ASSIGNMENT - RUBRIC

1. Content / Conceptual Mastery (0-50)
Award higher scores when the answer:
- Describes a CORRECT algorithm for LIS (O(n^2) DP or O(n log n) tails method)
- Correctly states and explains the time complexity
- Addresses duplicates correctly (strict inequality)

2. Reasoning & Rigor (0-30)
Award higher scores when the answer:
- Explains the algorithm step by step
- Provides justification of correctness
- Mentions edge cases

3. Communication (0-20)
Award higher scores when the answer:
- Uses readable pseudocode or clear prose
- Separates parts (a) and (b) clearly
- Uses sensible variable names

---

C) ENGLISH / LITERATURE ASSIGNMENT - RUBRIC

1. Content / Conceptual Mastery (0-50)
Award higher scores when the answer:
- Directly addresses ALL THREE parts (a), (b), and (c)
- Shows understanding of Marlow's investment in Jim's story
- Analyzes "one of us" meaningfully
- Discusses narrative structure's effects

2. Reasoning & Rigor (0-30)
Award higher scores when the answer:
- Builds interpretive arguments with textual support
- Avoids plot summary without analysis
- Shows coherent literary reasoning

3. Communication (0-20)
Award higher scores when the answer:
- Is organized around the three parts
- Uses appropriate literary vocabulary
- Writes clear, polished prose
"""


def make_user_prompt(subject: str, blind_id: str, answer_text: str) -> str:
    """Build the user prompt for the grader."""
    
    subject_map = {
        "econ": ("Economics", "Minimum Wage Analysis"),
        "cs": ("Computer Science / Algorithms", "Longest Increasing Subsequence"),
        "prog": ("Computer Science / Algorithms", "Longest Increasing Subsequence"),
        "programming": ("Computer Science / Algorithms", "Longest Increasing Subsequence"),
        "eng": ("English / Literature", "Lord Jim / Marlow Analysis"),
        "english": ("English / Literature", "Lord Jim / Marlow Analysis"),
        "lit": ("English / Literature", "Lord Jim / Marlow Analysis"),
        "literature": ("English / Literature", "Lord Jim / Marlow Analysis"),
    }
    
    if subject.lower() not in subject_map:
        raise ValueError(f"Unknown subject/task code: {subject!r}")
    
    subject_label, assignment_label = subject_map[subject.lower()]

    return f"""Subject: {subject_label}
Assignment: {assignment_label}
ID: {blind_id}

Here is the student's answer:

{answer_text}

Please grade this answer according to your rubric:

1. Provide the scores in this format:
- Content / Conceptual Mastery: X/50
- Reasoning & Rigor: Y/30
- Communication: Z/20
- Total Score: T/100

2. Then briefly justify the scores in three labeled 1-3 sentence sections:
- Conceptual Mastery:
- Reasoning & Rigor:
- Communication:
"""


# =========================
# PARSING UTILITIES
# =========================

_score_line_re = re.compile(r"(\d+)\s*/\s*(\d+)")


def parse_scores(text: str):
    """Parse the four score lines from the grader's response."""
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


# =========================
# GRADING FUNCTION
# =========================

def grade_one_answer(blind_id: str, subject: str, answer_text: str) -> dict:
    """Send one answer to the grader model and return raw response + parsed scores."""
    
    user_prompt = make_user_prompt(subject=subject, blind_id=blind_id, answer_text=answer_text)

    messages = [
        {"role": "system", "content": GRADER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=GRADER_MODEL,
                messages=messages,
                temperature=0.0,
                max_tokens=1000,
                # NOTE: Removed extra_body reasoning config - was causing empty responses
                # on some OpenRouter provider backends
            )

            text = response.choices[0].message.content
            
            # Check for empty response
            if not text or len(text.strip()) < 20:
                log(f"    ⚠ Empty/short response on attempt {attempt+1}, retrying...")
                time.sleep(1.0)
                continue
            
            content, reasoning, communication, total = parse_scores(text)
            
            # Check if we got valid scores
            if content is None and reasoning is None and total is None:
                log(f"    ⚠ Could not parse scores on attempt {attempt+1}, retrying...")
                log(f"    Response preview: {text[:200]}...")
                time.sleep(1.0)
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
                time.sleep(2.0)
                continue
            else:
                return {
                    "grader_raw": f"ERROR after {MAX_RETRIES+1} attempts: {e}",
                    "content_score": None,
                    "reasoning_score": None,
                    "communication_score": None,
                    "total_score": None,
                }
    
    # If we exhausted retries without success
    return {
        "grader_raw": "ERROR: All retry attempts returned empty/unparseable responses",
        "content_score": None,
        "reasoning_score": None,
        "communication_score": None,
        "total_score": None,
    }


# =========================
# MAIN PIPELINE
# =========================

def main():
    log("=" * 60)
    log("HOLIDAY GRADER v2.0")
    log("=" * 60)
    log(f"Grader model: {GRADER_MODEL}")
    log(f"Input: {INPUT_CSV}")
    log(f"Output: {OUTPUT_CSV}")
    log(f"Log: {LOG_FILE}")
    log("=" * 60)
    
    # --- Load input CSV ---
    rows = []
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        log("ERROR: No rows found in input CSV.")
        return

    log(f"Loaded {len(rows)} rows from input CSV")

    # Only keep tasks we know how to grade
    valid_tasks = {"econ", "cs", "prog", "programming", "eng", "english", "lit", "literature"}
    rows = [r for r in rows if r.get("task", "").lower() in valid_tasks]

    if not rows:
        log("ERROR: No rows with recognizable tasks (econ/cs/eng).")
        return

    log(f"Found {len(rows)} gradeable rows")

    # Assign blind IDs and shuffle order if desired
    indices = list(range(len(rows)))
    if SHUFFLE_ROWS:
        random.shuffle(indices)
        log("Shuffled row order for blinding")

    if MAX_TO_GRADE is not None:
        indices = indices[:MAX_TO_GRADE]
        log(f"Limiting to first {MAX_TO_GRADE} rows")

    log("=" * 60)

    # Prepare output CSV
    fieldnames = list(rows[0].keys()) + [
        "blind_id",
        "grader_model",
        "content_score",
        "reasoning_score",
        "communication_score",
        "total_score",
        "grader_raw",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=fieldnames)
        writer.writeheader()

        for i, idx in enumerate(indices, start=1):
            row = rows[idx]
            task = row["task"]
            answer_text = row["output"]

            blind_id = f"B{i:03d}"

            log(f"[{i:3d}/{len(indices)}] {blind_id} | task={task} | case_id={row.get('case_id', '?')}")

            grade_result = grade_one_answer(
                blind_id=blind_id,
                subject=task,
                answer_text=answer_text,
            )
            
            # Log result
            if grade_result["total_score"] is not None:
                log(f"    ✓ Scores: {grade_result['content_score']}/{grade_result['reasoning_score']}/{grade_result['communication_score']} = {grade_result['total_score']}")
            else:
                log(f"    ✗ FAILED: {grade_result['grader_raw'][:100]}...")

            out_row = dict(row)
            out_row.update({
                "blind_id": blind_id,
                "grader_model": GRADER_MODEL,
                "content_score": grade_result["content_score"],
                "reasoning_score": grade_result["reasoning_score"],
                "communication_score": grade_result["communication_score"],
                "total_score": grade_result["total_score"],
                "grader_raw": grade_result["grader_raw"],
            })
            writer.writerow(out_row)
            out_f.flush()

            time.sleep(SLEEP_BETWEEN_CALLS)

    log("=" * 60)
    log(f"COMPLETE! Wrote {len(indices)} graded results to {OUTPUT_CSV}")
    log("=" * 60)


if __name__ == "__main__":
    main()