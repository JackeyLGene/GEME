"""
GEM 6.1 — Q-Sandbox Observation Report.

World: Robinson Q (successor + addition + multiplication, no induction).
Input: Human-readable arithmetic expressions.
        "1+1=2", "0+1=1", "x+y=y+x", ...
System: GEME classifies each → harm/stress → transition → emergence.
Output: The human observer reads the full pipeline.

No hidden state. No pre-selected answers. Just structured visibility.
"""

import sys, io
sys.path.insert(0, r'g:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from gira.phase6.entity import GEME
from gira.phase6.wittgenstein import WittgensteinTable
from gira.phase3.language import eq, fn, var, constant, forall
from gira.phase3.q_axioms import robinson_q


x, y, z = var("x"), var("y"), var("z")

# ============================================================
# Human-readable input catalog
# ============================================================
# Each input is what a human writes and reads.
# The Wittgenstein Table translates it internally.
# ============================================================
INPUTS = [
    # Human expression                             → Formal formula (for GEME)
    ("0=0",           "trivial",                    eq(constant("0"), constant("0"))),
    ("1+1=2",         "ground arithmetic",          eq(fn("+", fn("s", constant("0")), fn("s", constant("0"))),
                                                         fn("s", fn("s", constant("0"))))),
    ("1+1=3",         "ground false",               eq(fn("+", fn("s", constant("0")), fn("s", constant("0"))),
                                                         fn("s", fn("s", fn("s", constant("0")))))),
    ("0+1=1",         "ground identity",            eq(fn("+", constant("0"), fn("s", constant("0"))),
                                                         fn("s", constant("0")))),
    ("x+0=x",         "identity",                   eq(fn("+", x, constant("0")), x)),
    ("x×0=0",         "multiplication zero",         eq(fn("\u00d7", x, constant("0")), constant("0"))),
    ("∀x∀y(x+y=y+x)", "commutativity of addition",  forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))),
    ("∀x∀y(x×y=y×x)", "commutativity of multiplication", forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x))))),
    ("∀x∀y∀z(x+(y+z)=(x+y)+z)", "associativity of addition", forall("x", forall("y", forall("z",
        eq(fn("+", x, fn("+", y, z)), fn("+", fn("+", x, y), z)))))),
    ("∀x∀y∀z(x×(y×z)=(x×y)×z)", "associativity of multiplication", forall("x", forall("y", forall("z",
        eq(fn("\u00d7", x, fn("\u00d7", y, z)), fn("\u00d7", fn("\u00d7", x, y), z)))))),
    ("∀x∀y∀z(x×(y+z)=(x×y)+(x×z))", "distributivity", forall("x", forall("y", forall("z",
        eq(fn("\u00d7", x, fn("+", y, z)), fn("+", fn("\u00d7", x, y), fn("\u00d7", x, z))))))),
    ("∀x(x×1=x)",     "multiplicative identity",    forall("x", eq(fn("\u00d7", x, fn("s", constant("0"))), x))),
]


