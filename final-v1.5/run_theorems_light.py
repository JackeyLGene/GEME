"""Lightweight theorem robustness tests: circ, time, born."""
import sys, os, json, math, subprocess
BASE = 'g:/GEME/standalone'
OUT = 'g:/GEME/docs/robustness_results'
PY = r'C:\Users\Administrator.DESKTOP-EM03IHL\.workbuddy\binaries\python\versions\3.14.3\python.exe'
os.makedirs(OUT, exist_ok=True)
results = {}

# T7: circle quantized levels — 5 seeds
print("=== T7: Circle quantized levels 5 seeds ===")
for s in range(5):
    p = subprocess.run([PY, os.path.join(BASE, 'circle_quantized_levels.py')], capture_output=True, text=True, timeout=120, env={**os.environ, 'PYTHONUTF8': '1'})
    lines = [l for l in p.stdout.strip().split('\n') if l]
    results[f'T7_levels_seed{s}'] = lines[-3:] if len(lines) >= 3 else lines[-1:]
    print(f"  seed {s}: {lines[-1][:100] if lines else '?'}")

# T9: Time dilation via internal gamma
print("\n=== T9: Time dilation 10 seeds ===")
sys.path.insert(0, 'g:/GEME/final-v1.5')
from geme import GEME, _VEC_DIM as _D27
import random as _qr2
from statistics import mean, stdev

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
    total_merges = sum(f.merged for f in g.memory.frames)
    g_val = total_merges / 2000
    t9.append(round(g_val, 3))
results['T9_time_dilation'] = {
    'mean': round(mean(t9), 3), 'std': round(stdev(t9), 3) if len(t9)>1 else 0, 'all': t9
}
print(f"  gamma = {results['T9_time_dilation']['mean']} +/- {results['T9_time_dilation']['std']}")

# T10: Born rule (native quantum_test.py)
print("\n=== T10: Born rule 5 seeds ===")
for s in range(5):
    p = subprocess.run([PY, os.path.join(BASE, 'quantum_test.py')], capture_output=True, text=True, timeout=120)
    lines = [l for l in p.stdout.strip().split('\n') if l]
    results[f'T10_born_seed{s}'] = lines[-3:] if len(lines) >= 3 else lines[-1:]
    print(f"  seed {s}: {lines[-1][:100] if lines else '?'}")

with open(os.path.join(OUT, 'phase5_theorems_light.json'), 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {OUT}/phase5_theorems_light.json")
