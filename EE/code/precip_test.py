"""Precipitation quick test."""
import sys; sys.path.insert(0, '.')
from geruon import Geruon, Phase, Codex
from geme import eq, fn, const, structural_signature
import random as _rnd

# Define symbols explicitly — no dependency on GEME's internal _ALPHABET
SYMBOLS = ['0','1','s','+','x','y','z','swap','pair','comm','succ']
codex = Codex.from_alphabet(SYMBOLS, vec_dim=16, seed=42)
r = _rnd.Random(42)
g = Geruon(vec_dim=16, memory_cap=24, cooccur_window=80, codex=codex)
g.memory.quantum_mode = True
g.memory._qrand = _rnd.Random(99)

symbols = ['0','1','s','+','x','y','z','swap','pair','comm','succ']
for step in range(1500):
    a = r.choice(symbols)
    b = r.choice(symbols)
    c = r.choice(symbols)
    if step % 3 == 0:
        f = eq(fn(a, const(b)), const(c))
    elif step % 3 == 1:
        f = eq(fn('swap', const(a), const(b)), fn('swap', const(b), const(a)))
    else:
        f = eq(fn(a, fn(b, const(c))), fn(b, fn(a, const(c))))
    g.process_sig(f, structural_signature(f))

m = g.metrics()
print(f"Frames: {m['frame_count']}  pred={m['pred_total']}  acc={m['pred_accuracy']:.3f}")
print(f"tau={g.tau:.4f}  phase={g.phase.value}  doubt={m['doubt_mode']}")
print(f"Precipitated: {m['precipitated']}  candidates: {m['precipitate_candidates']}")

# Enrich codex from precipitated frames
n = g.enrich()
print(f"Codex entries after enrich: {len(codex)} (added {n})")

dep_frames = [f for f in g.memory.frames if f.precipitated]
if dep_frames:
    print("Deposited frames:")
    for f in dep_frames:
        print(f"  {f.sig[:30]} layer={f.layer} w={f.weight:.1f} sc={f.survival_cycles} act={f.activations}")
else:
    print("No precipitated frames yet.")
    cands = sorted(g.memory.frames,
                   key=lambda f: (f.survival_cycles + f.activations), reverse=True)[:8]
    print("Top candidates:")
    for f in cands:
        stable = g.memory.is_meta_stable(f.fid)
        print(f"  {f.sig[:30]} layer={f.layer} w={f.weight:.1f} sc={f.survival_cycles} act={f.activations} stable={stable}")

# Show codex deposit entries
dep_entries = [(s, v) for s, v in codex._table.items() if s.startswith('deposit')]
if dep_entries:
    print(f"\nCodex deposit entries ({len(dep_entries)}):")
    for s, v in dep_entries[:5]:
        print(f"  {s}: vec[:3]={[round(x,3) for x in v[:3]]}")
print(f"Codex generation: {codex._generation}")
