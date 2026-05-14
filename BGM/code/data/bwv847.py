"""BWV 847 — Prelude in C minor, Well-Tempered Clavier Book 1.
Two sections: Grave (block chords, slow) + Allegro (runs, fast).
Hz-encoded for GEME experiments.

Format: (chord_notes, beats, section_label, voice_count)
"""
NOTES_Hz = {
    'C3':130.81,'C#3':138.59,'D3':146.83,'D#3':155.56,'E3':164.81,'F3':174.61,
    'F#3':185.00,'G3':196.00,'G#3':207.65,'A3':220.00,'A#3':233.08,'B3':246.94,
    'C4':261.63,'C#4':277.18,'D4':293.66,'D#4':311.13,'E4':329.63,'F4':349.23,
    'F#4':369.99,'G4':392.00,'G#4':415.30,'A4':440.00,'A#4':466.16,'B4':493.88,
    'C5':523.25,'C#5':554.37,'D5':587.33,'D#5':622.25,'E5':659.25,'F5':698.46,
    'F#5':739.99,'G5':783.99,'G#5':830.61,'A5':880.00,
}

FREQ_MIN, FREQ_MAX, BINS = 65, 1050, 27

def chord_hz_vec(notes):
    v = [0.0] * BINS
    for n in notes:
        f = NOTES_Hz.get(n, 440)
        idx = int((f - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * (BINS - 1))
        idx = max(0, min(BINS - 1, idx))
        v[idx] += 1.0
    s = sum(v)
    return [x/s for x in v] if s > 0 else v

# BWV 847 Prelude — 38 bars
# Grave section (bars 1-4): dramatic block chords, 4 voices
# Allegro section (bars 5-38): fast contrapuntal runs, 2-3 voices
SCORE = [
    # === Grave: block chords, slow texture ===
    (['C4','D#4','G4'], 4, 'Grave', 3),
    (['C4','F4','A#4'], 4, 'Grave', 3),
    (['C4','E4','G4'], 4, 'Grave', 3),
    (['C#4','F4','A#4'], 4, 'Grave', 3),
    (['D4','F4','B4'], 4, 'Grave', 3),
    (['C4','E4','G4'], 4, 'Grave', 3),
    (['C4','F4','A#4'], 4, 'Grave', 3),
    (['B3','D4','F4','G4'], 4, 'Grave', 4),  # G7
    # === Allegro: running figures, lighter texture ===
    (['C4','E4','G4'], 2, 'Allegro', 2),
    (['B3','D4','F4'], 2, 'Allegro', 2),
    (['C4','E4','G4'], 2, 'Allegro', 2),
    (['A3','C4','F4'], 2, 'Allegro', 2),
    (['G3','B3','D4','G4'], 2, 'Allegro', 4),
    (['C4','E4','G4','C5'], 2, 'Allegro', 4),
    (['F3','A3','C4','F4'], 2, 'Allegro', 4),
    (['G3','B3','D4','G4'], 2, 'Allegro', 4),
    (['C4','E4','G4','C5'], 2, 'Allegro', 4),
    (['F4','A4','C5','F5'], 2, 'Allegro', 4),
    (['E4','G4','C5','E5'], 2, 'Allegro', 4),
    (['D4','F4','A4','D5'], 2, 'Allegro', 4),
    (['C4','E4','G4','C5'], 2, 'Allegro', 4),
    (['B3','D4','F4','B4'], 2, 'Allegro', 4),
    (['C4','E4','G4','C5'], 2, 'Allegro', 4),
    (['D4','F4','A4','D5'], 2, 'Allegro', 3),
    (['G3','B3','D4','G4'], 2, 'Allegro', 4),
    (['C4','E4','G4'], 2, 'Allegro', 3),
    (['F3','A3','C4'], 2, 'Allegro', 3),
    (['F#3','A3','C4','D4'], 2, 'Allegro', 4),
    (['G3','B3','D4'], 2, 'Allegro', 3),
    (['A3','C4','E4','A4'], 2, 'Allegro', 4),
    (['G3','B3','D4','G4'], 2, 'Allegro', 4),
    (['F3','A3','C4','F4'], 2, 'Allegro', 4),
    (['E3','G3','C4','E4'], 2, 'Allegro', 4),
    (['D3','F3','A3','D4'], 2, 'Allegro', 4),
    (['C3','E3','G3','C4'], 2, 'Allegro', 4),
    (['G2','B2','D3','G3'], 2, 'Allegro', 4),
    (['C3','E3','G3','C4'], 6, 'Allegro', 4),  # final
]

if __name__ == '__main__':
    from collections import Counter
    sections = Counter(s for _,_,s,_ in SCORE)
    print(f'BWV847: {len(SCORE)} entries')
    print(f'Sections: {dict(sections)}')
    print(f'Range: G2 ({NOTES_Hz["G2"]} Hz) - F5 ({NOTES_Hz["F5"]} Hz)')
