# holiday_grader.py
#
# Grades model answers from the holiday experiment CSV using a rubric-driven
# grader model on OpenRouter.

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

# Max number of rows to grade (None = all)
MAX_TO_GRADE = 3  # set to 10 for pilot; later change to None

PROJECT_DIR = r"C:\Main\Research\LazyHolidays"
DATA_DIR    = os.path.join(PROJECT_DIR, "data")
LOG_DIR     = os.path.join(PROJECT_DIR, "logs")  # not used yet, but ready

INPUT_CSV = os.path.join(
    DATA_DIR,
    "run_20251209_231758.csv",
)

OUTPUT_CSV = os.path.join(
    DATA_DIR,   # or LOG_DIR if you prefer graded files to live in logs
    f"run_20251209_231758_graded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
)


# --- API Key / Client ---
# Paste your actual OpenRouter key here on your machine.
# OPENROUTER_API_KEY = Your key here ^_^

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# --- Grader model ---
GRADER_MODEL = "openai/gpt-5.1"
# or, if you prefer the cheaper one:
# GRADER_MODEL = "openai/gpt-4.1-mini"


# You can swap to something like:
# GRADER_MODEL = "anthropic/claude-3.7-sonnet"

# Shuffle order before grading (helps with blinding)
SHUFFLE_ROWS = True

# Gentle rate-limit between calls
SLEEP_BETWEEN_CALLS = 1.0


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

Grade as you would for third- or fourth-year undergraduates at a good state university. Scores above 90 should correspond to clearly strong work, not just “basically correct.” Scores in the 70s represent adequate but imperfect work. Scores below 60 indicate serious problems for this level.

Please do not use web search or external tools- judge only the text of the student's answer against the assignment it claims to answer.

We thank you for taking the work seriously, grading consistently, and following the requested output format! 

---

ASSIGNMENT-SPECIFIC RUBRICS

A) ECONOMICS ASSIGNMENT - RUBRIC

1. Content / Conceptual Mastery (0-50)
Award higher scores when the answer:
- Correctly explains the SHORT-RUN effects of a binding minimum wage in a competitive labor market:
  - Wage set above equilibrium → quantity of labor demanded falls, quantity supplied rises → excess supply of labor (unemployment).
  - Employment falls relative to competitive equilibrium.
  - Total surplus falls; some surplus is redistributed from firms to employed workers; deadweight loss is created.
- Explicitly addresses unemployment, employment, and total surplus.
- Provides at least TWO DISTINCT LONG-RUN adjustment channels, for example:
  - Substitution toward capital/automation.
  - Changes in workforce composition (firms become choosier; low-skill workers are displaced).
  - Adjustments in non-wage margins (benefits, hours, job amenities).
  - Price pass-through and demand effects.
  - Firm entry/exit in affected industries.
- Avoids major conceptual confusions (e.g. mixing up supply vs demand; claiming minimum wage reduces unemployment).

2. Reasoning & Rigor (0-30)
Award higher scores when the answer:
- Uses clear comparative statics logic (“Because the wage is set above W*, firms demand less labor and…”).
- Separates short-run from long-run reasoning.
- Connects the policy change to outcomes via a clear chain of cause and effect.
- Shows some awareness of assumptions (competitive market, ceteris paribus).
- Avoids inconsistent or self-contradictory reasoning.

3. Communication (0-20)
Award higher scores when the answer:
- Is well organized (explicit parts (a) and (b) or clearly separated sections).
- Uses appropriate economic vocabulary (equilibrium, excess supply, deadweight loss, marginal, etc.) without glaring misuse.
- Is readable and coherent at the paragraph level.

---

B) PROGRAMMING / ALGORITHMS ASSIGNMENT - RUBRIC

The problem is: design an algorithm for the length of the longest strictly increasing subsequence (LIS) in an array that may contain duplicates.

