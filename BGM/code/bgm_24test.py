"""
24 Preludes Test: L3→L4 boundary consistency + post-boundary style signature.
Hypothesis: L3→L4 is consistent (G0's internal rhythm).
Style/emotion lives in L4+ behavior — pred_err pattern post-transition.
"""
import sys, os, time, statistics
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet

# Define preludes as (notes, beats) lists
from data.bwv846 import SCORE as s_846, chord_hz_vec as hz
from data.bwv847_fugue import SCORE as s_847f, chord_hz_vec as hz_f
from data.bwv_contrast import BWV848 as s_848, BWV849 as s_849, BWV851 as s_851, hz_vec

hz_vec_846 = hz
hz_vec_847f = hz_f

PRELUDES = {
    'BWV846 C maj (simple, uniform)': (s_846, hz),
    'BWV847 Fugue C min (structured)': (s_847f, hz_f),
    'BWV848 C# maj (bright, arpegg)': (s_848, hz_vec),
    'BWV849 C# min (chromatic, dense)': (s_849, hz_vec),
    'BWV851 D min (energetic, fast)': (s_851, hz_vec),
}

def run(name, score, encoder, passes=4):
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, seed_base=42)
    track = net.enable_tracking()

    for _ in range(passes):
        for entry in score:
            if len(entry) == 2: notes, beats = entry
            else: notes, beats = entry[0], entry[1]
            v = encoder(notes)
            for _ in range(beats):
                net.step(v, '')

    l4 = track['g0_pred_err']

    # L3→L4 boundary
    boundary = next((i for i, cnt in enumerate(l4) if cnt > 0), None)

    # Post-boundary behavior: L4 events after first
    deltas = [l4[i] - l4[i-1] for i in range(1, len(l4))]
    total_events = sum(1 for d in deltas if d > 0)
    events_after = total_events - 1 if total_events > 0 else 0

    # L4 density: L4 events per 100 steps after boundary
    post_steps = max(1, len(l4) - (boundary or 0))
    density = events_after / post_steps * 100 if post_steps > 0 else 0

    # Final state
    m = net.metrics()
    mi_vals = [u['MI'] for u in m['units']]
    mi_spread = max(mi_vals) - min(mi_vals)
    g0_mi = m['g0']['MI']

    return {
        'boundary': boundary,
        'events': total_events,
        'events_after': events_after,
        'density': round(density, 1),
        'mi_spread': round(mi_spread, 4),
        'g0_mi': round(g0_mi, 4),
    }

if __name__ == '__main__':
    t0 = time.time()

    print('=' * 55)
    print('24 Preludes Test — L3→L4 Boundary + Style Signature')
    print('=' * 55)
    print(f'{"Prelude":30s} {"L3→L4":>6s} {"Events":>7s} {"After":>6s} {"Dens":>5s} {"MI spread":>10s} {"G0 MI":>7s}')
    print('-' * 75)

    rows = []
    for name, (score, encoder) in PRELUDES.items():
        r = run(name, score, encoder)
        rows.append((name, r))
        print(f'{name[:29]:29s} {r["boundary"]:>6} {r["events"]:>7} {r["events_after"]:>6} '
              f'{r["density"]:>5.1f} {r["mi_spread"]:>10.4f} {r["g0_mi"]:>7.4f}')

    boundaries = [r['boundary'] for _, r in rows if r['boundary'] is not None]
    tot_events = [r['events'] for _, r in rows]

    print('-' * 75)
    print(f'L3→L4 boundary consistency:')
    print(f'  Range: {min(boundaries)}–{max(boundaries)} steps')
    print(f'  Mean: {statistics.mean(boundaries):.1f} ± {statistics.stdev(boundaries):.1f} steps')

    print(f'\nTotal events: {min(tot_events)}–{max(tot_events)}')
    print(f'Time: {(time.time()-t0):.1f}s')
