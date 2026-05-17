"""
GI measurement — diverse formula input with structural markers.

Uses the formula patterns that reliably produce phase dynamics (validated
in gi_diag.py), structured into "passes" that mimic musical repetition
with variation. Each pass is a cycle through the same formula types
but with different symbol instantiations.

The period-doubling measurement: T_early (learning), T_mid (transient),
T_late (consolidation). GI_n = T_{n+1}/T_n should approach delta=4.669.
"""
import sys, os, math, statistics, random as _rnd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase
from geme import eq, fn, const, structural_signature, symbol_vector

VEC_DIM = 27
STEPS = 15000

# Generate diverse formula stream
r = _rnd.Random(42)
symbols = ['0','1','s','+','x','y','z','swap','pair','comm','succ','forall','exists']
stream_sigs = []  # for tracking
stream_vecs = []

for step in range(STEPS):
    a, b, c, d = r.choice(symbols), r.choice(symbols), r.choice(symbols), r.choice(symbols)
    p = step % 5
    if p == 0:
        f = eq(fn(a, const(b)), const(c))
    elif p == 1:
        f = eq(fn('swap', const(a), const(b)),
               fn('swap', const(b), const(a)))
    elif p == 2:
        f = eq(fn(a, fn(b, const(c))), fn(b, fn(a, const(c))))
    elif p == 3:
        f = eq(fn('pair', const(a), const(b)),
               fn('comm', const(b), const(a)))
    else:
        f = eq(fn(a, const(b)),
               fn(a, fn('succ', const(b))))
    stream_vecs.append(list(symbol_vector(f)))
    stream_sigs.append(structural_signature(f))

print(f"GI Period-Doubling Measurement")
print(f"Steps: {STEPS}  Symbols: {len(symbols)}  Pattern types: 5")
print("=" * 55)

g = Geruon(vec_dim=VEC_DIM, memory_cap=32, cooccur_window=120)
g.memory.quantum_mode = True
g.memory._qrand = _rnd.Random(99)

phase_traj = []
tau_traj = []
induction_steps = []  # steps at which induction (consolidation) fired
induction_intervals = []  # steps between successive inductions

last_induction = 0
for step in range(STEPS):
    g.process_vec(stream_vecs[step], stream_sigs[step])
    phase_traj.append(g.phase.value)
    tau_traj.append(g.tau)
    # Detect induction via _last_induction change
    if g._last_induction != last_induction:
        last_induction = g._last_induction
        induction_steps.append(step)
        if len(induction_steps) >= 2:
            induction_intervals.append(
                induction_steps[-1] - induction_steps[-2])

print(f"Inductions: {len(induction_steps)}  (intervals: {len(induction_intervals)})")
print(f"Final: tau={g.tau:.4f} phase={g.phase.value}")
ph_counts = {}
for ph in phase_traj:
    ph_counts[ph] = ph_counts.get(ph,0)+1
print(f"Phase distribution: {dict(sorted(ph_counts.items()))}")

if len(induction_intervals) < 6:
    print("Not enough inductions for period measurement")
    exit()

# Induction intervals over time — split into thirds
n = len(induction_intervals)
seg1 = induction_intervals[:n//3]
seg2 = induction_intervals[n//3:2*n//3]
seg3 = induction_intervals[2*n//3:]

T = []
for label, seg in [("early", seg1), ("mid", seg2), ("late", seg3)]:
    if len(seg) >= 2:
        T.append(statistics.mean(seg))
        print(f"  T_{label}: {T[-1]:.1f}  (n={len(seg)}  values={[round(x,1) for x in seg[:8]]})")
    else:
        T.append(None)

# GI = period ratio
delta = 4.669
print(f"\nFeigenbaum delta = {delta}")
for i in range(len(T)-1):
    if T[i] and T[i+1] and T[i] > 0:
        gi = T[i+1]/T[i]
        err = (gi-delta)/delta*100
        print(f"  GI_{i+1} = T_{i+1}/T_{i} = {gi:.3f}  (err: {err:+.1f}%)")

# Show raw intervals
print(f"\nRaw induction intervals (first 20):")
print(f"  {[round(x,1) for x in induction_intervals[:20]]}")
