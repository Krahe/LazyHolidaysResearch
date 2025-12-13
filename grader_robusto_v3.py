# grader_robusto_v3.py
# ROBUSTO EDITION v3.0 - MODULAR PER-SUBJECT PROMPTS
# ~8× more token efficient than mega-prompt approach!
#
# 7 subjects: CS, Econ, Lit, Physics, Biochem, Math, Philosophy, Tech & Society

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

# Input/output files - UPDATE THIS FOR EACH RUN
INPUT_CSV = os.path.join(DATA_DIR, "run_20251211_084623.csv")

RUN_ID = datetime.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_CSV = os.path.join(DATA_DIR, f"graded_{RUN_ID}.csv")
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
# MODULAR GRADER PROMPTS
# =========================

# Shared header for all subjects
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

# Shared footer for all subjects
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


# =========================
# INDIVIDUAL SUBJECT RUBRICS
# =========================

RUBRIC_CS = """## ASSIGNMENT: COMPUTER SCIENCE / ALGORITHMS
### Longest Strictly Increasing Subsequence

**Task:**
Given an unsorted array of n integers (may contain duplicates), design an algorithm that returns the length of the longest strictly increasing subsequence (not necessarily contiguous).
(a) Describe an algorithm and explain its time complexity.
(b) Outline implementation in pseudocode.

**Content / Conceptual Mastery (0-50):**
- Describes a CORRECT algorithm for LIS:
  - O(n²) DP: dp[i] = length of LIS ending at index i; dp[i] = 1 + max(dp[j]) for all j < i where arr[j] < arr[i]
  - OR O(n log n) tails method: maintain array where tails[k] = smallest tail of increasing subsequences of length k+1, update via binary search
- Correctly states time complexity
- Handles duplicates correctly (strict inequality: < not ≤)

Score bands:
- 45-50: Both algorithms OR one with excellent depth, correct complexities
- 38-44: One correct algorithm with correct complexity, clear understanding
- 30-37: Correct algorithm but complexity wrong or explanation unclear
- 20-29: Partial understanding, significant gaps
- 0-19: Fundamentally incorrect or incomplete

**Reasoning & Rigor (0-30):**
- 25-30: Step-by-step explanation, initialization, recurrence, final answer extraction, correctness justification
- 18-24: Mostly clear but some steps abbreviated
- 10-17: Algorithm named but not explained
- 0-9: No coherent explanation

**Communication (0-20):**
- 17-20: Well-organized, readable pseudocode, clear prose
- 12-16: Understandable but could be cleaner
- 6-11: Disorganized or hard to follow
- 0-5: Incoherent
"""


RUBRIC_ECON = """## ASSIGNMENT: ECONOMICS
### Minimum Wage in Competitive Labor Market

**Task:**
Consider a competitive labor market where a binding minimum wage is introduced above equilibrium.
(a) Explain effects on employment, unemployment, and total surplus in the short run.
(b) Explain two different long-run adjustment channels that might partially offset initial employment effects.

**Content / Conceptual Mastery (0-50):**
- SHORT-RUN effects correctly explained:
  - Wage above equilibrium → Qd falls, Qs rises → excess supply (unemployment)
  - Employment falls to Qd (demand-determined)
  - Total surplus falls; deadweight loss; some surplus redistributed to employed workers
- TWO DISTINCT long-run channels, such as:
  - Capital/automation substitution
  - Workforce composition changes (firms become choosier)
  - Non-wage margin adjustments (benefits, hours, amenities)
  - Price pass-through and demand effects
  - Firm entry/exit
  - Efficiency wage effects (productivity increases)
  - Human capital investment
- Avoids major confusions

Score bands:
- 45-50: All short-run effects correct, two distinct long-run channels with clear mechanisms
- 38-44: Mostly correct, minor gaps in one area
- 30-37: Partial understanding, one channel weak or unclear
- 20-29: Major conceptual errors but some relevant content
- 0-19: Fundamentally incorrect

**Reasoning & Rigor (0-30):**
- 25-30: Clear comparative statics, separates short-run from long-run, cause-effect chains explicit
- 18-24: Solid but some shortcuts
- 10-17: Assertions without clear reasoning
- 0-9: Incoherent or contradictory

**Communication (0-20):**
- 17-20: Well-organized, appropriate economic vocabulary
- 12-16: Clear but informal
- 6-11: Disorganized
- 0-5: Incoherent
"""


