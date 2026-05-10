"""
GEM 6.1 — Internal Harm from Pattern Repetition.

Unified harm operator:
  external harm: L(F) > L(S) → 1
  internal harm: L(F) ≤ L(S) → 1 - H(freq)/M(memory)

Concrete swap instances repeated → frequency grows → 
information density per instance drops →
internal harm accumulates → transition → 
induction rule generalizes the pattern → memory freed.
"""

import sys, io, math
sys.path.insert(0, r'G:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from gira.phase6.entity import GEME
from gira.phase4.pattern_tracker import compute_signature
from gira.phase3.language import eq, fn, constant
from gira.phase3.q_axioms import robinson_q
from collections import defaultdict


def numeral(n):
    t = constant("0")
    for _ in range(n):
        t = fn("s", t)
    return t


def concrete_eq(a, b, op):
    if op == "+":
        return eq(fn("+", numeral(a), numeral(b)),
                  fn("+", numeral(b), numeral(a)))
    elif op == "\u00d7":
        return eq(fn("\u00d7", numeral(a), numeral(b)),
                  eq(fn("\u00d7", numeral(b), numeral(a))))


class HarmTracker:
    """Tracks both external and internal harm across signals."""

    def __init__(self, decay=0.95, alpha=0.1):
        self.counts = defaultdict(int)    # signature → count
        self.memory = {}
        self.decay = decay
        self.alpha = alpha
        self.stress = 0.0
        self.total = 0
        self.harm_log = []
    
    def update(self, formula, L_F, system_level):
        """Unified harm calculation for ANY signal.
        
        Algorithm:
          1. Compute structural signature
          2. Increment signature frequency
          3. Calculate internal harm from frequency/information ratio
          4. Combine with external harm (L(F) > L(S))
        """
        sig = compute_signature(formula)
        self.counts[sig] += 1
        self.total += 1
        n = self.counts[sig]
        
        # External harm: signal exceeds system capacity
        external = 1.0 if L_F > system_level else 0.0
        
        # Internal harm: information ratio
        #   H(sig) per instance = 1/n (each repetition adds less info)
        #   M(sig) = 1 (each instance takes one slot)
        #   harm_internal = 1 - H/M = 1 - 1/n
        internal = 1.0 - (1.0 / (1.0 + n))
        
        # Unified harm: worst of both
        harm = max(external, internal)
        
        # Stress update
        self.stress = self.decay * self.stress + self.alpha * harm
        
        self.harm_log.append({
            "frame": self.total,
            "signature": sig,
            "frequency": n,
            "external_harm": external,
            "internal_harm": internal,
            "combined": harm,
            "stress": self.stress,
        })
        
        return harm, self.stress
    
    def top_patterns(self, k=5):
        """Most frequent pattern signatures."""
        return sorted(self.counts.items(), key=lambda x: -x[1])[:k]


def run():
    sep = "=" * 70
    
    tracker = HarmTracker()
    
    # Concrete swap instances
    swaps = []
    for i in range(1, 7):
        for j in range(i + 1, 7):
            swaps.append((concrete_eq(i, j, "+"),
                         f"{i}+{j}={j}+{i}"))
    
    print(sep)
    print("  GEM 6.1 — INTERNAL HARM DEMONSTRATION")
    print("  Each concrete swap = low info repeated pattern")
    print("  Internal harm grows as frequency increases")
    print(sep)
    
    print(f"\n  Training: {len(swaps)} concrete additive swaps")
    print(f"  Each is L1 (in grammar). No external harm.")
    print(f"  Internal harm drives transition.")
    print(f"\n  {'Frame':<6} {'Signature':<45} {'Freq':<6} {'Int Harm':<10} {'Stress':<8} {'Type'}")
    print(f"  {'-'*70}")
    
    for round_idx in range(6):
        for formula, label in swaps:
            L_F = 1  # ground true
            harm, stress = tracker.update(formula, L_F, 0)
            
            if tracker.total <= 5 or tracker.total % 10 == 0 or stress > 0.65:
                sig = compute_signature(formula)
                n = tracker.counts[sig]
                internal = 1.0 - (1.0 / (1.0 + n))
                t = "← TRIGGER" if stress > 0.65 else ""
                print(f"  {tracker.total:<6} {sig:<45} {n:<6} {internal:<10.3f} {stress:<8.3f} {t}")
    
    print(f"\n[1] TOP PATTERNS")
    for sig, count in tracker.top_patterns(5):
        print(f"  {sig}: {count} occurrences — "
              f"internal harm = {1.0 - (1.0/(1.0+count)):.3f}")
    
    # Simulate what happens AFTER compression
    print(f"\n[2] AFTER COMPRESSION (one induction rule replaces 15 instances)")
    compressed_harm = 1.0 - (1.0 / (1.0 + 1))  # one rule instance
    print(f"  One rule instance: harm = {compressed_harm:.3f}")
    print(f"  Before: 15 instances → harm = {1.0 - (1.0/16.0):.3f}")
    print(f"  Harm reduced: {1.0 - (1.0/16.0) - compressed_harm:.3f}")
    
    print(f"\n[3] CONCLUSION")
    print(f"  {'-'*55}")
    print(f"  Internal harm = 1 - 1/(1 + frequency(signature))")
    print(f"  Same signature, more instances → less info per instance")
    print(f"  → System accumulates stress → compression needed")
    print(f"  → Induction rule emerges → memory freed → harm drops")
    print(f"  → Abstract variable concept emerges from concrete patterns")
    print(f"{sep}")


if __name__ == "__main__":
    run()
