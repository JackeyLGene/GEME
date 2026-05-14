"""Test G0's L5-L6 closed loop: doubt → g0_weight modulation."""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet
from data.bwv847_fugue import SCORE, chord_hz_vec as hz

def run_one(label, closed_loop, passes=4):
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, closed_loop=closed_loop, seed_base=42)
    for _ in range(passes):
        for entry in SCORE:
            notes, beats = entry[0], entry[1]
            v = hz(notes)
            for _ in range(beats):
                net.step(v, '')
    return net

print('='*55)
print('G0 L5-L6 Closed Loop — Fugue BWV 847')
print('='*55)

for cl, label in [(False, 'OPEN LOOP (fixed g0_weight=0.3)'),
                   (True, 'CLOSED LOOP (doubt modulates coupling)')]:
    net = run_one(label, cl)
    m = net.metrics()
    mi = [u['MI'] for u in m['units']]
    print(f'\n{label}')
    print(f'  g0_weight (final): {net.g0_weight:.3f}')
    print(f'  G0 frames: {m["g0"]["frames"]}, G0 L4: {m["g0"]["L4"]}')
    print(f'  MI spread: {max(mi)-min(mi):.4f}')
    print(f'  G0 doubt: {net.g0.metrics().get("doubt_mode", False)}')

t0 = time.time()
run_one('', True)
print(f'\nTime: {(time.time()-t0):.1f}s')
