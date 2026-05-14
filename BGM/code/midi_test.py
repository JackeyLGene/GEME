"""MIDI BWV846 — test if G0 behaves differently with note_on/note_off overlap."""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet
from data.midi_bwv846 import generate_sequence

def run(label, seq, passes=3):
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, seed_base=42)
    track = net.enable_tracking()

    for _ in range(passes):
        for vec, _ in seq:
            net.step(vec)

    l4 = track['g0_pred_err']
    boundary = next((i for i,c in enumerate(l4) if c > 0), None)
    deltas = sum(1 for i in range(1,len(l4)) if l4[i] > l4[i-1])

    print(f'\n{label}')
    print(f'  Steps: {len(l4)}')
    print(f'  L3→L4 boundary: {boundary}')
    print(f'  L4 events: {deltas}')
    print(f'  Final G0 L4: {l4[-1] if l4 else "N/A"}')

    return boundary, deltas

if __name__ == '__main__':
    t0 = time.time()
    
    print('='*55)
    print('MIDI vs Chord encoding — G0 comparison')
    print('='*55)
    
    seq_midi = generate_sequence(passes=3)
    print(f'\nMIDI sequence length: {len(seq_midi)} steps')
    
    run('MIDI encoding (note_on/note_off + overlap)', seq_midi)
    
    print(f'\nTotal time: {(time.time()-t0):.1f}s')