RUBRIC_LIT = """## ASSIGNMENT: ENGLISH / LITERATURE
### Lord Jim / Marlow Analysis

**Task:**
In Joseph Conrad's Lord Jim, Marlow serves as narrator, obsessively returning to Jim's case.
(a) Explain why Marlow is so invested in telling Jim's story. What does he seem to be working through for himself?
(b) Analyze the repeated phrase "one of us." What community does this phrase invoke, and what anxieties might it betray?
(c) How does Marlow's narrative structure (layered, recursive storytelling) shape the reader's understanding of Jim's character and legacy?

**Content / Conceptual Mastery (0-50):**
- Addresses ALL THREE parts (a), (b), and (c)
- Shows understanding of Marlow's investment (identification, moral reckoning, professional identity)
- Analyzes "one of us" meaningfully (maritime community, colonial/racial undertones, anxieties about failure/honor)
- Discusses narrative structure's effects (uncertainty, multiple perspectives, reader as judge)

Score bands:
- 45-50: All three parts with depth, textual awareness, sophisticated interpretation
- 38-44: All parts addressed, mostly strong but one area thinner
- 30-37: Two parts strong, one weak or missing
- 20-29: Superficial treatment, plot summary dominates
- 0-19: Fundamentally misunderstands or ignores parts

**Reasoning & Rigor (0-30):**
- 25-30: Builds interpretive arguments with textual support, avoids plot summary without analysis
- 18-24: Solid interpretation but light on evidence
- 10-17: Assertions without support
- 0-9: Incoherent or contradictory

**Communication (0-20):**
- 17-20: Organized around three parts, appropriate literary vocabulary, polished prose
- 12-16: Clear but informal
- 6-11: Disorganized
- 0-5: Incoherent
"""


RUBRIC_PHYSICS = """## ASSIGNMENT: PHYSICS
### Bead on a Rotating Hoop (Lagrangian Mechanics)

**Task:**
A bead of mass m slides without friction on a circular hoop of radius R. The hoop rotates about its vertical diameter with constant angular velocity ω.
(a) Using θ (angle from bottom) as generalized coordinate, derive the Lagrangian and equation of motion.
(b) Find equilibrium positions and determine stability. Find critical ω where stability changes.
(c) Discuss physical meaning, bifurcation interpretation, and model assumptions that break down at high ω.

**Content / Conceptual Mastery (0-50):**

**(a) Lagrangian & Equation of Motion:**
- Correct kinetic energy: T = (1/2)mR²(θ̇² + ω²sin²θ)
- Correct potential energy: V = -mgRcosθ (or equivalent)
- Correct Lagrangian: L = T - V
- Correct equation of motion: θ̈ = sinθ(ω²cosθ - g/R) or equivalent

**(b) Equilibria & Stability:**
- Equilibria: θ = 0 (bottom), θ = π (top); for ω² ≥ g/R: cosθ₀ = g/(ω²R)
- Stability: θ = π always unstable; θ = 0 stable if ω < ωc, unstable if ω > ωc; tilted equilibria stable when they exist
- Critical value: ωc = √(g/R)

**(c) Physical Interpretation:**
- Bifurcation: supercritical pitchfork (one stable → one unstable + two stable)
- Model breakdowns at high ω: hoop rigidity, friction, air resistance, bead losing contact

Score bands:
- 45-50: All parts correct, clear bifurcation discussion, multiple model limitations
- 38-44: Minor errors but correct physics and critical ω
- 30-37: Lagrangian mostly right but equation of motion has errors, or stability misclassified
- 20-29: Significant gaps, some relevant ideas
- 0-19: Fundamentally incorrect

**Reasoning & Rigor (0-30):**
- 25-30: Full derivation chain, distinguishes equilibrium from stability, clear bifurcation logic
- 18-24: Mostly complete but some steps abbreviated
- 10-17: Results stated without derivation
- 0-9: Confused or contradictory

**Communication (0-20):**
- 17-20: Clear parts (a), (b), (c), proper notation, readable equations
- 12-16: Understandable but notation sloppy
- 6-11: Hard to follow
- 0-5: Incoherent
"""


