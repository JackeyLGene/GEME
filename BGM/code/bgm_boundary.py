"""
BGM Boundary Analysis: G0's L3→L4 transition.

We bypassed this: jumped straight to novelty (L5-L6) without asking
WHEN G0 first generates L4 frames. That transition is the real boundary.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet
from data.bwv847_fugue import SCORE as SCORE_FUGUE, chord_hz_vec as hz_fugue
from data.bwv846 import SCORE as SCORE_846, chord_hz_vec as hz_846

def trace_l3_l4(name, piece_score, encoder, passes=8):
    """Track exactly when G0 transitions from L3 (stable) to L4 (prediction)."""
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, seed_base=42)
    track = net.enable_tracking()

    for _ in range(passes):
        for entry in piece_score:
            if len(entry) == 2:
                notes, beats = entry
                label = str(notes)
            else:
                notes, beats = entry[0], entry[1]
                label = entry[2]
            v = encoder(notes)
            for _ in range(beats):
                net.step(v, step_label=label)

    l4 = track['g0_pred_err']
    labels = track['step_labels']

    # Find transition: where L4 goes from 0 → 1+
    pre_l4_steps = 0
    transition_step = None
    for i, cnt in enumerate(l4):
        if cnt > 0:
            transition_step = i
            break
        pre_l4_steps += 1

    # Count total L4 frame generations (delta increases)
    total_l4_events = sum(1 for i in range(1, len(l4)) if l4[i] > l4[i-1])

    print(f'\n{"="*55}')
    print(f'{name}')
    print(f'{"="*55}')
    print(f'  Steps before first L4 frame: {pre_l4_steps} ')
    print(f'  Transition at step:           {transition_step} ')
    print(f'  First label:                  {labels[transition_step] if transition_step else "N/A"} ')
    print(f'  Total L4 events (delta):      {total_l4_events} ')
    print(f'  L4 events after stabilization: {max(0, total_l4_events - 1)} ')
    
    # The key insight: how much "familiarization" does G0 need before it starts predicting?
    print(f'  Familiarization cost (steps): {pre_l4_steps} ')
    
    return {
        'name': name,
        'pre_l4_steps': pre_l4_steps,
        'transition_step': transition_step,
        'total_l4_events': total_l4_events,
    }

if __name__ == '__main__':
    t0 = time.time()

    print('=' * 55)
    print('G0 L3→L4 Boundary: When does prediction emerge?')
    print('=' * 55)

    r1 = trace_l3_l4('BWV 846 (C major prelude — uniform texture)',
                     SCORE_846, hz_846, passes=4)
    r2 = trace_l3_l4('BWV 847 Fugue (C minor — structural events)',
                     SCORE_FUGUE, hz_fugue, passes=4)

    print(f'\n{"="*55}')
    print('Comparison')
    print(f'{"="*55}')
    print(f'  {"Piece":30s} {"Pre-L4 steps":>15s} {"Events":>8s}')
    print(f'  {"-"*30} {"-"*15} {"-"*8}')
    for r in [r1, r2]:
        print(f'  {r["name"][:30]:30s} {r["pre_l4_steps"]:>15d} {r["total_l4_events"]:>8d}')
    
    print(f'\nTotal time: {(time.time()-t0):.1f}s')
