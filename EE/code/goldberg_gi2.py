"""
Goldberg Variations → MIDI encode → Geruon GI measurement.

Uses the structural Goldberg score + midi_encoder to produce
a temporally rich event stream, then measures phase transition
period-doubling across multiple seeds.
"""
import sys, os, math, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
sys.path.insert(0, os.path.join(_here, 'data'))

from geruon import Geruon, Phase
from bwv988_goldberg import goldberg_score
from midi_encoder import midi_encode

VEC_DIM = 27
PASSES = 3  # repeat the entire Goldberg cycle
SEEDS = 10

# Generate score and encode
print("Generating Goldberg score...")
score = goldberg_score(rng_seed=42)
print(f"  Score: {len(score)} events")

# MIDI encode — produces (vec, label) pairs
encoded = midi_encode(score, passes=PASSES)
print(f"  Encoded: {len(encoded)} vectors ({PASSES} passes)")

stream_vecs = [vec for vec, label in encoded]
stream_labels = [label for vec, label in encoded]

print(f"  Stream: {len(stream_vecs)} steps")
print(f"  Unique labels: {len(set(l for l in stream_labels if l))}")
print("=" * 55)

def measure_one(seed, cap=24):
    """Run one Geruon through the Goldberg stream, measure phase periods."""
    g = Geruon(vec_dim=VEC_DIM, memory_cap=cap, cooccur_window=100)
    g.memory.quantum_mode = True
    g.memory._qrand = __import__('random').Random(seed + 1000)

    phase_traj = []
    for step, (vec, label) in enumerate(encoded):
        g.process_vec(list(vec), label or f'step{step}')
        phase_traj.append(g.phase.value)

    # Phase transitions
    transitions = []
    for i in range(1, len(phase_traj)):
        if phase_traj[i] != phase_traj[i-1]:
            transitions.append((i, phase_traj[i-1], phase_traj[i]))

    # Phase distribution
    ph_c = {}
    for ph in phase_traj: ph_c[ph] = ph_c.get(ph,0)+1

    return g.tau, transitions, ph_c


# Run with different capacities for heterogeneity
configs = [(16, 100), (22, 200), (28, 300)]

print(f"Seeds={SEEDS}  Passes={PASSES}  Configs={len(configs)}")
all_results = []

for cap, seed_base in configs:
    cap_results = []
    for s in range(SEEDS):
        tau, trans, ph_c = measure_one(seed_base + s, cap=cap)
        n = len(trans)
        if n >= 6:
            t_steps = [t[0] for t in trans]
            intervals = [t_steps[i+1]-t_steps[i] for i in range(len(t_steps)-1)]
            m = len(intervals)
            T0 = statistics.mean(intervals[:m//3]) if m//3>0 else 0
            T1 = statistics.mean(intervals[m//3:2*m//3]) if m//3>0 else 0
            T2 = statistics.mean(intervals[2*m//3:]) if m//3>0 else 0
            gi1 = T1/T0 if T0>0 else 0
            gi2 = T2/T1 if T1>0 else 0
            cap_results.append((n, T0, T1, T2, gi1, gi2, tau, max(ph_c,key=ph_c.get)))
        else:
            cap_results.append((n, 0,0,0,0,0, tau, '?'))

    # Average across seeds for this config
    valid = [r for r in cap_results if r[0] >= 6]
    if valid:
        avg_gi1 = statistics.mean([r[4] for r in valid])
        avg_gi2 = statistics.mean([r[5] for r in valid])
        avg_n = statistics.mean([r[0] for r in valid])
        print(f"  cap={cap}: {len(valid)}/{SEEDS} seeds valid, "
              f"avg {avg_n:.0f} trans, GI=[{avg_gi1:.2f}, {avg_gi2:.2f}]")
    else:
        print(f"  cap={cap}: 0/{SEEDS} seeds valid")
    all_results.append((cap, cap_results))

# Overall GI
all_gi1 = []
all_gi2 = []
for cap, results in all_results:
    for r in results:
        if r[0] >= 6:
            if r[4] > 0: all_gi1.append(r[4])
            if r[5] > 0: all_gi2.append(r[5])

delta = 4.669
if all_gi1:
    print(f"\nOverall GI_1: mean={statistics.mean(all_gi1):.3f} "
          f"median={statistics.median(all_gi1):.3f} "
          f"err={(statistics.mean(all_gi1)-delta)/delta*100:+.1f}%")
if all_gi2:
    print(f"Overall GI_2: mean={statistics.mean(all_gi2):.3f} "
          f"median={statistics.median(all_gi2):.3f} "
          f"err={(statistics.mean(all_gi2)-delta)/delta*100:+.1f}%")
print(f"Feigenbaum delta = {delta}")
