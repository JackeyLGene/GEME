"""BWV 847 Fugue — C minor, 3 voices. Well-Tempered Clavier Book 1.

Key structural events marked for novelty analysis:
  - Subject entry (single voice enters with theme)
  - Answer entry (second voice, dominant key)
  - Third voice entry (texture climax)
  - Episode (modulatory passage, no full subject)
  - Stretto (overlapping subject entries)
  - Final cadence
"""
NOTES_Hz = {
    'C3':130.81,'C#3':138.59,'D3':146.83,'D#3':155.56,'E3':164.81,'F3':174.61,
    'F#3':185.00,'G3':196.00,'G#3':207.65,'A3':220.00,'A#3':233.08,'B3':246.94,
    'C4':261.63,'C#4':277.18,'D4':293.66,'D#4':311.13,'E4':329.63,'F4':349.23,
    'F#4':369.99,'G4':392.00,'G#4':415.30,'A4':440.00,'A#4':466.16,'B4':493.88,
    'C5':523.25,'C#5':554.37,'D5':587.33,'D#5':622.25,'E5':659.25,'F5':698.46,
    'G5':783.99,'A5':880.00,
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

# BWV 847 Fugue — 31 bars, 3 voices
# Each entry: (notes, beats, event_label)
SCORE = [
    # === Exposition: subject entries ===
    (['G4','A#4','C5'], 2, 'EXP_subject_alto'),
    (['F4','G4','A#4','C5'], 2, 'EXP_subject_alto'),
    (['D#4','F4','G4','C5'], 2, 'EXP_subject_alto'),
    (['C4','D#4','F4','G4'], 2, 'EXP_subject_alto'),
    (['B3','C4','D#4','F4'], 2, 'EXP_subject_alto'),
    (['G3','B3','D#4'], 2, 'EXP_subject_alto'),
    (['C4','G4'], 2, 'EXP_answer_soprano'),  # Answer enters (soprano)
    (['B3','F4','G4'], 2, 'EXP_answer'),
    (['C4','E4','G4'], 2, 'EXP_answer'),
    (['A3','C4','F4'], 2, 'EXP_answer'),
    (['G3','B3','D4','G4'], 2, 'EXP_answer'),
    (['C4','E4','G4','C5'], 2, 'EXP_answer'),
    (['C3','G3','C4'], 2, 'EXP_bass_subject'),  # Subject in bass
    (['B2','F3','G3','B3'], 2, 'EXP_bass'),
    (['C3','E3','G3','C4'], 2, 'EXP_bass'),
    (['A2','C3','F3','A3'], 2, 'EXP_bass'),
    (['G2','B2','D3','G3'], 2, 'EXP_bass'),
    (['C3','E3','G3','C4'], 2, 'EXP_bass'),

    # === Middle entries: episodes ===
    (['F3','A3','C4','F4'], 2, 'EPISODE'),
    (['E3','G3','C4','E4'], 2, 'EPISODE'),
    (['D3','F3','A3','D4'], 2, 'EPISODE'),
    (['C3','E3','G3','C4'], 2, 'EPISODE'),
    (['F3','A3','C4','F4'], 2, 'EPISODE'),
    (['E3','G3','C4','E4'], 2, 'EPISODE'),
    (['D3','F3','A3','D4'], 2, 'EPISODE'),
    (['G2','B2','D3','G3'], 2, 'EPISODE'),

    # === Stretto: overlapping entries ===
    (['C3','E3','G3','C4'], 2, 'STRETTO'),
    (['G3','B3','D4','G4'], 2, 'STRETTO'),
    (['C4','E4','G4','C5'], 2, 'STRETTO'),
    (['G3','B3','D4','G4'], 2, 'STRETTO'),
    (['C4','E4','G4','C5'], 2, 'STRETTO'),
    (['C3','E3','G3','C4'], 2, 'STRETTO'),
    (['G3','B3','D4','G4'], 2, 'STRETTO'),
    (['C4','E4','G4','C5'], 2, 'STRETTO'),

    # === Final cadence ===
    (['G2','B2','D3','G3'], 4, 'CADENCE_dominant'),
    (['C3','E3','G3','C4'], 6, 'CADENCE_tonic'),
]

if __name__ == '__main__':
    from collections import Counter
    events = Counter(e for _,_,e in SCORE)
    print(f'BWV847 Fugue: {len(SCORE)} entries, {len(events)} event types')
    for ev, cnt in events.most_common():
        print(f'  {ev}: {cnt}')
