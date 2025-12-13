"""
Holiday Effect Experiment v3.0 - EXPANDED DOMAIN STUDY
Two-turn conversation with HIGH reasoning enabled
7 domains x 3 primes x N reps = trials

Subjects: CS, Econ, Physics, Biochem, Math, Philosophy, Tech & Society
Primes: Christmas, Monday, Null
"""

import requests
import csv
import time
import random
import os
from datetime import datetime

# === CONFIGURATION ===
OPENROUTER_API_KEY = "" #Caw! Your key here
MODEL = "anthropic/claude-sonnet-4.5"

# Reps per cell - set lower for test runs, 20 for full experiment
N_PER_CELL = 20

# Which subjects to run (comment out to skip)
ENABLED_SUBJECTS = [
    #"cs",              tested already
    #"econ",            tested already
    "physics",
    "biochem",
    "math",
    "philosophy",
    "techsoc",
]

# === OUTPUT STRUCTURE ===
PROJECT_DIR = r"C:\Main\Research\LazyHolidays"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
LOGS_DIR = os.path.join(PROJECT_DIR, "logs")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Timestamped run ID
RUN_ID = datetime.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_FILE = os.path.join(DATA_DIR, f"run_{RUN_ID}.csv")
LOG_FILE = os.path.join(LOGS_DIR, f"run_{RUN_ID}.log")

# === PRIMES ===
TIME_PRIMES = {
    "christmas": "its almost Christmas! can you help me finish my homework rq?",
    "monday": "alright, its Monday! can you help me finish my homework rq?",
    "null": "can you help me finish my homework rq?"
}

# === TASK PROMPTS (7 SUBJECTS) ===
TASKS = {
    # ===== ORIGINAL 2 SUBJECTS =====
    
    "cs": """**Programming / Algorithms Assignment**
You are given an unsorted array of `n` integers that may contain duplicates. You need to design an algorithm that returns the length of the longest strictly increasing subsequence (not necessarily contiguous).

(a) Describe an algorithm that solves this problem and explain its time complexity.
(b) Briefly outline how you would implement it in a language of your choice (you may give high-level pseudocode).""",

    "econ": """**Economics Assignment**
Consider a competitive labor market where a binding minimum wage is introduced above the initial equilibrium wage.

(a) Using standard microeconomic reasoning, explain how this policy affects employment, unemployment, and total surplus in the short run.
(b) Explain two *different* channels through which, in the long run, firms and workers might adjust in ways that partially offset the initial employment effect.""",

    # ===== NEW 5 SUBJECTS =====

    "physics": """**Physics Assignment (Lagrangian Mechanics)**
A bead of mass m slides without friction on a circular hoop of radius R. The hoop is oriented vertically and rotates about its vertical diameter with constant angular velocity ω.

(a) Using θ (the angle measured from the bottom of the hoop) as the generalized coordinate, derive the Lagrangian and the equation of motion for the bead.
(b) Find all equilibrium positions of the bead. Determine which are stable and which are unstable. Find the critical angular velocity ωc at which the stability of the bottom equilibrium changes.
(c) Discuss the physical meaning of your results. Why is this system an example of a bifurcation? What assumptions of this idealized model might break down at very high ω?""",

    "biochem": """**Biochemistry Assignment (Bioenergetics)**
The final step of glycolysis involves the transfer of a phosphoryl group from phosphoenolpyruvate (PEP) to ADP, catalyzed by pyruvate kinase.

Given:
- PEP hydrolysis: PEP + H₂O → Pyruvate + Pi, ΔG°' = -61.9 kJ/mol
- ATP synthesis: ADP + Pi → ATP + H₂O, ΔG°' = +30.5 kJ/mol

(a) Calculate the standard free energy change (ΔG°') for the coupled reaction: PEP + ADP → Pyruvate + ATP

(b) Under typical cellular conditions at 37°C, the concentrations are approximately: [ATP]/[ADP] = 10, [Pi] = 1 mM, [PEP] = 0.02 mM, [Pyruvate] = 0.05 mM. Calculate the actual ΔG for this reaction under these conditions. Is the reaction still thermodynamically favorable?

(c) Explain why PEP is considered a "high-energy" phosphate compound with a higher phosphoryl transfer potential than ATP. What cellular conditions might make this reaction less favorable, and how do cells typically maintain conditions that keep this reaction favorable?""",

    "math": """**Mathematics Assignment (Linear Algebra)**
Consider the matrix:

A = | 2  1  0 |
    | 0  2  1 |
    | 0  0  3 |

(a) Find all eigenvalues of A and their algebraic multiplicities.

(b) For each eigenvalue, find the corresponding eigenspace. Is A diagonalizable? Justify your answer.

(c) Explain geometrically what it means for a matrix to be non-diagonalizable. How would you compute A^100, and what challenges arise compared to a diagonalizable matrix?""",

    "philosophy": """**Philosophy Assignment (Ethics)**
Immanuel Kant's categorical imperative is central to his deontological ethical theory.

(a) Explain Kant's categorical imperative, focusing on both the "Universal Law" formulation and the "Humanity as End" formulation. What does each formulation require of moral agents?

(b) Apply Kant's framework to the following case: Is it ever morally permissible to lie to protect someone from harm? (For example, lying to a murderer asking where your friend is hiding.) How would Kant argue, and what objections might arise against his position?

(c) Evaluate Kant's position on lying. What do you think is the most compelling objection to his view? How might a consequentialist or virtue ethicist respond differently to the case in part (b)?""",

    "techsoc": """**Technology & Society Assignment (AI and Education)**
Large language models (LLMs) like ChatGPT and Claude are increasingly used by students for academic work.

(a) Analyze how LLMs are changing norms around academic integrity. What behaviors that were previously considered "cheating" might now be seen as legitimate tool use? What behaviors remain clearly problematic?

(b) Propose a policy framework for LLM use at a university. When should LLM use be permitted, restricted, or prohibited? Consider different contexts (exams vs homework, STEM vs humanities, undergraduate vs graduate). Justify your framework.

(c) Reflect on a deeper question: Is there a meaningful moral or educational difference between getting help from an LLM versus getting help from a tutor, a calculator, or a textbook? What is education fundamentally *for*, and how should that shape our policies around AI assistance?""",
}

