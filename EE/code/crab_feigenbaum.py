"""
Crab Canon Feigenbaum scan: measure phase durations at varying gap densities.
Input: Crab Canon (forward + backward voices) with periodic silence gaps.
Gap density = bifurcation parameter r. Phase durations should period-double.
"""
import sys, os, math, statistics, random
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'BGM', 'code'))
from geruon import Geruon, Phase

# Crab Canon material: BWV 847 fugue subject as canon content
from data.bwv847_fugue import SCORE
from data.bwv846 import chord_hz_vec as hz

# Build forward & backward streams
fwd = []
for notes, beats, *_ in SCORE:
    v = hz(notes)
    for _ in range(beats):
        fwd.append(v)
bwd = list(reversed(fwd))

ZERO = [0.0] * 27

def run_canon(gap_every, seed=42, steps=400):
    """Run crab canon with gap insertion every gap_every steps."""
    r = random.Random(seed)
    g = Geruon(vec_dim=16, memory_cap=16, cooccur_window=60)
    g.memory.quantum_mode = True
    g.memory._qrand = random.Random(seed + 777)

    for t in range(steps):
        # Interleave forward and backward voices + gaps
        if gap_every > 0 and t % gap_every == 0:
            v = ZERO
            sig = 'silence'
        else:
            idx = t % min(len(fwd), len(bwd))
            v = [max(fwd[idx][i], bwd[idx][i]) for i in range(27)]
            # Normalize
            s = math.sqrt(sum(x*x for x in v))
            if s > 0:
                v = [x/s for x in v]
            sig = f'voice_{int(math.floor(t/4))}'
        g.process_vec(v, sig)

    # Track LOCKED-to-LOCKED intervals (period-doubling cascade)
    locked_steps = []
    for s, _, ph_to in g.memory._phase_transitions:
        if ph_to == Phase.LOCKED:
            locked_steps.append(s)

    locked_intervals = []
    for i in range(1, len(locked_steps)):
        locked_intervals.append(locked_steps[i] - locked_steps[i-1])

    # Track CRITICAL-to-CRITICAL intervals as secondary measure
    critical_steps = []
    for s, _, ph_to in g.memory._phase_transitions:
        if ph_to == Phase.CRITICAL:
            critical_steps.append(s)

    critical_intervals = []
    for i in range(1, len(critical_steps)):
        critical_intervals.append(critical_steps[i] - critical_steps[i-1])

    return {
        'tau': g.tau,
        'final_phase': g.phase.value,
        'transition_count': len(g.memory._phase_transitions),
        'locked_intervals': locked_intervals,
        'critical_intervals': critical_intervals,
        'n_locks': len(locked_steps),
    }

print('Crab Canon Feigenbaum scan: gap density as bifurcation parameter')
print(f'{"Gap":>5s} {"Transitions":>10s} {"Locks":>6s} {"Lock intervals":>20s} {"Ratios (next/prev)":>20s}')
print('-' * 65)

for gap in [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20]:
    result = run_canon(gap, seed=42, steps=600)
    intervals_str = ''
    ratio_str = ''
    if result['locked_intervals']:
        intervals_str = str([int(round(x)) for x in result['locked_intervals'][:8]])
        if len(result['locked_intervals']) >= 3:
            ratios = []
            for i in range(1, len(result['locked_intervals'])):
                if result['locked_intervals'][i-1] > 0:
                    ratios.append(result['locked_intervals'][i] / result['locked_intervals'][i-1])
            if ratios:
                ratio_str = f'{max(ratios):.3f}' if ratios else ''
    print(f'{gap:>5d} {result["transition_count"]:>10d} {result["n_locks"]:>6d} '
          f'{intervals_str:>20s} {ratio_str:>20s}')
