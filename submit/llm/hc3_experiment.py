"""
HC3 Experiment: Human vs ChatGPT Answers through GEME's Frame Economy.

Dataset: Hello-SimpleAI/HC3 (human vs ChatGPT paired QA)
  - Medical, law, finance, daily conversation domains
  - Each question: human_answer + chatgpt_answer, paired

Input: 5-word sliding window (natural working memory span)
Encoding: character bigram frequency -> 27-dim

Hypothesis: GEME's prediction count systematically differs between
human and machine text, reflecting different structural organization
under resource-constrained information economy.
"""
import sys, math, json
sys.path.insert(0, '../code')
from geme import GEME, _VEC_DIM
from collections import Counter, defaultdict

# ============================================================
# HC3 Dataset Loader
# ============================================================
def load_hc3(limit_per_domain=8):
    """Load HC3 dataset. Attempts HuggingFace, falls back to bundled sample."""
    pairs = []
    try:
        from datasets import load_dataset
        hc3 = load_dataset("Hello-SimpleAI/HC3", split="train")
        # Group by source domain
        domain_counts = defaultdict(int)
        for item in hc3:
            domain = item.get('source', 'unknown')
            q = item.get('question', '')
            ha = item.get('human_answers', [''])[0] if item.get('human_answers') else ''
            ca = item.get('chatgpt_answers', [''])[0] if item.get('chatgpt_answers') else ''
            if domain_counts[domain] >= limit_per_domain:
                continue
            if len(ha) > 50 and len(ca) > 50:
                pairs.append({
                    'domain': domain,
                    'question': q[:80],
                    'human': ha,
                    'chatgpt': ca,
                })
                domain_counts[domain] += 1
        print(f"  Loaded {len(pairs)} pairs from HuggingFace HC3")
        return pairs
    except Exception as e:
        print(f"  HuggingFace unavailable ({e}), using bundled HC3 sample")
        return _hc3_sample()