RUBRIC_BIOCHEM = """## ASSIGNMENT: BIOCHEMISTRY
### PEP Bioenergetics and Coupled Reactions

**Task:**
Given: PEP hydrolysis ΔG°' = -61.9 kJ/mol; ATP synthesis ΔG°' = +30.5 kJ/mol.
(a) Calculate ΔG°' for coupled reaction: PEP + ADP → Pyruvate + ATP
(b) Calculate actual ΔG at 37°C given: [ATP]/[ADP] = 10, [PEP] = 0.02 mM, [Pyruvate] = 0.05 mM. Is reaction still favorable?
(c) Discuss: Why is PEP "high-energy"? When might reaction become less favorable? How do cells maintain favorable conditions?

**Content / Conceptual Mastery (0-50):**

**(a) Coupled ΔG°':**
- ΔG°' = -61.9 + 30.5 = -31.4 kJ/mol (accept -31 to -32)

**(b) Actual ΔG:**
- Q = [Pyruvate][ATP] / [PEP][ADP] = (0.05/0.02) × 10 = 25
- ΔG = ΔG°' + RTlnQ; RT ≈ 2.58 kJ/mol at 310K; ln(25) ≈ 3.22
- ΔG ≈ -31.4 + 8.3 = -23.1 kJ/mol (accept -21 to -25)
- Conclusion: Still favorable (negative ΔG)

**(c) Biological Significance:**
- PEP "high-energy" because: hydrolysis releases enol-pyruvate → tautomerizes to keto-pyruvate (very favorable); resonance stabilization; product stability, NOT bond strength
- Less favorable: high [Pyruvate], high [ATP]/[ADP], low [PEP]
- Cells maintain: remove pyruvate (PDH, LDH), ATP consumption, allosteric regulation of pyruvate kinase, glycolytic flux

Score bands:
- 45-50: Both calculations correct, explains tautomerization, multiple physiological factors
- 38-44: Calculations correct, explanation somewhat thin
- 30-37: One calculation error, or vague biological explanation
- 20-29: Major calculation errors, minimal biological insight
- 0-19: Fundamentally incorrect

**Reasoning & Rigor (0-30):**
- 25-30: Shows setup, correct formula use, units, clear logic
- 18-24: Right formulas but some shortcuts
- 10-17: Little visible structure
- 0-9: Major formula misuse

**Communication (0-20):**
- 17-20: Clean separation of parts, equations readable, biology coherent
- 12-16: Understandable but compressed
- 6-11: Disorganized
- 0-5: Incoherent
"""


