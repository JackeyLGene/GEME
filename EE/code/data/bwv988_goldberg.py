"""
Goldberg Variations BWV 988 — stylized structural score.

Encodes the essential musical architecture:
- Aria (opening frame)
- 30 variations, every 3rd is a canon with increasing interval (1-9)
- Aria da capo (closing frame)

Each variation captures: voice count, rhythmic density, canon interval,
harmonic tension, and position in the overall recursive structure.

Format: list of (notes, beats) compatible with midi_encoder.py
"""
import sys, os, math, random as _rnd

# ── Note palette ──
# Voice ranges: bass (C2-B2), tenor (C3-B3), alto (C4-B4), soprano (C5-B5)
BASS   = ['C2','D2','E2','F2','G2','A2','B2']
TENOR  = ['C3','D3','E3','F3','G3','A3','B3']
ALTO   = ['C4','D4','E4','F4','G4','A4','B4']
SOPRANO = ['C5','D5','E5','F5','G5','A5','B5']

# Canon intervals (which voices to combine)
CANON_INTERVALS = {3:1,6:2,9:3,12:4,15:5,18:6,21:7,24:8,27:9}

def goldberg_score(rng_seed=42):
    """Generate full Goldberg Variations as (notes, beats) score."""
    r = _rnd.Random(rng_seed)
    score = []

    # ── Opening Aria ──
    score += _aria(r, 'open')

    # ── 30 variations ──
    for v in range(1, 31):
        ci = CANON_INTERVALS.get(v, 0)
        score += _variation(r, v, ci)

    # ── Closing Aria ──
    score += _aria(r, 'close')

    return score


def _aria(r, which):
    """Aria — the recursive frame. 32 bars of sarabande rhythm."""
    events = []
    bass = BASS
    alto = ALTO
    sop = SOPRANO

    motif = [
        (4, 3), (2, 1), (4, 2), (2, 2),  # bar 1-2
        (4, 2), (3, 2), (2, 2), (3, 2),  # bar 3-4
        (5, 2), (4, 1), (3, 1), (2, 4),  # bar 5-6
        (4, 2), (3, 2), (5, 2), (2, 2),  # bar 7-8
    ]

    for rep in range(2):  # Aria has two repeats
        for note_idx, beats in motif:
            # 3-voice texture
            b = r.choice(bass)
            a = r.choice(alto)
            s = r.choice(sop)
            events.append(((b, a, s), beats))

    if which == 'close':
        # Da capo: return to opening material but resolved
        events.append(((sop[0], alto[0], bass[0]), 4))  # final chord

    return events


def _variation(r, var_num, canon_interval):
    """Generate one variation with structural character based on position."""
    events = []
    n_bars = 16 if var_num <= 15 else 32  # later variations are longer

    # Voice count increases with variation number
    if var_num <= 10:
        voices = 2
        palette = [ALTO, SOPRANO]
    elif var_num <= 20:
        voices = 3
        palette = [TENOR, ALTO, SOPRANO]
    else:
        voices = 4
        palette = [BASS, TENOR, ALTO, SOPRANO]

    # Rhythmic density: more notes per bar in later variations
    base_beats = 2 if var_num <= 10 else (1 if var_num <= 20 else 0.5)
    events_per_bar = 4 if var_num <= 10 else (6 if var_num <= 25 else 8)

    is_canon = canon_interval > 0

    for bar in range(n_bars):
        for _ in range(events_per_bar):
            notes = []

            if is_canon:
                # Canon: voice 1 leads, voice 2 follows at interval
                lead = r.choice(palette[min(len(palette)-1, 1)])
                follow_palette = palette[0]  # lower voice for canon
                follow_idx = (ALTO.index(lead) if lead in ALTO
                              else SOPRANO.index(lead) if lead in SOPRANO
                              else 0)
                follow_note = (follow_palette[
                    min(len(follow_palette)-1,
                        max(0, follow_idx - canon_interval))])
                notes = [lead, follow_note]
                # Add bass for 3+ voice canons
                if voices >= 3:
                    notes.append(r.choice(BASS))
            else:
                # Free variation: pick from available palettes
                for v in range(voices):
                    p = palette[min(v, len(palette)-1)]
                    notes.append(r.choice(p))

            # Rhythmic variation
            beat = max(0.25, base_beats * r.uniform(0.5, 1.5))
            events.append((tuple(notes[:4]), int(beat)))

    # Every 3rd variation has a structural cadence at the end
    if var_num % 3 == 0:
        # Cadence: longer sustained chord
        cadence_notes = tuple(r.choice(p) for p in palette[:voices])
        events.append((cadence_notes, 4))

    return events
