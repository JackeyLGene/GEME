"""
Gap density → Feigenbaum threshold.

BGM found: gap density > 1/16 is the threshold for τ differentiation.
1/16 = 1/4². GI = 4. Hypothesis: the gap density threshold IS the
Feigenbaum accumulation point measured in the information domain.

Test: sweep gap densities from 1/2 to 1/32, find the critical point
where phase behavior changes qualitatively. The critical density d_c
should satisfy d_c * GI² ≈ 1 for GI → delta = 4.669.
"""
import sys, os, math, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'BGM', 'code'))

from geruon import Geruon, Phase
from data.bwv847_fugue import SCORE, chord_hz_vec as hz

# Build crab canon
subject = SCORE
fwd = []
for notes, beats, _ in subject:
    v = hz(notes)
    for _ in range(beats):
        fwd.append(list(v))
bwd = list(reversed(fwd))
n = min(len(fwd), len(bwd))
base = []
for i in range(n):
    b = [(fwd[i][j] + bwd[i][j])/2.0 for j in range(len(fwd[i]))]
    base.append(b)

ZERO = [0.0]*27

# Sweep gap densities
# gap_every = 2 → density 1/2, gap_every = 4 → 1/4, ..., 32 → 1/32
gap_intervals = [2, 3, 4, 6, 8, 12, 16, 24, 32]
CYCLES = 15

print("Gap density sweep — phase differentiation threshold")
print(f"Base: {len(base)} steps, {CYCLES} cycles")
print("=" * 65)
print(f"{'gap':>5s} {'density':>8s} {'trans':>6s} {'phases':>7s} "
      f"{'tau':>7s} {'final_ph':>10s} {'dom_ph':>10s}")

results = []
for gap_k in gap_intervals:
    # Build stream with gaps
    stream = []
    for c in range(CYCLES):
        for i, vec in enumerate(base):
            stream.append(vec)
            if (i+1) % gap_k == 0:
                stream.append(ZERO)

    g = Geruon(vec_dim=27, memory_cap=20, cooccur_window=100)
    g.memory.quantum_mode = True

    phase_traj = []
    for step, vec in enumerate(stream):
        g.process_vec(list(vec), f's{step% (len(base)+1)}')
        phase_traj.append(g.phase.value)

    trans = []
    for i in range(1, len(phase_traj)):
        if phase_traj[i] != phase_traj[i-1]:
            trans.append(i)

    ph_c = {}
    for ph in phase_traj: ph_c[ph] = ph_c.get(ph,0)+1

    density = 1.0 / gap_k
    unique = len(ph_c)
    dom = max(ph_c, key=ph_c.get)

    print(f"{gap_k:>5d} {density:>8.4f} {len(trans):>6d} {unique:>7d} "
          f"{g.tau:>7.3f} {g.phase.value:>10s} {dom:>10s}")

    results.append((gap_k, density, len(trans), unique, g.tau, dom))

# Critical point analysis
# The phase transition occurs where the system visits multiple phases
# and doesn't stay locked in a single phase
print(f"\nCritical threshold analysis:")
print(f"BGM threshold: gap density > 1/16 = {1/16:.4f}")
print(f"Prediction: d_c * GI² ≈ 1")

for gap_k, density, n_trans, n_phases, tau, dom in results:
    # Systems that stay dynamic (not locked) = more phases visited
    is_dynamic = n_phases >= 3 and dom != 'locked'
    gi_est = math.sqrt(1.0 / density) if density > 0 else float('inf')
    print(f"  gap={gap_k:2d} d={density:.4f} dynamic={is_dynamic} "
          f"GI_est={gi_est:.2f} (1/sqrt(d) = sqrt({1/density:.1f}))")