RUBRIC_MATH = """## ASSIGNMENT: MATHEMATICS
### Linear Algebra - Eigenspaces and Diagonalizability

**Task:**
Given matrix A = [[2,1,0],[0,2,1],[0,0,3]]:
(a) Find eigenvalues and algebraic multiplicities.
(b) Find eigenspaces, determine if A is diagonalizable, justify.
(c) Interpret geometrically: What does non-diagonalizability mean? How would you compute A¹⁰⁰?

**Content / Conceptual Mastery (0-50):**

**(a) Eigenvalues:**
- A is upper triangular → eigenvalues are diagonal entries
- λ = 2 (algebraic multiplicity 2), λ = 3 (algebraic multiplicity 1)

**(b) Eigenspaces & Diagonalizability:**
- E₂ = span{(1,0,0)ᵀ}, geometric multiplicity = 1
- E₃ = span{(1,1,1)ᵀ}, geometric multiplicity = 1
- NOT diagonalizable: geometric multiplicity (1) < algebraic multiplicity (2) for λ = 2

**(c) Interpretation:**
- Geometric: No basis of eigenvectors; A includes shearing, not just scaling; Jordan block structure
- Computing A¹⁰⁰: Use Jordan form A = PJP⁻¹, so A¹⁰⁰ = PJ¹⁰⁰P⁻¹
- For 2×2 Jordan block: [[λ,1],[0,λ]]ⁿ = [[λⁿ, nλⁿ⁻¹],[0,λⁿ]]
- Polynomial terms appear: 100·2⁹⁹ in superdiagonal

Score bands:
- 45-50: Correct eigenvalues/multiplicities, correct eigenspaces, correct non-diagonalizability with justification, Jordan form + polynomial terms mentioned
- 38-44: Minor slips but fundamentally correct
- 30-37: Eigenvalues correct but eigenspaces or justification weak
- 20-29: Major errors (claims diagonalizable, wrong eigenspaces)
- 0-19: Fundamentally incorrect

**Reasoning & Rigor (0-30):**
- 25-30: Explicit (A-λI)v = 0 setup, row reduction shown, clear justification
- 18-24: Reasoning sound but compressed
- 10-17: Results without justification
- 0-9: Confused or contradictory

**Communication (0-20):**
- 17-20: Clear parts, matrices legible, geometric/computational explanation coherent
- 12-16: Understandable but notation sloppy
- 6-11: Hard to follow
- 0-5: Incoherent
"""


RUBRIC_PHILOSOPHY = """## ASSIGNMENT: PHILOSOPHY
### Kant's Categorical Imperative and the Ethics of Lying

**Task:**
(a) Explain Kant's categorical imperative: Universal Law formulation and Humanity as End formulation.
(b) Apply to: Is it permissible to lie to protect someone from harm (e.g., lying to a murderer at the door)? How would Kant argue? What objections arise?
(c) Evaluate Kant's position. What's the most compelling objection? How would a consequentialist or virtue ethicist respond differently?

**Content / Conceptual Mastery (0-50):**

**(a) Categorical Imperative:**
- Categorical = unconditional command of reason (vs hypothetical)
- Universal Law: "Act only according to that maxim you can will as universal law" - test for contradiction
- Humanity Formulation: "Treat humanity always as an end, never merely as a means" - rational agency = dignity

**(b) Application to Lying:**
- Kant's position: Lying is NEVER permissible, even to murderer at door
- Arguments: Universalizing lying destroys trust; lying treats deceived person as mere means
- Objections: Counterintuitive/extreme; conflict of duties; maxim reformulation; ignores consequences

**(c) Evaluation:**
- Compelling objection: Absolute rules fail in extreme cases; "rule worship"
- Consequentialist: Assess by outcomes; lying prevents murder = better utility; lying permitted/required
- Virtue ethics: Phronesis (practical wisdom); honesty is virtue but not only one; context-sensitive

Score bands:
- 45-50: Both formulations accurate, correct Kantian argument, substantive objections, both alternatives correctly described
- 38-44: Essentially correct with minor gaps
- 30-37: Knows Kant rejects lying but formulations vague, or alternatives thin
- 20-29: Major confusions (mixes categorical/hypothetical, misrepresents Kant)
- 0-19: Fundamentally incorrect

**Reasoning & Rigor (0-30):**
- 25-30: Logical progression from formulations → implications → objections → alternatives
- 18-24: Mostly coherent but informal
- 10-17: Assertions without argument
- 0-9: Incoherent or misattributes positions

**Communication (0-20):**
- 17-20: Clear (a), (b), (c); key terms used correctly
- 12-16: Understandable but some jargon misuse
- 6-11: Disorganized
- 0-5: Incoherent
"""


