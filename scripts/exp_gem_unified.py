"""
GEM Unified Domain Classification Test.

Demonstrates the domain-aware L-scale:
  Arithmetic domain: standard L0-L4 (Q grammar)
  Raw domain: EXTRA-DOMAIN (L(raw)-0) — not in system grammar
  Geometric domain: not registered → also EXTRA-DOMAIN

The Wittgenstein Table assigns domain.
The DomainAwareClassifier routes classification.
The human observer sees which domains have been explored.
"""

import sys, io
sys.path.insert(0, r'g:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from gira.phase6.domain_classifier import (
    DomainAwareClassifier, DomainLevel, build_default_classifier,
)
from gira.phase6.wittgenstein import WittgensteinTable
from gira.phase3.language import eq, fn, var, constant, forall
from gira.phase3.q_axioms import robinson_q


def main():
    print("=" * 65)
    print("GEM UNIFIED DOMAIN CLASSIFICATION")
    print("=" * 65)
    
    table = WittgensteinTable()
    dac = build_default_classifier()
    axioms = robinson_q()
    
    x, y, z = var("x"), var("y"), var("z")
    
    test_signals = [
        # Arithmetic domain — standard L0-L4
        ("add_comm", "∀x∀y(x+y=y+x)", "arithmetic",
         forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))),
        ("x+0=x", "x+0=x", "arithmetic",
         eq(fn("+", x, constant("0")), x)),
        ("0+0=0", "0+0=0", "arithmetic",
         eq(constant("0"), constant("0"))),
        
        # Raw domain — EXTRA-DOMAIN: system has no grammar for letters
        ("letter_a", "a", "raw",
         eq(constant("97"), constant("0"))),
        ("letter_b", "b", "raw",
         eq(constant("98"), constant("0"))),
        ("letter_c", "c", "raw",
         eq(constant("99"), constant("0"))),
        
        # Geometric domain — not registered yet
        ("geo_parallel", "∀P∃L(parallel(L,P))", "geometric",
         eq(constant("0"), constant("0"))),
    ]
    
    print(f"\n  {'Domain':<12} {'Status':>8}  Signal               Classification")
    print(f"  {'-'*65}")
    
    for name, raw, domain, formula in test_signals:
        t = table.translate(raw)
        result = dac.classify(formula, domain, axioms, [])
        
        if result.level == 0:
            status = "EXTRA"  # domain not in grammar
        elif result.level <= 2:
            status = "OK"
        elif result.level == 3:
            status = "BOUNDARY"
        else:
            status = "GODEL"
        
        print(f"  {domain:<12} [{status:>8}]  {name:<18} {result}")
    
    # Domain summary
    print(f"\n  {'DOMAIN SUMMARY':^65}")
    domains = dac.domains()
    print(f"  Registered domains: {domains}")
    print(f"  Extra-domain signals: raw, geometric")
    print(f"\n  To process raw signals: dac.add_domain('raw', ...)")
    print(f"  To process geometric: dac.add_domain('geometric', ...)")
    
    print(f"\n{'='*65}")
    print("  Unified L-scale: domain → [status check] → L(D)-level")
    print("  EXTRA-DOMAIN = growth opportunity, not error")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