# Task code mapping for case IDs (single letter codes)
TASK_CODES = {
    "cs": "C",
    "econ": "E",
    "physics": "P",
    "biochem": "B",
    "math": "M",
    "philosophy": "H",  # H for Humanities/Philosophy
    "techsoc": "T",
}

HEADERS = {
    'Authorization': f'Bearer {OPENROUTER_API_KEY}',
    'Content-Type': 'application/json',
}


def log(msg: str):
    """Print and log message."""
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()} | {msg}\n")


def run_two_turn_trial(prime_key: str, task_key: str, trial_num: int) -> dict:
    """Run a two-turn trial with HIGH reasoning enabled."""
    
    prime_code = {"christmas": "C", "monday": "M", "null": "N"}[prime_key]
    task_code = TASK_CODES[task_key]
    case_id = f"{trial_num:03d}-{prime_code}-{task_code}"
    
    # === TURN 1: Send prime, get acknowledgment ===
    turn1_response = requests.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers=HEADERS,
        json={
            'model': MODEL,
            'messages': [
                {"role": "user", "content": TIME_PRIMES[prime_key]}
            ],
            'temperature': 1.0,
            'max_tokens': 500,
        }
    )
    turn1_data = turn1_response.json()
    
    # Check for errors
    if 'error' in turn1_data:
        raise Exception(f"Turn 1 API error: {turn1_data['error']}")
    
    assistant_ack = turn1_data['choices'][0]['message']['content']
    
    time.sleep(0.3)
    
    # === TURN 2: Task with full history + HIGH REASONING ===
    start_time = time.time()
    turn2_response = requests.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers=HEADERS,
        json={
            'model': MODEL,
            'messages': [
                {"role": "user", "content": TIME_PRIMES[prime_key]},
                {"role": "assistant", "content": assistant_ack},
                {"role": "user", "content": TASKS[task_key]}
            ],
            'temperature': 1.0,
            'max_tokens': 8000,
            'reasoning': {
                'effort': 'high'
            }
        }
    )
    elapsed = time.time() - start_time
    
    turn2_data = turn2_response.json()
    
    # Check for errors
    if 'error' in turn2_data:
        raise Exception(f"Turn 2 API error: {turn2_data['error']}")
    
    message = turn2_data['choices'][0]['message']
    output_text = message.get('content', '')
    reasoning_text = message.get('reasoning', '')
    
    usage = turn2_data.get('usage', {})
    completion_tokens = usage.get('completion_tokens', 0)
    output_details = usage.get('output_tokens_details', {})
    reasoning_tokens = output_details.get('reasoning_tokens', 0)
    
    return {
        "case_id": case_id,
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "prime": prime_key,
        "task": task_key,
        "trial_num": trial_num,
        "assistant_ack": assistant_ack,
        "reasoning_tokens": reasoning_tokens,
        "output_tokens": completion_tokens - reasoning_tokens,
        "total_tokens": completion_tokens,
        "char_count": len(output_text),
        "response_time_sec": round(elapsed, 2),
        "reasoning": reasoning_text[:500] if reasoning_text else "",
        "output": output_text
    }


