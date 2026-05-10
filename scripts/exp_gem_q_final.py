"""
GEM 6.1 — Q-Sandbox: Concrete → Induction Emergence.

S-levels (signal level, not system level):
  S1: ground truth (within grammar)
  S2: derivable via inference
  S3: in-grammar but undecidable (boundary)
  S4: self-referential (Godel)

Training: concrete swap instances only (no universal formulas).
System accumulates internal stress from pattern repetition.
Transition → rule synthesis → S3→S2 emergence.
"""

import sys, io
sys.path.insert(0, r'G:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from gira.phase6.entity import GEME
from gira.phase3.language import eq, fn, constant, var, forall
from gira.phase3.q_axioms import robinson_q


def numeral(n):
    t = constant("0")
    for _ in range(n):
        t = fn("s", t)
    return t


def swap_eq(a, b, op):
    if op == "+":
        return eq(fn("+", numeral(a), numeral(b)),
                  fn("+", numeral(b), numeral(a)))
    return eq(fn("\u00d7", numeral(a), numeral(b)),
              fn("\u00d7", numeral(b), numeral(a)))


# Training: concrete instances only (no universal formulas)
ADD_SWAPS = [(swap_eq(i, j, "+"), f"{i}+{j}={j}+{i}")
             for i in range(1, 6) for j in range(i+1, 6)]
MUL_SWAPS = [(swap_eq(i, j, "\u00d7"), f"{i}x{j}={j}x{i}")
             for i in range(1, 5) for j in range(i+1, 5)]

# Test targets (universal formulas — never seen in training)
x, y = var("x"), var("y")
ADD_COMM = forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))
MUL_COMM = forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x))))


def run():
    sep = "=" * 70
    entity = GEME(axioms=robinson_q())
    
    # Pre-test: evaluate universal formulas
    add_pre, _, _ = entity.evaluate(ADD_COMM)
    mul_pre, _, _ = entity.evaluate(MUL_COMM)
    
    all_data = ADD_SWAPS + MUL_SWAPS
    
    print(sep)
    print("  GEM 6.1 — Q-SANDBOX FINAL")
    print("  Training: concrete swap instances, 0 universal formulas")
    print(sep)
    
    print(f"\n[1] TRAINING (stress accumulation)")
    print(f"  {'Frm':<5} {'Statement':<18} {'S':<3} {'Str-E':<7} {'Str-I':<7}")
    print(f"  {'-'*45}")
    
    for rnd in range(6):
        for formula, label in all_data:
            r = entity.process(formula)
            if r["frame"] <= 8 or r["frame"] % 15 == 0:
                print(f"  {r['frame']:<5} {label:<18} S{r['S_F']:<2} {r['stress_ext']:<7.3f} {r['stress_int']:<7.3f}")
        if entity.system_level > 0:
            break
    
    add_post, _, _ = entity.evaluate(ADD_COMM)
    mul_post, _, _ = entity.evaluate(MUL_COMM)
    
    print(f"\n[2] EMERGENCE (universal formulas)")
    print(f"  {'Statement':<32} {'Before':<8} {'After':<8}")
    print(f"  {'-'*50}")
    for name, pre, post in [("∀x∀y(x+y=y+x)", add_pre, add_post),
                             ("∀x∀y(x×y=y×x)", mul_pre, mul_post)]:
        delta = f"S{pre} → S{post}  {'EMERGED' if post < pre else '—'}"
        print(f"  {name:<32} S{pre:<7} S{post:<7} {delta}")
    
    print(f"\n[3] WITTGENSTEIN TABLE (symbol usage)")
    print(f"  {'Symbol':<8} {'GN':<6} {'Count':<8}")
    print(f"  {'-'*25}")
    for sym, cnt in sorted(entity.symbol_usage_report().items(), key=lambda x: -x[1]):
        gn = ord(sym) if len(sym) == 1 else hash(sym) % 100
        print(f"  {sym!r:<8} {gn:<6} {cnt:<8}")
    
    ev = entity.stress_vector()
    print(f"\n[4] SUMMARY")
    print(f"  {'-'*50}")
    print(f"  Training:     {entity.entity.frame_count} frames, {len(all_data)} concrete statements")
    print(f"  Level:        L(E) = {entity.system_level}")
    print(f"  Stress:       external={ev[0]:.3f}  internal={ev[1]:.3f}")
    print(f"  Rules:        {len(entity.extracted_rules)}")
    emerged = (add_pre >= 3 and add_post < 3) or (mul_pre >= 3 and mul_post < 3)
    print(f"  Emergence:    {'YES' if emerged else 'NO'}")
    
    print(f"\n{sep}")
    print("  GEME — cognitive oscilloscope.")
    print("  Concrete → abstract. Structure visible.")
    print(sep)


if __name__ == "__main__":
    run()
