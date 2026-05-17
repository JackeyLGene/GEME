"""
Feigenbaum δ from Gödel recursion depth, not from input scanning.
Run a single Geruon; measure circularity recurrence period at each recursion depth.
"""
import sys, os, math, statistics, random
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'BGM', 'code'))
from geruon import Geruon, Phase, StructuralSig, detect_circularity
from data.bwv847_fugue import SCORE
from data.bwv846 import chord_hz_vec as hz

# Build a stable input stream (BWV 847 fugue, score encoding)
fugue_stream = []
for notes, beats, *_ in SCORE:
    v = hz(notes)
    s = math.sqrt(sum(x*x for x in v))
    if s > 0:
        v = [x/s for x in v]
    for _ in range(beats):
        fugue_stream.append(v)

VEC_DIM = 16
ZERO = [0.0] * VEC_DIM

r = random.Random(42)
g = Geruon(vec_dim=VEC_DIM, memory_cap=16, cooccur_window=60)
g.memory.quantum_mode = True
g.memory._qrand = random.Random(42 + 777)

# Track L4 creation intervals and ref chain depth
l4_steps = []        # steps at which L4 frames were created
l4_depths = []       # ref chain depths at each L4 creation
l4_taus = []         # τ at each L4 creation

for step in range(1200):
    # Stable input: fugue with fixed gap pattern
    idx = step % len(fugue_stream)
    if step % 5 == 0:
        v = ZERO; sig = 'silence'
    else:
        v_raw = fugue_stream[idx]
        # Project 27-dim BGM stream to Geruon's vec_dim
        v = [sum(v_raw[j::VEC_DIM]) for j in range(VEC_DIM)]
        s2 = math.sqrt(sum(x*x for x in v))
        v = [x/max(s2, 0.001) for x in v]
        sig = f'voice_{idx}'
    g.process_vec(v, sig)

    # Track L4 frame creation and ref chain depth
    m = g.metrics()
    l4_count = m.get('L4_frame_count', 0)
    if l4_count > len(l4_steps):
        l4_steps.append(step)
        l4_taus.append(g.tau)
        # Max ref depth among all L4 frames
        max_depth = 0
        for f in g.memory.frames:
            ss = getattr(f, 'struct_sig', None)
            if ss and ss.refs:
                # Walk the ref chain to find max depth
                chain = ss.refs
                d = 1
                while chain:
                    d += 1
                    # Follow first ref's refs
                    next_refs = []
                    for r in chain:
                        next_refs.extend(r.refs)
                    chain = tuple(set(next_refs))[:4]
                    if d > 20:
                        break
                max_depth = max(max_depth, d)
        l4_depths.append(max_depth)

print('Gödel Recursion: tracking L4 frame creation intervals vs τ phase')
print(f'{"Step":>6s} {"L4 frames":>10s} {"Max ref depth":>14s} {"τ":>8s} {"Phase":>10s} {"L4-to-L4 interval":>20s}')
print('-' * 70)

# Batch report every 50 steps
l4_intervals = []
for i, s in enumerate(l4_steps):
    if i > 0:
        l4_intervals.append(s - l4_steps[i-1])

prev_report = 0
for step in range(50, 1201, 50):
    idx_last = max([i for i, s in enumerate(l4_steps) if s <= step] + [0])
    l4_count = idx_last + 1
    max_depth = max(l4_depths[:idx_last+1]) if l4_depths else 0
    tau_now = l4_taus[idx_last] if l4_taus and idx_last < len(l4_taus) else 0
    phase_now = g.memory.phase.value
    # Average interval in this window
    window_intervals = [l4_intervals[i] for i in range(prev_report, min(len(l4_intervals), idx_last))]
    avg_interval = statistics.mean(window_intervals) if window_intervals else 0
    prev_report = idx_last
    print(f'{step:>6d} {l4_count:>10d} {max_depth:>14d} '
          f'{tau_now:>8.4f} {phase_now:>10s} {avg_interval:>20.1f}')

# The key: does the L4 interval ratio converge?
if len(l4_intervals) >= 8:
    ratios = []
    for i in range(4, min(len(l4_intervals), 16)):
        if l4_intervals[i-4] > 0:
            ratios.append(l4_intervals[i] / l4_intervals[i-4])
    if ratios:
        avg_r = statistics.mean(ratios)
        print(f'\nL4 interval growth ratio (should → 4.669 if δ is in recursion): {avg_r:.4f}')
        print(f'Raw intervals (last 10): {[f"{x:.0f}" for x in l4_intervals[-10:]]}')

print(f'\nFinal: τ={g.tau:.4f}, phase={g.phase.value}, '
      f'transitions={len(g.memory._phase_transitions)}, '
      f'total L4 events={len(l4_steps)}')
