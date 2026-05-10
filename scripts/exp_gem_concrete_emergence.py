"""
GEM 6.1 — Concrete Induction Emergence.

No formulas with variables in training.
Only concrete arithmetic: "1+2=2+1", "2+3=3+2", ..., "1×2=2×1", ...

Patterns emerge from concrete instances:
  System sees 50+ "swap" patterns with different concrete numbers
  → PatternAnalyzer detects the "swap" cluster
  → InductionSynthesizer proposes variable-based generalization
  → ∀x∀y(x+y=y+x) emerges — without being pre-given
"""

import sys, io
sys.path.insert(0, r'G:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from gira.phase6.entity import GEME
from gira.phase4.pattern_tracker import compute_signature
from gira.phase3.language import eq, fn, constant
from gira.phase3.q_axioms import robinson_q


def numeral(n: int):
    """Build sⁿ(0) as a Term."""
    t = constant("0")
    for _ in range(n):
        t = fn("s", t)
    return t


def concrete_eq(a: int, b: int, op: str) -> 'Formula':
    """Concrete equation: a op b = b op a."""
    if op == "+":
        return eq(fn("+", numeral(a), numeral(b)),
                  fn("+", numeral(b), numeral(a)))
    elif op == "\u00d7":
        return eq(fn("\u00d7", numeral(a), numeral(b)),
                  fn("\u00d7", numeral(b), numeral(a)))
    raise ValueError(f"unknown op: {op}")


# ============================================================
# Concrete training sets — no variables, no quantifiers
# ============================================================
ADDITIVE_SWAPS = [
    (concrete_eq(i, j, "+"), f"{i}+{j}={j}+{i}")
    for i in range(1, 6) for j in range(i + 1, 6)
]  # 10 concrete swap instances

MULTIPLICATIVE_SWAPS = [
    (concrete_eq(i, j, "\u00d7"), f"{i}\u00d7{j}={j}\u00d7{i}")
    for i in range(1, 5) for j in range(i + 1, 5)
]  # 6 concrete swap instances

# ============================================================
# Evaluation candidates (with variables — never seen in training)
# ============================================================
from gira.phase3.language import var, forall, constant
x = var("x")
y = var("y")

add_comm_forall = forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))
mul_comm_forall = forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x))))


def run():
    sep = "=" * 70
    
    entity = GEME(axioms=robinson_q())
    
    # ── Pre-evaluate comm ∀-formulas (unknown to system) ──
    L_add_pre, _, _ = entity.evaluate(add_comm_forall)
    L_mul_pre, _, _ = entity.evaluate(mul_comm_forall)
    
    print(sep)
    print("  GEM 6.1 — CONCRETE INDUCTION EMERGENCE")
    print("  No universal formulas in training.")
    print("  Only concrete instances: 1+2=2+1, 2+3=3+2, ...")
    print(sep)
    
    print(f"\n[1] TRAINING: Concrete Swap Instances")
    print(f"  {'-'*55}")
    print(f"  Additive swaps:  {len(ADDITIVE_SWAPS)} concrete equations")
    
    # ── Training Phase ──
    for i in range(4):  # 4 rounds of training
        for formula, label in ADDITIVE_SWAPS:
            result = entity.process(formula)
        for formula, label in MULTIPLICATIVE_SWAPS:
            entity.process(formula)
        if entity.system_level > 0:
            print(f"  Transition at round {i+1}")
            break
    
    print(f"  Total frames: {entity.entity.frame_count}")
    print(f"  Final stress: {entity.stress:.3f}")
    
    # ── Post-evaluation ──
    L_add_post, _, _ = entity.evaluate(add_comm_forall)
    L_mul_post, _, _ = entity.evaluate(mul_comm_forall)
    
    print(f"\n[2] EMERGENCE (L3 → L2)")
    print(f"  {'-'*55}")
    add_emerged = L_add_pre >= 3 and L_add_post < 3
    mul_emerged = L_mul_pre >= 3 and L_mul_post < 3
    print(f"  ∀x∀y(x+y=y+x):  L{L_add_pre} → L{L_add_post}  {'EMERGED' if add_emerged else '-'}")
    print(f"  ∀x∀y(x×y=y×x):  L{L_mul_pre} → L{L_mul_post}  {'EMERGED' if mul_emerged else '-'}")
    
    print(f"\n[3] RULES SYNTHESIZED: {len(entity.extracted_rules)}")
    for i, rule in enumerate(entity.extracted_rules, 1):
        print(f"  Rule {i}: {rule.name()}")
    
    print(f"\n[4] SUMMARY")
    print(f"  {'-'*55}")
    print(f"  Training: 10 concrete additive swaps + 6 multiplicative swaps")
    print(f"  Test:     ∀-formulas never seen in training")
    emerged_count = sum([add_emerged, mul_emerged])
    print(f"  Emergence: {emerged_count}/2 universal formulas emerged")
    print(f"\n  {'✓' if emerged_count > 0 else '×'} Variables emerged from concrete instances")
    
    print(f"\n{sep}")
    print(f"  GEME oscilloscope. Concrete → Abstract. Witnessed.")
    print(f"{sep}")


if __name__ == "__main__":
    run()