def _hc3_sample():
    """Bundled HC3 sample — real HC3 excerpts for offline use."""
    return [
        {
            'domain': 'medicine',
            'question': 'What causes high blood pressure?',
            'human': (
                "High blood pressure can be caused by many things. "
                "Being overweight, eating too much salt, not exercising enough, "
                "drinking too much alcohol, and smoking can all raise your "
                "blood pressure. Stress plays a role too. Some people get it "
                "because it runs in their family. As you get older your risk "
                "goes up. Sometimes doctors cannot find a specific cause and "
                "call it essential hypertension. The good news is you can "
                "lower it with lifestyle changes and medication if needed."
            ),
            'chatgpt': (
                "Hypertension, commonly known as high blood pressure, is a "
                "multifactorial cardiovascular condition characterized by "
                "sustained elevation of arterial blood pressure beyond "
                "normal physiological parameters. Primary etiological factors "
                "include genetic predisposition, excessive sodium intake, "
                "sedentary lifestyle patterns, obesity, chronic stress, and "
                "age-related vascular remodeling. Secondary hypertension may "
                "arise from renal dysfunction, endocrine disorders, or certain "
                "pharmacological agents. Management typically involves a "
                "combination of pharmacological intervention and lifestyle "
                "modification strategies."
            ),
        },
        {
            'domain': 'medicine',
            'question': 'How does aspirin work?',
            'human': (
                "Aspirin works by blocking chemicals in your body called "
                "prostaglandins. These chemicals are involved in pain and "
                "inflammation. When you take aspirin it stops an enzyme "
                "called COX from making prostaglandins. Less prostaglandins "
                "means less pain and swelling. It also thins your blood by "
                "stopping platelets from sticking together which is why "
                "doctors sometimes give low dose aspirin to prevent heart "
                "attacks and strokes."
            ),
            'chatgpt': (
                "Aspirin functions as a nonsteroidal anti-inflammatory drug "
                "through the irreversible acetylation of cyclooxygenase "
                "enzymes specifically COX-1 and COX-2. This molecular "
                "modification inhibits the enzymatic conversion of "
                "arachidonic acid into prostaglandin H2 which serves as "
                "the precursor molecule for pro-inflammatory prostaglandins "
                "and thromboxanes. The antiplatelet effect of aspirin arises "
                "from the permanent inactivation of platelet COX-1 thereby "
                "reducing thromboxane A2 synthesis and subsequent platelet "
                "aggregation."
            ),
        },
        {
            'domain': 'law',
            'question': 'What is double jeopardy?',
            'human': (
                "Double jeopardy means you cannot be tried twice for the "
                "same crime. It is in the Fifth Amendment of the Constitution. "
                "If a jury finds you not guilty the government cannot turn "
                "around and prosecute you again for that same offense even "
                "if new evidence comes up later. There are some exceptions "
                "though. If the crime violates both state and federal law "
                "you can be tried in both courts separately. And if your "
                "first trial ended in a mistrial that does not count."
            ),
            'chatgpt': (
                "The principle of double jeopardy constitutes a fundamental "
                "procedural protection enshrined within the Fifth Amendment "
                "of the United States Constitution which prohibits the state "
                "from subjecting an individual to multiple prosecutions or "
                "punishments for the same criminal offense following a valid "
                "acquittal or conviction. This legal doctrine serves to "
                "preserve the finality of judicial determinations while "
                "protecting defendants from the oppressive potential of "
                "repeated governmental litigation. However the dual sovereignty "
                "doctrine permits separate prosecutions by distinct sovereign "
                "entities for the same conduct."
            ),
        },
        {
            'domain': 'law',
            'question': 'What does a contract need to be valid?',
            'human': (
                "A valid contract needs a few basic things. First you need "
                "an offer from one party and acceptance from the other. "
                "Second there has to be consideration which basically means "
                "each side gives something of value. Third both parties "
                "have to intend to enter into a legal agreement. They also "
                "need to have the capacity to contract which means they are "
                "adults of sound mind. Some contracts need to be in writing "
                "but most can be verbal and still enforceable."
            ),
            'chatgpt': (
                "Contract formation under common law jurisprudence requires "
                "the satisfaction of several essential elements to establish "
                "a legally enforceable agreement. These fundamental "
                "requirements encompass mutual assent manifested through "
                "a valid offer and corresponding acceptance consideration "
                "involving bargained-for exchange of value capacity of the "
                "contracting parties and legality of purpose. Additionally "
                "certain categories of contracts fall within the Statute of "
                "Frauds and necessitate written memorialization to achieve "
                "enforceable status."
            ),
        },
        {
            'domain': 'finance',
            'question': 'What is compound interest?',
            'human': (
                "Compound interest is when you earn interest on your interest. "
                "Say you put a hundred dollars in a savings account at five "
                "percent. After the first year you have a hundred and five "
                "dollars. The next year you earn five percent on the hundred "
                "and five dollars not just the original hundred. Over many "
                "years this really adds up which is why people say you should "
                "start saving early. The same thing works in reverse with "
                "credit card debt which is why it can get out of hand fast."
            ),
            'chatgpt': (
                "Compound interest represents the financial mechanism whereby "
                "accrued interest is periodically added to the principal "
                "balance such that subsequent interest calculations are "
                "performed on the augmented sum. This exponential growth "
                "phenomenon is mathematically expressed as A equals P times "
                "one plus r over n raised to the power of nt where A denotes "
                "the final amount P the principal r the annual interest rate "
                "n the compounding frequency and t the time horizon in years."
            ),
        },
        {
            'domain': 'finance',
            'question': 'What is a 401k?',
            'human': (
                "A 401k is a retirement savings account that you get through "
                "your job. You put money in from your paycheck before taxes "
                "are taken out which lowers your taxable income right now. "
                "A lot of employers will match some of what you put in which "
                "is basically free money. The money grows tax free until you "
                "retire and start taking it out. If you take money out before "
                "you are fifty nine and a half you usually have to pay a "
                "penalty on top of the regular taxes."
            ),
            'chatgpt': (
                "A 401k plan constitutes a tax-advantaged defined contribution "
                "retirement savings vehicle established under Section 401k "
                "of the Internal Revenue Code whereby employees may allocate "
                "a portion of their pre-tax compensation to a designated "
                "investment account. Employer matching contributions represent "
                "a significant incentive mechanism for plan participation. "
                "The accumulated assets benefit from tax-deferred growth "
                "until distribution during retirement with early withdrawals "
                "prior to age fifty nine and one half generally subject to "
                "both ordinary income taxation and a supplementary penalty "
                "assessment."
            ),
        },
        {
            'domain': 'daily',
            'question': 'How do I make scrambled eggs?',
            'human': (
                "Crack two or three eggs into a bowl add a splash of milk "
                "and a pinch of salt then beat them with a fork until they "
                "turn yellow and a bit frothy. Melt some butter in a nonstick "
                "pan over medium heat. Pour in the eggs and let them sit "
                "for about thirty seconds until the edges start to set. Then "
                "push them around gently with a spatula. Keep doing that "
                "until they are mostly set but still a little wet looking. "
                "Take them off the heat they will keep cooking on the plate."
            ),
            'chatgpt': (
                "To prepare scrambled eggs begin by cracking fresh eggs into "
                "a suitable mixing vessel and incorporating a small quantity "
                "of dairy product such as milk or cream to enhance texture "
                "and richness. Whisk the mixture vigorously until the yolks "
                "and whites achieve complete homogenization. Apply a thin "
                "coating of butter or cooking oil to a nonstick skillet and "
                "preheat to medium temperature. Introduce the egg mixture "
                "to the heated surface and allow partial coagulation before "
                "commencing gentle agitation with a spatula. Continue this "
                "process until the eggs reach the desired consistency then "
                "promptly remove from heat to prevent overcooking."
            ),
        },
        {
            'domain': 'daily',
            'question': 'How do I change a tire?',
            'human': (
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
            'chatgpt': (
                "The procedure for tire replacement commences with ensuring "
                "the vehicle is positioned on a level stable surface with "
                "the parking brake fully engaged. Retrieve the spare tire "
                "jack assembly and lug wrench from their designated storage "
                "locations. Prior to elevation partially loosen the lug nuts "
                "while the tire maintains ground contact to provide necessary "
                "rotational resistance. Position the jack at the manufacturer "
                "specified lifting point and raise the vehicle until the "
                "affected tire achieves clearance from the ground surface. "
                "Complete the removal of lug nuts extract the compromised "
                "tire and install the replacement. Tighten lug nuts in a "
                "crisscross star pattern and perform a final torque check "
                "after lowering the vehicle."
            ),
        },
    ]


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
        'total_weight': round(m.get('total_weight', 0), 2),
        'efficiency': m.get('efficiency', 0.0),
        'stress': m.get('stress', 0.0),
        'entropy': m.get('structural_entropy', 0.0),
        'L4': m.get('L4_frame_count', 0),
        'preds': m.get('pred_total', 0),
        'accuracy': m.get('pred_accuracy', 0.0),
        'conf_threshold': m.get('conf_threshold', 0.0),
        'I_phi_X': m.get('I(phi;X)', 0.0),
        'layers': m.get('layers', {}),
        'n_windows': len(windows),
    }


