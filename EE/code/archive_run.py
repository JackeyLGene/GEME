"""N We × G gens, persistent ProcessPool — pre-encoded, zero-file IO."""
import sys, os, time, importlib.util, math, multiprocessing, random, json
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import Counter
_code_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _code_dir)
sys.path.insert(0, os.path.join(_code_dir, '..', '..', 'BGM', 'code'))
from data.midi_encoder import midi_encode, NOTES_Hz, FREQ_MIN, FREQ_MAX, BINS
from accumulation import Archive

def note_name(dim):
    freq = FREQ_MIN + dim/(BINS-1)*(FREQ_MAX-FREQ_MIN)
    return min(NOTES_Hz.items(), key=lambda x: abs(x[1]-freq))[0]

def we_worker(args):
    """Worker: receives pre-encoded events. No file IO, no midi_encode."""
    idx, seed, events, archive_entries, gen = args
    t0 = time.time()
    from geruon import Codex
    from we_core import We
    inherited = None
    if archive_entries:
        inherited = Codex.empty(name="arch", vec_dim=27)
        for sym, vec in archive_entries:
            inherited.add(sym, list(vec))
    w = We(n_selves=3, seed=seed)
    w.run_stream(events, inherited)
    t1 = time.time()
    entries = []
    for sym, vec in w.collective_codex._table.items():
        clean = [0.0 if (v != v or v == float('inf') or v == float('-inf')) else v for v in vec]
        entries.append((sym, clean))
    return {'idx': idx, 'gen': gen, 'entries': entries,
            'run_s': round(t1-t0, 1), 'codex': len(entries)}

def main():
    _p = os.path.join(_code_dir, 'data', 'wtc_scores.py')
    _s = importlib.util.spec_from_file_location('wtc', _p)
    _m = importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
    WTC = _m.WTC_SCORES

    N_WE = 16; N_GENS = 3; CYCLES = 2
    N_WORKERS = min(N_WE, os.cpu_count() or 8)
    SEEDS = [42+i*17 for i in range(N_WE)]
    SEG_SIZE = max(1, len(WTC) // (N_WE * 2))

    rng = random.Random(42)

    print(f"Archive: {N_WE} We × {N_GENS} gens, {N_WORKERS} workers")
    print(f"Segment: {SEG_SIZE} pieces each (~{SEG_SIZE*30} MIDI events)")
    print(f"{'='*70}")

    # ── Pre-encode ALL segments in main process (zero IO in workers) ──
    print("Pre-encoding segments...", end=' ', flush=True)
    encoded_segments = []
    for i in range(N_WE):
        start = rng.randint(0, max(0, len(WTC) - SEG_SIZE))
        raw = midi_encode(WTC[start:start + SEG_SIZE], passes=1)
        encoded_segments.append(raw * CYCLES)
    print(f"done ({N_WE} segments).")

    archive = Archive()

    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        for gen in range(N_GENS):
            t0 = time.time()
            archive_entries = [(sym, tuple(vec)) for sym, vec in archive.codex._table.items()]

            # Submit all workers — no file IO
            work_items = []
            for i in range(N_WE):
                work_items.append((i, SEEDS[i], encoded_segments[i],
                                   archive_entries, gen))

            # collect() → returns results to main memory
            results = pool.map(we_worker, work_items)

            for data in results:
                entries = data['entries']
                cx = type('Codex', (), {'_table': {}})()
                cx._table = {sym: vec for sym, vec in entries}
                archive.collect(cx, gen)

            elapsed = time.time() - t0
            codes = sorted(archive.codex._table.items(),
                          key=lambda x: -math.sqrt(sum(v*v for v in x[1])))
            print(f"G{gen}: {elapsed:.0f}s  archive={archive.size()}")
            for sym, vec in codes[:3]:
                active = [(i, round(v,3)) for i, v in enumerate(vec) if abs(v) > 0.02]
                notes = [f"{note_name(d)}={v:.3f}" for d, v in active[:4]]
                print(f"  {sym}: [{', '.join(notes)}]")

    print(f"\n{'='*70}")
    surv = archive.survivals(min_gens=2)
    print(f"Survived >=2 gens: {len(surv)} entries  (of {archive.size()} total)")
    for sym, gens in sorted(surv.items(), key=lambda x: -len(x[1]))[:8]:
        vec = archive.codex._table.get(sym)
        notes = []
        if vec:
            active = [(i, round(v,3)) for i, v in enumerate(vec) if abs(v) > 0.02]
            notes = [f"{note_name(d)}={v:.3f}" for d, v in active[:4]]
        print(f"  {sym}: gens={sorted(gens)} [{', '.join(notes)}]")

    note_counts = Counter()
    for _, vec in archive.codex._table.items():
        for i, v in enumerate(vec):
            if abs(v) > 0.02: note_counts[note_name(i)] += 1
    print(f"\nNote diversity: {len(note_counts)}  Top: {note_counts.most_common(12)}")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
