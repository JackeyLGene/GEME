# Super quick robustness: 5 seeds, minimal iterations
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM

def time_dilation(seed):
    r = random.Random(seed)
    g = GEME(memory_cap=16, cooccur_window=40, cooccur_thresh=0.08, max_chains=5)
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.5]*50; g._induction_threshold = 2.0
    t = 0.0
    for _ in range(500):
        t += 0.01
        for x in range(0, 100, 10):
            dens = 5.0 / (1 + x * 0.1)
            num = max(1, int(dens * r.random() * 2))
            for _ in range(num):
                v = [0.0]*_VEC_DIM; v[x % _VEC_DIM] = dens/(dens+1)
                g.process_vec(v, f"x{x}")
    pd = {}
    for f in g.memory.frames:
        s = f.sig_full or f.sig
        for p in range(0, 100, 10):
            if f"x{p}" in s and f.weight > 3:
                pd[p] = pd.get(p, 0) + f.weight
    hi = [pd[p] for p in pd if p < 20 and pd[p] > 0]
    lo = [pd[p] for p in pd if p > 60 and pd[p] > 0]
    return statistics.mean(hi)/max(statistics.mean(lo),1) if hi and lo else 0

def quantum_split(seed):
    v1=[0.0]*_VEC_DIM; v1[0]=1.0
    v2=[0.0]*_VEC_DIM; v2[10]=1.0
    v_in=[0.0]*_VEC_DIM; v_in[0]=0.5; v_in[10]=0.5
    g=GEME(memory_cap=5); g.memory.quantum_mode=True; g.memory.preserve_sig=True
    g.memory._merge_thresh_val=0.8; g.memory._merge_dists=[0.8]*50
    import types
    def zp(self,v,s,src=""):
        import math as _m; import random as _qr
        t=self.memory._adaptive_thresh(); self.memory._merge_thresh_val=t or 0
        c=[]; bi,bd=-1,float('inf')
        for i,f in enumerate(self.memory.frames):
            d=_m.sqrt(sum((v[j]-f.vec[j])**2 for j in range(_VEC_DIM)))
            if d<bd: bd=d; bi=i
            if hasattr(self.memory,'quantum_mode') and self.memory.quantum_mode and t and d<=t:
                c.append((i,d,f))
        if t is None and bi>=0 and bd!=float('inf'):
            self.memory._learn_dists.append(bd)
        if self.memory.quantum_mode and c:
            if not hasattr(self.memory,'_qr'): self.memory._qr=_qr.Random(seed)
            ps=0; pr=[]
            for i,d,f in c:
                p=_m.exp(-d/max(t,0.001)); pr.append((i,d,f,p)); ps+=p
            if ps>0:
                r=self.memory._qr.random()*ps; ac=0; si=None
                for i,d,f,p in pr:
                    ac+=p
                    if r<=ac: si=i; break
                if si is not None:
                    f=self.memory.frames[si]; self.memory.total_weight-=f.weight
                    f.weight+=1; f.merged+=1; self.memory.total_weight+=f.weight
                    self.memory._step_counter+=1
                    self.memory._window.append((s,self.memory._step_counter,tuple(v)))
                    return
        self.frame_count+=1; self._input_count+=1
        self.memory.observe(v,s,src)
    g.process_vec = types.MethodType(zp, g)
    g.process_vec(v1,'a'); g.process_vec(v2,'b')
    for _ in range(500): g.process_vec(v_in,'t')
    ca=cb=0
    for f in g.memory.frames:
        s=f.sig_full or f.sig
        if 'a' in s: ca=int(f.weight)-1
        if 'b' in s: cb=int(f.weight)-1
    return ca, cb

print("时间膨胀（5种子）：")
dr=[]
for s in range(50,55):
    r=time_dilation(s); dr.append(r)
    print(f"  seed {s}: {r:.2f}")
if dr: print(f"  均值: {statistics.mean(dr):.2f} ± {statistics.stdev(dr):.3f}")

print("\n量子分裂（5种子）：")
sr=[]
for s in range(200,205):
    ca,cb=quantum_split(s); t=ca+cb
    p=ca/t*100 if t else 0; sr.append(p)
    print(f"  seed {s}: a={ca} b={cb} ({p:.1f}%)")
if sr: print(f"  均值: {statistics.mean(sr):.1f}% ± {statistics.stdev(sr):.2f}%")

print("\n✓ 模型稳定" if all(1<r<4 for r in dr) else "✗")
