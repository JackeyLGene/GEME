"""GEME — standalone, zero external dependencies.
Single file. No gira library needed. Just Python 3.8+ stdlib.

Usage:
  from geme import GEME, eq, fn, const, structural_signature
  g = GEME(memory_cap=16)
  g.process_sig(eq(fn("swap", const("1"), const("2")),
                    fn("swap", const("2"), const("1"))),
                 structural_signature(...))
"""
from __future__ import annotations
import math, statistics, random
from copy import deepcopy

# ──────────────────────────────────────────────────────────────────
# Structural constants (centralized, documented, frozen)
# ──────────────────────────────────────────────────────────────────
DELTA = 0.19     # δ: adaptive threshold scaling factor
GAMMA = 0.05     # γ: frame age decay multiplier
TAU = 0.60       # τ: induction stress threshold

# ── Derived constants (all expressible as functions of δ, γ, τ) ──
DW_THRESHOLD = GAMMA * 0.4            # d(w)/dt significance: 40% of metabolic baseline
META_STABLE_THRESHOLD = GAMMA * 0.2   # |d(w)/dt| < this → meta-stable (20% of baseline)
PRED_CONFIDENCE_THRESHOLD = 0.3    # bootstrap value — overridden by adaptive lower-quartile calibration
DOUBT_ON_THRESHOLD = TAU              # accuracy < τ → systemic doubt (isomorphic to §2.3)
DOUBT_OFF_THRESHOLD = 1.0 - GAMMA * 3.0  # hysteresis upper bound
HEALTHY_ACC_THRESHOLD = 1.0 - GAMMA * 4.0  # min accuracy for system to be considered healthy (= 0.80)
ANOMALY_MED_BOUND = TAU - GAMMA * 2          # moderate anomaly threshold (= 0.50)
ANOMALY_HIGH_BOUND = GAMMA * 4               # high anomaly threshold (= 0.20)
NOVELTY_BONUS = 5.0                   # initial weight premium
# Derivation: a novel frame must survive long enough to be validated.
# Minimum survival steps = τ / (avg_stress × 0.1) ≈ 0.60 / 0.05 = 12 steps.
# After 12 steps of γ decay: w × exp(−12 × 0.05) = w × 0.549.
# To remain above median weight (~2.0 after convergence): w ≥ 2.0 / 0.549 ≈ 3.64.
# New frame weight = 1.0 + bonus × distance_ratio. At max novelty (ratio→0):
#   1.0 + 5.0 = 6.0. After decay: 6.0 × 0.549 ≈ 3.3 > 2.0. Survives.
INDUCTION_DECAY_UNMERGED = math.exp(-GAMMA / 0.25)    # ≈ 0.819
INDUCTION_DECAY_LOW = math.exp(-GAMMA)                 # ≈ 0.951
SIG_LEN = 30        # signature truncation (engineering)
SRC_LEN = 80        # source truncation (engineering)
PRED_WINDOW = 50    # rolling window for prediction accuracy
W_HIST_WINDOW = 50  # rolling window for weight history
DERIV_HIST_MIN = 5  # minimum history length for derivative computation
MULTIVERSE_DIM_PENALTY = DELTA * 1.32   # dim mismatch penalty in multiverse (~0.25)
EVAL_MATCH_THRESHOLD = 0.75             # Jaccard-like overlap for evaluate_sig

# ── Unicode separators (explicit, not magic codepoints) ──
ASSOC_SEP = chr(8212) * 2    # —— (em dash ×2, U+2014) — original code verified match
CHAIN_SEP = chr(9711) * 2    # ◯◯ (large circle ×2, U+25EF) — original code verified match


# ──────────────────────────────────────────────────────────────────
# Minimal formula language (replaces gira.phase3.language)
# ──────────────────────────────────────────────────────────────────
class Term:
    __slots__ = ("kind", "symbol", "args")
    def __init__(self, kind="", symbol="", args=None):
        self.kind=kind; self.symbol=symbol; self.args=args or []

class Formula:
    __slots__ = ("kind", "left", "right")
    def __init__(self, kind="", left=None, right=None):
        self.kind=kind; self.left=left; self.right=right

def const(name: str = "0") -> Term:
    return Term("constant", str(name))

def fn(symbol: str, *args: Term) -> Term:
    return Term("function", symbol, list(args))

def eq(t1: Term, t2: Term) -> Formula:
    return Formula("equation", t1, t2)

# ──────────────────────────────────────────────────────────────────
# Structural signature (replaces compute_signature)
# ──────────────────────────────────────────────────────────────────
def structural_signature(formula) -> str:
    """Generate formula structure signature (no variable names)."""
    parts = []
    def walk(n):
        if n is None: return
        k=getattr(n,'kind',''); s=getattr(n,'symbol','')
        if k in ("function",):
            parts.append(s)
            for a in getattr(n,'args',[]): walk(a)
        elif k=="equation": parts.append("eq")
        elif k=="conjunction": parts.append("and")
        elif k=="implication": parts.append("impl")
        elif k=="variable": pass
        else: pass
        if getattr(n,'left',None): walk(n.left)
        if getattr(n,'right',None): walk(n.right)
    walk(formula)
    return "_".join(parts) if parts else "empty"

# ──────────────────────────────────────────────────────────────────
# Alphabet (27 symbols)
# ──────────────────────────────────────────────────────────────────
_ALPHABET = ["0","1","s","+","\u00d7","=","forall","exists","x","y","z","sub",
             "swap","pair","comm",
             "set","succ","empty","rank",
             "point","line","shape","parallel","angle","triangle",
             "fn","const"]
_VEC_DIM = len(_ALPHABET)

