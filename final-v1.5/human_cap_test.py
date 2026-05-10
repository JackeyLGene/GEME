"""Human-constrained parameter test: does cap≈7 produce different L4?"""
import sys, math
sys.path.insert(0, '.')
from geme import GEME, _VEC_DIM as _D27
import random as _qr2

for label, cap, wsize in [
    ('human WM=7 ', 7,  20),
    ('human WM=5 ', 5,  15),
    ('small cap 10', 10, 30),
    ('default 32 ', 32, 50),
    ('large cap 64', 64, 80),
]:
    for qseed in [0, 5, 10]:
        g = GEME(memory_cap=cap, cooccur_window=wsize)
        g.memory.preserve_sig = True
        g.memory.quantum_mode = True
        g.memory._merge_dists = [0.3] * 50
        g._induction_threshold = 3.0
        g.memory._qrand = _qr2.Random(qseed)
        tick = 0
        for i in range(2000):
            v = [0.0] * _D27
            v[0] = math.cos(2 * math.pi * i * 0.01)
            v[1] = math.sin(2 * math.pi * i * 0.01)
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
        bridges = len([f for f in g.memory.frames if chr(8212)*2 in (f.sig_full or f.sig)])
        print(f'{label} cap={cap:2d} qseed={qseed:2d}: frames={m["frame_count"]:2d} L4={m["L4_frame_count"]} self={selfs} bridge={bridges} MI={m["I(phi;X)"]:.4f}')
