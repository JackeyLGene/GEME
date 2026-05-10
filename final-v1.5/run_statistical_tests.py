"""Statistical tests for all core claims: p-values, CIs, effect sizes."""
import sys, math, json, os
sys.path.insert(0, '.')
from geme import GEME, _VEC_DIM
import random as _qr2
from statistics import mean, stdev

OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'robustness_results')
os.makedirs(OUT, exist_ok=True)

# == Test 1: MI is significantly near-zero (one-sample t-test against 0) ==
print("Test 1: MI vs baseline 0")
def t_one_sample(data, mu=0):
    n = len(data)
    m = mean(data); s = stdev(data)
    t_stat = (m - mu) / (s / math.sqrt(n))
    # Approximate df=n-1, using normal approximation for large n
    return {'mean': round(m,6), 'std': round(s,6), 't': round(t_stat,3), 'n': n}

# Use existing 20-seed data
data_20_path = os.path.join(OUT, 'claim_confirmation.json')
if os.path.exists(data_20_path):
    with open(data_20_path) as f:
        d20 = json.load(f)
    mi_data = d20['MI_20seeds']['all']
else:
    mi_data = []  # fallback

if mi_data:
    r = t_one_sample(mi_data, 0)
    print(f"  H0: MI = 0, H1: MI > 0")
    print(f"  Mean = {r['mean']}, t({r['n']-1}) = {r['t']}")
    # p-value approximation from normal
    import math
    p = math.exp(-0.717 * abs(r['t']) - 0.416 * abs(r['t'])**2)  # approximation
    print(f"  p < {p:.2e} (approximate)")
    print(f"  Significant: {'YES - MI is structurally > 0' if r['t'] > 2 else 'NO'}")
    # CI
    ci = 1.96 * r['std'] / math.sqrt(r['n'])
    print(f"  95% CI: [{r['mean']-ci:.6f}, {r['mean']+ci:.6f}]")

# == Test 2: Q vs Q+G vs PA (paired t-tests) ==
print("\nTest 2: Q+G vs PA equivalence (n=10)")
# Run fresh Q+G vs PA comparison with per-seed data
Q = [('inject',[0,0,1,0,0,0,1,0,0]),('zero',[0,0,0,1,0,0,1,0,0]),
     ('add_z',[1,0,0,0,1,0,0,0,0]),('add_s',[0,1,0,0,1,0,0,0,0]),
     ('mul_z',[1,0,0,0,0,1,0,0,0]),('mul_s',[0,1,0,0,0,1,0,0,0]),
     ('succ',[0,0,0,0,0,0,1,0,0])]
G_SENT = ('G',[0,0,0,1,0,0,0,0,1])
IND = ('induct',[0,0,0,0,0,0,0,1,0])

def run_triplet(s):
    result = {}
    for label, axioms in [('Q', Q), ('Q+G', Q+[G_SENT]), ('PA', Q+[IND])]:
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
        l4 = m.get('L4_frame_count', 0) or 0
        preds = m.get('pred_total', 0)
        acc = m.get('pred_accuracy', 0.0) or 0.0
        result[label] = {'L4': l4, 'preds': preds, 'acc': acc}
    return result

all_data = {'Q':{'L4':[],'preds':[],'acc':[]}, 'Q+G':{'L4':[],'preds':[],'acc':[]}, 'PA':{'L4':[],'preds':[],'acc':[]}}
for s in range(10):
    r = run_triplet(s)
    for label in ['Q','Q+G','PA']:
        all_data[label]['L4'].append(r[label]['L4'])
        all_data[label]['preds'].append(r[label]['preds'])
        all_data[label]['acc'].append(r[label]['acc'])

for k in ['L4','preds','acc']:
    q = all_data['Q'][k]; qg = all_data['Q+G'][k]; pa = all_data['PA'][k]
    print(f"  {k}: Q={mean(q):.3f} Q+G={mean(qg):.3f} PA={mean(pa):.3f}")
    print(f"    Q std={stdev(q):.4f} Q+G std={stdev(qg):.4f} PA std={stdev(pa):.4f}")
    # Difference Q+G vs PA
    diff = [qg[i]-pa[i] for i in range(10)]
    print(f"    Q+G - PA diff: mean={mean(diff):.4f} std={stdev(diff):.4f}")
    if max(diff)==0 and min(diff)==0:
        print(f"    Q+G == PA exactly (all diffs = 0)")
    else:
        d_stat = (mean(diff) - 0) / max(stdev(diff), 1e-10) * math.sqrt(10)
        print(f"    Paired t: t(9)={d_stat:.3f}")

# Save
results = {'MI_20seeds_t_test': {'n':len(mi_data), 'mean':round(mean(mi_data),6), 'std':round(stdev(mi_data),6),
    '95CI':[round(mean(mi_data)-1.96*stdev(mi_data)/math.sqrt(len(mi_data)),6),
            round(mean(mi_data)+1.96*stdev(mi_data)/math.sqrt(len(mi_data)),6)]},
    'Q_vs_PA': {'Q_mean_preds': mean(all_data['Q']['preds']), 'QG_mean_preds': mean(all_data['Q+G']['preds']),
    'PA_mean_preds': mean(all_data['PA']['preds']), 'Q_std_preds': stdev(all_data['Q']['preds']),
    'QG_std_preds': stdev(all_data['Q+G']['preds']), 'PA_std_preds': stdev(all_data['PA']['preds'])}}

with open(os.path.join(OUT, 'statistical_tests.json'), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {OUT}/statistical_tests.json")
