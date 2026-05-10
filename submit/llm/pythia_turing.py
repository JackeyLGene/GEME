"""
Pythia Turing Test: local Pythia vs human text through GEME.

Three Pythia models (410m, 1.4b, 6.9b) generate answers to the same
questions from HC3. Human reference answers from bundled HC3 sample.

GEME processes all texts as 5-word sliding windows -> char-bigram 27-dim.
Hypothesis: frame-economic metrics differ between human and Pythia text.
"""
import sys, math, json, time
sys.path.insert(0, '../code')
from geme import GEME, _VEC_DIM
from collections import Counter
import torch, os

# ============================================================
# HC3 Questions (from bundled sample)
# ============================================================
QUESTIONS = [
    ("medicine", "What causes high blood pressure?"),
    ("medicine", "How does aspirin work?"),
    ("law",      "What is double jeopardy?"),
    ("law",      "What does a contract need to be valid?"),
    ("finance",  "What is compound interest?"),
    ("finance",  "What is a 401k?"),
    ("daily",    "How do I make scrambled eggs?"),
    ("daily",    "How do I change a tire?"),
]

HUMAN_ANSWERS = {
    "What causes high blood pressure?": (
        "High blood pressure can be caused by many things. "
        "Being overweight, eating too much salt, not exercising enough, "
        "drinking too much alcohol, and smoking can all raise your "
        "blood pressure. Stress plays a role too. Some people get it "
        "because it runs in their family. As you get older your risk "
        "goes up. Sometimes doctors cannot find a specific cause and "
        "call it essential hypertension. The good news is you can "
        "lower it with lifestyle changes and medication if needed."
    ),
    "How does aspirin work?": (
        "Aspirin works by blocking chemicals in your body called "
        "prostaglandins. These chemicals are involved in pain and "
        "inflammation. When you take aspirin it stops an enzyme "
        "called COX from making prostaglandins. Less prostaglandins "
        "means less pain and swelling. It also thins your blood by "
        "stopping platelets from sticking together which is why "
        "doctors sometimes give low dose aspirin to prevent heart "
        "attacks and strokes."
    ),
    "What is double jeopardy?": (
        "Double jeopardy means you cannot be tried twice for the "
        "same crime. It is in the Fifth Amendment of the Constitution. "
        "If a jury finds you not guilty the government cannot turn "
        "around and prosecute you again for that same offense even "
        "if new evidence comes up later. There are some exceptions "
        "though. If the crime violates both state and federal law "
        "you can be tried in both courts separately. And if your "
        "first trial ended in a mistrial that does not count."
    ),
    "What does a contract need to be valid?": (
        "A valid contract needs a few basic things. First you need "
        "an offer from one party and acceptance from the other. "
        "Second there has to be consideration which basically means "
        "each side gives something of value. Third both parties "
        "have to intend to enter into a legal agreement. They also "
        "need to have the capacity to contract which means they are "
        "adults of sound mind. Some contracts need to be in writing "
        "but most can be verbal and still enforceable."
    ),
    "What is compound interest?": (
        "Compound interest is when you earn interest on your interest. "
        "Say you put a hundred dollars in a savings account at five "
        "percent. After the first year you have a hundred and five "
        "dollars. The next year you earn five percent on the hundred "
        "and five dollars not just the original hundred. Over many "
        "years this really adds up which is why people say you should "
        "start saving early. The same thing works in reverse with "
        "credit card debt which is why it can get out of hand fast."
    ),
    "What is a 401k?": (
        "A 401k is a retirement savings account that you get through "
        "your job. You put money in from your paycheck before taxes "
        "are taken out which lowers your taxable income right now. "
        "A lot of employers will match some of what you put in which "
        "is basically free money. The money grows tax free until you "
        "retire and start taking it out. If you take money out before "
        "you are fifty nine and a half you usually have to pay a "
        "penalty on top of the regular taxes."
    ),
    "How do I make scrambled eggs?": (
        "Crack two or three eggs into a bowl add a splash of milk "
        "and a pinch of salt then beat them with a fork until they "
        "turn yellow and a bit frothy. Melt some butter in a nonstick "
        "pan over medium heat. Pour in the eggs and let them sit "
        "for about thirty seconds until the edges start to set. Then "
        "push them around gently with a spatula. Keep doing that "
        "until they are mostly set but still a little wet looking. "
        "Take them off the heat they will keep cooking on the plate."
    ),
    "How do I change a tire?": (
        "First make sure you are on flat ground and the parking brake "
        "is on. Get the spare tire and the jack and the lug wrench "
        "out of the trunk. Loosen the lug nuts a little bit before "
        "you jack up the car they will be easier to turn while the "
        "tire is on the ground. Then put the jack under the frame "
        "near the flat tire and raise the car until the tire is "
        "off the ground. Take the lug nuts all the way off pull "
        "the flat tire off and put the spare on. Tighten the nuts "
        "in a star pattern not in a circle. Lower the car and give "
        "the nuts one final tighten."
    ),
}

