"""PhasePrompt v2: A/B/C/D 四组对比 — Pythia-1.4b + GSM8K"""
import sys, torch, re, random, time
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "EleutherAI/pythia-1.4b"
print(f"Loading {MODEL}...")
tok = AutoTokenizer.from_pretrained(MODEL)
if tok.pad_token is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map="auto")
model.eval()

gsm8k = load_dataset("gsm8k", "main", split="test")
_r = random.Random(42)
sample = _r.sample(list(gsm8k), 30)
print(f"GSM8K 30 loaded\n")

def gold(t):
    m = re.search(r"####\s*(-?[\d,.]+)", t)
    return m.group(1) if m else None

@torch.no_grad()
def call(prompt):
    inp = tok(prompt, return_tensors="pt", truncation=True, max_length=512).to(model.device)
    out = model.generate(**inp, max_new_tokens=128, temperature=0.1, do_sample=True, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0][inp.input_ids.shape[1]:], skip_special_tokens=True).strip()

PROMPTS = {
    "A_bare": "{}",
    "B_COT": "Problem: {}\nLet's think step by step.",
    "C_G":   "[self-ref] You are solving a multi-step math problem. First identify the type, then apply rules, then compute.\n\nProblem: {}",
    "D_both":"[self-ref] You are solving a multi-step math problem.\n\nProblem: {}\nLet's think step by step.",
}

for label, template in PROMPTS.items():
    correct, total = 0, 0
    t0 = time.time()
    for item in sample:
        q = item["question"]
        expected = gold(item["answer"])
        prompt = template.format(q)
        out = call(prompt)
        ok = expected and expected in out
        if ok: correct += 1
        total += 1
        sys.stdout.write(f"\r{label} {correct}/{total} {correct/max(total,1):.0%}")
        sys.stdout.flush()
    elapsed = time.time() - t0
    print(f"\n{label}: {correct}/{total} = {correct/total:.0%}  [{elapsed:.0f}s]")
