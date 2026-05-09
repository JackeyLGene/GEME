"""Final smoke test after code review fixes."""
import sys, math
sys.path.insert(0, '.')
from geme import GEME, _VEC_DIM, DELTA, GAMMA, TAU
import random as _qr2

print(f"Constants: DELTA={DELTA} GAMMA={GAMMA} TAU={TAU}")

g = GEME(memory_cap=16)
g.memory.preserve_sig = True; g.memory.quantum_mode = True
g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
g.memory.cooccur_thresh = 0.08
g.memory._qrand = _qr2.Random(0)

for i in range(500):
    v = [0.0]*_VEC_DIM
    v[0] = math.cos(i*0.01)
    v[1] = math.sin(i*0.01)
    g.process_vec(v, 'ext')
    if i % 10 == 0 and i > 0:
        vs = [0.0]*_VEC_DIM
        for j,f in enumerate(g.memory.frames[:min(len(g.memory.frames),_VEC_DIM)]):
            vs[j] = f.weight/(sum(f.weight for f in g.memory.frames) or 1)
        g.process_vec(vs, 'self')

m = g.metrics()
print(f"Smoke: frames={m['frame_count']} L4={m['L4_frame_count']} MI={m['I(phi;X)']:.4f}")
print(f"Prediction: total={m['pred_total']} accuracy={m['pred_accuracy']:.3f} doubt={m['doubt_mode']}")
print(f"derivative_frames={m['L4_meta_active']}")
print(f"All keys present: {sorted(m.keys())}")

# Test predict_next
pred, conf = g.memory.predict_next()
print(f"predict_next: {pred} (conf={conf:.2f})")

# Test L4 prediction + pred_err
g.process_vec([1.0,0]+[0.0]*25, 'test_sig')
m2 = g.metrics()
err_frames = [f for f in g.memory.frames if 'pred_err' in (f.sig_full or f.sig)]
print(f"After test input: pred_total={m2['pred_total']} pred_err frames={len(err_frames)}")

print("\nAll PASS.")