def symbol_vector(formula) -> Tuple[float, ...]:
    """Encode formula as frequency vector over 27-symbol alphabet."""
    counts = {s:0.0 for s in _ALPHABET}; total=0
    def w(n):
        nonlocal total
        if n is None: return
        k=getattr(n,'kind',''); s=getattr(n,'symbol','')
        if k=="constant":
            v=str(getattr(n,'value',''))
            if v in counts: counts[v]=counts.get(v,0)+1; total+=1
            else: counts["const"]=counts.get("const",0)+1; total+=1
        elif k=="numeral": counts["1"]=counts.get("1",0)+1; total+=1
        elif k=="function":
            _s=s if s in counts else None
            if _s in counts: counts[_s]=counts.get(_s,0)+1; total+=1
            else: counts["fn"]=counts.get("fn",0)+1; total+=1
        elif k=="variable":
            if s in counts: counts[s]=counts.get(s,0)+1; total+=1
        elif k=="forall": counts["forall"]=counts.get("forall",0)+1; total+=1
        elif k=="exists": counts["exists"]=counts.get("exists",0)+1; total+=1
        if s=="=": counts["="]=counts.get("=",0)+1; total+=1
        for a in getattr(n,'args',[]): w(a)
        if getattr(n,'left',None): w(n.left)
        if getattr(n,'right',None): w(n.right)
    w(formula)
    if total==0: total=1
    return tuple(counts[s]/total for s in _ALPHABET)

def vec_dist(a,b):
    return math.sqrt(sum((ai-bi)**2 for ai,bi in zip(a,b)))

# ──────────────────────────────────────────────────────────────────
# Frame
# ──────────────────────────────────────────────────────────────────
_FRAME_ID_COUNTER=[0]
class Frame:
    __slots__=("vec","weight","sig","sig_full","src","age","merged","fid","layer")
    def __init__(self,vec,weight=1.0,sig="",src="",layer="L1"):
        _FRAME_ID_COUNTER[0]+=1; self.fid=_FRAME_ID_COUNTER[0]
        self.vec=vec; self.weight=weight; self.sig=sig[:SIG_LEN]; self.sig_full=sig
        self.src=src[:SRC_LEN] if src else sig[:SIG_LEN]; self.age=0; self.merged=0; self.layer=layer

