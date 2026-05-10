"""
GEME V6 — Supplementary experiments: robustness, patterns, params, S4 ratio.
"""
import sys, random, time, math
sys.path.insert(0, r'G:\GEME\src')

from gira.phase6.geme_v6 import GEME
from gira.phase4.pattern_tracker import compute_signature
from gira.phase3.language import eq, fn, var, constant, forall, Term
from gira.phase3.q_axioms import robinson_q

def NUM(n):
    t = constant("0")
    for _ in range(n): t = fn("s", t)
    return t
x, y, z = var("x"), var("y"), var("z")

# ── Target formulas ──
TARGETS = {
    "add_comm": forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x)))),
    "mul_comm": forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x)))),
    "add_assoc": forall("x", forall("y", forall("z",
        eq(fn("+", fn("+", x, y), z), fn("+", x, fn("+", y, z)))))),
    "distrib": forall("x", forall("y", forall("z",
        eq(fn("\u00d7", x, fn("+", y, z)), fn("+", fn("\u00d7", x, y), fn("\u00d7", x, z)))))),
    "add_zero": forall("x", eq(fn("+", x, constant("0")), x)),
    "mul_one": forall("x", eq(fn("\u00d7", x, constant("1")), x)),
}

# ── Data generators ──
def gen_S0(n, seed=42):
    random.seed(seed)
    d = []
    for _ in range(n):
        a, b = random.randint(1, 8), random.randint(1, 8)
        op = random.choice(["+", "\u00d7"])
        d.append((eq(fn(op, NUM(a), NUM(b)), NUM(a + b if op == "+" else a * b)), "S0"))
    return d

def gen_S1(n, seed=43):
    random.seed(seed)
    d = []
    for _ in range(n):
        a, b = random.randint(1, 6), random.randint(0, 3)
        d.append((eq(fn("+", NUM(a), NUM(b)), NUM(a + b)), "S1"))
    return d

def gen_S2(n, op="+", seed=None):
    if seed is not None: random.seed(seed)
    d = []
    for _ in range(n):
        a, b = random.randint(1, 5), random.randint(1, 5)
        d.append((eq(fn(op, NUM(a), NUM(b)), fn(op, NUM(b), NUM(a))), "S2"))
    return d

def gen_S2_assoc(n, seed=None):
    if seed is not None: random.seed(seed)
    d = []
    for _ in range(n):
        a, b, c = random.randint(1, 4), random.randint(1, 4), random.randint(1, 4)
        d.append((eq(fn("+", fn("+", NUM(a), NUM(b)), NUM(c)),
                     fn("+", NUM(a), fn("+", NUM(b), NUM(c)))), "S2_assoc"))
    return d

def gen_S2_distrib(n, seed=None):
    if seed is not None: random.seed(seed)
    d = []
    for _ in range(n):
        a, b, c = random.randint(1, 3), random.randint(1, 3), random.randint(1, 3)
        d.append((eq(fn("\u00d7", NUM(a), fn("+", NUM(b), NUM(c))),
                     fn("+", fn("\u00d7", NUM(a), NUM(b)), fn("\u00d7", NUM(a), NUM(c)))), "S2_distrib"))
    return d

def gen_S4(formula, label):
    gn = formula.gn()
    s = Term("function", "sub", [Term("numeral", value=gn), Term("numeral", value=17), Term("numeral", value=gn)])
    return (eq(s, s), label)

S4_LIST = [gen_S4(TARGETS["add_comm"], "S4:add")]

# ============================================================
# Experiment 1: High noise robustness
# ============================================================
def exp_high_noise():
    print("=" * 65)
    print("  1. HIGH NOISE ROBUSTNESS")
    print("=" * 65)
    for s4, label in [(S4_LIST, "WITH S4"), ([], "NO S4")]:
        e = GEME(axioms=robinson_q(), memory_cap=10, merge_thresh=0.15)
        data = gen_S0(40) + gen_S1(20) + gen_S2(10) + s4
        random.Random(42).shuffle(data)
        for rnd in range(10):
            for form, _ in data: e.process(form)
        results = {nm: e.evaluate(f) for nm, f in TARGETS.items()}
        emerged = [nm for nm, v in results.items() if v == 2]
        print(f"\n  {label} (40 S0 + 20 S1 + 10 S2)")
        print(f"    S4 ratio: {e.emergence_score('equation_fn_same')[1]:.2f}")
        print(f"    Emerged: {', '.join(emerged) if emerged else 'NONE'}")

