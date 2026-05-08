"""PhasePrompt — GSM8K + exact answer (pythia-410m)"""
import json, sys, time, torch, re, random
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "EleutherAI/pythia-410m"
print(f"Loading {MODEL}...")
tok = AutoTokenizer.from_pretrained(MODEL)
if tok.pad_token is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map="auto")
model.eval()

gsm8k = load_dataset("gsm8k", "main", split="test")
_r = random.Random(42)
sample = _r.sample(list(gsm8k), 30)
print(f"GSM8K 30 loaded. Device: {'cuda' if torch.cuda.is_available() else 'cpu'}\n")

def extract_gold(text):
    m = re.search(r"####\s*(-?[\d,.]+)", text)
    return m.group(1) if m else None

@torch.no_grad()
def call(prompt):
    inp = tok(prompt, return_tensors="pt", truncation=True, max_length=512).to(model.device)
    out = model.generate(**inp, max_new_tokens=128, temperature=0.1, do_sample=True, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0][inp.input_ids.shape[1]:], skip_special_tokens=True).strip()

G_STR = "你正在解决一个多步数学应用题。展示推导过程：先建立规则，再代入，最后得答案。"

for label, use_g in [("No G", False), ("With G", True)]:
    correct, total = 0, 0
    for item in sample:
        q = item["question"]
        gold = extract_gold(item["answer"])
        prompt = f"[结构自指] {G_STR}\n\n问题：{q}" if use_g else q
        out = call(prompt)
        ok = gold and gold in out
        if ok: correct += 1
        total += 1
        sys.stdout.write(f"\r{label} {correct}/{total}")
        sys.stdout.flush()
    print(f"\n{label}: {correct}/{total} = {correct/total:.0%}")