# ============================================================
# Pythia Generator
# ============================================================
def load_pythia(model_name, device="cuda" if torch.cuda.is_available() else "cpu"):
    """Load a Pythia model from local cache."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model_id = f"EleutherAI/{model_name}"
    print(f"  Loading {model_id} on {device}...")
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto",
    )
    model.eval()
    return tok, model, device


@torch.no_grad()
def generate_answer(question, tok, model, device, max_new=150):
    """Generate an answer to a question."""
    prompt = f"Question: {question}\n\nAnswer:"
    inputs = tok(prompt, return_tensors="pt", truncation=True, max_length=256).to(device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new,
        temperature=0.7,
        do_sample=True,
        pad_token_id=tok.pad_token_id,
    )
    decoded = tok.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    return decoded.strip()


# ============================================================
# GEME Processor
# ============================================================
def build_bigram_map(texts, top_n=27):
    counts = Counter()
    for t in texts:
        tl = t.lower()
        for i in range(len(tl) - 1):
            counts[tl[i:i+2]] += 1
    top = [bg for bg, _ in counts.most_common(top_n)]
    return {bg: i for i, bg in enumerate(top)}


def window_encode(window, bg_map):
    text = ' '.join(window).lower()
    vec = [0.0] * _VEC_DIM
    total = 0
    for i in range(len(text) - 1):
        bg = text[i:i+2]
        if bg in bg_map:
            vec[bg_map[bg]] += 1.0
            total += 1
    if total > 0:
        vec = [v / total for v in vec]
    return vec


def chunk_text(text, window_size=5, stride=2):
    words = text.split()
    windows = []
    for i in range(0, max(1, len(words) - window_size + 1), stride):
        windows.append(words[i:i+window_size])
    return windows


def process_text(text, bg_map, capacity=16):
    windows = chunk_text(text, window_size=5, stride=2)
    if len(windows) < 3:
        return None
    g = GEME(memory_cap=capacity)
    g.memory.preserve_sig = True
    g.memory.quantum_mode = True
    g.memory.cooccur_thresh = 0.08
    for w in windows:
        vec = window_encode(w, bg_map)
        g.process_vec(vec, ' '.join(w[:3]))
    g.memory.induction_clean()
    m = g.metrics()
    return {
        'frame_count': m.get('frame_count', 0),
        'entropy': m.get('structural_entropy', 0.0),
        'efficiency': m.get('efficiency', 0.0),
        'preds': m.get('pred_total', 0),
        'accuracy': m.get('pred_accuracy', 0.0),
        'I_phi_X': m.get('I(phi;X)', 0.0),
        'n_windows': len(windows),
    }


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print("=" * 70)
    print("Pythia Turing Test: Human vs Local Pythia Models")
    print("=" * 70)

    # Choose model (fastest for testing)
    model_name = "pythia-410m"
    tok, model, device = load_pythia(model_name)

    # Generate Pythia answers
    print("\n  Generating Pythia answers...")
    pythia_answers = {}
    for domain, question in QUESTIONS:
        ans = generate_answer(question, tok, model, device)
        # Trim to match human answer length
        if len(ans.split()) > 100:
            ans = ' '.join(ans.split()[:100])
        pythia_answers[question] = ans
        print(f"    [{domain}] {question[:40]}... -> {len(ans.split())} words")

    # Build bigram map from ALL texts
    all_texts = list(HUMAN_ANSWERS.values()) + list(pythia_answers.values())
    bg_map = build_bigram_map(all_texts, top_n=_VEC_DIM)
    print(f"\n  Bigram vocabulary: {len(bg_map)}")

    # Process through GEME
    print(f"\n{'Domain':<12} {'Human_preds':>11} {'Pythia_preds':>12} {'H_ent':>7} {'P_ent':>7} {'H_frames':>9} {'P_frames':>9} {'Direction':>10}")
    print("-" * 80)

    human_results = []
    pythia_results = []

    for domain, question in QUESTIONS:
        h_text = HUMAN_ANSWERS[question]
        p_text = pythia_answers[question]

        hm = process_text(h_text, bg_map)
        pm = process_text(p_text, bg_map)

        if hm and pm:
            human_results.append(hm)
            pythia_results.append(pm)
            direction = "HUMAN>" if hm['preds'] > pm['preds'] else "PYTHIA>"
            print(f"{domain:<12} {hm['preds']:11d} {pm['preds']:12d} "
                  f"{hm['entropy']:7.3f} {pm['entropy']:7.3f} "
                  f"{hm['frame_count']:9d} {pm['frame_count']:9d} "
                  f"{direction:>10}")

    # Aggregate
    if human_results and pythia_results:
        n = len(human_results)
        print(f"\n{'='*70}")
        print(f"AGGREGATE (n={n} pairs, model={model_name})")
        print(f"{'='*70}")

        for metric, label in [
            ('preds', 'Prediction count'),
            ('entropy', 'Structural entropy'),
            ('frame_count', 'Frame count'),
            ('efficiency', 'Efficiency'),
            ('I_phi_X', 'I(phi;X)'),
        ]:
            h_vals = [m[metric] for m in human_results]
            p_vals = [m[metric] for m in pythia_results]
            h_avg = sum(h_vals) / n
            p_avg = sum(p_vals) / n
            n_h = sum(1 for h, p in zip(h_vals, p_vals) if h > p)
            n_p = sum(1 for h, p in zip(h_vals, p_vals) if h < p)
            n_t = sum(1 for h, p in zip(h_vals, p_vals) if h == p)
            direction = f"{n_h}/{n} Human" if n_h > n_p else f"{n_p}/{n} Pythia"
            print(f"  {label:<22} H={h_avg:.3f} P={p_avg:.3f} delta={h_avg-p_avg:+.3f}  {direction}" + (f" ({n_t} ties)" if n_t else ""))

    print(f"\n  Done. Model: {model_name} on {device}.")
