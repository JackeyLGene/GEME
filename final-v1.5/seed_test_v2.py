"""Multi-seed test: vary quantum merge seed to see L4 distribution."""
import sys, math
sys.path.insert(0, 'g:/GEME/final-v1.5')
from geme import GEME, _VEC_DIM as _D27
import random as _qr

print("L4 vs quantum merge seed (fixed input, varying internal qrand)")
print(f"{'qseed':>6} {'frames':>6} {'L4':>4} {'self':>4} {'MI':>8} {'eff':>6}")
print("-" * 45)

results = []
for qseed in range(20):
    # Override the qrand before GEME init
    _qr.seed = lambda s: None  # no-op (we'll patch directly)
    g = GEME(memory_cap=32)
    g.memory.preserve_sig = True
    g.memory.quantum_mode = True
    g.memory._merge_dists = [0.3] * 50
    g._induction_threshold = 3.0
    # Directly set the qrand seed
    import random as _qr2
    g.memory._qrand = _qr2.Random(qseed)
    
    tick = 0
    for i in range(2000):
        t = i * 0.01
        v = [0.0] * _D27
        v[0] = math.cos(2 * math.pi * t)
        v[1] = math.sin(2 * math.pi * t)
        g.process_vec(v, 'ext')
        tick += 1
        if tick >= 10:
            vs = [0.0] * _D27
            for j, f in enumerate(g.memory.frames[:min(len(g.memory.frames), _D27)]):
                vs[j] = f.weight / (sum(f.weight for f in g.memory.frames) or 1)
            g.process_vec(vs, 'self')
            tick = 0
    
    m = g.metrics()
    selfs = len([f for f in g.memory.frames if 'self' in (f.sig or f.sig_full or '')])
    results.append((qseed, m['frame_count'], m['L4_frame_count'], selfs, m['I(phi;X)'], m['efficiency']))
    print(f"{qseed:6d} {m['frame_count']:6d} {m['L4_frame_count']:4d} {selfs:4d} {m['I(phi;X)']:8.4f} {m['efficiency']:6.3f}")

print()
l4s = [r[2] for r in results]
print(f"L4 summary: min={min(l4s)} max={max(l4s)} mean={sum(l4s)/len(l4s):.1f} median={sorted(l4s)[len(l4s)//2]}")
print(f"MI: all {'≤ 0.01' if all(r[4]<=0.01 for r in results) else '> 0.01 in some seeds!'}")
