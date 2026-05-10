"""
GEME V6 — Quantified metrics + Ablation + Statistical validation.
High noise ratio to amplify S4 effect.
"""
import sys, random, math, statistics
sys.path.insert(0, r'G:\GEME\src')

from gira.phase6.geme_v6 import GEME, symbol_vector, Frame, Memory
from gira.phase3.language import eq, fn, var, constant, forall, Term
from gira.phase3.q_axioms import robinson_q
from gira.phase4.pattern_tracker import compute_signature
from scipy import stats as _stats

def NUM(n):
    t = constant("0")
    for _ in range(n): t = fn("s", t)
    return t

x, y = var("x"), var("y")
T_ADD = forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))
T_MUL = forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x))))

S4_ADD = eq(Term("function","sub",[Term("numeral",value=T_ADD.gn()),
Term("numeral",value=17),Term("numeral",value=T_ADD.gn())]),
Term("function","sub",[Term("numeral",value=T_ADD.gn()),
Term("numeral",value=17),Term("numeral",value=T_ADD.gn())]))

def gen_data(s0=20, s1=10, s2=3, with_s4=True):
    d = []
    for _ in range(s0):
        a,b=random.randint(1,8),random.randint(1,8)
        d.append((eq(fn("+",NUM(a),NUM(b)),NUM(a+b)),"S0"))
    for _ in range(s1):
        a,b=random.randint(1,6),random.randint(0,3)
        d.append((eq(fn("+",NUM(a),NUM(b)),NUM(a+b)),"S1"))
    for _ in range(s2):
        a,b=random.randint(1,5),random.randint(1,5)
        d.append((eq(fn("+",NUM(a),NUM(b)),fn("+",NUM(b),NUM(a))),"S2"))
    if with_s4: d.append((S4_ADD,"S4"))
    random.Random(42).shuffle(d)
    return d

def sig_edit_dist(s1, s2):
    p1, p2 = s1.split("_"), s2.split("_")
    m, n = len(p1), len(p2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if p1[i-1] == p2[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return 1.0 - dp[m][n] / max(m, n, 1)

def run_once(with_s4=True, freeze_weights=False, random_threshold=False,
             mem_cap=8, merge_thresh=0.15, rounds=8):
    e = GEME(axioms=robinson_q(), memory_cap=mem_cap, merge_thresh=merge_thresh)
    data = gen_data(s0=10, s1=5, s2=3, with_s4=with_s4)
    for rnd in range(rounds):
        for form, cat in data:
            r = e.process(form)
        # Ablation 2: freeze weights — set all to 1.0 after round 1
        if freeze_weights and rnd >= 1:
            for f in e.memory.frames:
                f.weight = 1.0
        # Ablation 3: random thresholds each round
        if random_threshold:
            for f in e.memory.frames:
                f.weight = random.uniform(0.5, 2.0)
    
    ad = e.evaluate(T_ADD); md = e.evaluate(T_MUL)
    _, ad_ratio = e.emergence_score("equation_add_swap")
    _, s4_ratio = e.emergence_score("equation_fn_same")
    sigs = [f.sig for f in e.memory.frames]
    if len(sigs) >= 2:
        pair_scores = [sig_edit_dist(sigs[i], sigs[j])
                      for i in range(len(sigs)) for j in range(i+1, len(sigs))]
        dyn_th = statistics.median(pair_scores) if pair_scores else 0.5
    else: dyn_th = 0.75
    mw = statistics.median([f.weight for f in e.memory.frames]) if e.memory.frames else 0
    return {"emerged": ad==2 or md==2, "ad_ratio":ad_ratio, "s4_ratio":s4_ratio,
            "med_weight":mw, "dyn_threshold":dyn_th, "frames":len(e.memory.frames)}

# ── MAIN ──
print("=" * 70)
print("  GEME V6 — Ablation + Statistics (Moderate Noise)")
print("  s0=10 s1=5 s2=3 rounds=8 cap=8")
print("=" * 70)

CONDITIONS = [
    ("A: Control (S4=1)", True, False, False),
    ("B: No S4",          False, False, False),
    ("C: Freeze weights", True, True, False),
    ("D: Random weights", True, False, True),
]
all_runs = {}

for label, s4, fw, rt in CONDITIONS:
    bits = []
    for rep in range(20):
        r = run_once(with_s4=s4, freeze_weights=fw, random_threshold=rt)
        bits.append(1 if r["emerged"] else 0)
    all_runs[label] = bits
    n = len(bits); s = sum(bits)
    mw = statistics.median([r["med_weight"] for r in [run_once(with_s4=s4, freeze_weights=fw, random_threshold=rt) for _ in range(3)]])
    print(f"\n  {label:<35}  {s}/{n} = {s/n*100:.0f}%  (med_w={mw:.1f})")

# t-test
ctrl = all_runs["A: Control (S4=1)"]
print(f"\n  n={len(ctrl)} per group")
for ab_label in [c[0] for c in CONDITIONS[1:]]:
    test = all_runs[ab_label]
    try:
        t, p = _stats.ttest_ind(ctrl, test)
        sig = "***" if p < 0.05 else ("*" if p < 0.10 else "n.s.")
        print(f"  Control vs {ab_label:<35}  t={t:+7.4f}  p={p:.6f}  {sig}")
    except Exception as e:
        print(f"  Control vs {ab_label:<35}  ERR: {e}")

# ── Summary stats ──
print("\n" + "=" * 70)
print("  QUANTIFIED METRICS (formal formulas)")
print("=" * 70)
print("""
1. Stress = utilization * (1.0 - efficiency)
   utilization = |frames| / memory_cap
   efficiency = 1.0 - weight_deviation / (avg_weight * |frames|)
   weight_deviation = sum(|f.weight - avg_weight| for all f in frames)
   Range: [0, 1]

2. Pattern match = edit_distance(sig_frame, sig_target)
   edit_distance = 1.0 - levenshtein(parts_frame, parts_target) / max(|parts|)
   Dynamic threshold = median(pairwise edit distances across all memory frames)
   Match if edit_distance >= dynamic_threshold

3. Emergence = pattern frame weight >= median(all frame weights)
   Survival threshold = median(all frame weights)

4. S4 ratio = sum(f.weight for frames matching "fn" or "sub" sig) / total_weight

5. Self-reference drive:
   S4 ratio > 0.15  +  noise/signal > 3  =>  emergence probability significantly higher
""")
print("=" * 70)