RUBRIC_TECHSOC = """## ASSIGNMENT: TECHNOLOGY & SOCIETY
### AI and Academic Integrity

**Task:**
(a) Analyze how LLMs are changing norms around academic integrity. What previously "cheating" behaviors might now be legitimate tool use? What remains clearly problematic?
(b) Propose a university policy framework: When should LLM use be permitted, restricted, or prohibited? Justify.
(c) Reflect: Is there a meaningful difference between LLM help vs. tutors, calculators, textbooks? What is education fundamentally FOR, and how should that shape AI policy?

**Content / Conceptual Mastery (0-50):**

**(a) Shifting Norms:**
- Cheating → possibly legitimate: grammar/style editing, brainstorming, concept explanation, draft feedback
- Clearly problematic: submitting AI-generated work as own, using during closed-book exams, ghostwriting personal statements
- Key distinction: transparency/authorship vs deception/substitution

**(b) Policy Framework:**
- Structured tiered approach (not just "allow" or "ban"):
  - Permitted with disclosure (brainstorming, editing, explanation)
  - Restricted (skill assessments - editing only, process evidence required)
  - Prohibited (exams, licensure, personal reflections)
- Justification: assessment integrity, skill development, fairness, AI literacy

**(c) Deeper Reflection:**
- Similarities: tutors explain, textbooks inform, calculators compute
- Key differences: LLMs generate full solutions, simulate voice/reasoning, enable easy ghostwriting
- Education's purpose: credentialing, skill/understanding, character/judgment
- Connect purpose to policy: scaffold learning vs substitute for learning

Score bands:
- 45-50: Concrete examples both directions, structured policy with justification, thoughtful reflection on education's purpose
- 38-44: Solid but one part underdeveloped
- 30-37: Some good points but thin policy or shallow reflection
- 20-29: Superficial treatment, no real policy framework
- 0-19: Off-topic or fails to engage

**Reasoning & Rigor (0-30):**
- 25-30: Logical flow, weighs competing considerations, distinguishes facts from values
- 18-24: Mostly coherent but one-sided
- 10-17: Assertions without justification
- 0-9: Contradictory or incoherent

**Communication (0-20):**
- 17-20: Clear structure, terms intelligible, readable
- 12-16: Understandable but could be better organized
- 6-11: Hard to follow
- 0-5: Incoherent
"""


# =========================
# PROMPT ASSEMBLY
# =========================

# Map subject codes to their rubrics
RUBRIC_MAP = {
    "cs": RUBRIC_CS,
    "prog": RUBRIC_CS,
    "programming": RUBRIC_CS,
    
    "econ": RUBRIC_ECON,
    "economics": RUBRIC_ECON,
    
    "eng": RUBRIC_LIT,
    "english": RUBRIC_LIT,
    "lit": RUBRIC_LIT,
    "literature": RUBRIC_LIT,
    
    "physics": RUBRIC_PHYSICS,
    "phys": RUBRIC_PHYSICS,
    
    "biochem": RUBRIC_BIOCHEM,
    "biochemistry": RUBRIC_BIOCHEM,
    "bio": RUBRIC_BIOCHEM,
    
    "math": RUBRIC_MATH,
    "linalg": RUBRIC_MATH,
    "linear_algebra": RUBRIC_MATH,
    
    "phil": RUBRIC_PHILOSOPHY,
    "philosophy": RUBRIC_PHILOSOPHY,
    "kant": RUBRIC_PHILOSOPHY,
    "ethics": RUBRIC_PHILOSOPHY,
    
    "tech": RUBRIC_TECHSOC,
    "techsoc": RUBRIC_TECHSOC,
    "ai_edu": RUBRIC_TECHSOC,
    "ai_education": RUBRIC_TECHSOC,
}

