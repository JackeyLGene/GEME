"""
Single Geruon phase transition period-doubling measurement.

The 5K-step run found: T_early=93.7 → T_mid=179.2 → T_late=493.8,
with GI sequence 1.91 → 2.76 trending toward delta=4.669.

This script reproduces with better statistics: multiple seeds, pre-lock focus.
"""
import sys, os, math, statistics, random as _rnd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase
from geme import eq, fn, const, structural_signature, symbol_vector

VEC_DIM = 27
STEPS = 5000
SEEDS = 10

def run_one(seed, cap=24):
    r = _rnd.Random(seed)
    symbols = ['0','1','s','+','x','y','z','swap','pair','comm','succ']
    g = Geruon(vec_dim=VEC_DIM, memory_cap=cap, cooccur_window=100)
    g.memory.quantum_mode = True
    g.memory._qrand = _rnd.Random(seed + 1000)

    phase_traj = []
    for step in range(STEPS):
        a,b,c = r.choice(symbols),r.choice(symbols),r.choice(symbols)
        p = step % 3
        if p == 0: f = eq(fn(a, const(b)), const(c))
        elif p == 1: f = eq(fn('swap', const(a), const(b)), fn('swap', const(b), const(a)))
        else: f = eq(fn(a, fn(b, const(c))), fn(b, fn(a, const(c))))
        g.process_vec(list(symbol_vector(f)), structural_signature(f))
        phase_traj.append(g.phase.value)

    # Find phase transitions
    transitions = []
    for i in range(1, len(phase_traj)):
        if phase_traj[i] != phase_traj[i-1]:
            transitions.append((i, phase_traj[i-1], phase_traj[i]))

    return g.tau, phase_traj, transitions


print(f"GI Period-Doubling  Steps={STEPS}  Seeds={SEEDS}")
print("=" * 55)

all_gis = []
for seed in range(SEEDS):
    tau, pt, trans = run_one(seed)
    n = len(trans)
    if n < 6:
        print(f"  seed{seed}: {n} trans — insufficient")
        continue

    t_steps = [t[0] for t in trans]
    intervals = [t_steps[i+1]-t_steps[i] for i in range(len(t_steps)-1)]
    m = len(intervals)

    # Split into thirds
    T0 = statistics.mean(intervals[:m//3]) if m//3>0 else 0
    T1 = statistics.mean(intervals[m//3:2*m//3]) if m//3>0 else 0
    T2 = statistics.mean(intervals[2*m//3:]) if m//3>0 else 0

    gi1 = T1/T0 if T0>0 else 0
    gi2 = T2/T1 if T1>0 else 0

    ph_c = {}
    for ph in pt: ph_c[ph] = ph_c.get(ph,0)+1
    dom = max(ph_c, key=ph_c.get)

    print(f"  s{seed}: {n} trans tau={tau:.3f} {dom} "
          f"T=[{T0:.0f},{T1:.0f},{T2:.0f}] GI=[{gi1:.2f},{gi2:.2f}]")
    all_gis.append((gi1, gi2))

if all_gis:
    gi1s = [g[0] for g in all_gis if g[0] > 0]
    gi2s = [g[1] for g in all_gis if g[1] > 0]
    delta = 4.669
    if gi1s:
        print(f"\nGI_1: mean={statistics.mean(gi1s):.3f} range=[{min(gi1s):.3f},{max(gi1s):.3f}] "
              f"err={(statistics.mean(gi1s)-delta)/delta*100:+.1f}%")
    if gi2s:
        print(f"GI_2: mean={statistics.mean(gi2s):.3f} range=[{min(gi2s):.3f},{max(gi2s):.3f}] "
              f"err={(statistics.mean(gi2s)-delta)/delta*100:+.1f}%")
