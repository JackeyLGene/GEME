"""
BGM Novelty Analysis: G0 pred_err timestamps → fugue structure detection.
Test if G0 detects subject entries (texture/event changes in fugue structure).
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet
from data.bwv847_fugue import SCORE as SCORE_FUGUE, chord_hz_vec as hz_fugue
from data.bwv846 import SCORE as SCORE_846, chord_hz_vec as hz_846
from collections import Counter

def analyze(name, piece_score, encoder, label_key=2, passes=8):
    """Run G0 on a piece, return novelty events mapped to labels."""
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
                label = entry[label_key]
            v = encoder(notes)
            for _ in range(beats):
                net.step(v, step_label=label)

    l4 = track['g0_pred_err']
    labels = track['step_labels']

    # Delta novelty
    novelty = []
    for i in range(1, len(l4)):
        if l4[i] > l4[i-1]:
            novelty.append({
                'step': i, 'label': labels[i],
                'pass': i // len(piece_score),
            })

    label_dist = Counter(n['label'] for n in novelty)
    total = len(novelty)

    print(f'\n{"="*55}')
    print(f'{name} — steps={len(l4)}, novelty={total}')
    print(f'{"="*55}')
    
    if novelty:
        for lbl, cnt in label_dist.most_common(20):
            pct = 100 * cnt / total
            print(f'  {lbl:30s} {cnt:3d} ({pct:.0f}%)')

    return novelty

if __name__ == '__main__':
    t0 = time.time()
    
    # Fugue test
    nv = analyze('BWV 847 Fugue (C minor, 3 voices)', SCORE_FUGUE, hz_fugue)
    
    # Focus on event types
    if nv:
        event_types = Counter()
        for n in nv:
            prefix = n['label'].split('_')[0] if '_' in n['label'] else n['label']
            event_types[prefix] += 1
        print(f'\nBy event type:')
        for ev, cnt in event_types.most_common():
            print(f'  {ev:10s}: {cnt}')
    
    print(f'\nTotal time: {(time.time()-t0):.1f}s')
