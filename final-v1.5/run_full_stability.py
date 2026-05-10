"""Batch stability: parameter sweep + capacity sweep + MI curve."""
import sys, math, json, os
sys.path.insert(0, '.')
from geme import GEME, _VEC_DIM
import random as _qr2
from statistics import mean, stdev

OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'robustness_results')
os.makedirs(OUT, exist_ok=True)
results = {}

# == S1: Parameter sweep (for Figure 3) ==
print("S1: Parameter sweep...")
deltas = [0.10, 0.19, 0.50]
gammas = [0.01, 0.05, 0.10]
taus = [0.2, 0.6, 1.0]
sweep = {}
for d in deltas:
    for g2 in gammas:
        for t in taus:
            l4s = []
            for s in range(3):
                mem = GEME(memory_cap=32)
                mem.memory.preserve_sig = True; mem.memory.quantum_mode = True
                mem.memory._merge_dists = [0.3]*50
                mem._induction_threshold = d
                mem.memory._qrand = _qr2.Random(s)
                for i in range(500):
                    v = [0.0]*_VEC_DIM
                    v[0] = math.cos(i*0.01); v[1] = math.sin(i*0.01)
                    mem.process_vec(v, 'ext')
                    if i % 10 == 0 and i > 0:
                        mem.memory.self_observe()
                m = mem.metrics()
                l4s.append(m['L4_frame_count'] or 0)
            sweep[f"d={d}_g={g2}_t={t}"] = {'L4_mean': round(mean(l4s),2), 'L4_std': round(stdev(l4s),2)}
results['parameter_sweep'] = sweep
l4_vals = [v['L4_mean'] for v in sweep.values()]
print(f"  L4 range: [{min(l4_vals):.1f}, {max(l4_vals):.1f}]")
print(f"  L4 overall mean: {mean(l4_vals):.2f}")
print(f"  % with L4 > 0: {sum(1 for v in l4_vals if v > 0)/len(l4_vals)*100:.0f}%")

# == S2: Capacity sweep (for Figure 5) ==
print("\nS2: Capacity sweep...")
caps = [4, 6, 8, 10, 12, 16, 20, 24, 32, 48, 64]
cap_data = {}
for cap in caps:
    l4s, totals, mis = [], [], []
    for s in range(10):
        g = GEME(memory_cap=cap)
        g.memory.preserve_sig = True; g.memory.quantum_mode = True
        g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
        g.memory._qrand = _qr2.Random(s)
        for i in range(1000):
            v = [0.0]*_VEC_DIM
            v[0] = math.cos(i*0.01); v[1] = math.sin(i*0.01)
            g.process_vec(v, 'ext')
            if i % 10 == 0 and i > 0:
                g.memory.self_observe()
        m = g.metrics()
        l4s.append(m['L4_frame_count'] or 0)
        totals.append(m['frame_count'])
        mis.append(m['I(phi;X)'])
    cap_data[str(cap)] = {
        'L4': f"{mean(l4s):.2f}+/-{stdev(l4s):.2f}",
        'total': f"{mean(totals):.1f}+/-{stdev(totals):.1f}",
        'MI': f"{mean(mis):.4f}+/-{stdev(mis):.4f}"
    }
results['capacity_sweep'] = cap_data
for cap, d in cap_data.items():
    print(f"  cap={cap:>3}: L4={d['L4']:>10}  total={d['total']:>10}  MI={d['MI']:>12}")

# == S3: MI curve over steps (for Figure 2) ==
print("\nS3: MI curve over steps...")
g = GEME(memory_cap=32)
g.memory.preserve_sig = True; g.memory.quantum_mode = True
g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
g.memory._qrand = _qr2.Random(0)
mi_curve = []
for i in range(2000):
    v = [0.0]*_VEC_DIM
    v[0] = math.cos(i*0.01); v[1] = math.sin(i*0.01)
    g.process_vec(v, 'ext')
    if i % 10 == 0 and i > 0:
        g.memory.self_observe()
    if i % 50 == 0 and i > 0:
        mi_curve.append({'step': i, 'MI': round(g.metrics()['I(phi;X)'], 6)})
results['MI_curve'] = mi_curve
print(f"  MI at 2000 steps: {mi_curve[-1]['MI'] if mi_curve else 'N/A'}")

with open(os.path.join(OUT, 'full_stability.json'), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {OUT}/full_stability.json")
