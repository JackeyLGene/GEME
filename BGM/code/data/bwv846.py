"""BWV 846 — Prelude in C major, Well-Tempered Clavier Book 1.
Hz-encoded chord vectors for GEME experiments.

Each entry: (chord_notes, beats_in_measure)
35 measures, ~140 time steps at ♩=1.
"""
# Note frequencies (Hz) — C2 to C6
NOTES_Hz = {
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

FREQ_MIN, FREQ_MAX, BINS = 65, 1050, 27

def chord_hz_vec(notes):
    """Encode simultaneous notes as summed Hz-bin vector (27-dim)."""
    v = [0.0] * BINS
    for n in notes:
        f = NOTES_Hz.get(n, 440)
        idx = int((f - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * (BINS - 1))
        idx = max(0, min(BINS - 1, idx))
        v[idx] += 1.0
    s = sum(v)
    return [x/s for x in v] if s > 0 else v

# Full prelude: (notes, beats)
# Harmonic progression: C → G7 → C → Am → F → G7 → C → D7 → G → C → G7 → C → Am → D7 → G → C → Dm7 → G → C
SCORE = [
    (['C4','E4','G4'], 4), (['C4','E4','G4'], 4),                    # C
    (['C4','E4','A4'], 4), (['C4','E4','A4'], 4),                    # Am
    (['C4','F4','A4'], 4), (['C4','F4','A4'], 4),                    # F
    (['B3','D4','F4','G4'], 4), (['B3','D4','F4','G4'], 4),          # G7
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),          # C
    (['C4','E4','A4','C5'], 4), (['C4','E4','A4','C5'], 4),          # Am
    (['C4','F4','A4','C5'], 4), (['C4','F4','A4','C5'], 4),          # F
    (['B3','D4','F4','G4','B4'], 4), (['B3','D4','F4','G4','B4'], 4),# G7
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),          # C
    (['D4','F#4','A4','C5'], 4), (['D4','F#4','A4','C5'], 4),        # D7
    (['G3','B3','D4','G4'], 4), (['G3','B3','D4','G4'], 4),          # G
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),          # C
    (['F3','A3','C4','F4'], 4), (['F3','A3','C4','F4'], 4),          # F
    (['B3','D4','F4','G4'], 4), (['B3','D4','F4','G4'], 4),          # G7
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),          # C
    (['A3','C4','E4','A4'], 4), (['A3','C4','E4','A4'], 4),          # Am
    (['D4','F#4','A4','C5'], 4), (['D4','F#4','A4','C5'], 4),        # D7
    (['G3','B3','D4','G4'], 4), (['G3','B3','D4','G4'], 4),          # G
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),          # C
    (['F3','A3','C4','F4'], 4), (['F3','A3','C4','F4'], 4),          # F
    (['F#3','A3','C4','D4','F4'], 4), (['F#3','A3','C4','D4','F4'], 4),# Dm7
    (['G3','B3','D4','G4'], 4), (['G3','B3','D4','G4'], 4),          # G
    (['C4','E4','G4','C5'], 4), (['C4','E4','G4','C5'], 4),          # C
    (['C4','E4','G4'], 6),                                             # final
]

if __name__ == '__main__':
    # Test
    from collections import Counter
    keys = Counter()
    for notes, _ in SCORE:
        keys[tuple(sorted(notes))] += 1
    print(f'BWV846: {len(SCORE)} entries, {len(keys)} unique chords')
    print(f'Voice range: {sorted(n for notes,_ in SCORE for n in notes)[0]} - {sorted(n for notes,_ in SCORE for n in notes)[-1]}')
