# Quick robustness: 10 seeds each experiment
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM

def test_time_dilation(seed):
    r = random.Random(seed)
    g = GEME(memory_cap=32, cooccur_window=50, cooccur_thresh=0.08, max_chains=10)
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.5]*50; g._induction_threshold = 2.0
    
    t = 0.0; pos_data = {}
    for _ in range(2000):
        t += 0.01
        for x in range(0, 100, 5):
            dens = 5.0 / (1 + x * 0.1)
            num = max(1, int(dens * r.random() * 2))
            for _ in range(num):
                v = [0.0]*_VEC_DIM; v[x % 27] = dens/(dens+1)
                g.process_vec(v, f"x{x}")
    for f in g.memory.frames:
        s = f.sig_full or f.sig
        for p in range(0, 100, 5):
            if f"x{p}" in s and f.weight > 5:
                if p not in pos_data: pos_data[p] = 0
                pos_data[p] += f.weight
    high = [pos_data[p] for p in pos_data if p < 20]
    low = [pos_data[p] for p in pos_data if p > 60]
    if high and low:
        return statistics.mean(high) / max(statistics.mean(low), 1)
    return 0.0

def test_quantum_split(seed):
    v1=[0.0]*_VEC_DIM; v1[0]=1.0
    v2=[0.0]*_VEC_DIM; v2[10]=1.0
    v_in=[0.0]*_VEC_DIM; v_in[0]=0.5; v_in[10]=0.5
    
    # Zeno merge version
    import types
    g=GEME(memory_cap=5); g.memory.quantum_mode=True; g.memory.preserve_sig=True
    g.memory._merge_thresh_val=0.8; g.memory._merge_dists=[0.8]*50
    
    def z_process_vec(self,vec,sig,src=""):
        th=self.memory._adaptive_thresh()
        self.memory._merge_thresh_val=th or 0
        cand=[]; bi,bd=-1,float('inf')
        for i,f in enumerate(self.memory.frames):
            d=math.sqrt(sum((vec[j]-f.vec[j])**2 for j in range(_VEC_DIM)))
            if d<bd: bd=d; bi=i
            if hasattr(self.memory,'quantum_mode') and self.memory.quantum_mode and th:
                if d<=th: cand.append((i,d,f))
        if th is None and bi>=0 and bd!=float('inf'):
            self.memory._learn_dists.append(bd)
        if hasattr(self.memory,'quantum_mode') and self.memory.quantum_mode and cand:
            if not hasattr(self.memory,'_qrand'):
                self.memory._qrand = random.Random(seed*999+1)
            ps=0; pr=[]
            for i,d,f in cand:
                p=math.exp(-d/max(th,0.001)); pr.append((i,d,f,p)); ps+=p
            if ps>0:
                r=self.memory._qrand.random()*ps; ac=0
                for i,d,f,p in pr:
                    ac+=p
                    if r<=ac: bi=i; bd=d; break
                f=self.memory.frames[bi]; self.memory.total_weight-=f.weight
                f.weight+=1; f.merged+=1; self.memory.total_weight+=f.weight
                self.memory._step_counter+=1
                self.memory._window.append((sig,self.memory._step_counter,tuple(vec)))
                return
        self.frame_count+=1; self._input_count+=1
        self.memory.observe(vec,sig,src)
    
    g.process_vec = types.MethodType(z_process_vec, g)
    g.process_vec(v1,'a'); g.process_vec(v2,'b')
    for _ in range(500): g.process_vec(v_in,'test')
    ca=cb=0
    for f in g.memory.frames:
        s=f.sig_full or f.sig
        if 'a' in s: ca=int(f.weight)-1
        if 'b' in s: cb=int(f.weight)-1
    return ca, cb

# Time dilation: 10 seeds
print("="*55)
print("稳健性测试")
print("="*55)
print()
print("1. 时间膨胀（10个随机种子）：")
dl_results = []
for s in range(42, 52):
    r = test_time_dilation(s)
    dl_results.append(r)
    print(f"   seed {s}: 帧生成率比 = {r:.3f}")
mean_r = statistics.mean(dl_results)
std_r = statistics.stdev(dl_results) if len(dl_results) > 1 else 0
print(f"  平均: {mean_r:.3f} ± {std_r:.3f}")
print(f"  {'✓ 稳定' if std_r/mean_r < 0.3 else '✗ 不稳定'}")

# Quantum split: 10 seeds
print(f"\n2. 量子Zeno分裂（10个种子，每500次合并）：")
split_results = []
for s in range(100, 110):
    ca, cb = test_quantum_split(s)
    total = ca + cb
    pct = ca / max(total, 1) * 100
    split_results.append(pct)
    print(f"   seed {s}: a={ca} b={cb} ({pct:.1f}%→a)")
mean_p = statistics.mean(split_results)
std_p = statistics.stdev(split_results) if len(split_results) > 1 else 0
print(f"  平均a%: {mean_p:.2f}% ± {std_p:.2f}%")
if 40 < mean_p < 60:
    print(f"  ✓ 50/50分裂确认（与理论一致）")
else:
    print(f"  ✗ 偏差")

print(f"\n{'='*55}")
print(f"结论：")
print(f"  时间膨胀: {'通过' if std_r/mean_r < 0.3 else '需复查'}")
print(f"  量子分裂: {'通过' if 40 < mean_p < 60 else '需复查'}")
print(f"  稳定性因子: {std_r/mean_r:.2f} (越小越稳定)")
