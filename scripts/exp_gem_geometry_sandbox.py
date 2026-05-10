"""
GEM 6.2 — Geometry Sandbox (Absolute Geometry -> Euclidean Geometry)

World: Tarski's absolute geometry axioms (Euclid I-IV, no parallel postulate).
System: GEME observes geometric formulas.
Boundary: The parallel postulate is undecidable in absolute geometry.
Emergence: After adopting the parallel postulate, new Euclidean theorems
           become derivable. We do NOT know which theorem emerges first.

This is the first genuinely open-ended GEM experiment:
  We provide the axioms, but NOT which theorems should emerge.
  The system explores the formula space and discovers its own path.
"""

import sys, io, random
sys.path.insert(0, r'g:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
from gira.phase6.entity import GEME
from gira.phase3.language import eq, fn, var, constant, forall, exists, neg, impl


# ============================================================
# Absolute Geometry Axioms (Tarski's Axioms 1-9, no parallel)
# ============================================================
# Simplified encoding: using points as variables x,y,z
# and a few geometric predicates
#
# B(x,y,z) = "y is between x and z"
# xy ≅ uv  = "segment xy is congruent to uv"  (encoded as eq(dist(x,y), dist(u,v)))
#
# For the sandbox, we use an algebraic encoding:
#   "dist(x,y)" as a distance function between two points

x, y, z, u, v, w = (var(c) for c in "xyxuvw")

def dist(a, b):
    """Distance between two points (pseudo-metric)."""
    return fn("d", a, b)

# Axiom 1: Reflexivity of congruence: xy ≅ yx
ax1 = eq(dist(x, y), dist(y, x))

# Axiom 2: Transitivity of congruence: xy ≅ zu ∧ xy ≅ vw → zu ≅ vw
ax2 = impl(eq(dist(x, y), dist(z, u)), eq(dist(x, y), dist(v, w)))

# Axiom 3: Identity of congruence: xy ≅ zz → x = y
ax3 = impl(eq(dist(x, y), dist(z, z)), eq(x, y))

# Axiom 4: Segment construction: ∃z [B(x,y,z) ∧ yz ≅ ab]
ax4 = exists("z", eq(dist(y, var("z")), dist(u, v)))

# Axiom 5: Five-segment axiom
ax5 = eq(dist(x, y), dist(x, y))  # simplified

# Axiom 6: Identity of betweenness: B(x,y,x) → x=y
ax6 = impl(eq(x, y), eq(x, x))  # placeholder

# Axiom 7: Pasch's axiom (inner form)
ax7 = exists("z", eq(dist(x, var("z")), dist(x, var("z"))))

# Axiom 8: Lower dimension: ∃xyz ¬(B(x,y,z) ∨ B(y,z,x) ∨ B(z,x,y))
ax8 = exists("x", forall("y", eq(x, y)))

# Axiom 9: Upper dimension (2D): ¬∃xyzuv ...
ax9 = forall("x", forall("y", eq(x, y)))

GEOMETRY_AXIOMS = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9]


# ============================================================
# Simplification: Algebraic Geometry
# ============================================================
# The above is too complex for our formula DSL. Let's use a
# simpler encoding:
#
# We encode absolute geometry properties as algebraic formulas.
# Points = pairs (px, py) in a field.
# We treat operations like: midpoint, parallel test, collinearity.

def build_algebraic_geometry_axioms():
    """Simplified algebraic geometry axioms.
    
    Core predicates encoded as arithmetic equalities:
    - "PQ is parallel to RS" = some algebraic condition
    - "P is midpoint of QR" = coordinates equal
    """
    a, b, c, d, e, f = var("a"), var("b"), var("c"), var("d"), var("e"), var("f")
    
    return [
        # Existence of points
        eq(a, a),
        eq(b, b),
        # Segment axioms (algebraic)
        eq(fn("+", a, b), fn("+", b, a)),  # commutativity of addition
        eq(fn("+", a, fn("+", b, c)), fn("+", fn("+", a, b), c)),  # associativity
        # Multiplication -> field structure (Tarski's requirement)
        eq(fn("\u00d7", a, b), fn("\u00d7", b, a)),
        eq(fn("\u00d7", a, fn("\u00d7", b, c)), fn("\u00d7", fn("\u00d7", a, b), c)),
        # Distributivity
        eq(fn("\u00d7", a, fn("+", b, c)),
           fn("+", fn("\u00d7", a, b), fn("\u00d7", a, c))),
    ]


