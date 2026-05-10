"""One GEME, growing through Godel's proof like a person reading it.
Sequential: axioms → encoding → diagonal → undecidable.
Each section builds on frames formed by the previous sections.
The same GEME. One growth trajectory."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature

g = GEME(memory_cap=16, cooccur_window=80, cooccur_thresh=0.15, max_chains=10)

print("=== ONE GEME, GROWING THROUGH GODEL ===")
print()

# ── Section 1: PM Axioms (formal system foundation) ──
print("Phase 1: Reading PM axioms...")
pm1 = eq(fn("axiom_PM1", fn("implies", fn("or", const("p"), const("p")), const("p"))), const("true"))
pm2 = eq(fn("axiom_PM2", fn("implies", const("q"), fn("or", const("p"), const("q")))), const("true"))
pm3 = eq(fn("axiom_PM3", fn("implies", fn("or", const("p"), const("q")), fn("or", const("q"), const("p")))), const("true"))
for _ in range(30):
    for f in [pm1, pm2, pm3]: g.process_sig(f, structural_signature(f))

print(f"  Frames after axioms: {len(g.memory.frames)}")
print(f"  Associations: {len([f for f in g.memory.frames if '──' in f.sig])}")

# ── Section 2: Godel numbering (mapping symbols to numbers) ──
print("\nPhase 2: Reading Godel numbering...")
enc1 = eq(fn("encode", fn("formula", const("F"))), fn("godel_num", const("n")))
enc2 = eq(fn("decode", fn("godel_num", const("n"))), fn("formula", const("F")))
enc3 = eq(fn("prime_factor", fn("num", const("n"))), fn("exponent", const("e")))
for _ in range(30):
    for f in [enc1, enc2, enc3]: g.process_sig(f, structural_signature(f))

print(f"  Frames after encoding: {len(g.memory.frames)}")
assocs = [f for f in g.memory.frames if '──' in f.sig]
chains = [f for f in g.memory.frames if '══' in f.sig]
print(f"  Associations: {len(assocs)}, Chains: {len(chains)}")

# ── Section 3: Diagonal lemma (self-reference builds on encoding) ──
print("\nPhase 3: Reading diagonal lemma...")
diag1 = eq(fn("substitute", const("F(x)"), const("x"), fn("godel_num", fn("formula", const("F(x)")))), fn("formula", const("G")))
diag2 = eq(fn("formula_G", fn("not", fn("provable", fn("godel_num", fn("formula", const("G")))))), const("self_ref"))
for _ in range(20):
    for f in [diag1, diag2]: g.process_sig(f, structural_signature(f))

print(f"  Frames after diagonal: {len(g.memory.frames)}")
assocs = [f for f in g.memory.frames if '──' in f.sig]
chains = [f for f in g.memory.frames if '══' in f.sig]
print(f"  Associations: {len(assocs)}, Chains: {len(chains)}")

# ── Section 4: Undecidability conclusion ──
print("\nPhase 4: Reading undecidability conclusion...")
und1 = eq(fn("not", fn("provable", fn("godel_num", fn("formula", const("G"))))), const("theorem1"))
und2 = eq(fn("not", fn("provable", fn("godel_num", fn("not", fn("formula", const("G")))))), const("theorem2"))
con1 = eq(fn("consistent", fn("system_P")), fn("cannot_prove", fn("consistent", fn("system_P"))))
for _ in range(20):
    for f in [und1, und2, con1]: g.process_sig(f, structural_signature(f))

print(f"\n=== FINAL STATE (after full growth) ===")
print(f"  Total frames: {len(g.memory.frames)}")
assocs = [f for f in g.memory.frames if '──' in f.sig]
chains = [f for f in g.memory.frames if '══' in f.sig]
print(f"  Associations: {len(assocs)}, Chains: {len(chains)}")

print(f"\n  Top frames by weight:")
for i, f in enumerate(sorted(g.memory.frames, key=lambda x: x.weight, reverse=True)):
    sig = f.sig_full if hasattr(f, 'sig_full') and f.sig_full else f.sig
    t = "CHAIN" if "══" in sig else ("ASSOC" if "──" in sig else "FRAME")
    print(f"  [{i}] {t} w={f.weight:5.0f} {sig[:65]}")
    if i >= 7: break

print(f"\n{'='*55}")
print("One GEME grew through Godel's proof.")
print("Frames formed at each stage carry forward to the next.")
print("The system's frame economy at the end reflects the")
print("structural architecture of the proof it processed.")
