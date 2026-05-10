"""GEME V6 — S4 driven emergence.

Feed S4 self-referential signals + minimal S0/S1/S3.
No concrete S2 swap patterns.
Observe if commutativity still emerges.
"""
import sys, random
sys.path.insert(0, r'G:\GEME\src')

from gira.phase6.geme_v6 import GEME
from gira.phase3.language import eq, fn, var, constant, forall, Term
from gira.phase3.q_axioms import robinson_q


def numeral(n):
    t = constant("0")
    for _ in range(n): t = fn("s", t)
    return t


# ── S4 constructor ──
def gen_S4(formula, label=""):
    """Create S4: sub(#GN, code, #GN) = sub(#GN, code, #GN)."""
    gn = formula.gn()
    gn_t = Term("numeral", value=gn)
    code_t = Term("numeral", value=17)
    s = Term("function", "sub", [gn_t, code_t, gn_t])
    return (eq(s, s), f"S4:{label}")


# ── S0 fragments ──
def gen_S0(n):
    data = []
    for i in range(n):
        c = chr(ord('a') + (i % 5))
        t = eq(constant(c), constant(c))
        data.append((t, "S0"))
    return data


# ── S1 ground ──
def gen_S1(n):
    random.seed(1)
    data = []
    for _ in range(n):
        a = random.randint(0, 6)
        b = random.randint(0, 6)
        v = a + b
        t = eq(fn("+", numeral(a), numeral(b)), numeral(v))
        data.append((t, "S1"))
    return data


# ── S3 quantified (no concrete swaps) ──
def gen_S3(n):
    x, y = var("x"), var("y")
    formulas = [
        forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x)))),
        forall("x", eq(fn("+", x, constant("0")), x)),
        forall("x", eq(fn("\u00d7", x, constant("1")), x)),
    ]
    data = []
    for i in range(n):
        t = formulas[i % len(formulas)]
        data.append((t, "S3"))
    return data


# Test targets
x, y = var("x"), var("y")
T_ADD = forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))
T_MUL = forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x))))


def run():
    e = GEME(axioms=robinson_q(), memory_cap=25, merge_thresh=0.01, stress_threshold=0.8)
    
    # Build training data with S4
    s0 = gen_S0(8)
    s1 = gen_S1(12)
    s3 = gen_S3(10)
    
    # S4: mix of self-referential formulas
    s4 = []
    for label, formula in [
        ("add-swap", T_ADD),
        ("mul-swap", T_MUL),
        ("x+0=x", eq(fn("+", x, constant("0")), x)),
        ("x*1=x", eq(fn("\u00d7", x, constant("1")), x)),
    ]:
        s4.append(gen_S4(formula, label))
    
    # Full dataset: NO concrete S2 swap patterns
    data = s0 + s1 + s3 + s4
    random.Random(42).shuffle(data)
    
    print("=" * 65)
    print("  GEME V6 — S4 Driven Emergence")
    print("=" * 65)
    print(f"  S0: {len(s0)} fragments")
    print(f"  S1: {len(s1)} ground")
    print(f"  S3: {len(s3)} quantified (no concrete!)")
    print(f"  S4: {len(s4)} self-referential")
    print(f"  Total: {len(data)} frames")
    print("  [NO concrete S2 swap instances]")
    print()
    
    # Track per category
    from collections import defaultdict
    cat_mem = defaultdict(list)
    
    s_add_pre = e.evaluate(T_ADD)
    s_mul_pre = e.evaluate(T_MUL)
    
    print("  Frm  cat        mem  eff     util  stress accum  S_F  L(E)")
    print("  " + "-" * 65)
    
    for rnd in range(8):
        for form, cat in data:
            r = e.process(form)
            cat_mem[cat[:3]].append(r["mem"])
            if r["frame"] % 8 == 0:
                print("  %-4d %-10s %-4d %-6.4f %-6.4f %-6.4f %-6.4f %-4d %d"
                      % (r["frame"], cat[:10], r["mem"], r["eff"],
                         r["util"], r["stress"], r["accum"],
                         r["S_F"], r["L_E"]))
        if e.system_level > 1:
            break
    
    s_add_post = e.evaluate(T_ADD)
    s_mul_post = e.evaluate(T_MUL)
    
    print(f"\n  UNIVERSAL FORMULAS:")
    for nm, pre, post in [("add-swap", s_add_pre, s_add_post),
                           ("mul-swap", s_mul_pre, s_mul_post)]:
        delta = "EMERGED" if post < pre else "-"
        print(f"    {nm:14}  S{pre} -> S{post}  {delta}")
    print(f"\n  L(E)={e.system_level}  rules={len(e.extracted_rules)}  memory={len(e.memory.frames)}/{e.memory.capacity}")
    for r in e.extracted_rules:
        print(f"    {r.name()}")
    
    # Avg memory per cat
    print(f"\n  Avg memory usage per category (last 5 frames):")
    for cat, vals in sorted(cat_mem.items()):
        if vals:
            print(f"    {cat}:  avg mem = {sum(vals[-5:])/min(5,len(vals)):.1f}")
    print("=" * 65)


if __name__ == "__main__":
    run()
