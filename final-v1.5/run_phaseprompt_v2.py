"""PhasePrompt v2 — 原版Gprompt重跑"""
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

gsm8k = load_dataset("gsm8k", "main", split="test")
_r = random.Random(42)
sample = _r.sample(list(gsm8k), N_SAMPLES)

def gold(t):
    m = re.search(r"####\s*(-?[\d,.]+)", t)
    return m.group(1) if m else None

@torch.no_grad()
def call(prompt):
    inp = tok(prompt, return_tensors="pt", truncation=True, max_length=512).to(model.device)
    out = model.generate(**inp, max_new_tokens=256, temperature=0.1, do_sample=True, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0][inp.input_ids.shape[1]:], skip_special_tokens=True).strip()

G_STR = "You are solving a multi-step math problem. First identify the type, then apply rules, then compute."

PROMPTS = {
    "A_bare": "Problem: {}\nAnswer:",
    "B_COT": "Problem: {}\nLet's think step by step.\n",
    "C_G": "[self-ref] " + G_STR + "\n\nProblem: {}\nAnswer:",
    "D_COT_G": "[self-ref] " + G_STR + "\n\nProblem: {}\nLet's think step by step.\n",
    "E_filler": "Problem: {}\nLet's think step by step.\nThe sky is blue and the grass is green. The sun is warm.\n",
}

results = {}
for cond, template in PROMPTS.items():
    print(f"[{time.strftime('%H:%M')}] Running {cond}...")
    correct = 0
    for i, q in enumerate(sample):
        prompt = template.format(q['question'])
        answer = call(prompt)
        gs = gold(q['answer'])
        if gs and gs in answer:
            correct += 1
        if (i+1) % 25 == 0:
            print(f"  {i+1}/{N_SAMPLES} so far: {correct}/{i+1} = {correct/(i+1):.1%}")
    acc = correct / N_SAMPLES
    results[cond] = {'accuracy': round(acc, 4), 'correct': correct, 'total': N_SAMPLES}
    print(f"  {cond}: {correct}/{N_SAMPLES} = {acc:.2%}")
    with open(os.path.join(OUT, 'phaseprompt_v2_interim.json'), 'w') as f:
        json.dump(results, f, indent=2)

with open(os.path.join(OUT, 'phaseprompt_v2_final.json'), 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n[{time.strftime('%H:%M')}] Done.")
for c, r in results.items():
    print(f"  {c:15s}: {r['correct']}/{r['total']} = {r['accuracy']:.2%}")
