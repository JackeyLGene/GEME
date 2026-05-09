"""Test L4 prediction + L5 accuracy + L6 doubt."""
import sys
sys.path.insert(0, '.')
from geme import GEME, _VEC_DIM as _D27
import random as _qr2

# ============ Test A: Predictable sequence ============
print("=== Test A: Predictable sequence (cat→on→mat) ===")
g = GEME(memory_cap=16); g.memory.preserve_sig=True; g.memory.quantum_mode=True
g.memory._merge_dists=[0.3]*50; g._induction_threshold=3.0; g.memory.cooccur_thresh=0.08
g.memory._qrand = _qr2.Random(0)

for _ in range(20):
    g.process_vec([1.0,0,0]+[0.0]*24, 'cat')
    g.process_vec([0.0,1.0,0]+[0.0]*24, 'on')
    g.process_vec([0.0,0.0,1.0]+[0.0]*24, 'mat')

m = g.metrics()
print(f"frames={m['frame_count']} L4={m['L4_frame_count']} MI={m['I(phi;X)']:.4f}")
print(f"predictions: total={m['pred_total']} accuracy={m['pred_accuracy']:.3f} doubt={m['doubt_mode']}")

# ============ Test B: Anomaly injection ============
print("\n=== Test B: Anomaly (cat→on→mat→under) ===")
g2 = GEME(memory_cap=16); g2.memory.preserve_sig=True; g2.memory.quantum_mode=True
g2.memory._merge_dists=[0.3]*50; g2._induction_threshold=3.0; g2.memory.cooccur_thresh=0.08
g2.memory._qrand = _qr2.Random(0)

for _ in range(15):
    g2.process_vec([1.0,0,0]+[0.0]*24, 'cat')
    g2.process_vec([0.0,1.0,0]+[0.0]*24, 'on')
    g2.process_vec([0.0,0.0,1.0]+[0.0]*24, 'mat')
# Now inject anomaly
g2.process_vec([1.0,0,0]+[0.0]*24, 'cat')
g2.process_vec([0.0,1.0,0]+[0.0]*24, 'on')
g2.process_vec([0.0,0.0,0.0]+[1.0]+[0.0]*23, 'under')

m = g2.metrics()
print(f"frames={m['frame_count']} L4={m['L4_frame_count']} MI={m['I(phi;X)']:.4f}")
print(f"predictions: total={m['pred_total']} accuracy={m['pred_accuracy']:.3f} doubt={m['doubt_mode']}")
err_frames = [f for f in g2.memory.frames if 'pred_err' in (f.sig_full or f.sig)]
doubt_frames = [f for f in g2.memory.frames if 'sys_doubt' in (f.sig_full or f.sig)]
print(f"error frames: {len(err_frames)} doubt frames: {len(doubt_frames)}")
for f in err_frames:
    print(f"  pred_err: {(f.sig_full or f.sig)[:25]} w={int(f.weight)}")
for f in doubt_frames:
    print(f"  sys_doubt: {(f.sig_full or f.sig)[:25]} w={int(f.weight)}")