def render():
    sep = "=" * 70
    sub = "-" * 70
    
    entity = GEME(axioms=robinson_q())
    
    # ── Pre-classification ──
    pre = {}
    for name, _, formula in INPUTS:
        L_F, _, _ = entity.evaluate(formula)
        pre[name] = L_F
    
    boundaries = [(n, f) for n, _, f in INPUTS if pre[n] >= 3]
    in_grammar = [(n, f) for n, _, f in INPUTS if pre[n] < 3]
    
    # ============================================================
    # [1] TRAINING DATA
    # ============================================================
    print(sep)
    print("  GEM 6.1 — Q-SANDBOX OBSERVATION REPORT")
    print("  Robot: Human reads the arithmetic. GEME sees the structure.")
    print(sep)
    print()
    print("[1] TRAINING DATA")
    print(sub)
    print("  World: Robinson Q (successor + addition + multiplication)")
    print("  Induction: NOT present in axioms — it must emerge.")
    print(f"  Training signals: {len(boundaries)}")
    print()
    print("  Frame  Human Input                 L    Harm   Signal Stress")
    print("  " + "-" * 58)
    
    for round_idx in range(8):
        for name, formula in boundaries:
            result = entity.process(formula)
            if result["frame"] <= 8 or result["frame"] % 30 == 0:
                L_F = result.get("L_F", 3)
                print(f"  {result['frame']:<6} {name:<32} L{L_F:<3} {result.get('boundary',1.0):.1f}    {result['stress']:.3f}")
        if entity.system_level > 0:
            break
    
    print(f"\n  Total frames: {entity.entity.frame_count}")
    print(f"  Final stress: {entity.stress:.3f}")
    print(f"  Transition at frame: {entity.entity._last_transition_frame}")
    
    # ============================================================
    # [2] INPUT SPACE
    # ============================================================
    print()
    print()
    print("[2] INPUT SPACE (Human Expression)")
    print(sub)
    print("  Each input is a human-readable arithmetic statement.")
    print("  After training: re-evaluation.")
    print()
    print("  Human Input                      Type                 L-pre    L-post")
    print("  " + "-" * 58)
    
    for name, desc, formula in INPUTS:
        L_pre = pre[name]
        L_post, _, _ = entity.evaluate(formula)
        status = "[emerged]" if L_pre >= 3 and L_post < 3 else "[ok]" if L_post < 3 else "[-]"
        print(f"  {name:<34} {desc:<18} L{L_pre:<6} L{L_post:<6} {status}")
    
    # ============================================================
    # [3] BOUNDARY MAP
    # ============================================================
    print()
    print()
    print("[3] BOUNDARY MAP (Wittgenstein Table Signatures)")
    print(sub)
    print("  These are the structural signatures generated by the")
    print("  Wittgenstein Table — not human labels.")
    print()
    print("  Signature                                           Count")
    print("  " + "-" * 58)
    
    sig_counts = {}
    for rec in entity.boundary_history:
        sig = rec.signature
        sig_counts[sig] = sig_counts.get(sig, 0) + 1
    
    for sig, count in sorted(sig_counts.items(), key=lambda x: -x[1]):
        print(f"  {sig:<50} {count:<4}")
    
    # ============================================================
    # [4] EMERGENCE LOG
    # ============================================================
    print()
    print()
    print("[4] EMERGENCE LOG")
    print(sub)
    print("  Formulas that crossed the boundary (L3→L2):")
    print()
    
    emerged = []
    for name, _, formula in INPUTS:
        L_post, _, _ = entity.evaluate(formula)
        if pre[name] >= 3 and L_post < 3:
            emerged.append((name, pre[name], L_post))
    
    if emerged:
        print(f"  {'Human Input':<34} {'Before':<8} {'After':<8}")
        print(f"  " + "-" * 50)
        for name, old, new in emerged:
            print(f"  {name:<34} L{old:<7} L{new:<7}")
        print(f"\n  Total: {len(emerged)}/{len(boundaries)} boundary formulas emerged.")
    else:
        print("  No emergence observed.")
    
    # ============================================================
    # [5] RULE CATALOG
    # ============================================================
    print()
    print()
    print("[5] RULE CATALOG (Synthesized Induction Rules)")
    print(sub)
    print(f"  Rules synthesized after transition: {len(entity.extracted_rules)}")
    print()
    for i, rule in enumerate(entity.extracted_rules, 1):
        tmpl = str(rule.predicate_template)[:60] if rule.predicate_template else "N/A"
        print(f"  Rule {i}")
        print(f"    Name: {rule.name()}")
        print(f"    Template: {tmpl}")
        print()
    
    # ============================================================
    # [6] SUMMARY
    # ============================================================
    print()
    print("[6] SUMMARY")
    print(sub)
    print(f"  World:      Robinson Q")
    print(f"  Inputs:     {len(INPUTS)} human-readable expressions")
    print(f"  Grammar:    {len(in_grammar)} in-grammar + {len(boundaries)} boundary")
    print(f"  Training:   {entity.entity.frame_count} frames")
    print(f"  Transition: L(E) 0 → {entity.system_level}")
    print(f"  Signatures: {len(sig_counts)} structural patterns")
    print(f"  Rules:      {len(entity.extracted_rules)} induction rules")
    print(f"  Emergence:  {len(emerged)}/{len(boundaries)} boundary formulas ({len(emerged)/len(boundaries)*100:.0f}%)")
    print()
    print(sep)
    print("  GEME is a cognitive oscilloscope.")
    print("  The human reads the input. The human reads the output.")
    print("  Pattern recognition belongs to the observer.")
    print(sep)


if __name__ == "__main__":
    render()

