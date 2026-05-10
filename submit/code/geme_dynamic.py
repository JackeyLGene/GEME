# GEME -- 动态维度版
# 没有VEC_DIM。没有字母表。维度从输入中生长。
import sys, math, statistics, random, copy

# ──────────────────────────────────────────────────────────────────
# Structural constants (imported from geme.py for consistency)
# ──────────────────────────────────────────────────────────────────
try:
    from geme import (DELTA, GAMMA, TAU, NOVELTY_BONUS,
                      ASSOC_SEP, CHAIN_SEP,
                      INDUCTION_DECAY_UNMERGED, INDUCTION_DECAY_LOW)
except ImportError:
    DELTA = 0.19; GAMMA = 0.05; TAU = 0.6; NOVELTY_BONUS = 5.0
    ASSOC_SEP = "──"; CHAIN_SEP = "══"
    INDUCTION_DECAY_UNMERGED = math.exp(-GAMMA / 0.25)
    INDUCTION_DECAY_LOW = math.exp(-GAMMA)

class Frame:
    __slots__=("vec","weight","age","merged","sig","sig_full","src","fid")
    _fid_counter=0
    def __init__(self,vec,weight=1.0,sig="",src=""):
        Frame._fid_counter+=1; self.fid=Frame._fid_counter
        self.vec=tuple(vec); self.weight=weight
        self.age=0; self.merged=0
        self.sig=sig[:30]; self.sig_full=sig; self.src=src

def _v_len(t): return len(t)
def _v_get(t,i): return t[i] if i<len(t) else 0.0
def _v_merge(o, n, w):
    ml=max(len(o),len(n))
    return tuple(((_v_get(o,i)*w+_v_get(n,i))/(w+1)) for i in range(ml))
def _v_dist(a,b):
    ml=max(len(a),len(b)); d=0.0
    for i in range(ml): d+=(_v_get(a,i)-_v_get(b,i))**2
    return math.sqrt(d)