1. Content / Conceptual Mastery (0-50)
Award higher scores when the answer:
- Describes a CORRECT algorithm for LIS, such as:
  - The classic O(n^2) dynamic programming solution:
    - For each index i, LIS ending at i = 1 + max LIS ending at j < i with a[j] < a[i], etc.
  - OR the O(n log n) “tails array” / patience sorting style solution:
    - Maintain an array where tails[k] is the minimum possible tail value of an increasing subsequence of length k+1, updated via binary search.
- Correctly states and explains the time complexity:
  - O(n^2) for the straightforward DP, or O(n log n) for the optimized method.
- Recognizes that the subsequence is not required to be contiguous and must be strictly increasing.
- Addresses the presence of duplicates correctly (e.g., uses > rather than >= in comparisons for strictness).

2. Reasoning & Rigor (0-30)
Award higher scores when the answer:
- Explains the algorithm step by step, not just naming it.
  - For DP: initialization, nested loops, update rule, and how the final answer is obtained.
  - For tails method: how binary search is used to place each element, and why the length of the tails array gives the LIS length.
- Provides at least a high-level justification of correctness (e.g., why the DP recurrence captures all increasing subsequences, or why tails[k] is maintained as the best possible tail).
- Mentions edge cases (empty array, single-element array) or at least doesn't contradict them.

3. Communication (0-20)
Award higher scores when the answer:
- Uses readable pseudocode or clearly structured prose so that another programmer could implement the algorithm.
- Separates part (a) (algorithm + complexity) from part (b) (implementation outline), or clearly indicates when each part is being addressed.
- Uses sensible variable names and clear sentences.

---

C) ENGLISH / LITERATURE ASSIGNMENT (Lord Jim / Marlow - 3-part question) - RUBRIC

1. Content / Conceptual Mastery (0-50)
Award higher scores when the answer:
- Directly and substantively addresses ALL THREE parts: (a), (b), and (c). Partial coverage (e.g., only (a)+(b)) should not receive top scores.
- For (a): Explains why Marlow is so invested in Jim's story in a way that goes beyond “he finds it interesting”:
  - Identifies what Marlow seems to be working through for himself (e.g., guilt, complicity, questions of honour, failure, “romantic” ideals of seafaring, the problem of judgment).
