"""
Crab Canon + gap insertion → bidirectional phase oscillation → GI measurement.

BGM discovery: gap density > 1/16 steps is the threshold for differentiation.
Gaps create discrete boundaries that prevent the co-occurrence window from
saturating, enabling the phase to cycle back from LOCKED to EXPANDING.

The gap period itself becomes the Feigenbaum variable: as gap density varies,
the phase oscillation period doubles at characteristic ratios.
"""
import sys, os, math, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'BGM', 'code'))

from geruon import Geruon, Phase
from data.bwv847_fugue import SCORE, chord_hz_vec as hz

# Build crab canon stream (full subject, blended)
subject = SCORE
fwd = []
for notes, beats, _ in subject:
    v = hz(notes)
    for _ in range(beats):
        fwd.append(list(v))
bwd = list(reversed(fwd))
n = min(len(fwd), len(bwd))
blended = []
for i in range(n):
    b = [(fwd[i][j] + bwd[i][j])/2.0 for j in range(len(fwd[i]))]
    blended.append(b)

# Zero vector for gap insertion
ZERO = [0.0]*27

def gap_stream(base, gap_every, cycles=20):
    """Insert a zero-vector gap every N steps. BGM threshold: gap > 1/16 steps."""
    stream = []
    for c in range(cycles):
        for i, vec in enumerate(base):
            stream.append(vec)
            if (i+1) % gap_every == 0:
                stream.append(ZERO)  # gap = discrete boundary
    return stream

# Test gap periods: 4, 8, 12, 16, 20, 24 steps
# BGM: gap density > 1/16 → gap_every < 16
# Feigenbaum: period-doubling should appear as gap_every varies
gap_periods = [4, 8, 12, 16, 24]

print(f"Crab Canon base: {len(blended)} steps")
print(f"Testing gap periods: {gap_periods}")
print("=" * 60)

for gap_k in gap_periods:
    stream = gap_stream(blended, gap_k, cycles=20)
    total = len(stream)
    g = Geruon(vec_dim=27, memory_cap=20, cooccur_window=100)
    g.memory.quantum_mode = True

    phase_traj = []
    for step, vec in enumerate(stream):
        g.process_vec(list(vec), f'crab_{step % (len(blended)+1)}')
        phase_traj.append(g.phase.value)

    trans = []
    for i in range(1, len(phase_traj)):
        if phase_traj[i] != phase_traj[i-1]:
            trans.append(i)

    ph_c = {}
    for ph in phase_traj: ph_c[ph] = ph_c.get(ph,0)+1
    unique_phases = len(ph_c)

    if len(trans) >= 6:
        intervals = [trans[i+1]-trans[i] for i in range(len(trans)-1)]
        T_mean = statistics.mean(intervals)
        # Measure period-doubling: split intervals in half
        h = len(intervals)//2
        T0 = statistics.mean(intervals[:h]) if h>0 else 0
        T1 = statistics.mean(intervals[h:]) if h>0 else 0
        gi = T1/T0 if T0>0 else 0
        print(f"  gap={gap_k:2d}: {len(trans):3d} trans {unique_phases} phases "
              f"T={T_mean:.1f} T0={T0:.1f} T1={T1:.1f} GI={gi:.3f} "
              f"tau={g.tau:.3f} {g.phase.value}")
    else:
        print(f"  gap={gap_k:2d}: {len(trans):3d} trans {unique_phases} phases "
              f"tau={g.tau:.3f} {g.phase.value} — locked")

# Key test: phase cycling across gap periods
# Does gap insertion enable the phase to oscillate?
print(f"\nPhase cycling check (does system visit >1 phase?):")
for gap_k in gap_periods:
    stream = gap_stream(blended, gap_k, cycles=20)
    g = Geruon(vec_dim=27, memory_cap=20, cooccur_window=100)
    g.memory.quantum_mode = True
    for step, vec in enumerate(stream):
        g.process_vec(list(vec), f'crab_{step % (len(blended)+1)}')
    phases_seen = set()
    for ph in [g.phase.value]:  # only final phase
        pass
    # Track phases throughout
    all_phases = set()
    g2 = Geruon(vec_dim=27, memory_cap=20, cooccur_window=100)
    g2.memory.quantum_mode = True
    for step, vec in enumerate(stream):
        g2.process_vec(list(vec), f'crab_{step % (len(blended)+1)}')
        all_phases.add(g2.phase.value)
    print(f"  gap={gap_k:2d}: {len(all_phases)} phases visited: {sorted(all_phases)} "
          f"tau={g2.tau:.3f}")
