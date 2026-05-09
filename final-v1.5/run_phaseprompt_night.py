"""
PhasePrompt — 夜间全量跑
GSM8K 100题 × 5条件 (bare / CoT / G / CoT+G / filler control)
Pythia-1.4b
结果写文件，明早看
"""
import sys, os, json, re, random, time, torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'robustness_results')
os.makedirs(OUT, exist_ok=True)

MODEL = "EleutherAI/pythia-1.4b"
N_SAMPLES = 100

print(f"[{time.strftime('%H:%M')}] Loading {MODEL}...")
tok = AutoTokenizer.from_pretrained(MODEL)
if tok.pad_token is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map="auto")
model.eval()
print(f"[{time.strftime('%H:%M')}] Model loaded")

# GSM8K
gsm8k = load_dataset("gsm8k", "main", split="test")
_r = random.Random(42)
sample = _r.sample(list(gsm8k), N_SAMPLES)
print(f"[{time.strftime('%H:%M')}] GSM8K {N_SAMPLES} sampled")

def gold(t):
    m = re.search(r"####\s*(-?[\d,.]+)", t)
    return m.group(1) if m else None

@torch.no_grad()
def call(prompt, max_new=256):
    inp = tok(prompt, return_tensors="pt", truncation=True, max_length=512).to(model.device)
    out = model.generate(**inp, max_new_tokens=max_new, temperature=0.1, do_sample=True, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0][inp.input_ids.shape[1]:], skip_special_tokens=True).strip()

PROMPTS = {
    "A_bare": "Problem: {}\nAnswer:",
    "B_COT": "Problem: {}\nLet's think step by step.\n",
    "C_G": "Problem: {}\nYou are solving a math problem. Focus: {}\n",
    "D_COT_G": "Problem: {}\nLet's think step by step.\nYou are solving a math problem. Focus: {}\n",
    "E_filler": "Problem: {}\nLet's think step by step.\nThe sky is blue and the grass is green. The sun is warm.\n",
}

results = {}
for cond, template in PROMPTS.items():
    print(f"[{time.strftime('%H:%M')}] Running {cond}...")
    correct = 0; total = 0; outputs = []
    for q in sample:
        prompt = template.format(q['question'], q['question'][:30])
        answer = call(prompt)
        gs = gold(q['answer'])
        is_correct = gs and gs in answer
        if is_correct: correct += 1
        total += 1
        outputs.append({'gold': gs, 'got': answer[:80], 'correct': is_correct})
    acc = correct / total
    results[cond] = {'accuracy': round(acc, 4), 'correct': correct, 'total': total}
    print(f"  {cond}: {correct}/{total} = {acc:.2%}")
    # 每跑完一个条件写中间结果
    with open(os.path.join(OUT, f'phaseprompt_interim.json'), 'w') as f:
        json.dump(results, f, indent=2)

with open(os.path.join(OUT, 'phaseprompt_night.json'), 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n[{time.strftime('%H:%M')}] Done.")
for c, r in results.items():
    print(f"  {c:15s}: {r['correct']}/{r['total']} = {r['accuracy']:.2%}")