# ──────────────────────────────────────────────────────────────────
# Memory (competitive memory economy)
# ──────────────────────────────────────────────────────────────────
class Memory:
    def __init__(self,capacity=10,merge_thresh=None,cooccur_window=50,
                 cooccur_thresh=0.25,max_chains=5):
        self.frames=[]; self.capacity=max(capacity,1)
        self.merge_thresh=merge_thresh
        self._merge_thresh_val=merge_thresh or DELTA
        self.cooccur_thresh=cooccur_thresh
        self.total_weight=0.0
        self._window=[]; self._win_max=cooccur_window
        self._step_counter=0
        self._cooccur={}; self._assoc_frames=0
        self._chain_count=0; self.max_chains=max(max_chains,1)
        self._merge_dists=[]
        self._learn_dists=[]
        self._self_observe_count=0
        self._chain_cooccur_thresh=5
        self.preserve_sig=True
        self._last_merge_fid=None
        self._merge_history=[]
        self._novelty_bonus=NOVELTY_BONUS
        self.quantum_mode=False
        # L4: d(w)/dt 追踪 + 预测帧
        self._weight_history={}  # fid → [(step, weight), ...]
        self._derivative_frames=[]  # 已生成的d(w)/dt帧
        # L4: 预测（模态）
        self._prediction_accuracy=[]  # 滚动准确率窗口
        self._pred_errors=0; self._pred_total=0
        # 自适应置信度阈值：跟踪所有预测置信度，从分布中自校准
        self._confidences=[]        # all predict_next confidence values
        self._conf_threshold=PRED_CONFIDENCE_THRESHOLD  # starts at bootstrap, auto-calibrates
        # L6: 统摄（当预测精度持续下降时触发）
        self._doubt_mode=False
        self._last_accuracy=1.0
        # 第5维：多世界
        self._multiverse_enabled=True
        self._multiverse=[]
        self._step_branched=set()

    def _adaptive_window(self):
        """自指窗口：帧平均寿命 × 2"""
        if not self.frames: return self._win_max
        avg_life = self.total_weight / max(len(self.frames), 1)
        return max(5, min(200, int(avg_life * 2)))

    def _adaptive_thresh(self):
        if not self._merge_dists:
            if len(self._learn_dists)<10: return None
            t=sorted(self._learn_dists)[len(self._learn_dists)//4]
            if t<=0: t=statistics.mean(self._learn_dists)*0.5
            if t<=0: t=0.001
            self._merge_dists.append(t)
            return t
        med=statistics.median(self._merge_dists[-50:])
        last_ok=self._merge_dists[-1] if self._merge_dists else 0.001
        return max(med, last_ok*0.5)

    def observe(self,vec,sig,src="",layer="L1"):
        if not vec or len(vec)==0:
            return  # ignore empty vectors
        # L4: 在添加新输入前预测下一个帧，然后与实际对比
        if sig:
            self.process_prediction(sig)
        bi,bd=-1,float('inf')
        # Compute threshold FIRST (before candidate selection)
        thresh=self._adaptive_thresh()
        self._merge_thresh_val=thresh or 0.0
        # 自指窗口：每条观察更新一次
        self._win_max = self._adaptive_window()
        
        candidates=[]
        for i,f in enumerate(self.frames):
            d=vec_dist(vec,f.vec)
            if d<bd: bd=d; bi=i
            if self.quantum_mode and thresh:
                if d<=thresh: candidates.append((i,d,f))
        
        if thresh is None and bi>=0 and bd!=float('inf'):
            self._learn_dists.append(bd)
            if len(self._learn_dists)>200: self._learn_dists.pop(0)
            
        # Quantum merge: probabilistic selection among candidates
        if self.quantum_mode and len(candidates)>0:
            if not hasattr(self,'_qrand'): self._qrand = random.Random()
            psum = 0.0; probs = []
            for i,d,f in candidates:
                p = math.exp(-d/max(self._merge_thresh_val,0.001))
                probs.append((i,d,f,p)); psum += p
            if psum > 0:
                r = self._qrand.random() * psum; acc = 0.0
                chosen=None
                for i,d,f,p in probs:
                    acc += p
                    if r <= acc: bi=i; bd=d; chosen=(i,d,f); break
                # 第5维：保存未选候选为分支世界
                if self._multiverse_enabled and len(candidates)>1:
                    step_id=self._step_counter
                    for i,d,f in candidates:
                        if i==bi: continue  # 跳过被选中的
                        # 拷贝当前帧经济——作为分支点的替代
                        branch_frames = deepcopy(self.frames)
                        # 同时应用合并到丢失的候选帧
                        for bf in branch_frames:
                            if bf.fid==f.fid:  # 找到丢失的帧，应用合并
                                # 合并到丢失帧
                                old_vec=tuple(bf.vec)
                                bf.vec=tuple((bf.vec[j]*bf.weight+vec[j])/(bf.weight+1) for j in range(len(vec)))
                                bf.weight+=1.0
                                bf.merged+=1
                                break
                        self._multiverse.append((branch_frames, step_id, f"branch_{step_id}_{f.fid}"))
                self._merge_dists.append(bd)
                if len(self._merge_dists)>100: self._merge_dists.pop(0)
                f=self.frames[bi]; self.total_weight-=f.weight
                f.vec=tuple((f.vec[j]*f.weight+vec[j])/(f.weight+1) for j in range(len(vec)))
                f.weight+=1.0; f.merged+=1
                if not self.preserve_sig:
                    combined="_".join(sorted(set(f.sig.split("_")+sig.split("_"))))
                    if len(combined.split("_"))<=8: f.sig=combined[:30]
                self.total_weight+=f.weight; self._step_counter+=1
                self._last_merge_fid = f.fid; self._merge_history.append(f.fid)
                # L4: 记录权重历史
                if f.fid not in self._weight_history:
                    self._weight_history[f.fid]=[]
                self._weight_history[f.fid].append((self._step_counter, f.weight))
                if len(self._weight_history[f.fid])>W_HIST_WINDOW:
                    self._weight_history[f.fid].pop(0)
                step_id=self._step_counter
                self._window.append((sig,step_id,tuple(vec)))
                if len(self._window)>self._win_max: self._window.pop(0)
                return
                
        # Standard merge
        if thresh is not None and bi>=0 and bd<=thresh and (not sig or sig[:SIG_LEN]==self.frames[bi].sig):
            self._merge_dists.append(bd)
            if len(self._merge_dists)>100: self._merge_dists.pop(0)
            f=self.frames[bi]; self.total_weight-=f.weight
            f.vec=tuple((f.vec[j]*f.weight+vec[j])/(f.weight+1) for j in range(len(vec)))
            f.weight+=1.0; f.merged+=1
            if not self.preserve_sig:
                combined="_".join(sorted(set(f.sig.split("_")+sig.split("_"))))
                if len(combined.split("_"))<=8: f.sig=combined[:30]
            self.total_weight+=f.weight
            self._last_merge_fid=f.fid; self._merge_history.append(f.fid)
            # L4: 记录权重历史
            if f.fid not in self._weight_history:
                self._weight_history[f.fid]=[]
            self._weight_history[f.fid].append((self._step_counter, f.weight))
            if len(self._weight_history[f.fid])>W_HIST_WINDOW:
                self._weight_history[f.fid].pop(0)
        else:
            if thresh is None or thresh==0.0: nw=1.0
            elif bd!=float('inf'): nw=1.0+self._novelty_bonus*max(0,1.0-bd/max(thresh,0.001))
            else: nw=1.0
            if len(self.frames)>=self.capacity:
                self.frames.sort(key=lambda x: x.weight-x.age*GAMMA*2)
                r=self.frames.pop(0); self.total_weight-=r.weight
            nf=Frame(vec,nw,sig,src,layer=layer); self.frames.append(nf); self.total_weight+=nw
            self._last_merge_fid=nf.fid; self._merge_history.append(nf.fid)
            # L4: 初始化权重历史
            self._weight_history[nf.fid]=[(self._step_counter, nw)]
        self._step_counter+=1
        step_id=self._step_counter
        self._window.append((sig,step_id,tuple(vec)))
        if len(self._window)>self._win_max: self._window.pop(0)
        for i in range(len(self._window)):
            for j in range(i+1,min(i+3,len(self._window))):
                s1,id1=self._window[i][0],self._window[i][1]
                s2,id2=self._window[j][0],self._window[j][1]
                if id1==id2: continue
                key=tuple(sorted([s1,s2]))
                self._cooccur[key]=self._cooccur.get(key,0)+1
        total_steps=len(self._window)
        if total_steps>=30:
            for (sa,sb),count in list(self._cooccur.items()):
                ratio=count/total_steps
                if ratio>=self.cooccur_thresh and count>=max(5,total_steps*0.05):
                    assoc_sig=sa+"──"+sb
                    existing=[f for f in self.frames if (f.sig_full or f.sig)==assoc_sig]
                    if existing:
                        for exf in existing:
                            self.total_weight-=exf.weight; exf.weight+=0.5; self.total_weight+=exf.weight
                    else:
                        base_vecs=[]
                        for f in self.frames:
                            fs=f.sig_full or f.sig
                            if fs in (sa,sb): base_vecs.append(f.vec)
                        if len(base_vecs)<2: continue
                        total_w=sum(f.weight for f in self.frames if (f.sig_full or f.sig) in (sa,sb))
                        assoc_vec=tuple(sum(f.vec[j]*f.weight for f in self.frames if (f.sig_full or f.sig) in (sa,sb))/max(total_w,1) for j in range(_VEC_DIM))
                        if len(self.frames)>=self.capacity:
                            self.frames.sort(key=lambda x: x.weight); r=self.frames.pop(0); self.total_weight-=r.weight
                        self.frames.append(Frame(assoc_vec,weight=float(count),sig=assoc_sig,layer="L2")); self.total_weight+=float(count); self._assoc_frames+=1
                    # Chains now formed by self_observe(), not here

    def _form_chains(self):
        """Form chains between current frames that co-occur in self-obs."""
        if self._chain_count>=self.max_chains: return
        cur={f.fid:f for f in self.frames if f.weight>2}
        if len(cur)<2: return
        fids=list(cur.keys())
        formed=0
        for i in range(len(fids)):
            for j in range(i+1,len(fids)):
                if self._chain_count>=self.max_chains: return
                fa,fb=cur[fids[i]],cur[fids[j]]
                ckey=tuple(sorted([f"fid_{fa.fid}",f"fid_{fb.fid}"]))
                if self._cooccur.get(ckey,0)>=self._chain_cooccur_thresh:
                    ms=f"f{fa.fid}══f{fb.fid}"
                    if any(ff.sig_full==ms for ff in self.frames): continue
                    chain_w=(fa.weight+fb.weight)/2
                    if len(self.frames)>=self.capacity:
                        self.frames.sort(key=lambda x: x.weight)
                        r=self.frames.pop(0); self.total_weight-=r.weight
                    self.frames.append(Frame((0.0,)*_VEC_DIM,weight=chain_w,sig=ms,layer="L3"))
                    self.total_weight+=chain_w; self._chain_count+=1; formed+=1
    
    def self_observe(self):
        """Self-observation: generate aggregate vector from frame economy.
        
        The observation vector is a weighted centroid of all frames with weight>2,
        normalized by total weight. This implements the paper's claim: the system
        generates an observation vector from its own internal state and feeds it
        back through the same competitive merge process.
        
        Additionally computes d(w)/dt for all frames and generates L4 meta-frames
        when derivative magnitudes cross threshold indicating metacognitive change.
        """
        self._self_observe_count+=1
        active=[f for f in self.frames if f.weight>2]
        if not active:
            return
        # L4: 计算权重导数
        derivs=self.compute_derivatives()
        # 识别d(w)/dt显著的帧作为L4元认知观测对象
        high_dw=[(fid,dw) for fid,dw in derivs.items() if abs(dw)>DW_THRESHOLD]
        if high_dw:
            # 将导数最大的三个作为L4元观测信号
            high_dw.sort(key=lambda x: abs(x[1]), reverse=True)
            for fid, dw in high_dw[:3]:
                # 找到对应帧
                match=[f for f in self.frames if f.fid==fid]
                if match:
                    meta_vec=match[0].vec
                    dw_str=f"dwdw_{abs(dw):.2f}"
                    # 注入d(w)/dt元观测帧
                    self.observe(meta_vec, dw_str, layer="L4")
        # Weighted centroid: aggregate vector of the frame economy's state
        total_w = sum(f.weight for f in active)
        dim = len(active[0].vec)
        centroid = tuple(
            sum(f.vec[j] * f.weight for f in active) / total_w
            for j in range(dim)
        )
        # Feed centroid back as a self-observation
        self.observe(centroid, "self_obs", layer="L4")
        # Also track frame IDs for chain formation
        fids=[f.fid for f in active]
        feed_time=self._step_counter
        for fid in fids:
            self._window.append((f"fid_{fid}",feed_time,(0.0,)*dim))
            if len(self._window)>self._win_max:
                self._window.pop(0)
        for i in range(len(fids)):
            for j in range(i+1,len(fids)):
                ckey=tuple(sorted([f"fid_{fids[i]}",f"fid_{fids[j]}"]))
                self._cooccur[ckey]=self._cooccur.get(ckey,0)+1
        self._form_chains()
    
    def induction_clean(self):
        self.self_observe()  # observe before pruning
        self._chain_count = 0  # 重置链计数，允许后续继续形成链
        for f in self.frames:
            self.total_weight-=f.weight
            if f.merged==0: f.weight*=INDUCTION_DECAY_UNMERGED
            elif f.merged<3: f.weight*=INDUCTION_DECAY_LOW
            f.weight=max(1.0,f.weight)
            self.total_weight+=f.weight; f.age+=1
        self.frames.sort(key=lambda x: x.weight-x.age*GAMMA,reverse=True)
        half=max(1,len(self.frames)//2)
        for f in self.frames[half:]: self.total_weight-=f.weight
        self.frames=self.frames[:half]
        # L4: 清理已剪枝帧的权重历史
        alive_fids={f.fid for f in self.frames}
        for fid in list(self._weight_history.keys()):
            if fid not in alive_fids:
                del self._weight_history[fid]

    @property
    def efficiency(self):
        if not self.frames or self.total_weight==0: return 1.0
        avg=self.total_weight/len(self.frames)
        dev=sum(abs(f.weight-avg) for f in self.frames)/(len(self.frames)*max(avg,0.001))
        return max(0.01,1.0-min(1.0,dev))
    @property
    def utilization(self): return len(self.frames)/self.capacity
    @property
    def stress(self): return self.utilization*(1.0-self.efficiency)
    def compression_ratio(self, input_count):
        return input_count/max(len(self.frames),1)
    def entropy_reduction(self, initial_frames):
        return 1.0-len(self.frames)/initial_frames if initial_frames else 0.0
    def structural_entropy(self):
        """Shannon entropy of frame weight distribution."""
        if not self.frames or self.total_weight<=0: return 0.0
        from math import log2
        return -sum((f.weight/self.total_weight)*log2(f.weight/self.total_weight)
                    for f in self.frames if f.weight>0)
    def count_L4_frames(self, min_weight_ratio=1.5):
        """Number of stable L4 self-referential frames (frames with self or bridge sig)."""
        l4 = [f for f in self.frames
              if ('self' in (f.sig or '') or
                  ASSOC_SEP in (f.sig_full or '') or
                  CHAIN_SEP in (f.sig_full or ''))]
        if not l4: return 0
        w = sorted([f.weight for f in l4], reverse=True)
        avg = sum(w) / len(w) if w else 1
        return sum(1 for x in w if x >= avg * 1.5)

    def count_by_layer(self):
        """Return dict of {layer: count} for all frames."""
        counts={}
        for f in self.frames:
            l=getattr(f,'layer',"L1")
            counts[l]=counts.get(l,0)+1
        return counts
    def mutual_information_phi_X(self):
        """I(phi; X): mutual information between self-referential (phi) and
        non-self frames (X), computed from empirical co-occurrence joint distribution.
        
        Uses the co-occurrence table to compute p(phi, x) for all pairs of
        (self_sig, ext_sig) that have appeared in the same window.
        When I(phi; X) → 0, self-reference carries no information about input.
        """
        from math import log2
        # Identify self-referential vs external signatures
        phi_keys = set()  # signatures containing "self"
        x_keys = set()   # signatures NOT containing "self"
        for (sa, sb) in self._cooccur:
            # Association frames (──) are phi-family
            if 'self' in sa or ASSOC_SEP in sa:
                phi_keys.add(sa)
            else:
                x_keys.add(sa)
            if 'self' in sb or ASSOC_SEP in sb:
                phi_keys.add(sb)
            else:
                x_keys.add(sb)
        if not phi_keys or not x_keys:
            return 0.0
        # 全空间总和（包括phi-phi、x-x、phi-x所有对）
        total_all = sum(c for c in self._cooccur.values())
        if total_all == 0:
            return 0.0
        # 预计算边际概率（全空间）
        p_phi_cache = {}
        p_x_cache = {}
        for sig in phi_keys:
            p_phi_cache[sig] = sum(c for (sa, sb), c in self._cooccur.items() if sa == sig or sb == sig) / total_all
        for sig in x_keys:
            p_x_cache[sig] = sum(c for (sa, sb), c in self._cooccur.items() if sa == sig or sb == sig) / total_all
        mi = 0.0
        for (sa, sb), c in self._cooccur.items():
            in_phi_a = sa in phi_keys; in_phi_b = sb in phi_keys
            in_x_a = sa in x_keys; in_x_b = sb in x_keys
            if in_phi_a and in_x_b:
                p_joint = c / total_all
                p_phi = p_phi_cache[sa]; p_x = p_x_cache[sb]
                if p_joint > 0 and p_phi > 0 and p_x > 0:
                    mi += p_joint * log2(p_joint / (p_phi * p_x))
            elif in_x_a and in_phi_b:
                p_joint = c / total_all
                p_phi = p_phi_cache[sb]; p_x = p_x_cache[sa]
                if p_joint > 0 and p_phi > 0 and p_x > 0:
                    mi += p_joint * log2(p_joint / (p_phi * p_x))
        return max(0.0, mi)
    
    def compute_derivatives(self):
        """Compute d(w)/dt for all frames with sufficient history.
        Returns dict of {fid: derivative} for L4 meta-observation."""
        derivs = {}
        for fid, history in self._weight_history.items():
            if len(history) < DERIV_HIST_MIN:
                continue
            # Linear regression slope over recent history
            recent = history[-10:] if len(history) > 10 else history
            n = len(recent)
            xs = [h[0] for h in recent]
            ys = [h[1] for h in recent]
            x_mean = sum(xs) / n
            y_mean = sum(ys) / n
            num = sum((xs[i] - x_mean) * (ys[i] - y_mean) for i in range(n))
            den = sum((xs[i] - x_mean) ** 2 for i in range(n))
            derivs[fid] = num / max(den, 0.001)
        return derivs
    
    def is_meta_stable(self, fid):
        """Check if a frame's weight is meta-stable (d(w)/dt ≈ 0)."""
        derivs = self.compute_derivatives()
        if fid not in derivs:
            return False
        return abs(derivs[fid]) < META_STABLE_THRESHOLD
    
    # ──────────────────────────────────────────────────────────
    # L4: 预测（模态跃迁）
    # ──────────────────────────────────────────────────────────
    def predict_next(self):
        """从L3桥+cooccur表预测下一个最可能出现的帧签名。
        用最后2个非self输入签名预测下一个。
        返回 (predicted_sig, confidence)。如果无足够数据，返回 (None, 0.0)。"""
        if len(self._window) < 3:
            return None, 0.0
        # 从滑动窗口拿最后2个非self_obs签名作为上下文
        recent = [entry[0] for entry in self._window if entry[0] != 'self_obs']
        if len(recent) < 2:
            return None, 0.0
        ctx = recent[-2:]  # [前一个, 当前] → 预测下一个
        # 在cooccur表中搜同时与这两个签名的最关联的第三个
        scores = {}
        for sig in ctx:
            for (sa, sb), c in self._cooccur.items():
                if sa == sig and sb not in ctx:
                    scores[sb] = scores.get(sb, 0) + c
                elif sb == sig and sa not in ctx:
                    scores[sa] = scores.get(sa, 0) + c
        if not scores:
            return None, 0.0
        best = max(scores, key=scores.get)
        total = sum(scores.values())
        conf = scores[best] / max(total, 1)
        return best, conf
    
    def process_prediction(self, actual_sig):
        """L4: compare predict_next to actual signature.
        Confidence threshold auto-calibrates from the system's own distribution:
        tracks all confidence values, sets threshold at the 25th percentile —
        accepting the top 75% of the system's own confidence distribution."""
        if not actual_sig or actual_sig == 'self_obs':
            return None
        predicted, conf = self.predict_next()
        if predicted is None:
            return None
        # Track confidence for adaptive calibration (before threshold decision)
        if conf > 0:
            self._confidences.append(conf)
            if len(self._confidences) > 100:
                self._confidences.pop(0)
            # Auto-calibrate: threshold = 25th percentile of own confidence distribution
            if len(self._confidences) >= 20:
                sorted_conf = sorted(self._confidences)
                idx = max(0, len(sorted_conf) // 4)  # lower quartile
                self._conf_threshold = sorted_conf[idx]
        # Use adaptive threshold for decision
        if conf < self._conf_threshold:
            return None
        # L5: 记录准确率
        self._pred_total += 1
        if predicted == actual_sig:
            self._prediction_accuracy.append(1.0)
            self._pred_errors += 0
        else:
            self._prediction_accuracy.append(0.0)
            self._pred_errors += 1
            # L4: 预测误差 → 生成pred_err元帧
            err_str = f"pred_err_{conf:.2f}_{predicted[:8]}_{actual_sig[:8]}"
            # 用当前输入向量注入误差帧
            match = [f for f in self.frames if 'pred_err' in (f.sig_full or f.sig)]
            if not match:
                dummy_vec = (0.0,) * len(self.frames[0].vec) if self.frames else (0.0,) * _VEC_DIM
                if len(self.frames) >= self.capacity:
                    self.frames.sort(key=lambda x: x.weight)
                    r = self.frames.pop(0); self.total_weight -= r.weight
                nf = Frame(dummy_vec, weight=5.0, sig=err_str, layer="L4")
                self.frames.append(nf); self.total_weight += 5.0
        if len(self._prediction_accuracy) > PRED_WINDOW:
            self._prediction_accuracy.pop(0)
        # L6: 统摄—检测系统性准确率下降
        recent_acc = sum(self._prediction_accuracy[-10:]) / len(self._prediction_accuracy[-10:]) if self._prediction_accuracy else 1.0
        if not self._doubt_mode and len(self._prediction_accuracy) >= 10 and recent_acc < DOUBT_ON_THRESHOLD and self._last_accuracy > HEALTHY_ACC_THRESHOLD:
            self._doubt_mode = True
            doubt_str = f"sys_doubt_acc_{recent_acc:.2f}"
            match = [f for f in self.frames if 'sys_doubt' in (f.sig_full or f.sig)]
            if not match:
                dummy_vec = (0.0,) * len(self.frames[0].vec) if self.frames else (0.0,) * _VEC_DIM
                if len(self.frames) >= self.capacity:
                    self.frames.sort(key=lambda x: x.weight)
                    r = self.frames.pop(0); self.total_weight -= r.weight
                nf = Frame(dummy_vec, weight=10.0, sig=doubt_str, layer="L6")
                self.frames.append(nf); self.total_weight += 10.0
        elif self._doubt_mode and recent_acc > DOUBT_OFF_THRESHOLD:
            self._doubt_mode = False
        self._last_accuracy = recent_acc
        return {'predicted': predicted, 'actual': actual_sig, 'confidence': conf, 'accuracy': recent_acc}
    
    def metrics(self):
        """All key indicators in a single dict."""
        w=sorted([f.weight for f in self.frames], reverse=True)
        return {
            "frame_count": len(self.frames),
            "capacity": self.capacity,
            "total_weight": round(self.total_weight, 2),
            "efficiency": round(self.efficiency, 4),
            "utilization": round(self.utilization, 4),
            "stress": round(self.stress, 4),
            "structural_entropy": round(self.structural_entropy(), 4),
            "L4_frame_count": self.count_L4_frames(),
            "top_weights": [round(x,1) for x in w[:5]],
            "I(phi;X)": round(self.mutual_information_phi_X(), 6),
            "assoc_frames": self._assoc_frames,
            "self_observations": self._self_observe_count,
            "pred_total": self._pred_total,
            "pred_accuracy": round(sum(self._prediction_accuracy[-20:])/max(len(self._prediction_accuracy[-20:]),1),3) if self._prediction_accuracy else 0.0,
            "conf_threshold": round(self._conf_threshold, 4),
            "doubt_mode": self._doubt_mode,
            "derivative_frames": len(self._derivative_frames),
            "L4_meta_active": len([f for f in self.frames if 'dwdw' in (f.sig_full or f.sig)]),
            "layers": self.count_by_layer(),
        }

# ──────────────────────────────────────────────────────────────────
# GEME
# ──────────────────────────────────────────────────────────────────
class GEME:
    """Zero domain knowledge. No pretrained weights. No loss function.
    
    Extended with dynamic vocabulary (L1→L2 pipeline support):
      - vocab_mode: when True, surviving association frames are promoted
        to the vocabulary table after each induction cycle.
      - vocab: dict of {sig: (word_string, weight)} discovered from
        character-level processing.
      - promote_to_vocab(): scans memory, promotes eligible association
        frames to vocabulary entries.
      - get_vocab(): returns current vocabulary for L2 consumption."""
    def __init__(self,memory_cap=10,merge_thresh=None,cooccur_window=50,
                 cooccur_thresh=0.25,max_chains=5,time_window_size=0):
        self.memory=Memory(capacity=memory_cap,merge_thresh=merge_thresh,
                          cooccur_window=cooccur_window,cooccur_thresh=cooccur_thresh,
                          max_chains=max_chains)
        self._stress_accum=0.0; self._induction_threshold=TAU
        self.frame_count=0; self._last_induction=0; self._input_count=0
        self.time_window_size=time_window_size
        self._inputs_in_window=0
        # Dynamic vocabulary (for L1→L2 character-to-word pipeline)
        self.vocab_mode=False
        self.vocab={}  # sig → (word, weight)
        self._decoded_signatures={}
    
    def enable_vocab(self):
        """Enable dynamic vocabulary promotion."""
        self.vocab_mode=True
    
    def promote_to_vocab(self):
        """Promote surviving association frames to vocabulary.
        Called after induction. Only promotes frames with clean patterns."""
        for f in self.memory.frames:
            sig=f.sig_full or f.sig
            if "──" in sig and f.weight>5:
                # Extract characters from association signature
                parts=sig.split("──")
                chars=[]
                for p in parts:
                    for cm in range(32,126):
                        if f"c{cm:03d}" in p:
                            chars.append(chr(cm))
                if 2<=len(chars)<=8:
                    word="".join(sorted(set(chars),key=lambda x: chars.index(x)))
                    if word not in self.vocab or f.weight>self.vocab[word][1]:
                        self.vocab[word]=(word,f.weight)
                        self._decoded_signatures[word]=sig[:20]
    
    def get_vocab(self,min_weight=10):
        """Return vocabulary as {word: weight}. Filters by min_weight."""
        return {w:wgt for w,(_,wgt) in self.vocab.items() if wgt>=min_weight}
    
    def has_vocab(self,word):
        """Check if a word is in the discovered vocabulary."""
        return word in self.vocab

    def consolidate(self):
        """Consolidate after a time window: induce + self-observe + vocab."""
        self.memory.induction_clean()
        if self.vocab_mode: self.promote_to_vocab()
        self.memory._chain_count=0  # reset per window
        self._stress_accum=0.0; self._last_induction=self.frame_count
    
    def _induction_step(self, stress):
        """Time-window or stress-based induction. Shared by both process methods."""
        self._stress_accum+=stress*0.1
        fired=False
        if self.time_window_size>0:
            self._inputs_in_window+=1
            if self._inputs_in_window>=self.time_window_size:
                self.consolidate()
                self._inputs_in_window=0
                fired=True
        elif self._stress_accum>self._induction_threshold:
            cd=self.frame_count-self._last_induction
            if cd>=15:
                self.consolidate()
                fired=True
        return fired
    
    def process_sig(self, formula, sig=None):
        """Process a formula: encode to vector via symbol_vector, then delegate."""
        if sig is None: sig=structural_signature(formula)
        return self.process_vec(symbol_vector(formula), sig)
    
    def process_vec(self, vec, sig, src=""):
        """Process a pre-computed vector with signature (bypasses symbol_vector).
        For character-level processing where vectors must be distinct."""
        self.frame_count+=1; self._input_count+=1
        self.memory.observe(vec, sig, src)
        # 第5维：将输入传播到所有分支世界
        if self.memory._multiverse_enabled and self.memory._multiverse:
            new_mv=[]
            for branch_frames, step_branched, branch_id in self.memory._multiverse:
                if len(new_mv)>=20: break  # 上限防爆炸
                # 在分支帧集上找最近帧合并
                bi=-1; bd=float('inf')
                for i,f in enumerate(branch_frames):
                    # 动态维度：对齐长度
                    dl=min(len(vec),len(f.vec))
                    d=sum((vec[j]-f.vec[j])**2 for j in range(dl))
                    # 未对齐部分按不匹配处理（距离惩罚）
                    d += abs(len(vec)-len(f.vec)) * MULTIVERSE_DIM_PENALTY
                    if d<bd: bd=d; bi=i
                th=self.memory._adaptive_thresh() or DELTA
                if bi>=0 and bd<=th*th:
                    f=branch_frames[bi]
                    f.vec=tuple((f.vec[j]*f.weight+vec[j])/(f.weight+1) for j in range(len(vec)))
                    f.weight+=1.0; f.merged+=1
                else:
                    nf=deepcopy(branch_frames[0]) if branch_frames else None
                    if nf: branch_frames.append(nf)
                new_mv.append((branch_frames, step_branched, branch_id))
            self.memory._multiverse=new_mv
        stress=self.memory.stress
        ind=self._induction_step(stress)
        return {"frame":self.frame_count,"mem":len(self.memory.frames),
                "eff":round(self.memory.efficiency,4),"stress":round(stress,4),
                "induction":ind,"thresh":self.memory._merge_thresh_val}

    def evaluate_sig(self,sig):
        sp=set(sig.split("_"))
        sorted_w=sorted(f.weight for f in self.memory.frames)
        med=sorted_w[len(sorted_w)//2] if sorted_w else 1
        for f in self.memory.frames:
            if f.weight<med: continue
            fp=set(f.sig.split("_")); denom=min(len(sp),len(fp))
            if denom==0: continue
            ratio=len(sp&fp)/denom
            if ratio>=EVAL_MATCH_THRESHOLD: return 2
        return 3

    def metrics(self):
        """Unified metrics interface: returns all key indicators as dict."""
        m=self.memory.metrics()
        m["frame_count_total"]=self.frame_count
        m["input_count"]=self._input_count
        m["induction_threshold"]=self._induction_threshold
        if self._input_count>0:
            m["compression_ratio"]=round(self._input_count/max(len(self.memory.frames),1),1)
        return m

    # ──────────────────────────────────────────────────────────────
    # High-level API (friendly interface)
    # ──────────────────────────────────────────────────────────────
    def input(self, data, sig_hint=""):
        """Unified input: auto-detect text vs vector vs scalar.
        
        Examples:
            g.input("cat on mat")         # text → auto-encoded
            g.input([0.5, 0.3, ...])      # vector → direct
            g.input(42)                   # scalar → one-hot
        """
        import math as _m
        if isinstance(data, str):
            # Text input: character frequency → 27-dim vector
            char_counts = [0.0]*_VEC_DIM
            for ch in data:
                idx = ord(ch) % _VEC_DIM
                char_counts[idx] += 1.0
            norm = _m.sqrt(sum(x*x for x in char_counts))
            if norm > 0:
                char_counts = [x/norm for x in char_counts]
            sig = sig_hint or data[:8]
            return self.process_vec(char_counts, sig)
        elif isinstance(data, (list, tuple)):
            sig = sig_hint or 'vec'
            return self.process_vec(list(data), sig)
        elif isinstance(data, (int, float)):
            # Scalar: one-hot
            v = [0.0]*_VEC_DIM
            v[int(data) % _VEC_DIM] = 1.0
            sig = sig_hint or str(data)
            return self.process_vec(v, sig)
        else:
            raise TypeError(f"Unsupported input type: {type(data)}")

    def predict_next(self):
        """Return (predicted_label, confidence) for the next expected input.
        
        Returns:
            (str, float): predicted signature and confidence (0-1).
            (None, 0.0) if no prediction is available.
        """
        pred, conf = self.memory.predict_next()
        return (pred, round(conf, 3)) if pred else (None, 0.0)

    def anomaly_score(self):
        """How surprising is the current state? 0 = normal, 1 = very anomalous.
        
        Combines two signals:
          - prediction accuracy drop (recent vs long-term)
          - doubt mode flag
        
        Returns:
            float: 0.0 (stable) to 1.0 (highly anomalous)
        """
        m = self.metrics()
        if m.get('doubt_mode', False):
            return 0.8  # system is actively doubting
        acc = m.get('pred_accuracy', 0.0)
        if acc > HEALTHY_ACC_THRESHOLD:
            return 0.1
        elif acc > ANOMALY_MED_BOUND:
            return 0.3
        elif acc > ANOMALY_HIGH_BOUND:
            return 0.6
        else:
            return 0.9

    def state(self):
        """Human-readable summary of the system's internal state."""
        m = self.metrics()
        layers = m.get('layers', {})
        lines = [
            f"GEME State Summary",
            f"  Total inputs: {m.get('input_count', 0)}",
            f"  Frames: {m.get('frame_count', 0)} total",
            f"  By layer: {dict(sorted(layers.items()))}",
            f"  L4 active: {m.get('L4_frame_count', 0)}",
            f"  Prediction acc: {m.get('pred_accuracy', 0):.1%}",
            f"  Anomaly score: {self.anomaly_score():.2f}",
            f"  MI(phi;X): {m.get('I(phi;X)', 0):.4f}",
        ]
        return '\n'.join(lines)

    def save(self, path):
        """Save trained model state to file."""
        import json
        m = self.metrics()
        frames_data = [{
            'vec': f.vec, 'weight': f.weight,
            'sig': f.sig, 'layer': getattr(f, 'layer', 'L1')
        } for f in self.memory.frames]
        state = {
            'metrics': m,
            'frame_count': self.frame_count,
            'memory_cap': self.memory.capacity,
            'frames': frames_data,
        }
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)

    @classmethod
    def load(cls, path):
        """Load trained model state from file."""
        import json
        with open(path) as f:
            state = json.load(f)
        g = cls(memory_cap=state.get('memory_cap', 16))
        g.frame_count = state.get('frame_count', 0)
        g._input_count = state.get('input_count', state.get('frame_count', 0))
        for fd in state.get('frames', []):
            vec = fd['vec'] if isinstance(fd['vec'], (list, tuple)) else [0.0] * _VEC_DIM
            nf = Frame(tuple(vec), weight=fd.get('weight', 1.0),
                       sig=fd.get('sig', ''), layer=fd.get('layer', 'L1'))
            g.memory.frames.append(nf)
            g.memory.total_weight += nf.weight
        return g

    def input_file(self, path, encoding='utf-8'):
        """Process a text file line by line."""
        with open(path, encoding=encoding) as f:
            for line in f:
                line = line.strip()
                if line:
                    self.input(line)

# ──────────────────────────────────────────────────────────────────
# Self-test
# ──────────────────────────────────────────────────────────────────
if __name__=="__main__":
    # Quick smoke test: 100 inputs, expect no errors
    import random
    r=random.Random(42)
    g=GEME(memory_cap=16,cooccur_window=60)
    for _ in range(100):
        a=str(r.randint(0,9)); b=str(r.randint(0,9))
        f=eq(fn("swap",const(a),const(b)),fn("swap",const(b),const(a)))
        g.process_sig(f,structural_signature(f))
    print(f"OK: {g.frame_count} steps, {len(g.memory.frames)} frames, "
          f"efficiency={g.memory.efficiency:.3f}")
