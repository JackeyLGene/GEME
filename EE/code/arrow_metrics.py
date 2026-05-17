"""
L0→L1 metrics: GI, system complexity, information efficiency.

Measures across 10 seeds to establish statistical reliability.
"""
import sys, os, math, statistics, random as _rnd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase
from geme import eq, fn, const, structural_signature, symbol_vector

VEC_DIM = 27; STEPS = 4000; SEEDS = 10

def run_pair(seed):
    r = _rnd.Random(seed)
    symbols = ['0','1','s','+','x','y','z','swap','pair','comm','succ','forall','exists']
    g0 = Geruon(vec_dim=VEC_DIM, memory_cap=24, cooccur_window=100)
    g0.memory.quantum_mode = True; g0.memory._qrand = _rnd.Random(seed+100)
    g1 = Geruon(vec_dim=VEC_DIM, memory_cap=24, cooccur_window=100)
    g1.memory.quantum_mode = True; g1.memory._qrand = _rnd.Random(seed+200)

    ph0, ph1 = [], []
    trans0, trans1 = [], []
    mi0, mi1 = [], []

    for step in range(STEPS):
        a,b,c,d = r.choice(symbols),r.choice(symbols),r.choice(symbols),r.choice(symbols)
        p = step % 5
        if p == 0: f = eq(fn(a, const(b)), const(c))
        elif p == 1: f = eq(fn('swap', const(a), const(b)), fn('swap', const(b), const(a)))
        elif p == 2: f = eq(fn(a, fn(b, const(c))), fn(b, fn(a, const(c))))
        elif p == 3: f = eq(fn('pair', const(a), const(b)), fn('comm', const(b), const(a)))
        else: f = eq(fn(a, const(b)), fn(a, fn('succ', const(b))))

        g0.process_vec(list(symbol_vector(f)), structural_signature(f))
        ph0.append(g0.phase.value)
        if len(ph0)>=2 and ph0[-2]!=ph0[-1]: trans0.append(step)

        g1.process_vec(list(g0.arrow_output()), f'L0_arrow')
        ph1.append(g1.phase.value)
        if len(ph1)>=2 and ph1[-2]!=ph1[-1]: trans1.append(step)

        if step % 500 == 0:
            mi0.append(g0.metrics()['I(phi;X)'])
            mi1.append(g1.metrics()['I(phi;X)'])

    m0 = g0.metrics(); m1 = g1.metrics()
    # Phase periods
    T0 = _period(trans0); T1 = _period(trans1)
    gi = T1/T0 if (T0 and T1 and T0>0) else 0
    # Complexity: structural entropy + frame count
    c0 = m0['structural_entropy'] * m0['frame_count']; c1 = m1['structural_entropy'] * m1['frame_count']
    # Efficiency: I(Φ;X) / τ
    eff0 = m0['I(phi;X)'] / max(g0.tau, 0.001); eff1 = m1['I(phi;X)'] / max(g1.tau, 0.001)

    return {
        'tau0': g0.tau, 'tau1': g1.tau,
        'T0': T0, 'T1': T1, 'GI': gi,
        'comp0': c0, 'comp1': c1,
        'eff0': eff0, 'eff1': eff1,
        'trans0': len(trans0), 'trans1': len(trans1),
        'phases0': len(set(ph0)), 'phases1': len(set(ph1)),
        'mi0': m0['I(phi;X)'], 'mi1': m1['I(phi;X)'],
    }

def _period(trans):
    if len(trans) < 4: return None
    ints = [trans[i+1]-trans[i] for i in range(len(trans)-1)]
    return statistics.mean(ints)

print(f"L0→L1 Metrics  Steps={STEPS}  Seeds={SEEDS}")
print("=" * 65)

results = [run_pair(s) for s in range(SEEDS)]

# Aggregate
for label, key in [("GI", "GI"), ("T0", "T0"), ("T1", "T1")]:
    vals = [r[key] for r in results if r[key] and r[key] > 0]
    if vals:
        print(f"  {label}: mean={statistics.mean(vals):.3f} "
              f"median={statistics.median(vals):.3f} "
              f"range=[{min(vals):.3f},{max(vals):.3f}]")

print(f"\n{'Seed':<6s} {'τ0':>6s} {'τ1':>6s} {'T0':>7s} {'T1':>7s} {'GI':>7s} "
      f"{'eff0':>7s} {'eff1':>7s} {'ph0':>5s} {'ph1':>5s}")
print("-" * 75)
for i, r in enumerate(results):
    t0s = f"{r['T0']:.1f}" if r['T0'] else "N/A"
    t1s = f"{r['T1']:.1f}" if r['T1'] else "N/A"
    gis = f"{r['GI']:.3f}" if r['GI'] else "N/A"
    print(f"  {i:<4d} {r['tau0']:>6.3f} {r['tau1']:>6.3f} {t0s:>7s} {t1s:>7s} {gis:>7s} "
          f"{r['eff0']:>7.4f} {r['eff1']:>7.4f} {r['phases0']:>5d} {r['phases1']:>5d}")

# Summary
gi_vals = [r['GI'] for r in results if r['GI'] and r['GI'] > 0]
eff0s = [r['eff0'] for r in results]; eff1s = [r['eff1'] for r in results]
comp0s = [r['comp0'] for r in results]; comp1s = [r['comp1'] for r in results]
mi0s = [r['mi0'] for r in results]; mi1s = [r['mi1'] for r in results]

print(f"\nSummary (mean ± range):")
print(f"  GI:                {statistics.mean(gi_vals):.3f} [{min(gi_vals):.3f},{max(gi_vals):.3f}]")
print(f"  L0 τ:              {statistics.mean([r['tau0'] for r in results]):.3f}")
print(f"  L1 τ:              {statistics.mean([r['tau1'] for r in results]):.3f}")
print(f"  L0 I(Φ;X):         {statistics.mean(mi0s):.5f}")
print(f"  L1 I(Φ;X):         {statistics.mean(mi1s):.5f}")
print(f"  L0 efficiency:     {statistics.mean(eff0s):.4f}")
print(f"  L1 efficiency:     {statistics.mean(eff1s):.4f}")
print(f"  L0 complexity:     {statistics.mean(comp0s):.2f}")
print(f"  L1 complexity:     {statistics.mean(comp1s):.2f}")
print(f"  L0 phases:         {statistics.mean([r['phases0'] for r in results]):.1f}")
print(f"  L1 phases:         {statistics.mean([r['phases1'] for r in results]):.1f}")
print(f"  L0 transitions:    {statistics.mean([r['trans0'] for r in results]):.0f}")
print(f"  L1 transitions:    {statistics.mean([r['trans1'] for r in results]):.0f}")

# Feigenbaum comparison
delta = 4.669
gi_mean = statistics.mean(gi_vals)
print(f"\nFeigenbaum δ = {delta}  GI_mean = {gi_mean:.3f}  err = {(gi_mean-delta)/delta*100:+.1f}%")
