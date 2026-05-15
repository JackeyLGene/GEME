"""
Alertness: does simple music (BWV 846) cause τ to flatten faster than complex (BWV 847 fugue)?
Alert = τ oscillates. Bored = τ flatlines.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet
from data.bwv846 import SCORE as S_846, chord_hz_vec as hz_846
from data.bwv847_fugue import SCORE as S_847, chord_hz_vec as hz_847

MI_0, TAU_0 = 0.026, 0.6

def run_piece(name, score, encoder, passes=8):
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, seed_base=42)
    for unit in net.units: unit._induction_threshold = TAU_0

    tau_trace = []  # mean τ per pass
    l4_trace = []   # mean L4 per pass

    for p in range(passes):
        taus_this_pass = []  # all τ values in this pass
        l4_this_pass = []
        for entry in score:
            notes, beats = entry[0], entry[1]
            v = encoder(notes)
            for _ in range(beats):
                net.step(v, '')
                # Update τ dynamically
                for unit in net.units:
                    mi = unit.metrics().get('I(phi;X)', 0.001)
                    new_tau = TAU_0 * (MI_0 / max(mi, 0.001))
                    unit._induction_threshold = max(0.1, min(1.0, new_tau))
                    taus_this_pass.append(unit._induction_threshold)
                    l4_this_pass.append(unit.metrics().get('L4_frame_count', 0))

        tau_trace.append(sum(taus_this_pass)/len(taus_this_pass))
        l4_trace.append(sum(l4_this_pass)/len(l4_this_pass))

    # Alertness metric: τ oscillation in last 3 passes
    if len(tau_trace) >= 3:
        late_variation = max(tau_trace[-3:]) - min(tau_trace[-3:])
    else:
        late_variation = 0

    # L4 persistence: L4 events per step in last 3 passes
    steps_per_pass = sum(e[1] for e in score)
    late_l4 = sum(l4_trace[-3:]) / max(steps_per_pass * 3, 1)

    print(f'\n{name}')
    print(f'  τ per pass: {[round(t,3) for t in tau_trace]}')
    print(f'  L4 per pass: {[round(l,1) for l in l4_trace]}')
    print(f'  Late τ variation: {late_variation:.3f} (higher = more alert)')
    print(f'  Late L4 density:  {late_l4:.3f} (higher = more vigilant)')

    return {'name': name, 'tau_trace': tau_trace, 'l4_trace': l4_trace,
            'late_variation': late_variation, 'late_l4': late_l4}

print('='*55)
print('Alertness: Simple vs Complex Music')
print('='*55)

r1 = run_piece('BWV846 (C major — simple uniform)', S_846, hz_846)
r2 = run_piece('BWV847 Fugue (C minor — complex)', S_847, hz_847)

print(f'\n{"="*55}')
print('Comparison:')
print(f'  {"":30s} {"τ var (late)":>13s} {"L4/st (late)":>13s}')
print(f'  {"-"*30} {"-"*13} {"-"*13}')
print(f'  {r1["name"][:28]:28s} {r1["late_variation"]:>13.3f} {r1["late_l4"]:>13.3f}')
print(f'  {r2["name"][:28]:28s} {r2["late_variation"]:>13.3f} {r2["late_l4"]:>13.3f}')
alert_diff = r1['late_variation'] - r2['late_variation']
print(f'  Alertness diff: {"BORED (simple < complex)" if alert_diff < 0 else "INCONCLUSIVE"}')
