"""
Holiday Effect Experiment v2.1
Two-turn conversation with HIGH reasoning enabled
2 domains x 3 primes x 20 reps = 120 trials
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
N_PER_CELL = 20

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

# === TASK PROMPTS ===
TASKS = {
    "econ": """**Economics Assignment**
Consider a competitive labor market where a binding minimum wage is introduced above the initial equilibrium wage.

(a) Using standard microeconomic reasoning, explain how this policy affects employment, unemployment, and total surplus in the short run.
(b) Explain two *different* channels through which, in the long run, firms and workers might adjust in ways that partially offset the initial employment effect.""",

    "cs": """**Programming / Algorithms Assignment**
You are given an unsorted array of `n` integers that may contain duplicates. You need to design an algorithm that returns the length of the longest strictly increasing subsequence (not necessarily contiguous).

(a) Describe an algorithm that solves this problem and explain its time complexity.
(b) Briefly outline how you would implement it in a language of your choice (you may give high-level pseudocode)."""
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
    task_code = {"econ": "E", "cs": "C"}[task_key]
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
    
    trials = []
    trial_counter = {}
    
    for prime in TIME_PRIMES.keys():
        for task in TASKS.keys():
            key = (prime, task)
            trial_counter[key] = 0
            for _ in range(N_PER_CELL):
                trial_counter[key] += 1
                trials.append((prime, task, trial_counter[key]))
    
    random.shuffle(trials)
    
    log("=" * 60)
    log("HOLIDAY EFFECT EXPERIMENT v2.1 (Two-Turn + HIGH Reasoning)")
    log("=" * 60)
    log(f"Model: {MODEL}")
    log(f"Trials: {len(trials)} total")
    log(f"Reasoning: HIGH (80% of max_tokens)")
    log(f"Output: {OUTPUT_FILE}")
    log(f"Log: {LOG_FILE}")
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
            task_code = {"econ": "E", "cs": "C"}[task]
            
            log(f"[{i+1:3d}/{len(trials)}] {prime_code}-{task_code}-{trial_num:02d}...")
            
            try:
                result = run_two_turn_trial(prime, task, trial_num)
                writer.writerow(result)
                f.flush()
                
                log(f"    ✓ reason={result['reasoning_tokens']} out={result['output_tokens']} time={result['response_time_sec']}s")
                
                time.sleep(0.5)
                
            except Exception as e:
                log(f"    ✗ ERROR: {e}")
                continue
    
    log("=" * 60)
    log(f"COMPLETE! Results saved to {OUTPUT_FILE}")
    log("=" * 60)

if __name__ == "__main__":
    run_experiment()