# ============================================================
# Geometric Formula Space
# ============================================================

class GeometryFormulaSpace:
    """Generates geometric candidate formulas.
    
    These are properties that are:
    - Undecidable in absolute geometry (may need parallel postulate)
    - Decidable after adopting parallel postulate
    - Some are non-geometric (trivial in arithmetic) — controls
    """
    
    def __init__(self):
        a, b, c, d = var("a"), var("b"), var("c"), var("d")
        self.a, self.b, self.c, self.d = a, b, c, d
    
    def all_candidates(self) -> list:
        """Return all candidate formulas for exploration."""
        a, b, c, d = self.a, self.b, self.c, self.d
        
        return [
            # Elementary (should be L1)
            ("refl_add", eq(fn("+", a, constant("0")), a)),
            ("refl_mul", eq(fn("\u00d7", a, constant("1")), a)),
            
            # Commutativity (boundary candidates)
            ("add_comm", forall("a", forall("b", eq(fn("+", a, b), fn("+", b, a))))),
            ("mul_comm", forall("a", forall("b", eq(fn("\u00d7", a, b), fn("\u00d7", b, a))))),
            
            # Associativity
            ("add_assoc", forall("a", forall("b", forall("c",
                eq(fn("+", a, fn("+", b, c)), fn("+", fn("+", a, b), c)))))),
            ("mul_assoc", forall("a", forall("b", forall("c",
                eq(fn("\u00d7", a, fn("\u00d7", b, c)), fn("\u00d7", fn("\u00d7", a, b), c)))))),
            
            # Distributivity  
            ("distrib", forall("a", forall("b", forall("c",
                eq(fn("\u00d7", a, fn("+", b, c)),
                   fn("+", fn("\u00d7", a, b), fn("\u00d7", a, c))))))),
            
            # Geometric identity (Euclidean specific)
            ("geo_id", forall("a", forall("b",
                eq(fn("\u00d7", fn("+", a, b), fn("+", a, b)),
                   fn("+", fn("+", fn("\u00d7", a, a),
                                 fn("\u00d7", constant("2"), fn("\u00d7", a, b))),
                       fn("\u00d7", b, b)))))),
            
            # Control: non-geometric
            ("const_eq", eq(constant("0"), constant("0"))),
        ]


def main():
    print("=" * 65)
    print("GEM 6.2: Geometry Sandbox — Absolute -> Euclidean")
    print("=" * 65)
    
    print("\n  World: Algebraic field axioms (absolute geometry basis)")
    print("  Boundary: formulas undecidable in absolute geometry")
    print("  Emergence: discover which theorems become provable")
    
    # Build
    axioms = build_algebraic_geometry_axioms()
    space = GeometryFormulaSpace()
    entity = GEME(axioms=axioms)
    candidates = space.all_candidates()
    
    # Phase 1: Classification
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
    
    # Phase 2: Experience
    print(f"\n{'='*65}")
    print("PHASE 2: Experience Accumulation")
    print(f"{'='*65}")
    
    boundary_candidates = [f for n, f in candidates if baseline[n] >= 3]
    print(f"  Boundary candidates: {len(boundary_candidates)}")
    
    for i in range(20):
        for formula in boundary_candidates:
            entity.process(formula)
        if entity.system_level > 0:
            print(f"  Transition at iteration {i+1}")
            break
    
    print(f"\n  L(E) = {entity.system_level}")
    print(f"  Rules extracted: {len(entity.extracted_rules)}")
    
    # Phase 3: Post-experience
    print(f"\n{'='*65}")
    print("PHASE 3: Post-Experience Evaluation")
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
            emerged.append((name, old, L_F, str(formula)[:60]))
        print(f"  {name:<14} L{old:<8} L{L_F:<8} {change}")
    
    # Verdict
    print(f"\n{'='*65}")
    print("VERDICT")
    print(f"{'='*65}")
    if emerged:
        print(f"\n  {len(emerged)} formula(s) crossed the boundary in algebraic geometry:")
        for name, old, new, fstr in emerged:
            print(f"    {name}: L{old} -> L{new}  ({fstr})")
    else:
        print(f"\n  No emergence — absolute geometry has no induction boundary yet.")
    
    print(f"\n  Note: This algebraic encoding is simplified.")
    print(f"  Full Tarski geometry requires non-trivial syntactic extension.")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
