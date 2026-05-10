"""
GEM Phase 6.1 — PA Sandbox (Preset Frame + Arithmetical Truth)

World: PA axioms without full induction schema (PA^-)
System: GEME observes boundary formulas autonomously
Emergence: induction rules synthesized from boundary clusters

We do NOT specify which formulas should emerge.
We provide the grammar and let boundary experience drive discovery.
"""

import sys, io
sys.path.insert(0, r'g:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
from gira.phase6.entity import GEME
from gira.phase3.language import eq, fn, var, constant, forall
from gira.phase3.q_axioms import robinson_q


# ============================================================
# Formula Space Explorer
# ============================================================

class FormulaSpace:
    """Generates the formula space for PA sandbox exploration.
    
    Not the answer — just the candidate space.
    The SYSTEM determines which are boundaries and which emerge.
    """
    
    def __init__(self):
        x, y, z = var("x"), var("y"), var("z")
        self.x, self.y, self.z = x, y, z
    
    def all_candidates(self) -> list:
        """Return the full formula space for exploration."""
        x, y, z = self.x, self.y, self.z
        return [
            # Atomic equalities (L1 candidates — should be in-grammar)
            ("0+0", eq(fn("+", constant("0"), constant("0")), constant("0"))),
            
            # Simple ground equalities
            ("1+1=2", eq(fn("+", fn("s", constant("0")), fn("s", constant("0"))),
                         fn("s", fn("s", constant("0"))))),
            
            # Quantifier-free patterns (L1-L2)
            ("x+0", eq(fn("+", x, constant("0")), x)),
            ("x+y=y+x(0)", eq(fn("+",x,constant("0")),fn("+",constant("0"),x))),
            
            # Universal equalities (L3 candidates — undecidable in Q)
            ("add_comm", forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))),
            ("mul_comm", forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x))))),
            
            ("add_assoc", forall("x", forall("y", forall("z",
                eq(fn("+", x, fn("+", y, z)), fn("+", fn("+", x, y), z)))))),
            ("mul_assoc", forall("x", forall("y", forall("z",
                eq(fn("\u00d7", x, fn("\u00d7", y, z)), fn("\u00d7", fn("\u00d7", x, y), z)))))),
            
            ("distrib", forall("x", forall("y", forall("z",
                eq(fn("\u00d7", x, fn("+", y, z)), 
                   fn("+", fn("\u00d7", x, y), fn("\u00d7", x, z))))))),
            
            # Identity properties
            ("x*1=x", forall("x", eq(fn("\u00d7", x, fn("s", constant("0"))), x))),
            ("x*0=0", forall("x", eq(fn("\u00d7", x, constant("0")), constant("0")))),
            
            # Derived equalities (potentially new emergence)
            ("add_sq", forall("x", forall("y",
                eq(fn("+", fn("\u00d7", x, y), fn("\u00d7", x, y)),
                   fn("\u00d7", x, fn("+", y, y)))))),
            ("mul_add", forall("x", forall("y", forall("z",
                eq(fn("\u00d7", fn("+", x, y), z),
                   fn("+", fn("\u00d7", x, z), fn("\u00d7", y, z))))))),
        ]