# Subject display names for user prompt
SUBJECT_DISPLAY = {
    "cs": ("Computer Science / Algorithms", "Longest Increasing Subsequence"),
    "prog": ("Computer Science / Algorithms", "Longest Increasing Subsequence"),
    "programming": ("Computer Science / Algorithms", "Longest Increasing Subsequence"),
    
    "econ": ("Economics", "Minimum Wage Analysis"),
    "economics": ("Economics", "Minimum Wage Analysis"),
    
    "eng": ("English / Literature", "Lord Jim / Marlow Analysis"),
    "english": ("English / Literature", "Lord Jim / Marlow Analysis"),
    "lit": ("English / Literature", "Lord Jim / Marlow Analysis"),
    "literature": ("English / Literature", "Lord Jim / Marlow Analysis"),
    
    "physics": ("Physics", "Bead on Rotating Hoop - Lagrangian Mechanics"),
    "phys": ("Physics", "Bead on Rotating Hoop - Lagrangian Mechanics"),
    
    "biochem": ("Biochemistry", "PEP Bioenergetics and Coupled Reactions"),
    "biochemistry": ("Biochemistry", "PEP Bioenergetics and Coupled Reactions"),
    "bio": ("Biochemistry", "PEP Bioenergetics and Coupled Reactions"),
    
    "math": ("Mathematics", "Linear Algebra - Eigenspaces and Diagonalizability"),
    "linalg": ("Mathematics", "Linear Algebra - Eigenspaces and Diagonalizability"),
    "linear_algebra": ("Mathematics", "Linear Algebra - Eigenspaces and Diagonalizability"),
    
    "phil": ("Philosophy", "Kant's Categorical Imperative and Ethics of Lying"),
    "philosophy": ("Philosophy", "Kant's Categorical Imperative and Ethics of Lying"),
    "kant": ("Philosophy", "Kant's Categorical Imperative and Ethics of Lying"),
    "ethics": ("Philosophy", "Kant's Categorical Imperative and Ethics of Lying"),
    
    "tech": ("Technology & Society", "AI and Academic Integrity"),
    "techsoc": ("Technology & Society", "AI and Academic Integrity"),
    "ai_edu": ("Technology & Society", "AI and Academic Integrity"),
    "ai_education": ("Technology & Society", "AI and Academic Integrity"),
}


def get_grader_system_prompt(subject: str) -> str:
    """Build the complete grader system prompt for a specific subject."""
    subject_lower = subject.lower()
    
    if subject_lower not in RUBRIC_MAP:
        raise ValueError(f"Unknown subject: {subject!r}. Valid: {list(set(RUBRIC_MAP.keys()))}")
    
    rubric = RUBRIC_MAP[subject_lower]
    return GRADER_HEADER + rubric + GRADER_FOOTER


def make_user_prompt(subject: str, blind_id: str, answer_text: str) -> str:
    """Build the user prompt for the grader."""
    subject_lower = subject.lower()
    
    if subject_lower not in SUBJECT_DISPLAY:
        raise ValueError(f"Unknown subject: {subject!r}")
    
    subject_label, assignment_label = SUBJECT_DISPLAY[subject_lower]

    return f"""Subject: {subject_label}
Assignment: {assignment_label}
ID: {blind_id}

Here is the student's answer:

{answer_text}

Please grade this answer according to your rubric.
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
    
    # Get subject-specific system prompt (MODULAR!)
    system_prompt = get_grader_system_prompt(subject)
    user_prompt = make_user_prompt(subject=subject, blind_id=blind_id, answer_text=answer_text)

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
    log("HOLIDAY GRADER v3.0 - MODULAR PER-SUBJECT PROMPTS")
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
    valid_tasks = set(RUBRIC_MAP.keys())
    rows = [r for r in rows if r.get("task", "").lower() in valid_tasks]

    if not rows:
        log("ERROR: No rows with recognizable tasks.")
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
