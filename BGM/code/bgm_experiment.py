"""
BGM Experiment 1: Bach BWV 846 — 3 GEME units + G0.
Compare: G0 enabled vs G0 disabled (ablation).
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet
from data.bwv846 import SCORE, chord_hz_vec

def run(n_units=3, g0_enabled=True, g0_weight=0.3, passes=4, label=''):
    """Run experiment, return metrics dict."""
    net = GEMENet(n_units=n_units, g0_enabled=g0_enabled,
                  g0_weight=g0_weight, seed_base=42)
    for _ in range(passes):
        for notes, beats in SCORE:
            v = chord_hz_vec(notes)
            for _ in range(beats):
                net.step(v)
    return net.metrics()

if __name__ == '__main__':
    t0 = time.time()
    print('=' * 55)
    print('BGM Experiment 1: BWV 846 — 3 GEMEs + G0')
    print('=' * 55)

    # Condition A: G0 enabled
    print('\n[Condition A] G0 enabled (weight=0.3)')
    r_a = run(g0_enabled=True, g0_weight=0.3, label='A')
    for i, u in enumerate(r_a['units']):
        print(f'  GEME_{i}: Acc={u["acc"]:.3f}, L4={u["L4"]}, MI={u["MI"]:.4f}, L6={u["l6"]:.2f}')
    g0 = r_a['g0']
    print(f'  G0:     Frames={g0["frames"]}, L4={g0["L4"]}, MI={g0["MI"]:.4f}')

    # Condition B: G0 disabled (ablation)
    print('\n[Condition B] G0 disabled — ablation')
    r_b = run(g0_enabled=False, g0_weight=0.0, label='B')
    for i, u in enumerate(r_b['units']):
        print(f'  GEME_{i}: Acc={u["acc"]:.3f}, L4={u["L4"]}, MI={u["MI"]:.4f}, L6={u["l6"]:.2f}')

    # Check differentiation
    mis_a = [u['MI'] for u in r_a['units']]
    mis_b = [u['MI'] for u in r_b['units']]
    spread_a = max(mis_a) - min(mis_a)
    spread_b = max(mis_b) - min(mis_b)
    print(f'\n{"="*55}')
    print(f'MI spread with G0:    {spread_a:.4f}')
    print(f'MI spread without G0: {spread_b:.4f}')
    print(f'Differentiation: {"YES (+)" if spread_a > spread_b else "minimal"}')
    print(f'Time: {(time.time()-t0):.1f}s')
