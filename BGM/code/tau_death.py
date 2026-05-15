"""
Cognitive death: L4/L1 > 1 → GEME stops responding.
Locked unit keeps running but its output to G0 freezes.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet
from data.bwv847_fugue import SCORE, chord_hz_vec as hz
import copy

def run(death_enabled=False, passes=8):
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, seed_base=42)
    MI_0, TAU_0 = 0.026, 0.6

    for unit in net.units: unit._induction_threshold = TAU_0

    dead_units = set()
    frozen_l6 = {}
    death_step = {}

    for p in range(passes):
        for entry in SCORE:
            notes, beats = entry[0], entry[1]
            v = hz(notes)
            for _ in range(beats):
                net.step(v, '')

            # Check for death: L4/L1 > 0.1 (error density too high)
            if death_enabled:
                for i, unit in enumerate(net.units):
                    if i in dead_units: continue
                    m = unit.metrics()
                    layers = m.get('layers', {})
                    l4 = sum(v for k, v in layers.items() if 'L4' in k)
                    l1 = layers.get('L1', 1)
                    l3 = layers.get('L3', 1)
                    l4_ratio = l4 / max(l1 + l3, 1)

                    if l4_ratio > 0.1:
                        dead_units.add(i)
                        frozen_l6[i] = unit.anomaly_score()
                        death_step[i] = net._t
                        print(f'[DEATH] GEME_{i} died at step {net._t} (L4/L3={l4}/{l3}={l4_ratio:.3f})')

                # Freeze dead units' output to G0 (stop contributing to G0's input)
                for i in dead_units:
                    # Set the unit's anomaly_score to frozen value permanently
                    # This is done by manipulating the L6 state
                    unit = net.units[i]
                    # We simulate death by setting doubt_mode permanently
                    if not unit.metrics().get('doubt_mode', False):
                        unit.memory._doubt_mode = True
                        unit.memory._last_accuracy = 0.3

    mi_vals = [u.metrics().get('I(phi;X)', 0) for u in net.units]
    alive = [i for i in range(3) if i not in dead_units]
    g_m = net.g0.metrics()
    print(f'\nSummary:')
    print(f'  Death enabled: {death_enabled}')
    print(f'  Dead units: {sorted(dead_units)}')
    print(f'  Alive: {alive}')
    if alive:
        mi_alive = [mi_vals[i] for i in alive]
        print(f'  Alive MI spread: {max(mi_alive)-min(mi_alive):.4f}')
    if dead_units:
        print(f'  Death steps: {death_step}')
    print(f'  G0 MI: {g_m.get("I(phi;X)", 0):.4f}')

    return dead_units

print('='*55)
print('Cognitive Death: L4/L1 > 0.1 → GEME freezes')
print('='*55)

print('\n--- No death (baseline) ---')
run(death_enabled=False, passes=6)

print(f'\n--- Death enabled ---')
run(death_enabled=True, passes=6)
