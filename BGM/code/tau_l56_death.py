"""
τ as L5-L6 output, not input parameter.
τ = 1 - L5_rolling_accuracy (how often has G0 been wrong recently?)
If τ enters a positive-feedback death attractor: system can't recover.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet
from data.bwv847_fugue import SCORE, chord_hz_vec as hz

TAU_MIN, TAU_MAX = 0.1, 1.0

def run_tau_from_l5(use_l5_tau=False, passes=6):
    """Replace τ with L5-derived value on each step."""
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, seed_base=42)

    if use_l5_tau:
        for unit in net.units:
            unit._induction_threshold = 0.6  # start at default

    tau_trace = {i: [] for i in range(3)}

    for _ in range(passes):
        for entry in SCORE:
            notes, beats = entry[0], entry[1]
            v = hz(notes)
            for _ in range(beats):
                net.step(v, '')

            if use_l5_tau:
                for i, unit in enumerate(net.units):
                    # L5 data: prediction accuracy + doubt frequency
                    m = unit.metrics()
                    acc = m.get('pred_accuracy', 0.5)
                    doubt = 1 if m.get('doubt_mode', False) else 0
                    
                    # τ from L5: τ = 1 - accuracy
                    # When accuracy is high (confident) → τ low (fast cleaning, fresh frames)
                    # When accuracy is low (confused) → τ high (slow cleaning, accumulate)
                    tau_raw = 1.0 - acc + doubt * 0.3
                    tau = max(TAU_MIN, min(TAU_MAX, tau_raw))
                    unit._induction_threshold = tau
                    tau_trace[i].append(tau)

    m = net.metrics()
    mi_vals = [u['MI'] for u in m['units']]
    final_taus = [unit._induction_threshold for unit in net.units]

    return {
        'mi_vals': mi_vals,
        'mi_spread': max(mi_vals) - min(mi_vals),
        'final_taus': final_taus,
        'tau_trace': tau_trace,
        'g0_mi': m['g0']['MI'],
    }

def check_lock(trace):
    """Detect τ death attractor: last 10 steps show < 1% change."""
    if len(trace) < 20: return False, 0
    recent = trace[-10:]
    variation = max(recent) - min(recent)
    return variation < 0.01, variation

print('='*55)
print('τ from L5: Does the system self-lock?')
print('='*55)

for l5, label in [(False, 'Static τ (fixed=0.6)'),
                   (True, 'τ = 1 - L5_accuracy')]:
    r = run_tau_from_l5(use_l5_tau=l5, passes=6)

    print(f'\n{label}')
    print(f'  Final MI: {[round(m,4) for m in r["mi_vals"]]}')
    print(f'  Final τ:  {[round(t,3) for t in r["final_taus"]]}')
    print(f'  MI spread:{r["mi_spread"]:.4f}')
    print(f'  G0 MI:    {r["g0_mi"]:.4f}')

    if l5:
        for i in range(3):
            locked, lock_var = check_lock(r['tau_trace'][i])
            status = 'LOCKED' if locked else 'oscillating'
            print(f'  GEME_{i} τ trace: [{r["tau_trace"][i][:5]}] ... [{r["tau_trace"][i][-5:]}]  ({status})')
