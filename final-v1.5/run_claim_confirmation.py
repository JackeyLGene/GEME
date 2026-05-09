"""Confirm v2 paper claims: MI 20 seeds + Q+G≈PA L4 replication."""
import sys, math, json, os
sys.path.insert(0, '.')
from geme import GEME, _VEC_DIM, DELTA, GAMMA, TAU
import random as _qr2
from statistics import mean, stdev

OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'robustness_results')
os.makedirs(OUT, exist_ok=True)

results = {}

# ===== Claim A: MI = 0.032 +/- ? (20 seeds, 2000 steps, full cooccur space) =====
print("Running Claim A: MI over 20 seeds...")
mi_vals = []
for s in range(20):
    g = GEME(memory_cap=32)
    g.memory.preserve_sig = True; g.memory.quantum_mode = True
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    g.memory._qrand = _qr2.Random(s)
    for i in range(2000):
        t = i * 0.01
        v = [0.0]*_VEC_DIM
        v[0] = math.cos(2*math.pi*t); v[1] = math.sin(2*math.pi*t)
        g.process_vec(v, 'ext')
        if i % 10 == 0 and i > 0:
            vs = [0.0]*_VEC_DIM
            for j,f in enumerate(g.memory.frames[:min(len(g.memory.frames),_VEC_DIM)]):
                vs[j] = f.weight/(sum(f.weight for f in g.memory.frames) or 1)
            g.process_vec(vs, 'self')
    m = g.metrics()
    mi_vals.append(m['I(phi;X)'])
    if s % 5 == 4:
        print(f"  {s+1}/20 done, MI so far: {mean(mi_vals):.6f}")

results['MI_20seeds'] = {
    'mean': round(mean(mi_vals), 6),
    'std': round(stdev(mi_vals), 6),
    'all': [round(x, 6) for x in mi_vals]
}
print(f"  MI = {results['MI_20seeds']['mean']} +/- {results['MI_20seeds']['std']}")

# ===== Claim B: Q+G≈PA L4 prediction (10 seeds) =====
print("\nRunning Claim B: Q+G≈PA L4 prediction...")
Q = [
    ('inject',[0,0,1,0,0,0,1,0,0]),
    ('zero',  [0,0,0,1,0,0,1,0,0]),
    ('add_z', [1,0,0,0,1,0,0,0,0]),
    ('add_s', [0,1,0,0,1,0,0,0,0]),
    ('mul_z', [1,0,0,0,0,1,0,0,0]),
    ('mul_s', [0,1,0,0,0,1,0,0,0]),
    ('succ',  [0,0,0,0,0,0,1,0,0]),
]
G_SENT = ('G', [0,0,0,1,0,0,0,0,1])
IND = ('induct', [0,0,0,0,0,0,0,1,0])

def run_qg(label, axioms):
    l4s, preds, accs = [], [], []
    for s in range(10):
        g = GEME(memory_cap=16); g.memory.preserve_sig=True; g.memory.quantum_mode=True
        g.memory._merge_dists=[0.3]*30; g._induction_threshold=3.0; g.memory.cooccur_thresh=0.12
        g.memory._qrand = _qr2.Random(s)
        for _ in range(100):
            for name, vec in axioms:
                vv=[0.0]*27; vv[:len(vec)]=vec
                g.process_vec(vv, name[:5])
            vs=[0.0]*27
            for j,f in enumerate(g.memory.frames[:min(len(g.memory.frames),27)]):
                vs[j]=f.weight/(sum(f.weight for f in g.memory.frames) or 1)
            g.process_vec(vs,'self')
        m=g.metrics()
        l4s.append(m['L4_frame_count']); preds.append(m['pred_total']); accs.append(m['pred_accuracy'])
    return f"L4={mean(l4s):.1f}  preds={mean(preds):.0f}  acc={mean(accs):.3f}"

for label, axioms in [('Q', Q), ('Q+G', Q+[G_SENT]), ('PA', Q+[IND])]:
    r = run_qg(label, axioms)
    results[f'QGP_{label}'] = r
    print(f"  {label}: {r}")

# Save
with open(os.path.join(OUT, 'claim_confirmation.json'), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {OUT}/claim_confirmation.json")
