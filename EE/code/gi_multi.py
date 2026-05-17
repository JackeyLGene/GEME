"""
GI measurement — 3 independent Geruons, same input, different seeds.
GI = period ratio between units with different internal dynamics.
BGM found GI=4 comparing G0 period to unit period.
"""
import sys, os, math, statistics, random as _rnd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase
from geme import eq, fn, const, structural_signature, symbol_vector

VEC_DIM = 27
STEPS = 8000

# Generate diverse formula stream
r = _rnd.Random(42)
symbols = ['0','1','s','+','x','y','z','swap','pair','comm','succ','forall','exists']
stream_vecs = []
stream_sigs = []
for step in range(STEPS):
    a,b,c,d = r.choice(symbols),r.choice(symbols),r.choice(symbols),r.choice(symbols)
    p = step % 5
    if p == 0: f = eq(fn(a, const(b)), const(c))
    elif p == 1: f = eq(fn('swap', const(a), const(b)), fn('swap', const(b), const(a)))
    elif p == 2: f = eq(fn(a, fn(b, const(c))), fn(b, fn(a, const(c))))
    elif p == 3: f = eq(fn('pair', const(a), const(b)), fn('comm', const(b), const(a)))
    else: f = eq(fn(a, const(b)), fn(a, fn('succ', const(b))))
    stream_vecs.append(list(symbol_vector(f)))
    stream_sigs.append(structural_signature(f))

# 3 Geruons with DIFFERENT capacities — heterogeneity drives GI
configs = [
    (12, 60,  100),   # cap=12, small window
    (20, 90,  200),   # cap=20, medium window
    (32, 120, 300),   # cap=32, large window
]
units = []
for i, (cap, cowin, seed) in enumerate(configs):
    g = Geruon(vec_dim=VEC_DIM, memory_cap=cap, cooccur_window=cowin)
    g.memory.quantum_mode = True
    g.memory._qrand = _rnd.Random(seed)
    units.append(g)
    print(f"  Unit {i}: cap={cap} window={cowin}")

print(f"GI Multi-Unit  Steps={STEPS}  Units=3")
print("=" * 55)

# Run all units in parallel
induction_history = [[] for _ in range(3)]
last_ind = [0,0,0]

for step in range(STEPS):
    for i, g in enumerate(units):
        g.process_vec(stream_vecs[step], stream_sigs[step])
        if g._last_induction != last_ind[i]:
            last_ind[i] = g._last_induction
            induction_history[i].append(step)

# Compute induction periods
periods = []
for i in range(3):
    hist = induction_history[i]
    if len(hist) >= 3:
        ints = [hist[j+1]-hist[j] for j in range(len(hist)-1)]
        T = statistics.mean(ints)
        periods.append(T)
        print(f"  Unit {i}: {len(hist)} inductions, T={T:.1f} "
              f"tau={units[i].tau:.4f} {units[i].phase.value}")
    else:
        periods.append(None)
        print(f"  Unit {i}: {len(hist)} inductions (insufficient)")

# GI = period ratios
delta = 4.669
print(f"\nFeigenbaum delta = {delta}")
for i in range(len(periods)-1):
    if periods[i] and periods[i+1] and periods[i] > 0:
        gi = periods[i+1]/periods[i]
        err = (gi-delta)/delta*100
        print(f"  GI = T_{i+1}/T_{i} = {gi:.3f}  (err: {err:+.1f}%)")

# Also try: sort by period, compute ratio
sorted_periods = sorted([p for p in periods if p])
if len(sorted_periods) >= 2:
    gi_sorted = sorted_periods[-1]/sorted_periods[0]
    print(f"  GI (max/min) = {gi_sorted:.3f}")
