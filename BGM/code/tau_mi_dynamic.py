"""
τ = f(MI) dynamic coupling: each GEME's τ adapts based on its own MI.

τ_i(t+1) = clamp(τ₀ × MI₀ / MI_i(t), τ_min, τ_max)

No new variables. τ₀=0.6, MI₀=0.026 from Paper 1.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet
from data.bwv846 import SCORE, chord_hz_vec as hz

MI_0 = 0.026
TAU_0, TAU_MIN, TAU_MAX = 0.6, 0.2, 1.0

def run_dynamic(use_dynamic=False, passes=6):
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, seed_base=42)

    # Apply initial tau to all
    for unit in net.units: unit._induction_threshold = TAU_0

    tau_history = {i: [] for i in range(3)}
    mi_history = {i: [] for i in range(3)}

    for _ in range(passes):
        for entry in SCORE:
            notes, beats = entry[0], entry[1]
            v = hz(notes)
            for _ in range(beats):
                net.step(v, '')

            # Dynamic tau update after each step
            if use_dynamic:
                for i, unit in enumerate(net.units):
                    m = unit.metrics()
                    mi = m.get('I(phi;X)', 0.001)
                    # τ = τ₀ × MI₀ / MI
                    new_tau = TAU_0 * (MI_0 / max(mi, 0.001))
                    new_tau = max(TAU_MIN, min(TAU_MAX, new_tau))
                    unit._induction_threshold = new_tau

        # Record every pass
        for i, unit in enumerate(net.units):
            tau_history[i].append(unit._induction_threshold)
            mi_history[i].append(unit.metrics().get('I(phi;X)', 0))

    m = net.metrics()
    return {
        'tau_history': tau_history,
        'mi_history': mi_history,
        'final_mi': [unit.metrics().get('I(phi;X)', 0) for unit in net.units],
        'final_tau': [unit._induction_threshold for unit in net.units],
        'mi_spread': max([u['MI'] for u in m['units']]) - min([u['MI'] for u in m['units']]),
        'g0_mi': m['g0']['MI'],
    }

print('='*55)
print('τ = f(MI) Dynamic Coupling')
print(f'MI₀ = {MI_0}, τ₀ = {TAU_0}')
print('='*55)

for dyn, label in [(False, 'STATIC τ (fixed=0.6)'),
                    (True, 'DYNAMIC τ = f(MI)')]:
    r = run_dynamic(use_dynamic=dyn, passes=6)
    print(f'\n{label}')
    print(f'  Final MI:  {[round(m,4) for m in r["final_mi"]]}')
    print(f'  Final τ:   {[round(t,3) for t in r["final_tau"]]}')
    print(f'  MI spread: {r["mi_spread"]:.4f}')
    print(f'  G0 MI:     {r["g0_mi"]:.4f}')

    # Show evolution
    print(f'  τ evolution per pass:')
    for i in range(3):
        evo = [round(t,3) for t in r['tau_history'][i]]
        print(f'    GEME_{i}: {evo}')