class Memory:
    def __init__(self,capacity=10,cooccur_window=50,cooccur_thresh=0.25,max_chains=5):
        self.frames=[]; self.capacity=max(capacity,1)
        self._merge_thresh_val=DELTA; self.cooccur_thresh=cooccur_thresh
        self.total_weight=0.0
        self._window=[]; self._win_max=cooccur_window
        self._step_counter=0
        self._cooccur={}; self._assoc_frames=0
        self._chain_count=0; self.max_chains=max(max_chains,1)
        self._merge_dists=[]; self._learn_dists=[]
        self._self_observe_count=0; self._chain_cooccur_thresh=5
        self.preserve_sig=True
        self._last_merge_fid=None; self._merge_history=[]
        self._novelty_bonus=NOVELTY_BONUS
        self.quantum_mode=False
        self._multiverse_enabled=True; self._multiverse=[]
        self._vocab={}; self._rev_vocab=[]; self._vec_dim=0

    def _get_dim(self,sym):
        if sym not in self._vocab:
            self._vocab[sym]=self._vec_dim; self._rev_vocab.append(sym); self._vec_dim+=1
        return self._vocab[sym]

    def observe(self,vec,sig,src=""):
        bi,bd=-1,float('inf')
        thresh=self._adaptive_thresh(); self._merge_thresh_val=thresh or 0.0
        self._win_max=self._adaptive_window()
        candidates=[]
        for i,f in enumerate(self.frames):
            d=_v_dist(vec,f.vec)
            if d<bd: bd=d; bi=i
            if self.quantum_mode and thresh:
                if d<=thresh: candidates.append((i,d,f))
        if thresh is None and bi>=0 and bd!=float('inf'):
            self._learn_dists.append(bd)
            if len(self._learn_dists)>200: self._learn_dists.pop(0)
        if self.quantum_mode and len(candidates)>0:
            if not hasattr(self,'_qrand'): self._qrand=random.Random(42)
            psum=0.0; probs=[]
            for i,d,f in candidates:
                p=math.exp(-d/max(self._merge_thresh_val,0.001)); probs.append((i,d,f,p)); psum+=p
            if psum>0:
                r=self._qrand.random()*psum; acc=0.0
                for i,d,f,p in probs:
                    acc+=p
                    if r<=acc: bi=i; bd=d; break
                if self._multiverse_enabled and len(candidates)>1:
                    sid=self._step_counter
                    for i,d,f in candidates:
                        if i==bi: continue
                        bf=copy.deepcopy(self.frames)
                        for b in bf:
                            if b.fid==f.fid:
                                b.vec=_v_merge(b.vec,vec,b.weight)
                                b.weight+=1.0; b.merged+=1; break
                        self._multiverse.append((bf,sid,f"br_{sid}_{f.fid}"))
                self._merge_dists.append(bd)
                if len(self._merge_dists)>100: self._merge_dists.pop(0)
                f=self.frames[bi]; self.total_weight-=f.weight
                f.vec=_v_merge(f.vec,vec,f.weight); f.weight+=1.0; f.merged+=1
                if not self.preserve_sig:
                    cmb="_".join(sorted(set(f.sig.split("_")+sig.split("_"))))
                    if len(cmb.split("_"))<=8: f.sig=cmb[:30]
                self.total_weight+=f.weight; self._step_counter+=1
                self._last_merge_fid=f.fid; self._merge_history.append(f.fid)
                self._window.append((sig,self._step_counter,tuple(vec)))
                if len(self._window)>self._win_max: self._window.pop(0)
                return
        if thresh is not None and bi>=0 and bd<=thresh and (not sig or sig[:30]==self.frames[bi].sig):
            self._merge_dists.append(bd)
            if len(self._merge_dists)>100: self._merge_dists.pop(0)
            f=self.frames[bi]; self.total_weight-=f.weight
            f.vec=_v_merge(f.vec,vec,f.weight); f.weight+=1.0; f.merged+=1
            if not self.preserve_sig:
                cmb="_".join(sorted(set(f.sig.split("_")+sig.split("_"))))
                if len(cmb.split("_"))<=8: f.sig=cmb[:30]
            self.total_weight+=f.weight
            self._last_merge_fid=f.fid; self._merge_history.append(f.fid)
        else:
            if thresh is None or thresh==0.0: nw=1.0
            elif bd!=float('inf'): nw=1.0+self._novelty_bonus*max(0,1.0-bd/max(thresh,0.001))
            else: nw=1.0
            if len(self.frames)>=self.capacity:
                self.frames.sort(key=lambda x: x.weight-x.age*GAMMA*2)
                r=self.frames.pop(0); self.total_weight-=r.weight
            nf=Frame(vec,nw,sig,src); self.frames.append(nf); self.total_weight+=nw
            self._last_merge_fid=nf.fid; self._merge_history.append(nf.fid)
        self._step_counter+=1
        self._window.append((sig,self._step_counter,tuple(vec)))
        if len(self._window)>self._win_max: self._window.pop(0)
        for i in range(len(self._window)):
            for j in range(i+1,min(i+3,len(self._window))):
                s1,id1=self._window[i][0],self._window[i][1]
                s2,id2=self._window[j][0],self._window[j][1]
                if id1==id2: continue
                k=tuple(sorted([s1,s2]))
                self._cooccur[k]=self._cooccur.get(k,0)+1
        t=len(self._window)
        if t>=30:
            for (sa,sb),c in list(self._cooccur.items()):
                if c/t>=self.cooccur_thresh and c>=max(5,t*0.05):
                    self._assoc_frames+=1

    def _adaptive_thresh(self):
        if not self._merge_dists:
            if len(self._learn_dists)<10: return None
            t=sorted(self._learn_dists)[len(self._learn_dists)//4]
            if t<=0: t=statistics.mean(self._learn_dists)*0.5
            if t<=0: t=0.001
            self._merge_dists.append(t)
            return t
        if len(self._merge_dists)==0: return DELTA
        med=statistics.median(self._merge_dists[-min(50,len(self._merge_dists)):])
        return max(med, self._merge_dists[-1]*0.5)

    def _adaptive_window(self):
        if not self.frames: return self._win_max
        return max(5,min(200,int(self.total_weight/max(len(self.frames),1)*2)))

    @property
    def efficiency(self): return len([f for f in self.frames if f.weight>=5])/max(len(self.frames),1)
    @property
    def utilization(self): return min(1.0,len(self.frames)/self.capacity)
    @property
    def stress(self): return self.utilization*(1.0-self.efficiency)

class GEME:
    def __init__(self,memory_cap=10,cooccur_window=50,cooccur_thresh=0.25,max_chains=5,time_window_size=0):
        self.memory=Memory(capacity=memory_cap,cooccur_window=cooccur_window,cooccur_thresh=cooccur_thresh,max_chains=max_chains)
        self.frame_count=0; self._input_count=0; self._stress_accum=0.0
        self._induction_threshold=TAU; self._last_induction=0
        # 元自指：维表增长率
        self._meta_step=0; self._meta_interval=30
        self._vocab_history=[]; self._prev_vocab_size=0
    def process(self,text,sig_hint=None):
        for ch in text:
            if ch not in self.memory._vocab:
                dim=self.memory._get_dim(ch)
            v=[0.0]*self.memory._vec_dim; v[self.memory._vocab[ch]]=1.0
            s=sig_hint or ch
            self.process_vec(v,s)
    def process_vec(self,vec,sig,src=""):
        self.frame_count+=1; self._input_count+=1
        self.memory.observe(vec,sig,src)
        # 元自指：观测维表增长率
        self._meta_step+=1
        if self._meta_step>=self._meta_interval:
            vs=self.memory._vec_dim; gr=vs-self._prev_vocab_size
            self._vocab_history.append((self.frame_count,vs,gr))
            if len(self._vocab_history)>20: self._vocab_history.pop(0)
            self._prev_vocab_size=vs; self._meta_step=0
            if self._vocab_history and len(self._vocab_history)>1:
                prev_v=self._vocab_history[-2][1]
                growth_rate=(vs-prev_v)/float(self._meta_interval)
                meta_vec=[0.0]*vs
                if vs>0: meta_vec[vs-1]=1.0
                # 在已有向量末追加增长率维（如果空间够）
                self.process_vec(meta_vec,f"meta_growth_{growth_rate:.4f}")
        if self.memory._multiverse_enabled and self.memory._multiverse:
            nm=[]
            for bf,st,bid in self.memory._multiverse:
                if len(nm)>=20: break
                bi=-1; bd=float('inf')
                for i,f in enumerate(bf):
                    d=sum((_v_get(vec,j)-_v_get(f.vec,j))**2 for j in range(max(len(vec),len(f.vec))))
                    if d<bd: bd=d; bi=i
                th=self.memory._adaptive_thresh() or DELTA
                if bi>=0 and bd<=th*th:
                    f=bf[bi]; f.vec=_v_merge(f.vec,vec,f.weight); f.weight+=1.0; f.merged+=1
                nm.append((bf,st,bid))
            self.memory._multiverse=nm
        self._induction_step(self.memory.stress)
    def _induction_step(self,stress):
        self._stress_accum+=stress*0.1
        if self._stress_accum>self._induction_threshold and self.frame_count-self._last_induction>=15:
            self.consolidate(); return True
        return False
    def consolidate(self):
        self._last_induction=self.frame_count
        for f in copy.deepcopy(self.memory.frames):
            if f.merged==0: f.weight*=INDUCTION_DECAY_UNMERGED
            elif f.merged<3: f.weight*=INDUCTION_DECAY_LOW
            f.weight=max(1.0,f.weight)
        self.memory.frames.sort(key=lambda x: x.weight-x.age*GAMMA,reverse=True)
        self.memory._chain_count=0  # 同步fix: 重置链计数

if __name__=="__main__":
    g=GEME(memory_cap=32)
    g.memory.preserve_sig=True; g.memory.quantum_mode=True
    g.memory._merge_dists=[0.3]*50; g._induction_threshold=3.0
    print("测试：中英文混合输入（维表自动生长）")
    for _ in range(100):
        g.process("猫在垫子上")
        g.process("the cat is on the mat")
    print(f"词汇表大小: {g.memory._vec_dim}")
    print(f"帧数: {len(g.memory.frames)}")
    print(f"关联帧: {sum(1 for f in g.memory.frames if ASSOC_SEP in (f.sig_full or f.sig))}")
    print(f"翻译不变性检验: 中文符号{sum(1 for c in '猫在垫子上' if c in g.memory._vocab)}个, 英文符号{sum(1 for c in 'thecatisonmat' if c in g.memory._vocab)}个")
