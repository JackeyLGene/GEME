"""
GEM Full Observation Report — with Wittgenstein Table.

The complete GEM pipeline visible to the human observer:
  1. Wittgenstein Table — how external signals are translated
  2. Input Space — what entered the system
  3. Boundary Map — structural signatures at the boundary
  4. Emergence Log — what crossed the boundary
  5. Rule Catalog — what the system synthesized
"""

import sys, io
sys.path.insert(0, r'g:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from gira.phase6.entity import GEME
from gira.phase6.reporter import GEMReporter
from gira.phase6.wittgenstein import WittgensteinTable
from gira.phase3.language import eq, fn, var, constant, forall
from gira.phase3.q_axioms import robinson_q


x, y, z = var("x"), var("y"), var("z")

# Both arithmetic and non-arithmetic signals
SIGNALS = [
    # Arithmetic domain
    ("add_comm", "∀x∀y(x+y=y+x)"),
    ("mul_comm", "∀x∀y(x×y=y×x)"),
    ("add_assoc", "∀x∀y∀z(x+(y+z)=(x+y)+z)"),
    ("distrib", "∀x∀y∀z(x×(y+z)=(x×y)+(x×z))"),
    ("x+0=x", "x+0=x"),
    ("0+0=0", "0+0=0"),
    
    # Raw domain (non-arithmetic)
    ("letter_a", "a"),
    ("letter_z", "z"),
    ("letter_a2", "a"),
    ("letter_b", "b"),
    ("letter_a3", "a"),
    ("letter_c", "c"),
    ("digit_1", "1"),
    ("symbol_x", "x"),
    ("letter_b2", "b"),
]


def main():
    table = WittgensteinTable()
    entity = GEME(axioms=robinson_q())
    reporter = GEMReporter("GEM Observation — Wittgenstein Table + Emergence")
    
    # ── Phase 1: Translate all signals through the Wittgenstein Table ──
    translations = []
    for name, raw in SIGNALS:
        t = table.translate(raw)
        translations.append((name, t))
    
    # ── Phase 2: Classification ──
    formulas_map = {}
    for name, raw in SIGNALS:
        if "=" in raw and any(s in raw for s in ["+","×","∀"]):
            # Build Formula for arithmetic
            if name == "add_comm":
                f = forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))
            elif name == "mul_comm":
                f = forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x))))
            elif name == "add_assoc":
                f = forall("x", forall("y", forall("z", eq(fn("+", x, fn("+", y, z)), fn("+", fn("+", x, y), z)))))
            elif name == "distrib":
                f = forall("x", forall("y", forall("z", eq(fn("\u00d7", x, fn("+", y, z)), fn("+", fn("\u00d7", x, y), fn("\u00d7", x, z))))))
            elif name == "x+0=x":
                f = eq(fn("+", x, constant("0")), x)
            elif name == "0+0=0":
                f = eq(constant("0"), constant("0"))
            else:
                f = eq(constant("0"), constant("0"))
        else:
            # Raw signals — encode as constants
            code = ord(raw[0]) if raw else 0
            f = eq(constant(str(code)), constant("0"))
        
        formulas_map[name] = f
        L_F, _, _ = entity.evaluate(f)
        reporter.record_input(name, f, L_F)
    
    # ── Phase 3: Experience accumulation ──
    boundary_names = [n for n, f in formulas_map.items() 
                      if entity.evaluate(f)[0] >= 3]
    
    for i in range(20):
        for name in boundary_names:
            entity.process(formulas_map[name])
        if entity.system_level > 0:
            reporter.record_transition(entity.entity.frame_count, entity.system_level)
            break
    
    # ── Phase 4: Emergence detection ──
    baseline = {}
    for name, f in formulas_map.items():
        L_F, _, _ = entity.evaluate(f)
        baseline[name] = L_F
    
    for name, f in formulas_map.items():
        L_F, _, _ = entity.evaluate(f)
        old = baseline[name]
        if old >= 3 and L_F < 3:
            reporter.record_emergence(name, old, L_F, f)
    
    # ── Phase 5: Signature recording ──
    sig_counts = {}
    for rec in entity.boundary_history:
        sig = rec.signature
        sig_counts[sig] = sig_counts.get(sig, 0) + 1
    for sig, count in sig_counts.items():
        reporter.record_boundary(sig, count)
    
    # ── Phase 6: Rule catalog ──
    for rule in entity.extracted_rules:
        tmpl = str(rule.predicate_template)[:80] if rule.predicate_template else "N/A"
        reporter.record_rule(rule.name(), tmpl)
    
    # ── Render ──
    print("=" * 65)
    print("GEM FULL OBSERVATION REPORT".center(65))
    print("=" * 65)
    
    # Wittgenstein Table
    print(f"\n{' WITTGENSTEIN TABLE':^65}")
    print(f"  {'Domain':<12} {'Count':<8} External -> Internal Signature")
    print(f"  {'-'*55}")
    
    domain_counts = table.domain_frequencies()
    for domain in table.domains():
        entries = [t for _, t in translations if t.domain == domain]
        print(f"  {domain:<12} {domain_counts.get(domain,0):<8}")
        shown_sigs = set()
        for t in entries:
            if t.signature not in shown_sigs:
                print(f"    {t.external[:25]:<25} -> {t.signature}")
                shown_sigs.add(t.signature)
    
    print(f"\n  The Wittgenstein Table defines how external signals")
    print(f"  become structurally representable in GEM's grammar.")
    print(f"  Signatures are generated by the TABLE, not by humans.")
    
    # The rest of the report
    print(f"\n{reporter.render()}")


if __name__ == "__main__":
    main()
