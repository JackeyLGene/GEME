"""
Phase synchronization analysis — L0 vs L1.

Is L1 genuinely following L0's rhythm (synchronization),
or are both converging to the same period independently?
"""
import sys, os, math, statistics, random as _rnd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase
from geme import eq, fn, const, structural_signature, symbol_vector

VEC_DIM = 27; STEPS = 4000

r = _rnd.Random(42)
symbols = ['0','1','s','+','x','y','z','swap','pair','comm','succ','forall','exists']
g0 = Geruon(vec_dim=VEC_DIM, memory_cap=24, cooccur_window=100)
g0.memory.quantum_mode = True; g0.memory._qrand = _rnd.Random(100)
g1 = Geruon(vec_dim=VEC_DIM, memory_cap=24, cooccur_window=100)
g1.memory.quantum_mode = True; g1.memory._qrand = _rnd.Random(200)

# Record τ and phase at every step
tau0, tau1 = [], []
ph0, ph1 = [], []

for step in range(STEPS):
    a,b,c,d = r.choice(symbols),r.choice(symbols),r.choice(symbols),r.choice(symbols)
    p = step % 5
    if p == 0: f = eq(fn(a, const(b)), const(c))
    elif p == 1: f = eq(fn('swap', const(a), const(b)), fn('swap', const(b), const(a)))
    elif p == 2: f = eq(fn(a, fn(b, const(c))), fn(b, fn(a, const(c))))
    elif p == 3: f = eq(fn('pair', const(a), const(b)), fn('comm', const(b), const(a)))
    else: f = eq(fn(a, const(b)), fn(a, fn('succ', const(b))))
    g0.process_vec(list(symbol_vector(f)), structural_signature(f))
    tau0.append(g0.tau); ph0.append(g0.phase.value)
    g1.process_vec(list(g0.arrow_output()), f'L0_arrow')
    tau1.append(g1.tau); ph1.append(g1.phase.value)

# ── Phase trajectory cross-correlation ──
# Convert phase to numeric for correlation
ph_map = {'expanding':0, 'resting':1, 'tensing':2, 'critical':3, 'locked':4}
p0 = [ph_map[p] for p in ph0]
p1 = [ph_map[p] for p in ph1]

# Cross-correlation: how does L1 correlate with L0 at different lags?
print("Phase cross-correlation (lag = L1 delay after L0):")
print(f"{'lag':>5s} {'corr':>8s} {'interpretation'}")
for lag in [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 100, 200]:
    n = STEPS - lag
    x = p0[:n]; y = p1[lag:lag+n]
    mx = sum(x)/n; my = sum(y)/n
    num = sum((x[i]-mx)*(y[i]-my) for i in range(n))
    dx = math.sqrt(sum((xi-mx)**2 for xi in x))
    dy = math.sqrt(sum((yi-my)**2 for yi in y))
    r_corr = num/(dx*dy) if dx*dy>0 else 0
    note = ""
    if lag == 0: note = "simultaneous"
    elif lag < 5: note = "near-immediate"
    print(f"{lag:>5d} {r_corr:>8.4f}  {note}")

# ── τ cross-correlation ──
print(f"\nτ cross-correlation:")
for lag in [0, 1, 3, 8, 21, 55, 100]:
    n = STEPS - lag
    x = tau0[:n]; y = tau1[lag:lag+n]
    mx = sum(x)/n; my = sum(y)/n
    num = sum((x[i]-mx)*(y[i]-my) for i in range(n))
    dx = math.sqrt(sum((xi-mx)**2 for xi in x))
    dy = math.sqrt(sum((yi-my)**2 for yi in y))
    r_tau = num/(dx*dy) if dx*dy>0 else 0
    print(f"  lag={lag:>3d}: r={r_tau:>8.4f}")

# ── Phase transition coincidence ──
# When L0 transitions, does L1 transition within N steps?
trans0_steps = set()
for i in range(1, len(ph0)):
    if ph0[i] != ph0[i-1]: trans0_steps.add(i)
trans1_steps = set()
for i in range(1, len(ph1)):
    if ph1[i] != ph1[i-1]: trans1_steps.add(i)

window = 3
coincident = 0
for t0 in trans0_steps:
    for d in range(window+1):
        if t0 + d in trans1_steps:
            coincident += 1; break

total_l0 = len(trans0_steps); total_l1 = len(trans1_steps)
print(f"\nPhase transition coincidence (L1 follows within {window} steps):")
print(f"  L0 transitions: {total_l0}  L1 transitions: {total_l1}")
print(f"  L0→L1 within window: {coincident}/{total_l0} ({coincident/total_l0*100:.0f}%)")
print(f"  Random expectation: {total_l1*window/STEPS*100:.0f}%")

# ── Phase state distribution comparison ──
print(f"\nPhase distribution:")
for label, ph in [("L0", ph0), ("L1", ph1)]:
    counts = {}
    for p in ph: counts[p] = counts.get(p,0)+1
    dist = {k:f"{v/STEPS*100:.1f}%" for k,v in sorted(counts.items())}
    print(f"  {label}: {dist}")
