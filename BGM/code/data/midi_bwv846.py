"""BWV 846 — MIDI-encoded: note_on/note_off with sustain overlap."""
NOTES_Hz = {
    'C3':130.81,'C#3':138.59,'D3':146.83,'D#3':155.56,'E3':164.81,'F3':174.61,
    'F#3':185.00,'G3':196.00,'G#3':207.65,'A3':220.00,'A#3':233.08,'B3':246.94,
    'C4':261.63,'C#4':277.18,'D4':293.66,'D#4':311.13,'E4':329.63,'F4':349.23,
    'F#4':369.99,'G4':392.00,'G#4':415.30,'A4':440.00,'A#4':466.16,'B4':493.88,
    'C5':523.25,'D5':587.33,'E5':659.25,'F5':698.46,'G5':783.99,'A5':880.00,'B5':987.77,
}
FREQ_MIN, FREQ_MAX, BINS = 65, 1050, 27
DECAY = 0.85  # per-step sustain decay (note lingers after note_off)

def vec_for_active(active):
    """Sum Hz bins of currently-sounding notes, normalized."""
    v = [0.0]*BINS
    for n in active:
        f = NOTES_Hz.get(n, 440)
        idx = int((f-FREQ_MIN)/(FREQ_MAX-FREQ_MIN)*(BINS-1))
        v[max(0,min(BINS-1,idx))] += 1.0
    s = sum(v)
    return [x/s for x in v] if s > 0 else v

# BWV 846 Prelude as MIDI event stream
# Each chord is broken into note_on events + duration.
# Events: (type, notes, beats_to_next)
# After each event, notes decay but overlap.
EVENTS = [
    ('on', ['C4','E4','G4'], 8),
    ('on', ['C4','E4','A4'], 8),  # suspension
    ('on', ['C4','F4','A4'], 8),  # F
    ('on', ['B3','D4','F4','G4'], 8),  # G7
    ('on', ['C4','E4','G4','C5'], 4),  # C
    ('on', ['C4','E4','A4','C5'], 4),  # Am
    ('on', ['C4','F4','A4','C5'], 4),  # F
    ('on', ['B3','D4','F4','G4','B4'], 4),  # G7
    ('on', ['C4','E4','G4','C5'], 4),  # C
    ('on', ['D4','F#4','A4','C5'], 4),  # D7
    ('on', ['G3','B3','D4','G4'], 4),  # G
    ('on', ['C4','E4','G4','C5'], 4),  # C
    ('on', ['F3','A3','C4','F4'], 4),  # F
    ('on', ['B3','D4','F4','G4'], 4),  # G7
    ('on', ['C4','E4','G4','C5'], 4),  # C
    ('on', ['A3','C4','E4','A4'], 4),  # Am
    ('on', ['D4','F#4','A4','C5'], 4),  # D7
    ('on', ['G3','B3','D4','G4'], 4),  # G
    ('on', ['C4','E4','G4','C5'], 4),  # C
    ('on', ['F3','A3','C4','F4'], 4),  # F
    ('on', ['F#3','A3','C4','D4','F4'], 8),  # Dm7 (suspeded)
    ('on', ['G3','B3','D4','G4'], 8),  # G
    ('on', ['C4','E4','G4','C5'], 8),  # C
    ('off', [], 0),  # silence
]

def generate_sequence(passes=1):
    """Generate a sequence of (vec, label) pairs simulating MIDI playback."""
    sequence = []
    for _ in range(passes):
        active_notes = set()
        carry_over = {}  # note → remaining steps
    
        for evt_type, notes, duration in EVENTS:
            if evt_type == 'on':
                for n in notes:
                    active_notes.add(n)
                    carry_over[n] = duration  # will decay after event

            # Step through the duration
            for step in range(duration):
                # Apply decay to all active notes
                to_remove = []
                for n in list(carry_over.keys()):
                    carry_over[n] -= 1
                    if carry_over[n] <= 0:
                        active_notes.discard(n)
                        to_remove.append(n)
                for n in to_remove:
                    del carry_over[n]
                
                vec = vec_for_active(active_notes)
                sequence.append((vec, f'{len(active_notes)}_active'))
        
        # Final decay
        for _ in range(4):  # ring out
            active_notes = set()
            carry_over = {}
            sequence.append((vec_for_active(set()), 'silence'))
    
    return sequence

if __name__ == '__main__':
    seq = generate_sequence()
    active_counts = [label for _, label in seq]
    from collections import Counter
    print(f'BWV846 MIDI: {len(seq)} steps')
    print(f'Active notes: {dict(Counter(active_counts))}')
