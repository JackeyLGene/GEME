"""Multi-seed robustness test for GEME core claims."""
import sys, math, random
sys.path.insert(0, 'g:/GEME/final-v1.5')
from geme import GEME, _VEC_DIM as _D27, eq, fn, const, structural_signature

print("=" * 60)
print("Test 1: Self-test smoke across seeds")
print("=" * 60)
for seed in range(10):
    r = random.Random(seed)
    g = GEME(memory_cap=16, cooccur_window=60)
    for _ in range(100):
        a = str(r.randint(0, 9))
        b = str(r.randint(0, 9))
        f = eq(fn('swap', const(a), const(b)), fn('swap', const(b), const(a)))
        g.process_sig(f, structural_signature(f))
    m = g.metrics()
    print(f"  seed={seed:2d}  frames={m['frame_count']:2d}  L4={m['L4_frame_count']}  MI={m['I(phi;X)']:.4f}  eff={m['efficiency']:.3f}")

print()
print("=" * 60)
print("Test 2: L4 emergence across seeds (2000 step sine waves)")
print("=" * 60)
for seed in range(10):
    r = random.Random(seed)
    g = GEME(memory_cap=32)
    g.memory.preserve_sig = True
    g.memory.quantum_mode = True
    g.memory._merge_dists = [0.3] * 50
    g._induction_threshold = 3.0
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
    print(f"  seed={seed:2d}  frames={m['frame_count']:2d}  L4={m['L4_frame_count']}  self={selfs:2d}  MI={m['I(phi;X)']:.4f}  eff={m['efficiency']:.3f}")