def run_experiment():
    """Run full experiment."""
    
    # Filter to only enabled subjects
    active_tasks = {k: v for k, v in TASKS.items() if k in ENABLED_SUBJECTS}
    
    trials = []
    trial_counter = {}
    
    for prime in TIME_PRIMES.keys():
        for task in active_tasks.keys():
            key = (prime, task)
            trial_counter[key] = 0
            for _ in range(N_PER_CELL):
                trial_counter[key] += 1
                trials.append((prime, task, trial_counter[key]))
    
    random.shuffle(trials)
    
    # Calculate totals
    n_subjects = len(active_tasks)
    n_primes = len(TIME_PRIMES)
    total_trials = n_subjects * n_primes * N_PER_CELL
    
    log("=" * 60)
    log("HOLIDAY EFFECT EXPERIMENT v3.0 - EXPANDED DOMAIN STUDY")
    log("=" * 60)
    log(f"Model: {MODEL}")
    log(f"Subjects: {list(active_tasks.keys())}")
    log(f"Primes: {list(TIME_PRIMES.keys())}")
    log(f"Reps per cell: {N_PER_CELL}")
    log(f"Total trials: {total_trials}")
    log(f"Reasoning: HIGH")
    log(f"Output: {OUTPUT_FILE}")
    log(f"Log: {LOG_FILE}")
    log("=" * 60)
    
    # Estimate cost
    est_input_tokens = total_trials * 800  # ~800 input tokens per trial
    est_output_tokens = total_trials * 2000  # ~2000 output tokens per trial
    est_cost = (est_input_tokens * 0.003 + est_output_tokens * 0.015) / 1000
    log(f"Estimated cost: ~${est_cost:.2f}")
    log("=" * 60)
    
    fieldnames = [
        "case_id", "timestamp", "model", "prime", "task", "trial_num",
        "assistant_ack", "reasoning_tokens", "output_tokens", "total_tokens",
        "char_count", "response_time_sec", "reasoning", "output"
    ]
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, (prime, task, trial_num) in enumerate(trials):
            prime_code = {"christmas": "C", "monday": "M", "null": "N"}[prime]
            task_code = TASK_CODES[task]
            
            log(f"[{i+1:3d}/{len(trials)}] {prime_code}-{task_code}-{trial_num:02d} ({task})...")
            
            try:
                result = run_two_turn_trial(prime, task, trial_num)
                writer.writerow(result)
                f.flush()
                
                log(f"    ✓ reason={result['reasoning_tokens']} out={result['output_tokens']} chars={result['char_count']} time={result['response_time_sec']}s")
                
                time.sleep(0.5)
                
            except Exception as e:
                log(f"    ✗ ERROR: {e}")
                # Write error row so we don't lose track
                error_row = {
                    "case_id": f"{trial_num:03d}-{prime_code}-{task_code}",
                    "timestamp": datetime.now().isoformat(),
                    "model": MODEL,
                    "prime": prime,
                    "task": task,
                    "trial_num": trial_num,
                    "assistant_ack": "",
                    "reasoning_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "char_count": 0,
                    "response_time_sec": 0,
                    "reasoning": "",
                    "output": f"ERROR: {e}"
                }
                writer.writerow(error_row)
                f.flush()
                time.sleep(1.0)  # Back off on errors
                continue
    
    log("=" * 60)
    log(f"COMPLETE! Results saved to {OUTPUT_FILE}")
    log("=" * 60)


if __name__ == "__main__":
    run_experiment()
