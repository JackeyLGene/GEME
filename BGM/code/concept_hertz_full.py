"""
Concept validation: Full BWV 846 Prelude, three GEMEs, Hz encoding.
Tests if natural frequency-band differentiation occurs from varied input alone.
"""
import sys, math, time
sys.path.insert(0, '../../final-v1.5')
from geme import GEME
import random as _qr2

# 27 frequency bins: 65 Hz (C2) to 1050 Hz (C6+), ~7 octaves
FREQ_MIN, FREQ_MAX, BINS = 65, 1050, 27

def freq_to_vec(freq):
    idx = int((freq - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * (BINS - 1))
    idx = max(0, min(BINS - 1, idx))
    v = [0.0] * BINS; v[idx] = 1.0; return v

# Note frequencies (Hz) - chromatic scale C2-B5
NOTES = {
    'C2':65.41,'C#2':69.30,'D2':73.42,'D#2':77.78,'E2':82.41,'F2':87.31,
    'F#2':92.50,'G2':98.00,'G#2':103.83,'A2':110.00,'A#2':116.54,'B2':123.47,
    'C3':130.81,'C#3':138.59,'D3':146.83,'D#3':155.56,'E3':164.81,'F3':174.61,
    'F#3':185.00,'G3':196.00,'G#3':207.65,'A3':220.00,'A#3':233.08,'B3':246.94,
    'C4':261.63,'C#4':277.18,'D4':293.66,'D#4':311.13,'E4':329.63,'F4':349.23,
    'F#4':369.99,'G4':392.00,'G#4':415.30,'A4':440.00,'A#4':466.16,'B4':493.88,
    'C5':523.25,'C#5':554.37,'D5':587.33,'D#5':622.25,'E5':659.25,'F5':698.46,
    'F#5':739.99,'G5':783.99,'G#5':830.61,'A5':880.00,'A#5':932.33,'B5':987.77,
}

def chord_vec(notes):
    v = [sum(freq_to_vec(NOTES[n])[i] for n in notes) for i in range(BINS)]
    s = sum(v); return [x/s for x in v] if s > 0 else v

# === BWV 846 — Full Prelude (35 measures, harmonic progression) ===
# Format: (chord_notes, beats_in_measure)
BWV846_FULL = [
    (['C4','E4','G4'], 4), (['C4','E4','G4'], 4),
    (['C4','E4','A4'], 4), (['C4','E4','A4'], 4),
    (['C4','F4','A4'], 4), (['C4','F4','A4'], 4),
    (['B3','D4','F4','G4'], 4), (['B3','D4','F4','G4'], 4),  # G7
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),
    (['C4','E4','A4','C5'], 4), (['C4','E4','A4','C5'], 4),  # Am
    (['C4','F4','A4','C5'], 4), (['C4','F4','A4','C5'], 4),  # F
    (['B3','D4','F4','G4','B4'], 4), (['B3','D4','F4','G4','B4'], 4),  # G7
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),  # C
    (['D4','F#4','A4','C5'], 4), (['D4','F#4','A4','C5'], 4),  # D7
    (['G3','B3','D4','G4'], 4), (['G3','B3','D4','G4'], 4),  # G
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),  # C
    (['F3','A3','C4','F4'], 4), (['F3','A3','C4','F4'], 4),  # F
    (['B3','D4','F4','G4'], 4), (['B3','D4','F4','G4'], 4),  # G7
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),  # C
    (['A3','C4','E4','A4'], 4), (['A3','C4','E4','A4'], 4),  # Am
    (['D4','F#4','A4','C5'], 4), (['D4','F#4','A4','C5'], 4),  # D7
    (['G3','B3','D4','G4'], 4), (['G3','B3','D4','G4'], 4),  # G
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),  # C
    (['F3','A3','C4','F4'], 4), (['F3','A3','C4','F4'], 4),  # F
    (['F#3','A3','C4','D4','F4'], 4), (['F#3','A3','C4','D4','F4'], 4),  # Dm7
    (['G3','B3','D4','G4'], 4), (['G3','B3','D4','G4'], 4),  # G
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),  # C (cadence)
    (['C4','E4','G4'], 6),  # final chord, held
]

def spectral_centroid(vec):
    """Weighted mean of frequency bin indices — where is the center of mass?"""
    total = sum(vec)
    return sum(i * v for i, v in enumerate(vec)) / total if total > 0 else BINS/2

def run_geme(seed, label):
    g = GEME(memory_cap=16)
    g.memory.preserve_sig=True; g.memory.quantum_mode=True
    g.memory._merge_dists=[0.3]*30; g._induction_threshold=3.0
    g.memory.cooccur_thresh=0.08
    g.memory._qrand=_qr2.Random(seed)
    
    for _ in range(3):  # 3 complete playthroughs
        for notes, beats in BWV846_FULL:
            for _ in range(beats):
                g.process_vec(chord_vec(notes), 'bwv846')
                g.memory.self_observe()
    
    m = g.metrics()
    # Analyze frame centroid distribution
    centroids = []
    for f in g.memory.frames:
        c = spectral_centroid(f.vec)
        centroids.append(c)
    avg_centroid = sum(centroids) / len(centroids) if centroids else 0.0
    # Qualitative band assignment
    if avg_centroid < BINS/3: band = 'LOW (bass)'
    elif avg_centroid < BINS*2/3: band = 'MID'
    else: band = 'HIGH (treble)'
    
    return {'label': label, 'frames': m['frame_count'],
            'L4': m['L4_frame_count'], 'acc': m['pred_accuracy'],
            'MI': m.get('I(phi;X)', 0),
            'centroids': [round(c,1) for c in centroids],
            'avg_centroid': round(avg_centroid,1),
            'band': band}

if __name__ == '__main__':
    t0 = time.time()
    print('=' * 55)
    print('BWV 846 Full — Hz Encoding — Three GEMEs')
    print('=' * 55)
    
    results = []
    for i, name in enumerate(['GEME_A', 'GEME_B', 'GEME_C']):
        r = run_geme(i * 777, name)
        results.append(r)
        print(f'\n{r["label"]}')
        print(f'  Frames={r["frames"]}, L4={r["L4"]}, Acc={r["acc"]:.3f}, MI={r["MI"]:.4f}')
        print(f'  Spectral centroids: {r["centroids"]}')
        print(f'  Avg centroid: {r["avg_centroid"]}  →  {r["band"]}')
    
    bands = [r['band'] for r in results]
    distinct = len(set(bands))
    centroids = [r['avg_centroid'] for r in results]
    spread = max(centroids) - min(centroids)
    print(f'\n{"="*55}')
    print(f'Band assignments: {bands}')
    print(f'Distinct bands: {distinct}/{len(results)}')
    print(f'Centroid spread: {spread:.1f} bins (larger = more differentiation)')
    print(f'Differentiation: {"YES" if distinct > 1 else "NO — G0 feedback needed"}')
    print(f'Time: {(time.time()-t0):.1f}s')
