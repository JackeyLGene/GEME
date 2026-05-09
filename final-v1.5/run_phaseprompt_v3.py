"""PhasePrompt v3 — 真自指prompt (无任务标识依赖)"""
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

PROMPTS = {
    # A: 基线 — 无任何附加指令
    "A_bare": "Problem: {}\nAnswer:",

    # B: CoT — 过程指令（不是自指）
    "B_COT": "Problem: {}\nLet's think step by step.\n",

    # C: G — 纯自指（无任务标识，无过程指令）
    # "回想你以前知道的相关知识，然后回答"
    "C_G_self": "Problem: {}\nBefore answering, recall what you already know that is relevant. Answer:",

    # D: CoT + G — 自指回忆 + 逐步推理
    "D_COT_G": "Problem: {}\nBefore answering, recall what you already know that is relevant. Now reason step by step.\n",

    # E: 字数对照 — 和G等长的无意义追加
    "E_filler": "Problem: {}\nLet's think step by step.\nThe sky is blue. The grass is green. The sun is warm.\n",
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
            print(f"  {i+1}/{N_SAMPLES}: {correct}/{i+1} = {correct/(i+1):.1%}")
    acc = correct / N_SAMPLES
    results[cond] = {'accuracy': round(acc, 4), 'correct': correct, 'total': N_SAMPLES}
    print(f"  {cond}: {correct}/{N_SAMPLES} = {acc:.2%}")
    with open(os.path.join(OUT, 'phaseprompt_v3_interim.json'), 'w') as f:
        json.dump(results, f, indent=2)

with open(os.path.join(OUT, 'phaseprompt_v3_final.json'), 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n[{time.strftime('%H:%M')}] Done.")
for c, r in results.items():
    print(f"  {c:15s}: {r['correct']}/{r['total']} = {r['accuracy']:.2%}")