# ============================================================
# Experiment 2: More patterns (assoc, distrib)
# ============================================================
def exp_more_patterns():
    print("\n" + "=" * 65)
    print("  2. MORE PATTERNS — ASSOC + DISTRIB")
    print("=" * 65)
    configs = [
        ("ADD + S4", robinson_q(), S4_LIST + gen_S2_assoc(15)),
        ("ADD NO S4", robinson_q(), gen_S2_assoc(15)),
        ("MUL + S4", robinson_q(), S4_LIST + gen_S2_distrib(15, seed=55)),
        ("MUL NO S4", robinson_q(), gen_S2_distrib(15, seed=55)),
    ]
    for label, axioms, data_in in configs:
        e = GEME(axioms=axioms, memory_cap=10, merge_thresh=0.15)
        extra = gen_S0(10) + gen_S1(5)
        data = extra + data_in
        random.Random(42).shuffle(data)
        pre = {"add_assoc": e.evaluate(TARGETS["add_assoc"]),
               "distrib": e.evaluate(TARGETS["distrib"])}
        for rnd in range(15):
            for form, _ in data: e.process(form)
        post = {"add_assoc": e.evaluate(TARGETS["add_assoc"]),
                "distrib": e.evaluate(TARGETS["distrib"])}
        ad_em, ad_r = e.emergence_score("equation_add_succ_ee")
        # Rough pattern check
        print(f"\n  {label}")
        for nm, pr, po in [("add_assoc", pre["add_assoc"], post["add_assoc"]),
                           ("distrib", pre["distrib"], post["distrib"])]:
            e_flag = "E" if po < pr else "-"
            print(f"    {nm:10}  S{pr} -> S{po}  {e_flag}")

# ============================================================
# Experiment 3: Parameter sensitivity
# ============================================================
def exp_params():
    print("\n" + "=" * 65)
    print("  3. PARAMETER SENSITIVITY")
    print("=" * 65)
    print("\n  memory_cap sweep (merge_thresh=0.15):")
    print("  cap  mem_rules add_comm  mul_comm  S4_ratio")
    for cap in [6, 8, 10, 12, 15]:
        e = GEME(axioms=robinson_q(), memory_cap=cap, merge_thresh=0.15)
        data = gen_S0(15) + gen_S1(8) + gen_S2(8) + S4_LIST
        random.Random(42).shuffle(data)
        for rnd in range(12):
            for form, _ in data: e.process(form)
        ad = e.evaluate(TARGETS["add_comm"])
        md = e.evaluate(TARGETS["mul_comm"])
        _, sr = e.emergence_score("equation_fn_same")
        print(f"  {cap:<4} {e.memory.rule_count:<8} S{ad}      S{md}      {sr:.2f}")

    print("\n  merge_threshold sweep (memory_cap=10):")
    print("  thresh mem_rules add_comm  mul_comm  S4_ratio")
    for th in [0.08, 0.12, 0.15, 0.20, 0.30]:
        e = GEME(axioms=robinson_q(), memory_cap=10, merge_thresh=th)
        data = gen_S0(15) + gen_S1(8) + gen_S2(8) + S4_LIST
        random.Random(42).shuffle(data)
        for rnd in range(12):
            for form, _ in data: e.process(form)
        ad = e.evaluate(TARGETS["add_comm"])
        md = e.evaluate(TARGETS["mul_comm"])
        _, sr = e.emergence_score("equation_fn_same")
        print(f"  {th:<5.2f} {e.memory.rule_count:<8} S{ad}      S{md}      {sr:.2f}")

# ============================================================
# Experiment 4: S4 ratio quantification
# ============================================================
def exp_s4_ratio():
    print("\n" + "=" * 65)
    print("  4. S4 RATIO OVER TIME")
    print("=" * 65)
    print("\n  frame  mem  S4_w  total_w  ratio  stress  add_comm")
    e = GEME(axioms=robinson_q(), memory_cap=10, merge_thresh=0.15)
    data = gen_S0(15) + gen_S1(8) + gen_S2(8) + S4_LIST
    random.Random(42).shuffle(data)
    for rnd in range(15):
        for form, cat in data:
            r = e.process(form)
            # Compute S4 weight ratio
            s4_w = sum(f.weight for f in e.memory.frames
                       if "fn" in f.sig or "sub" in f.sig or "S4" in f.sig)
            tw = e.memory.total_weight
            sr4 = s4_w / max(tw, 1)
            if r["frame"] % 30 == 0 or r["frame"] == 1:
                ad = e.evaluate(TARGETS["add_comm"])
                print(f"  {r['frame']:<5} {r['mem']:<4} {s4_w:<6.1f} {tw:<8.1f} {sr4:<6.3f} {r['stress']:<7.4f} S{ad}")

# ============================================================
# Experiment 5: Performance
# ============================================================
def exp_perf():
    print("\n" + "=" * 65)
    print("  5. PERFORMANCE")
    print("=" * 65)
    for n_frames in [500, 2000, 5000]:
        e = GEME(axioms=robinson_q(), memory_cap=10, merge_thresh=0.15)
        data = gen_S0(20) + gen_S1(10) + gen_S2(5) + S4_LIST
        random.Random(42).shuffle(data)
        t0 = time.time()
        cnt = 0
        while cnt < n_frames:
            for form, _ in data:
                e.process(form)
                cnt += 1
                if cnt >= n_frames: break
        dt = time.time() - t0
        print(f"  {n_frames:5} frames: {dt:.2f}s  ({n_frames/max(dt,0.001):.0f} fps)  mem={len(e.memory.frames)}")

# ============================================================
# Run all
# ============================================================
if __name__ == "__main__":
    exp_high_noise()
    exp_more_patterns()
    exp_params()
    exp_s4_ratio()
    exp_perf()
    print("\n" + "=" * 65)
    print("  DONE")
    print("=" * 65)