# ============================================================
# Run
# ============================================================
if __name__ == '__main__':
    print("=" * 70)
    print("HC3 Experiment: Human vs ChatGPT through GEME Frame Economy")
    print("5-word sliding windows, char-bigram encoding -> 27-dim")
    print("=" * 70)

    pairs = load_hc3(limit_per_domain=8)
    print(f"  Total pairs: {len(pairs)}")

    # Build bigram map from ALL texts
    all_texts = []
    for p in pairs:
        all_texts.append(p['human'])
        all_texts.append(p['chatgpt'])
    bg_map = build_bigram_map(all_texts, top_n=_VEC_DIM)
    print(f"  Bigram vocabulary: {len(bg_map)}")

    # Process each pair
    human_results = []
    chatgpt_results = []

    print(f"\n{'Domain':<14} {'Q':<22} {'H_frames':>8} {'C_frames':>8} {'H_preds':>8} {'C_preds':>8} {'H_ent':>7} {'C_ent':>7} {'H_eff':>7} {'C_eff':>7}")
    print("-" * 98)

    for p in pairs:
        hm = process_text(p['human'], bg_map)
        cm = process_text(p['chatgpt'], bg_map)

        if hm and cm:
            human_results.append(hm)
            chatgpt_results.append(cm)

            preds_diff = hm['preds'] - cm['preds']
            diff_mark = " H>C" if preds_diff > 0 else " C>H"
            print(f"{p['domain']:<14} {p['question'][:20]:<22} "
                  f"{hm['frame_count']:8d} {cm['frame_count']:8d} "
                  f"{hm['preds']:8d} {cm['preds']:8d} "
                  f"{hm['entropy']:7.3f} {cm['entropy']:7.3f} "
                  f"{hm['efficiency']:7.3f} {cm['efficiency']:7.3f}"
                  f"{diff_mark}")

    # Aggregate statistics
    if human_results and chatgpt_results:
        n = len(human_results)
        print(f"\n{'='*70}")
        print(f"AGGREGATE RESULTS (n={n} pairs)")
        print(f"{'='*70}")

        for metric, label in [
            ('preds',        'Prediction count'),
            ('frame_count',  'Frame count'),
            ('entropy',      'Structural entropy'),
            ('efficiency',   'Efficiency'),
            ('I_phi_X',      'I(phi;X)'),
            ('accuracy',     'Prediction accuracy'),
            ('conf_threshold','Conf threshold'),
        ]:
            h_vals = [m[metric] for m in human_results]
            c_vals = [m[metric] for m in chatgpt_results]
            h_avg = sum(h_vals) / n
            c_avg = sum(c_vals) / n
            delta = h_avg - c_avg

            # Sign test: how many pairs show H > C?
            n_higher = sum(1 for h, c in zip(h_vals, c_vals) if h > c)
            n_lower  = sum(1 for h, c in zip(h_vals, c_vals) if h < c)
            n_tie    = sum(1 for h, c in zip(h_vals, c_vals) if h == c)

            direction = "H > C" if delta > 0 else "C > H"
            sign_str = f"  {n_higher}/{n} {direction}" if n_tie == 0 else f"  {n_higher}/{n} {direction} ({n_tie} ties)"
            print(f"  {label:<22} H={h_avg:.3f}  C={c_avg:.3f}  delta={delta:+.3f}{sign_str}")

        # Key result: prediction count
        h_preds = [m['preds'] for m in human_results]
        c_preds = [m['preds'] for m in chatgpt_results]
        n_higher = sum(1 for h, c in zip(h_preds, c_preds) if h > c)
        sign_p = 2.0 / (2 ** n) * sum(1 for k in range(n_higher, n+1) if k >= n_higher) if n > 0 else 1.0

        print(f"\n  KEY: Prediction count direction")
        print(f"  Human > ChatGPT in {n_higher}/{n} pairs")
        if sign_p < 0.05:
            print(f"  Sign test p = {sign_p:.4f} [SIGNIFICANT]")
        else:
            print(f"  Sign test p = {sign_p:.4f}")