- For (b): Analyzes the phrase "one of us":
  - Identifies what “us” refers to (e.g., seamen, Europeans, a professional/moral community, a colonial or racial in-group).
  - Explores what anxieties or tensions the phrase reveals (e.g., fear that Jim's failure reflects on the group; anxiety about who belongs inside/outside the circle of honourable men; unease about moral contamination).
- For (c): Discusses how Marlow's narrative structure shapes the reader's understanding of Jim:
  - Recognizes Marlow's layered, recursive storytelling (multiple tellings, framed conversations, gaps and delays in disclosure).
  - Explains how this structure affects Jim's character and legacy (e.g., makes Jim more ambiguous, mythic, or contested; shows Jim as a story others argue over rather than a simple “case”; blurs the line between Jim as person and Jim as narrative object).
- Shows a solid grasp of Lord Jim and Marlow's role as narrator, not just vague gestures.

2. Reasoning & Rigor (0-30)
Award higher scores when the answer:
- Clearly distinguishes between and organizes responses to (a), (b), and (c), either explicitly labeled or clearly segmented.
- Moves beyond plot summary into interpretation for each part:
  - For (a): connects Marlow's investment to specific aspects of his voice, comments, or reactions.
  - For (b): draws out implications of "one of us" with attention to community boundaries and unease, not just “it means they are similar.”
  - For (c): links specific structural features (frame narrative, repetition, delays, second-hand reports) to their effects on our perception of Jim.
- Uses brief, concrete references to the text (scenes, recurring phrases, patterns in Marlow's telling) to support claims, even if quotations are paraphrased.
- Avoids major misreadings or wild, unsupported assertions.

3. Communication (0-20)
Award higher scores when the answer:
- Is organized in a way that makes it easy to see how (a), (b), and (c) are being answered (e.g., separate paragraphs or clearly signposted transitions).
- Presents a coherent overall voice, with reasonably polished prose appropriate for an upper-division literature course.
- Uses relevant literary/narratological vocabulary where helpful (narrator, frame narrative, focalization, theme, audience, etc.) without obvious misuse.
- Maintains clarity at the sentence and paragraph level, so that the reader can follow the argument without having to reconstruct it.
"""


# =========================
# USER PROMPT BUILDER
# =========================

def make_user_prompt(subject: str, blind_id: str, answer_text: str) -> str:
    """
    Build the grading prompt for a single answer.

    IMPORTANT: We DO NOT mention prime here. The grader only sees subject + ID + answer.
    """
    if subject == "econ":
        subject_label = "Economics"
        assignment_label = "Minimum Wage in a Competitive Labor Market"
    elif subject in ("cs", "prog", "programming"):
        subject_label = "Programming"
        assignment_label = "Longest Strictly Increasing Subsequence"
    elif subject in ("eng", "english", "lit", "literature"):
        subject_label = "English"
        assignment_label = "Lord Jim ' Marlow as Narrator (3-part question)"
    else:
        raise ValueError(f"Unknown subject/task code: {subject!r}")

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

2. Then briefly justify the scores in three labeled 1–3 sentence sections:
- Conceptual Mastery:
- Reasoning & Rigor:
- Communication:
"""


# =========================
# PARSING UTILITIES
# =========================

_score_line_re = re.compile(r"(\d+)\s*/\s*(\d+)")


def parse_scores(text: str):
    """
    Parse the four score lines from the grader's response.

    Expects lines like:
    - Content / Conceptual Mastery: X/50
    - Reasoning & Rigor: Y/30
    - Communication: Z/20
    - Total Score: T/100
    """
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

def grade_one_answer(blind_id: str, subject: str, answer_text: str):
    """Send one answer to the grader model and return raw response + parsed scores."""
    user_prompt = make_user_prompt(subject=subject, blind_id=blind_id, answer_text=answer_text)

    messages = [
        {"role": "system", "content": GRADER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    response = client.chat.completions.create(
        model=GRADER_MODEL,
        messages=messages,
        temperature=0.0,          # deterministic grading
        max_tokens=800,
        # Reasoning config per OpenRouter docs; sent in extra_body for the OpenAI SDK. :contentReference[oaicite:1]{index=1}
        extra_body={
            "reasoning": {
                "effort": "high",   # tweak to "high" if you want max try-hard grading
                "exclude": True       # use reasoning internally but don't return chain-of-thought text
            }
        },
    )

    text = response.choices[0].message.content
    content, reasoning, communication, total = parse_scores(text)

    return {
        "grader_raw": text,
        "content_score": content,
        "reasoning_score": reasoning,
        "communication_score": communication,
        "total_score": total,
    }


# =========================
# MAIN PIPELINE
# =========================

def main():
    # --- Load input CSV ---
    rows = []
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print("No rows found in input CSV.")
        return

    # Only keep tasks we know how to grade
    valid_tasks = {"econ", "cs", "prog", "programming", "eng", "english", "lit", "literature"}
    rows = [r for r in rows if r["task"] in valid_tasks]

    if not rows:
        print("No rows with recognizable tasks (econ/cs/eng).")
        return

    # Assign blind IDs and shuffle order if desired
    indices = list(range(len(rows)))
    if SHUFFLE_ROWS:
        random.shuffle(indices)

    if MAX_TO_GRADE is not None:
        indices = indices[:MAX_TO_GRADE]


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

            print(f"Grading {blind_id} (task={task}, case_id={row['case_id']})...")

            try:
                grade_result = grade_one_answer(
                    blind_id=blind_id,
                    subject=task,
                    answer_text=answer_text,
                )
            except Exception as e:
                print(f"Error grading {blind_id}: {e}")
                grade_result = {
                    "grader_raw": f"ERROR: {e}",
                    "content_score": None,
                    "reasoning_score": None,
                    "communication_score": None,
                    "total_score": None,
                }

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

    print(f"Done. Wrote graded results to {OUTPUT_CSV!r}.")


if __name__ == "__main__":
    main()

