"""
GEM 6.1 — PA Sandbox with full observation pipeline.

Demonstrates the complete GEM design philosophy:
  Human feeds formulas → GEM classifies → Human observes emergence.

The human sees:
  1. What was fed (Input Space)
  2. What was at the boundary (Boundary Map)
  3. What crossed the boundary (Emergence Log)  
  4. What rules were synthesized (Rule Catalog)
  5. Structural signatures (Signature Atlas)

All of this is presented to the human — GEM doesn't make decisions.
The human recognizes the patterns.
"""

import sys, io
sys.path.insert(0, r'g:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
from gira.phase6.entity import GEME
from gira.phase6.reporter import GEMReporter
from gira.phase3.language import eq, fn, var, constant, forall
from gira.phase3.q_axioms import robinson_q
from gira.phase4.pattern_tracker import compute_signature


x, y, z = var("x"), var("y"), var("z")

FORMULAS = [
    # In-grammar (L1-L2)
    ("0+0=0",   eq(constant("0"), constant("0"))),
    ("x+0=x",   eq(fn("+", x, constant("0")), x)),
    ("x*0=0",   eq(fn("\u00d7", x, constant("0")), constant("0"))),
    
    # Boundary (L3 — undecidable in Q)
    ("add_comm",  forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))),
    ("mul_comm",  forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x))))),
    ("add_assoc", forall("x", forall("y", forall("z",
        eq(fn("+", x, fn("+", y, z)), fn("+", fn("+", x, y), z)))))),
    ("mul_assoc", forall("x", forall("y", forall("z",
        eq(fn("\u00d7", x, fn("\u00d7", y, z)), fn("\u00d7", fn("\u00d7", x, y), z)))))),
    ("distrib",   forall("x", forall("y", forall("z",
        eq(fn("\u00d7", x, fn("+", y, z)), fn("+", fn("\u00d7", x, y), fn("\u00d7", x, z))))))),
    ("x*1=x",     forall("x", eq(fn("\u00d7", x, fn("s", constant("0"))), x))),
    
    # Derived (potentially new emergence)
    ("sq_add",  forall("x", forall("y",
        eq(fn("\u00d7", fn("+", x, y), fn("+", x, y)),
           fn("+", fn("+", fn("\u00d7", x, x),
                      fn("\u00d7", constant("2"), fn("\u00d7", x, y))),
              fn("\u00d7", y, y)))))),
    ("dbl_mul", forall("x", forall("y",
        eq(fn("+", fn("\u00d7", x, y), fn("\u00d7", x, y)),
           fn("\u00d7", x, fn("+", y, y)))))),
]


def main():
    # Build
    entity = GEME(axioms=robinson_q())
    reporter = GEMReporter("GEM PA Sandbox — Observation Report")
    candidate_list = FORMULAS
    
    # ── Phase 1: Classification (the human sees the input space) ──
    baseline = {}
    for name, formula in candidate_list:
        L_F, _, _ = entity.evaluate(formula)
        baseline[name] = L_F
        reporter.record_input(name, formula, L_F)
    
    # ── Phase 2: Experience (GEM processes, human watches) ──
    boundary = [(n, f) for n, f in candidate_list if baseline[n] >= 3]
    
    for i in range(20):
        for _, formula in boundary:
            result = entity.process(formula)
        if entity.system_level > 0:
            reporter.record_transition(entity.entity.frame_count, entity.system_level)
            break
    
    # ── Phase 3: Emergence detection ──
    for name, formula in candidate_list:
        L_F, _, _ = entity.evaluate(formula)
        old = baseline[name]
        if old >= 3 and L_F < 3:
            reporter.record_emergence(name, old, L_F, formula)
    
    # ── Phase 4: Signature analysis ──
    sig_counts = {}
    for rec in entity.boundary_history:
        sig = rec.signature
        sig_counts[sig] = sig_counts.get(sig, 0) + 1
    for sig, count in sig_counts.items():
        reporter.record_boundary(sig, count)
    
    # ── Phase 5: Rule catalog ──
    for rule in entity.extracted_rules:
        tmpl = str(rule.predicate_template)[:80] if rule.predicate_template else "N/A"
        reporter.record_rule(rule.name(), tmpl)
    
    # ── Render ──
    print(reporter.render())


if __name__ == "__main__":
    main()
