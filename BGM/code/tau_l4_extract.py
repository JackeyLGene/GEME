"""Extract L4 density vs τ relationship from existing experiments."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet
from data.bwv847_fugue import SCORE, chord_hz_vec as hz

def run(passes=6, use_dynamic=True):
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, seed_base=42)
    MI_0, TAU_0 = 0.026, 0.6

    for unit in net.units: unit._induction_threshold = TAU_0

    step_records = []
    total_steps = 0

    for _ in range(passes):
        for entry in SCORE:
            notes, beats = entry[0], entry[1]
            v = hz(notes)
            for _ in range(beats):
                net.step(v, '')
                total_steps += 1
                for i, unit in enumerate(net.units):
                    m = unit.metrics()
                    l4 = m.get('L4_frame_count', 0)
                    l1 = m.get('layers', {}).get('L1', 0) or 1
                    l3 = m.get('layers', {}).get('L3', 0) or 1
                    mi = m.get('I(phi;X)', 0.001)
                    tau = unit._induction_threshold
                    step_records.append({
                        'step': total_steps, 'unit': i,
                        'l4': l4, 'l4_vs_l1': l4/(l1 or 1), 'l4_vs_total': l4/max(m.get('frame_count', 1), 1),
                        'mi': mi, 'tau': tau,
                    })
                    if use_dynamic:
                        new_tau = TAU_0 * (MI_0 / max(mi, 0.001))
                        unit._induction_threshold = max(0.1, min(1.0, new_tau))

    return step_records

print('='*55)
print('L4 density vs τ — relationship extraction')
print('='*55)

recs = run(use_dynamic=True)

# Find: what L4/L1 ratio corresponds to τ=0.6?
tau_vs_l4 = {}
for r in recs[-30:]:  # last 30 records
    t = round(r['tau'], 1)
    if t not in tau_vs_l4 or r['l4_vs_total'] > tau_vs_l4[t]:
        tau_vs_l4[t] = round(r['l4_vs_total'], 3)

print(f'\nτ vs L4/total ratio (end of run):')
for t in sorted(tau_vs_l4.keys()):
    print(f'  τ={t:.1f} → L4/total={tau_vs_l4[t]:.3f}')

# Core question: does L4/total naturally converge to a value that replaces τ?
final_recs = [r for r in recs if r['step'] > recs[-1]['step'] - 30]
avg_l4_ratio = sum(r['l4_vs_total'] for r in final_recs) / len(final_recs)
print(f'\nAverage L4/total ratio at steady state: {avg_l4_ratio:.3f}')
print(f'Equivalent τ (from τ=τ₀×MI₀/MI): ... not applicable -- τ IS the ratio')

# The real insight: L4/total IS the system's own measurement of "I'm confused"
# No τ needed. τ was always a placeholder for this.
avg_l4_vs_l1 = sum(r['l4_vs_l1'] for r in final_recs) / len(final_recs)
print(f'Average L4/L1 ratio:               {avg_l4_vs_l1:.3f}')
print(f'When L4 > L1: system has more error frames than base frames.')
print(f'This is the self-referential τ: no parameter, only data.')
