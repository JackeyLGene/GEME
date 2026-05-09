"""T9 T10 正确预设重跑"""
import sys, os, json, math
sys.path.insert(0, 'g:/GEME/final-v1.5')
from geme import GEME, _VEC_DIM as _D27
import random as _qr2
from statistics import mean, stdev
OUT = 'g:/GEME/docs/robustness_results'
os.makedirs(OUT, exist_ok=True)
results = {}

# T9: Time dilation — count circ frames
print("=== T9: Time dilation 10 seeds (correct metric) ===")
t9 = []
for s in range(10):
    g = GEME(memory_cap=32); g.memory.preserve_sig=True; g.memory.quantum_mode=True
    g.memory._merge_dists=[0.3]*50; g._induction_threshold=3.0; g.memory._qrand=_qr2.Random(s)
    for i in range(2000):
        t=i*0.01; v=[0.0]*_D27; v[0]=math.cos(2*math.pi*t); v[1]=math.sin(2*math.pi*t)
        g.process_vec(v,'ext')
        if i%10==0 and i>0:
            vs=[0.0]*_D27
            for j,f in enumerate(g.memory.frames[:min(len(g.memory.frames),_D27)]):
                vs[j]=f.weight/(sum(f.weight for f in g.memory.frames) or 1)
            g.process_vec(vs,'self')
    circ = [f for f in g.memory.frames if 'ext' in (f.sig or f.sig_full or '')]
    avg_angle = 2000*0.01  # total angle traversed
    n_unique = len(set(f.fid for f in circ))
    # gamma = total_angle / (unique_frames * step_per_frame)
    # More unique frames = better time resolution = less dilation
    gamma = avg_angle / max(n_unique, 1) * 2 * math.pi if n_unique > 0 else 0
    t9.append(round(gamma, 3))
    if s == 0:
        print(f"  unique ext frames: {n_unique}, gamma≈{gamma:.3f}")
results['T9_time_dilation'] = {
    'mean': round(mean(t9), 3), 'std': round(stdev(t9), 3) if len(t9)>1 else 0, 'all': t9
}
print(f"  gamma = {results['T9_time_dilation']['mean']} +/- {results['T9_time_dilation']['std']}")

# T10: Born rule — correct preset
print("\n=== T10: Born rule 10 seeds (correct preset) ===")
t10 = []
_V27 = 27
for s in range(10):
    g = GEME(memory_cap=5); g.memory.quantum_mode=True; g.memory.preserve_sig=True
    th = 0.8
    g.memory._merge_thresh_val = th
    g.memory._merge_dists = [th]*50
    g.memory._qrand = _qr2.Random(s)
    # Two far-apart prototypes
    v1=[0.0]*_V27; v1[0]=1.0
    v2=[0.0]*_V27; v2[10]=1.0
    g.process_vec(v1, 'a', 'prototype_a')
    g.process_vec(v2, 'b', 'prototype_b')
    # Mid-point vector: equal distances
    v_in=[0.0]*_V27; v_in[0]=0.5; v_in[10]=0.5
    da=math.sqrt(sum((v_in[j]-v1[j])**2 for j in range(_V27)))
    db=math.sqrt(sum((v_in[j]-v2[j])**2 for j in range(_V27)))
    # Quantum merge test
    count_a, count_b, total = 0, 0, 0
    for _ in range(3700):
        g.process_vec(v_in, 'in')
        total += 1
    # Count frames' weights to infer merge distribution
    for f in g.memory.frames:
        sig_short = (f.sig_full or f.sig)[:5]
        if 'a' in sig_short: count_a += int(f.weight)
        elif 'b' in sig_short: count_b += int(f.weight)
    rate_a = count_a / max(count_a+count_b, 1) if (count_a+count_b) > 0 else 0.5
    t10.append(round(rate_a, 4))
    if s == 0:
        print(f"  da={da:.3f} db={db:.3f} th={th} → rate_a={rate_a:.4f}")
results['T10_born_rule'] = {
    'mean': round(mean(t10), 4), 'std': round(stdev(t10), 4) if len(t10)>1 else 0, 'all': t10
}
print(f"  p(merge_A) = {results['T10_born_rule']['mean']} +/- {results['T10_born_rule']['std']}")
print(f"  预期 ≈ 0.500 (Born 50/50)")

with open(os.path.join(OUT, 'phase5_theorems_fixed.json'), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {OUT}/phase5_theorems_fixed.json")