def main():
    print("=" * 65)
    print("GEM 6.1: PA Sandbox — Arithmetical Truth Emergence")
    print("=" * 65)
    
    print("\n  World: PA^- (Robinson Q, no induction schema)")
    print("  System: GEME observes formula space")
    print("  Goal: observe WHAT emerges, not verify known answers")
    
    # Build
    space = FormulaSpace()
    entity = GEME(axioms=robinson_q())
    candidates = space.all_candidates()
    
    # ============================================================
    # Phase 1: Classification (pre-experience)
    # ============================================================
    print(f"\n{'='*65}")
    print("PHASE 1: Initial Classification (L(E)=0)")
    print(f"{'='*65}")
    print(f"  {'Name':<14} {'L':<3} Status")
    print(f"  {'-'*45}")
    
    baseline = {}
    for name, formula in candidates:
        L_F, harm, reason = entity.evaluate(formula)
        baseline[name] = L_F
        marker = "BOUNDARY" if L_F >= 3 else "OK"
        print(f"  {name:<14} L{L_F}  {marker}")
    
    # ============================================================
    # Phase 2: Experience Accumulation
    # ============================================================
    print(f"\n{'='*65}")
    print("PHASE 2: Experience Accumulation")
    print(f"  Injecting boundary candidates to drive transition...")
    print(f"{'='*65}")
    
    boundary_candidates = [f for n, f in candidates if baseline[n] >= 3]
    print(f"  Boundary candidates to inject: {len(boundary_candidates)}")
    
    # Inject boundary signals until transition or max iterations
    max_iters = 20  # up to 160 frames, should trigger transition
    for i in range(max_iters):
        for formula in boundary_candidates:
            result = entity.process(formula)
        if entity.system_level > 0:
            print(f"  Transition achieved at iteration {i+1}")
            break
    
    print(f"\n  Final state:")
    print(f"  L(E) = {entity.system_level}")
    print(f"  Stress = {entity.stress:.2f}")
    print(f"  Boundary records: {len(entity.boundary_history)}")
    print(f"  Extracted rules: {len(entity.extracted_rules)}")
    
    for r in entity.extracted_rules:
        tmpl = str(r.predicate_template)[:50] if r.predicate_template else "N/A"
        print(f"    - {r.name()}")
        print(f"      {tmpl}")
    
    # ============================================================
    # Phase 3: Post-Experience Evaluation
    # ============================================================
    print(f"\n{'='*65}")
    print("PHASE 3: Post-Experience Evaluation")
    print(f"  L(E) = {entity.system_level}")
    print(f"{'='*65}")
    print(f"  {'Name':<14} {'Before':<8} {'After':<8} Change")
    print(f"  {'-'*50}")
    
    emerged = []
    for name, formula in candidates:
        L_F, harm, reason = entity.evaluate(formula)
        old = baseline[name]
        change = ""
        if old >= 3 and L_F < 3:
            change = f"EMERGED (L{old} -> L{L_F})"
            emerged.append((name, old, L_F, str(formula)[:50]))
        elif L_F == old:
            change = "—"
        else:
            change = f"L{old} -> L{L_F}"
        print(f"  {name:<14} L{old:<8} L{L_F:<8} {change}")
    
    # ============================================================
    # Signature Analysis
    # ============================================================
    print(f"\n{'='*65}")
    print("PHASE 4: Signature Analysis")
    print(f"  Boundary clusters observed:")
    print(f"{'='*65}")
    
    from gira.phase4.pattern_tracker import compute_signature
    
    sig_counts = {}
    for record in entity.boundary_history:
        sig = record.signature
        sig_counts[sig] = sig_counts.get(sig, 0) + 1
    
    for sig, count in sorted(sig_counts.items(), key=lambda x: -x[1]):
        print(f"  {sig}: {count}")
    
    # ============================================================
    # Verdict
    # ============================================================
    print(f"\n{'='*65}")
    print("VERDICT")
    print(f"{'='*65}")
    
    if emerged:
        print(f"\n  {len(emerged)} formula(s) crossed the boundary:")
        for name, old, new, fstr in emerged:
            print(f"    {name}: L{old} -> L{new}  ({fstr})")
        
        print(f"\n  Emergence mechanism:")
        print(f"    1. System classified boundary formulas (L3)")
        print(f"    2. PatternTracker clustered by structural signature")
        print(f"    3. InductionSynthesizer proposed rules from clusters")
        print(f"    4. Rules injected -> L3 formulas became L1-")
        print(f"    5. System grew — without us specifying WHAT grows")
    else:
        print(f"\n  No emergence yet — more experience needed.")
    
    print(f"\n  Instrument output: boundary records, emergence records,")
    print(f"  signature clusters, extracted rules.")
    print(f"  All observed, not prescribed.")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
