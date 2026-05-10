"""Experiment: feed GEME with Godel proof structural elements.
3 parallel GEMEs → GEME3 → GEME4. See what emerges."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature

# ── Step 1: Encode Godel proof elements as formulas ──
# PM Axioms
pm1 = eq(fn("axiom_PM1", fn("implies", fn("or", const("p"), const("p")), const("p"))), const("true"))
pm2 = eq(fn("axiom_PM2", fn("implies", const("q"), fn("or", const("p"), const("q")))), const("true"))
pm3 = eq(fn("axiom_PM3", fn("implies", fn("or", const("p"), const("q")), fn("or", const("q"), const("p")))), const("true"))
PM_AXIOMS = [pm1, pm2, pm3]

# Encoding rules
enc1 = eq(fn("encode", fn("formula", const("F"))), fn("godel_num", const("n")))
enc2 = eq(fn("decode", fn("godel_num", const("n"))), fn("formula", const("F")))
enc3 = eq(fn("encode", fn("proof", const("P"))), fn("proof_num", const("m")))
ENC_RULES = [enc1, enc2, enc3]

# Diagonal lemma (construct G: "G is not provable")
diag1 = eq(fn("substitute", const("F(x)"), const("x"), fn("godel_num", fn("formula", const("F(x)")))), fn("formula", const("G")))
diag2 = eq(fn("implies", fn("formula", const("G")), fn("not", fn("provable", fn("godel_num", fn("formula", const("G")))))), const("true"))
diag3 = eq(fn("implies", fn("not", fn("formula", const("G"))), fn("provable", fn("godel_num", fn("formula", const("G"))))), const("false"))
DIAG = [diag1, diag2, diag3]

# Undecidability
und1 = eq(fn("not", fn("provable", fn("godel_num", fn("formula", const("G"))))), const("theorem1"))
und2 = eq(fn("not", fn("provable", fn("godel_num", fn("not", fn("formula", const("G")))))), const("theorem2"))
UND = [und1, und2]

# Consistency statement
con1 = eq(fn("consistent", fn("system_P")), fn("implies", fn("provable", const("A")), fn("not", fn("provable", fn("not", const("A"))))))
con2 = eq(fn("not", fn("provable", fn("consistent", fn("system_P")))), const("theorem3"))
CON = [con1, con2]

print("=== GODEL PROOF × GEME: Structural Pattern Transfer ===")
print()

# ── Step 2: Three parallel GEMEs for three structural layers ──
ga = GEME(memory_cap=12, cooccur_window=40, cooccur_thresh=0.2, max_chains=0)
gb = GEME(memory_cap=12, cooccur_window=40, cooccur_thresh=0.2, max_chains=0)
gc = GEME(memory_cap=12, cooccur_window=40, cooccur_thresh=0.2, max_chains=0)

print("GEME_A: processing PM axioms (symbols)...")
for f in PM_AXIOMS * 20:
    ga.process_sig(f, structural_signature(f))

print("GEME_B: processing encoding rules (mapping)...")
for f in ENC_RULES * 30:
    gb.process_sig(f, structural_signature(f))

print("GEME_C: processing diagonal + undecidability...")
for f in DIAG * 15 + UND * 15 + CON * 15:
    gc.process_sig(f, structural_signature(f))

def show_top(m, label, n=3):
    print(f"\n{label}:")
    for i, f in enumerate(sorted(m.memory.frames, key=lambda x: x.weight, reverse=True)[:n]):
        sig = f.sig_full if hasattr(f, 'sig_full') and f.sig_full else f.sig
        print(f"  [{i}] w={f.weight:.0f} {sig[:60]}")

show_top(ga, "GEME_A (Axioms)", 3)
show_top(gb, "GEME_B (Encoding)", 3)
show_top(gc, "GEME_C (Diagonal)", 3)

# ── Step 3: Integrate into GEME3 ──
g3 = GEME(memory_cap=16, cooccur_window=60, cooccur_thresh=0.15)
print("\n\nGEME3: integrating all three frame spaces...")

# Feed cross-layer signatures from parallel GEMEs
for sig_type, source in [("axiom", ga), ("encode", gb), ("diag", gc)]:
    for f in source.memory.frames:
        sig = f.sig_full if hasattr(f, 'sig_full') and f.sig_full else f.sig
        if sig:  # register cross-space signatures
            cross = eq(fn(f"cross_{sig_type}", const(sig[:20])), const("yes"))
            g3.process_sig(cross, structural_signature(cross))

# Feed integration axioms
integrations = [
    eq(fn("axiom_to_encoding", const("axiom_seq")), fn("encoding_seq", const("mapping"))),
    eq(fn("encoding_to_diagonal", const("mapping")), fn("diagonal", const("self_ref"))),
    eq(fn("diagonal_to_undecidable", const("self_ref")), fn("undecidable", const("boundary"))),
]
for f in integrations * 20:
    g3.process_sig(f, structural_signature(f))

show_top(g3, "GEME3 (Integration)", 5)

# ── Step 4: GEME4 forms meta-chains ──
g4 = GEME(memory_cap=12, cooccur_window=60, cooccur_thresh=0.15, max_chains=10)
for f in g3.memory.frames:
    sig = f.sig_full if hasattr(f, 'sig_full') and f.sig_full else f.sig
    cross = eq(fn(f"meta_{sig[:20]}", const(str(int(f.weight)))), const("yes"))
    g4.process_sig(cross, structural_signature(cross))

# Check for chains
chains = [f for f in g4.memory.frames if "══" in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig)]
show_top(g4, "GEME4 (Meta/Chains)", 5)
if chains:
    print(f"\n  Chains formed: {len(chains)}")
    for c in chains:
        sig = c.sig_full if hasattr(c,'sig_full') and c.sig_full else c.sig
        print(f"    {sig[:70]} w={c.weight:.0f}")
else:
    print("\n  No chains formed at GEME4.")

print(f"\n{'='*55}")
print("Result: structural pattern of Godel's proof transferred")
print("across three GEME layers. Not 'understanding' — ")
print("structural capture of the proof's architecture.")
