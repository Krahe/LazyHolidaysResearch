"""
Holiday Effect Experiment v1.0
Testing temporal priming effects on LLM output
2 domains x 3 primes x 20 reps = 120 calls
"""

import openai
import csv
import time
import random
from datetime import datetime

# === CONFIGURATION ===
OPENROUTER_API_KEY = "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"  # <-- PASTE YOUR KEY
MODEL = "anthropic/claude-sonnet-4.5"  # Sonnet 4.5 on OpenRouter
N_PER_CELL = 1
OUTPUT_FILE = f"holiday_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

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

# === API SETUP ===
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def run_single_trial(prime_key: str, task_key: str, trial_num: int) -> dict:
    """Run a single trial and return results."""
    
    # Construct full prompt
    full_prompt = f"{TIME_PRIMES[prime_key]}\n\n{TASKS[task_key]}"
    
    # Generate case ID: e.g., "001-C-E" for trial 1, Christmas, Econ
    prime_code = {"christmas": "C", "monday": "M", "null": "N"}[prime_key]
    task_code = {"econ": "E", "cs": "C"}[task_key]
    case_id = f"{trial_num:03d}-{prime_code}-{task_code}"
    
    # Call API
    start_time = time.time()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": full_prompt}],
        temperature=1.0,
        max_tokens=4096,
    )
    elapsed = time.time() - start_time
    
    # Extract data
    output_text = response.choices[0].message.content
    token_count = response.usage.completion_tokens
    
    return {
        "case_id": case_id,
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "prime": prime_key,
        "task": task_key,
        "trial_num": trial_num,
        "token_count": token_count,
        "char_count": len(output_text),
        "response_time_sec": round(elapsed, 2),
        "output": output_text
    }

def run_experiment():
    """Run full experiment with all conditions."""
    
    # Build trial list
    trials = []
    trial_counter = {}
    
    for prime in TIME_PRIMES.keys():
        for task in TASKS.keys():
            key = (prime, task)
            trial_counter[key] = 0
            for _ in range(N_PER_CELL):
                trial_counter[key] += 1
                trials.append((prime, task, trial_counter[key]))
    
    # Randomize order
    random.shuffle(trials)
    
    print(f"=" * 50)
    print(f"HOLIDAY EFFECT EXPERIMENT")
    print(f"=" * 50)
    print(f"Model: {MODEL}")
    print(f"Trials: {len(trials)} total")
    print(f"  - {N_PER_CELL} per cell × 3 primes × 2 tasks")
    print(f"Output: {OUTPUT_FILE}")
    print(f"=" * 50)
    
    # Run and save incrementally
    fieldnames = ["case_id", "timestamp", "model", "prime", "task", 
                  "trial_num", "token_count", "char_count", 
                  "response_time_sec", "output"]
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, (prime, task, trial_num) in enumerate(trials):
            prime_code = {"christmas": "C", "monday": "M", "null": "N"}[prime]
            task_code = {"econ": "E", "cs": "C"}[task]
            
            print(f"[{i+1:3d}/{len(trials)}] {prime_code}-{task_code}-{trial_num:02d}...", end=" ", flush=True)
            
            try:
                result = run_single_trial(prime, task, trial_num)
                writer.writerow(result)
                f.flush()
                print(f"✓ tokens={result['token_count']}")
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"✗ ERROR: {e}")
                continue
    
    print(f"\n{'=' * 50}")
    print(f"COMPLETE! Results saved to {OUTPUT_FILE}")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    run_experiment()