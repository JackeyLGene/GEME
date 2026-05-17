"""
L0 → L1 arrow test: centroid as cross-layer signal.

L0 receives diverse formula input. L1 receives L0's arrow_output
(fused content-time centroid). Measure whether L1 maintains dynamic
phase behavior vs locking immediately.
"""
import sys, os, math, statistics, random as _rnd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase
from geme import eq, fn, const, structural_signature, symbol_vector

VEC_DIM = 27
STEPS = 4000

# L0 and L1 — same architecture, L1 receives L0's arrow
g0 = Geruon(vec_dim=VEC_DIM, memory_cap=24, cooccur_window=100)
g0.memory.quantum_mode = True; g0.memory._qrand = _rnd.Random(100)
g1 = Geruon(vec_dim=VEC_DIM, memory_cap=24, cooccur_window=100)
g1.memory.quantum_mode = True; g1.memory._qrand = _rnd.Random(200)

# Input stream for L0
r = _rnd.Random(42)
symbols = ['0','1','s','+','x','y','z','swap','pair','comm','succ','forall','exists']

print(f"L0→L1 Arrow Test  Steps={STEPS}")
print(f"L0: formula input → arrow_output → L1")
print("=" * 55)

tau0 = []; tau1 = []
ph0 = []; ph1 = []
trans0 = []; trans1 = []

for step in range(STEPS):
    a,b,c,d = r.choice(symbols),r.choice(symbols),r.choice(symbols),r.choice(symbols)
    p = step % 5
    if p == 0: f = eq(fn(a, const(b)), const(c))
    elif p == 1: f = eq(fn('swap', const(a), const(b)), fn('swap', const(b), const(a)))
    elif p == 2: f = eq(fn(a, fn(b, const(c))), fn(b, fn(a, const(c))))
    elif p == 3: f = eq(fn('pair', const(a), const(b)), fn('comm', const(b), const(a)))
    else: f = eq(fn(a, const(b)), fn(a, fn('succ', const(b))))

    # L0: external input
    g0.process_vec(list(symbol_vector(f)), structural_signature(f))
    tau0.append(g0.tau); ph0.append(g0.phase.value)

    # L1: receives L0's arrow (fused content-time centroid)
    arrow = g0.arrow_output()
    g1.process_vec(list(arrow), f'L0_arrow')
    tau1.append(g1.tau); ph1.append(g1.phase.value)

# Phase transitions
for traj, trans in [(ph0, trans0), (ph1, trans1)]:
    for i in range(1, len(traj)):
        if traj[i] != traj[i-1]:
            trans.append(i)

# Report
for label, g, traj, trans, taus in [
    ("L0", g0, ph0, trans0, tau0),
    ("L1", g1, ph1, trans1, tau1)]:
    ph_c = {}; [ph_c.update({p: ph_c.get(p,0)+1}) for p in traj]
    print(f"\n{label}: tau={g.tau:.4f} {g.phase.value} "
          f"trans={len(trans)} phases={dict(sorted(ph_c.items()))}")

    # τ stats
    late_tau = statistics.mean(taus[-500:])
    early_tau = statistics.mean(taus[:500])
    print(f"  τ: early={early_tau:.3f} late={late_tau:.3f} Δ={late_tau-early_tau:+.3f}")
    print(f"  τ range: [{min(taus):.3f}, {max(taus):.3f}]")

# Verdict
l1_phases = len(set(ph1))
l1_trans = len(trans1)
if l1_trans >= 5 and l1_phases >= 2:
    print(f"\n✓ L1 maintains dynamic phase behavior ({l1_trans} transitions, {l1_phases} phases)")
elif l1_trans >= 2:
    print(f"\n△ L1 shows some dynamics but limited ({l1_trans} transitions)")
else:
    print(f"\n✗ L1 locked — arrow_output insufficient for cross-layer drive")
