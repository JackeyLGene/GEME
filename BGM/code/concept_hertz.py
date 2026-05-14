"""
Concept validation: Three GEMEs, same Hz-coded input → natural differentiation.
Bach WTC Book 1, Prelude in C major (BWV 846) — the most famous piece.
"""
import sys, math, time
sys.path.insert(0, '../../final-v1.5')
from geme import GEME
import random as _qr2

NOTE_FREQS = {
    'C2':65.41,'C#2':69.30,'D2':73.42,'D#2':77.78,'E2':82.41,'F2':87.31,
    'F#2':92.50,'G2':98.00,'G#2':103.83,'A2':110.00,'A#2':116.54,'B2':123.47,
    'C3':130.81,'C#3':138.59,'D3':146.83,'D#3':155.56,'E3':164.81,'F3':174.61,
    'F#3':185.00,'G3':196.00,'G#3':207.65,'A3':220.00,'A#3':233.08,'B3':246.94,
    'C4':261.63,'C#4':277.18,'D4':293.66,'D#4':311.13,'E4':329.63,'F4':349.23,
    'F#4':369.99,'G4':392.00,'G#4':415.30,'A4':440.00,'A#4':466.16,'B4':493.88,
    'C5':523.25,'C#5':554.37,'D5':587.33,'D#5':622.25,'E5':659.25,'F5':698.46,
    'F#5':739.99,'G5':783.99,'G#5':830.61,'A5':880.00,'A#5':932.33,'B5':987.77,
    'C6':1046.50,
}

FREQ_MIN, FREQ_MAX = 65, 1050
BINS = 27

def note_vec(note_name):
    """Encode a note as a 27-dim frequency-distribution vector."""
    f = NOTE_FREQS.get(note_name, 440)
    v = [0.0] * BINS
    idx = int((f - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * (BINS - 1))
    idx = max(0, min(BINS - 1, idx))
    v[idx] = 1.0
    return v

# === BWV 846 — C major prelude, first 8 bars (simplified chords tempo) ===
# Each entry: (chord_notes, beats)
BWV846 = [
    (['C4','E4','G4'], 2), (['C4','E4','G4'], 2),
    (['C4','E4','A4'], 2), (['C4','E4','A4'], 2),
    (['C4','F4','A4'], 2), (['C4','F4','A4'], 2),
    (['C4','F4','A4'], 2), (['C4','F4','A4'], 2),
    (['G3','B3','D4','G4'], 4),
    (['G3','B3','D4','G4'], 4),
    (['C4','E4','G4'], 2), (['C4','E4','G4'], 2),
    (['C4','E4','A4'], 2), (['C4','E4','A4'], 2),
    (['F3','A3','C4','F4'], 4),
    (['G3','B3','D4','G4'], 4),
]

def chord_vec(chord_notes):
    """Sum of individual note vectors, normalized."""
    v = [0.0] * BINS
    for n in chord_notes:
        nv = note_vec(n)
        for i in range(BINS): v[i] += nv[i]
    s = sum(v)
    return [x/s for x in v] if s > 0 else v

def run_geme(name, seed):
    g = GEME(memory_cap=16)
    g.memory.preserve_sig=True; g.memory.quantum_mode=True
    g.memory._merge_dists=[0.3]*30; g._induction_threshold=3.0
    g.memory.cooccur_thresh=0.08; g.memory._qrand=_qr2.Random(seed)
    
    for notes, beats in BWV846 * 4:  # 4 iterations
        for _ in range(beats):
            g.process_vec(chord_vec(notes), 'bwv846')
            g.memory.self_observe()
    
    m = g.metrics()
    # Measure frequency band preference
    band_counts = {'low':0,'mid':0,'high':0}
    for f in g.memory.frames[:8]:
        vec = f.vec
        low = sum(vec[:9]); mid = sum(vec[9:18]); high = sum(vec[18:])
        total = low + mid + high
        if total > 0:
            if low/total > 0.5: band_counts['low']+=1
            elif high/total > 0.5: band_counts['high']+=1
            else: band_counts['mid']+=1
    
    return {'name':name,'frames':m['frame_count'],'L4':m['L4_frame_count'],
            'acc':m['pred_accuracy'],'bands':band_counts,
            'MI':m.get('I(phi;X)',0),'g':g}

if __name__ == '__main__':
    t0 = time.time()
    print('=' * 55)
    print('Concept: Three GEMEs, Same Hz Input → Natural Differentiation')
    print('=' * 55)
    print()

    results = []
    for i, name in enumerate(['GEME_A (低音倾向)', 'GEME_B (中音倾向)', 'GEME_C (高音倾向)']):
        r = run_geme(name, i * 1000)
        results.append(r)
        print(f'{r["name"]}')
        print(f'  Frames={r["frames"]}, L4={r["L4"]}, Acc={r["acc"]:.3f}, MI={r["MI"]:.4f}')
        print(f'  Band preference: {r["bands"]}')
        print()

    # Check if differentiation occurred
    bands_set = {tuple(r['bands'].values()) for r in results}
    print(f'Unique band profiles: {len(bands_set)} out of {len(results)} GEMEs')
    print(f'Differentiation: {"YES - evolution occurring" if len(bands_set) >= 2 else "No - all same"}')
    
    print(f'\nTime: {(time.time()-t0):.1f}s')
