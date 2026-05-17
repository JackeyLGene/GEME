"""
BiasField P0 — cross-generational structural inheritance.

Gen 1: run, precipitate frames → bias field accumulates
Gen 2: initialize with bias field → structural inheritance
Verify: Gen 2 τ distribution correlated with Gen 1 traces.
No symbols. No names. Just gradient.
"""
import sys, os, math, statistics, random as _rnd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase, BiasField
from geme import eq, fn, const, structural_signature, symbol_vector

VEC_DIM = 27
STEPS = 3000
SEEDS = 5

def run_gen(bias=None, seed=42, steps=STEPS):
    """Run one generation. Returns (geruon, tau_traj, phase_traj)."""
    r = _rnd.Random(seed)
    symbols = ['0','1','s','+','x','y','z','swap','pair','comm','succ','forall','exists']
    g = Geruon(vec_dim=VEC_DIM, memory_cap=24, cooccur_window=100,
               bias_field=bias)
    g.memory.quantum_mode = True
    g.memory._qrand = _rnd.Random(seed + 1000)

    tau_traj = []
    phase_traj = []
    for step in range(steps):
        a,b,c,d = r.choice(symbols),r.choice(symbols),r.choice(symbols),r.choice(symbols)
        p = step % 5
        if p == 0: f = eq(fn(a, const(b)), const(c))
        elif p == 1: f = eq(fn('swap', const(a), const(b)), fn('swap', const(b), const(a)))
        elif p == 2: f = eq(fn(a, fn(b, const(c))), fn(b, fn(a, const(c))))
        elif p == 3: f = eq(fn('pair', const(a), const(b)), fn('comm', const(b), const(a)))
        else: f = eq(fn(a, const(b)), fn(a, fn('succ', const(b))))
        g.process_vec(list(symbol_vector(f)), structural_signature(f))
        tau_traj.append(g.tau)
        phase_traj.append(g.phase.value)
    return g, tau_traj, phase_traj


print("BiasField P0 — Cross-Generational Structural Inheritance")
print(f"Steps={STEPS}  Seeds={SEEDS}  vec_dim={VEC_DIM}")
print("=" * 60)

# ── Gen 1: accumulate bias fields ──
gen1_bfields = []
gen1_tau_means = []
for s in range(SEEDS):
    bf = BiasField(vec_dim=VEC_DIM)
    g1, t1, p1 = run_gen(bias=bf, seed=s, steps=STEPS)
    n_deposited = g1.enrich()
    gen1_bfields.append(bf)
    gen1_tau_means.append(statistics.mean(t1[-500:]))  # late-stage tau
    print(f"  Gen1[{s}]: tau={g1.tau:.3f} {g1.phase.value} "
          f"deposited={n_deposited} bias_count={bf._count} "
          f"Σw={bf._total_weight:.1f}")

print(f"\n  Gen1 mean late τ: {statistics.mean(gen1_tau_means):.3f}")

# ── Gen 2: inherit bias fields ──
gen2_tau_means = []
gen2_no_bias_means = []
for s in range(SEEDS):
    # With bias inheritance
    g2, t2, p2 = run_gen(bias=gen1_bfields[s], seed=s+100, steps=STEPS)
    gen2_tau_means.append(statistics.mean(t2[-500:]))
    # Control: no bias
    g2c, t2c, p2c = run_gen(bias=None, seed=s+100, steps=STEPS)
    gen2_no_bias_means.append(statistics.mean(t2c[-500:]))

    print(f"  Gen2[{s}]: bias τ={g2.tau:.3f} ({g2.phase.value}) "
          f"vs no-bias τ={g2c.tau:.3f} ({g2c.phase.value}) "
          f"Δ={g2.tau - g2c.tau:+.3f}")

print(f"\n  Gen2 mean late τ (bias):    {statistics.mean(gen2_tau_means):.3f}")
print(f"  Gen2 mean late τ (no-bias):  {statistics.mean(gen2_no_bias_means):.3f}")
delta_tau = statistics.mean(gen2_tau_means) - statistics.mean(gen2_no_bias_means)
print(f"  Δτ = {delta_tau:+.3f}")

# ── Correlation test ──
# Does Gen1's bias field weight correlate with Gen2's τ shift?
bias_weights = [bf._total_weight for bf in gen1_bfields]
tau_shifts = [gen2_tau_means[i] - gen2_no_bias_means[i] for i in range(SEEDS)]

if len(bias_weights) >= 3:
    r_corr = statistics.correlation(bias_weights, tau_shifts) if hasattr(statistics, 'correlation') else 0
    print(f"\n  Bias weight vs τ shift correlation: {r_corr:+.3f}" if r_corr != 0 else "")

print(f"\nVerdict: ", end='')
if abs(delta_tau) > 0.01:
    print(f"BiasField causes detectable τ shift (Δ={delta_tau:+.3f}). "
          f"Structural inheritance works.")
else:
    print(f"No detectable τ shift. Bias field may need more deposit mass.")
