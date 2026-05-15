"""
τ = f(MI): Derive the dynamic coupling, not scan it.

From GEME (Paper 1): I(φ;X) = 0.026 bits = the "free self-reference" baseline.
This is the Gödel number G in PA = Q + G.

In temporal domain (BGM): τ controls cleaning speed → controls self-reference freedom.

Hypothesis:
  τ = τ₀ × (MI₀ / MI)    where MI₀ = 0.026, τ₀ = 0.60

  MI = 0.026 → τ = 0.60 (equilibrium — self-reference is free)
  MI < 0.026 → τ > 0.60 (slow down — build frames to restore self-reference)
  MI > 0.026 → τ < 0.60 (speed up — clean stale frames)

No new variables. Only existing constants.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet
from data.bwv847_fugue import SCORE, chord_hz_vec as hz

MI_0 = 0.026  # from Paper 1: I(phi;X) ≈ 0.026 bits
TAU_0 = 0.60  # default induction threshold

# Test: static τ values to verify the dynamic relationship
def run_at_tau(tau, passes=3):
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, seed_base=42)
    for unit in net.units: unit._induction_threshold = tau
    net.g0._induction_threshold = tau

    for _ in range(passes):
        for entry in SCORE:
            notes, beats = entry[0], entry[1]
            v = hz(notes)
            for _ in range(beats):
                net.step(v, '')

    m = net.metrics()
    unit_mis = [u['MI'] for u in m['units']]
    return {
        'tau': tau,
        'unit_mi_mean': sum(unit_mis)/len(unit_mis),
        'g0_mi': m['g0']['MI'],
        'predicted_tau': round(TAU_0 * (MI_0 / max(sum(unit_mis)/len(unit_mis), 0.001)), 3),
    }

if __name__ == '__main__':
    t0 = time.time()
    print('='*55)
    print('τ = f(MI): Dynamic Coupling')
    print(f'MI₀ = {MI_0} (free self-reference from Paper 1)')
    print(f'τ₀  = {TAU_0} (default induction threshold)')
    print('='*55)
    print(f'{"τ_in":>5s} {"Unit MI μ":>10s} {"G0 MI":>8s} {"Predicted τ":>12s} {"Match?":>8s}')
    print('-'*55)

    for tau in [0.4, 0.6, 0.8]:
        r = run_at_tau(tau)
        # If τ_in → MI, then MI → predicted τ should ≈ τ_in
        pred = r['predicted_tau']
        match = '✓' if abs(pred - tau) < 0.15 else '∼' if abs(pred - tau) < 0.3 else '✗'
        print(f'{r["tau"]:>5.1f} {r["unit_mi_mean"]:>10.4f} {r["g0_mi"]:>8.4f} {pred:>12.3f} {match:>8s}')

    print('-'*55)
    print('If τ→MI produces predicted τ ≈ input τ, the coupling is self-consistent.')
    print(f'Time: {(time.time()-t0):.1f}s')

