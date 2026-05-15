"""
τ voice test: do GEMEs differentiate into as many τ values as there are voices?

Hypothesis: N voices → N distinct τ values after dynamic coupling.
Test: 1-voice → 5-voice synthetic music.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet

def generate_piece(voices=3, length=32):
    """Generate a simple polyphonic piece with N voices.
    Each voice has its own rhythm (different note durations per voice)."""
    # Voice 0: fast (quarter notes)
    # Voice 1: medium (half notes)
    # Voice 2: slow (whole notes)
    # Voice 3: very slow (double whole)
    # Voice 4: extremely slow (quad whole)
    durations = [2, 4, 8, 16, 32]
    notes_by_voice = [
        ['C4','D4','E4','F4','G4','A4','B4','C5'],
        ['C4','E4','G4','C5'],
        ['C4','G4','C5'],
        ['C4','C5'],
        ['C4'],
    ]
    piece = []
    for step in range(length):
        active = []
        for v in range(min(voices, len(notes_by_voice))):
            idx = (step // durations[v]) % len(notes_by_voice[v])
            active.append(notes_by_voice[v][idx])
        piece.append((active, 1))
    return piece

# Update SCORE dynamically
def run_voices(n_voices, passes=8):
    """Run dynamic τ on a piece with n_voices."""
    from data.bwv846 import chord_hz_vec as hz
    piece = generate_piece(voices=n_voices)
    
    net = GEMENet(n_units=n_voices, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, seed_base=42)
    MI_0, TAU_0, TAU_MIN, TAU_MAX = 0.026, 0.6, 0.2, 1.0
    
    for unit in net.units: unit._induction_threshold = TAU_0
    
    for _ in range(passes):
        for notes, _ in piece:
            v = hz(notes)
            for _ in range(1):
                net.step(v, '')
            for i, unit in enumerate(net.units):
                mi = unit.metrics().get('I(phi;X)', 0.001)
                new_tau = TAU_0 * (MI_0 / max(mi, 0.001))
                unit._induction_threshold = max(TAU_MIN, min(TAU_MAX, new_tau))
    
    m = net.metrics()
    final_taus = sorted([round(unit._induction_threshold, 3) for unit in net.units])
    final_mis = [round(unit.metrics().get('I(phi;X)', 0), 4) for unit in net.units]
    
    unique_taus = len(set(final_taus))
    tau_range = max(final_taus) - min(final_taus) if len(final_taus) > 1 else 0
    
    return {
        'voices': n_voices,
        'units': n_voices,
        'taus': final_taus,
        'mis': final_mis,
        'unique_taus': unique_taus,
        'tau_range': tau_range,
        'mi_spread': max(final_mis) - min(final_mis),
    }

print('='*55)
print('τ Voice Test: N voices → N distinct τ values')
print('='*55)
print(f'{"Voices":>6s} {"Units":>6s} {"Unique τ":>8s} {"τ range":>8s} {"MI spread":>10s} {"τ values":>20s}')
print('-'*55)

for voices in [1, 2, 3, 5]:
    r = run_voices(voices)
    taus_str = ', '.join(f'{t:.2f}' for t in r['taus'])
    print(f'{r["voices"]:>6d} {r["units"]:>6d} {r["unique_taus"]:>8d} '
          f'{r["tau_range"]:>8.3f} {r["mi_spread"]:>10.4f} {taus_str:>20s}')
