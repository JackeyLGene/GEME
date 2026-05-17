"""
SharedField — parallel Geruons sharing one BiasField.

No generations. No G0. No symbols. Just a shared gradient field.
Each unit deposits precipitate into the field and receives
continuous bias modulation from it.

This is the neuron-like architecture: the BiasField is the
synaptic cleft — units don't message each other, they modulate
the shared gradient that all units swim in.
"""
import sys, os, math, statistics, random as _rnd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase, BiasField
from geme import eq, fn, const, structural_signature, symbol_vector

VEC_DIM = 27
STEPS = 4000
N_UNITS = 5

# Shared gradient field — the synaptic cleft
field = BiasField(vec_dim=VEC_DIM)

# Create units — share field but each has different bias sensitivity
# (different receptor densities, like heterogeneous neurons)
bias_weights = [0.01, 0.02, 0.03, 0.05, 0.08]
units = []
for i in range(N_UNITS):
    g = Geruon(vec_dim=VEC_DIM, memory_cap=20, cooccur_window=100,
               bias_field=field, bias_weight=bias_weights[i])
    g.memory.quantum_mode = True
    g.memory._qrand = _rnd.Random(100 + i * 777)
    units.append(g)

print(f"SharedField — {N_UNITS} Geruons, 1 BiasField, No G0")
print(f"Steps={STEPS}  vec_dim={VEC_DIM}")
print("=" * 60)

# Phase tracking per unit
phase_logs = [[] for _ in range(N_UNITS)]
tau_logs = [[] for _ in range(N_UNITS)]

# Run: EACH unit gets DIFFERENT input (like different dendritic trees).
# All share the same gradient field (like shared extracellular medium).
# In Bacteria: spatial position → heterogeneous input.
# In SharedField: quantum seed + different input stream → heterogeneity.

# Generate per-unit input streams
symbols = ['0','1','s','+','x','y','z','swap','pair','comm','succ','forall','exists']
unit_streams = []
for i in range(N_UNITS):
    r_i = _rnd.Random(1000 + i * 777)
    vecs_i = []
    sigs_i = []
    for step in range(STEPS):
        a,b,c,d = r_i.choice(symbols),r_i.choice(symbols),r_i.choice(symbols),r_i.choice(symbols)
        p = step % 5
        if p == 0: f = eq(fn(a, const(b)), const(c))
        elif p == 1: f = eq(fn('swap', const(a), const(b)), fn('swap', const(b), const(a)))
        elif p == 2: f = eq(fn(a, fn(b, const(c))), fn(b, fn(a, const(c))))
        elif p == 3: f = eq(fn('pair', const(a), const(b)), fn('comm', const(b), const(a)))
        else: f = eq(fn(a, const(b)), fn(a, fn('succ', const(b))))
        vecs_i.append(list(symbol_vector(f)))
        sigs_i.append(structural_signature(f))
    unit_streams.append((vecs_i, sigs_i))

enrich_interval = 200
for step in range(STEPS):
    for i, g in enumerate(units):
        vecs_i, sigs_i = unit_streams[i]
        g.process_vec(list(vecs_i[step]), sigs_i[step])
        phase_logs[i].append(g.phase.value)
        tau_logs[i].append(g.tau)

    if step > 0 and step % enrich_interval == 0:
        for g in units:
            g.enrich()

# Report
print(f"\nField: {field}")
tau_finals = []
tau_spreads = []
for i, g in enumerate(units):
    tau_f = g.tau
    ph_c = {}
    for ph in phase_logs[i]: ph_c[ph] = ph_c.get(ph,0)+1
    tau_finals.append(tau_f)
    print(f"  U{i}: tau={tau_f:.4f} {g.phase.value} "
          f"phases={dict(sorted(ph_c.items()))}")

tau_spread = max(tau_finals) - min(tau_finals)
print(f"\n  τ spread: {tau_spread:.4f}")
print(f"  Unique phases: {len(set(g.phase.value for g in units))}")

# Also: last-1000-step τ means
late_taus = []
for i in range(N_UNITS):
    late_taus.append(statistics.mean(tau_logs[i][-1000:]))
print(f"  Late τ mean spread: {max(late_taus) - min(late_taus):.4f}")

# Key question: does the shared field maintain differentiation?
if tau_spread > 0.05:
    print(f"\n  ✓ Shared BiasField maintains τ differentiation (no G0 needed)")
else:
    print(f"\n  ✗ τ convergence — shared field alone insufficient")
