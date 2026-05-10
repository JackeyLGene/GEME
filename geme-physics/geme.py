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
from typing import List, Tuple
import math, statistics

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
    __slots__=("vec","weight","sig","sig_full","src","age","merged","fid")
    def __init__(self,vec,weight=1.0,sig="",src=""):
        _FRAME_ID_COUNTER[0]+=1; self.fid=_FRAME_ID_COUNTER[0]
        self.vec=vec; self.weight=weight; self.sig=sig[:30]; self.sig_full=sig
        self.src=src[:80] if src else sig[:30]; self.age=0; self.merged=0

# ──────────────────────────────────────────────────────────────────
# Memory (competitive memory economy)
# ──────────────────────────────────────────────────────────────────
class Memory:
    def __init__(self,capacity=10,merge_thresh=None,cooccur_window=50,
                 cooccur_thresh=0.25,max_chains=5):
        self.frames=[]; self.capacity=capacity
        self.merge_thresh=merge_thresh
        self._merge_thresh_val=merge_thresh or 0.15
        self.cooccur_thresh=cooccur_thresh
        self.total_weight=0.0
        self._window=[]; self._win_max=cooccur_window
        self._step_counter=0
        self._cooccur={}; self._assoc_frames=0
        self._chain_count=0; self.max_chains=max_chains
        self._merge_dists=[]
        self._learn_dists=[]
        self._self_observe_count=0
        self._chain_cooccur_thresh=5
        self.preserve_sig=True  # 合并时保持原始签名

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

    def observe(self,vec,sig,src=""):
        bi,bd=-1,float('inf')
        # Compute threshold FIRST (before candidate selection)
        thresh=self._adaptive_thresh()
        self._merge_thresh_val=thresh or 0.0
        
        candidates=[]
        for i,f in enumerate(self.frames):
            d=vec_dist(vec,f.vec)
            if d<bd: bd=d; bi=i
            if hasattr(self,'quantum_mode') and self.quantum_mode and thresh:
                if d<=thresh: candidates.append((i,d,f))
        
        if thresh is None and bi>=0 and bd!=float('inf'):
            self._learn_dists.append(bd)
            if len(self._learn_dists)>200: self._learn_dists.pop(0)
            
        # Quantum merge: probabilistic selection among candidates
        if hasattr(self,'quantum_mode') and self.quantum_mode and len(candidates)>0:
            import random as _qr
            if not hasattr(self,'_qrand'): self._qrand = _qr.Random(_qr.randint(0,999999))
            psum = 0.0; probs = []
            for i,d,f in candidates:
                p = math.exp(-d/max(self._merge_thresh_val,0.001))
                probs.append((i,d,f,p)); psum += p
            if psum > 0:
                r = self._qrand.random() * psum; acc = 0.0
                for i,d,f,p in probs:
                    acc += p
                    if r <= acc: bi=i; bd=d; break
                self._merge_dists.append(bd)
                if len(self._merge_dists)>100: self._merge_dists.pop(0)
                f=self.frames[bi]; self.total_weight-=f.weight
                f.vec=tuple((f.vec[j]*f.weight+vec[j])/(f.weight+1) for j in range(len(vec)))
                f.weight+=1.0; f.merged+=1
                if not self.preserve_sig:
                    combined="_".join(sorted(set(f.sig.split("_")+sig.split("_"))))
                    if len(combined.split("_"))<=8: f.sig=combined[:30]
                self.total_weight+=f.weight; self._step_counter+=1
                step_id=self._step_counter
                self._window.append((sig,step_id,tuple(vec)))
                if len(self._window)>self._win_max: self._window.pop(0)
                return
                
        # Standard merge
        if thresh is not None and bi>=0 and bd<=thresh and (not sig or sig[:30]==self.frames[bi].sig):
            self._merge_dists.append(bd)
            if len(self._merge_dists)>100: self._merge_dists.pop(0)
            f=self.frames[bi]; self.total_weight-=f.weight
            f.vec=tuple((f.vec[j]*f.weight+vec[j])/(f.weight+1) for j in range(len(vec)))
            f.weight+=1.0; f.merged+=1
            if not self.preserve_sig:
                combined="_".join(sorted(set(f.sig.split("_")+sig.split("_"))))
                if len(combined.split("_"))<=8: f.sig=combined[:30]
            self.total_weight+=f.weight
        else:
            if thresh is None or thresh==0.0: nw=1.0
            elif bd!=float('inf'): nw=1.0+5.0*max(0,1.0-bd/max(thresh,0.001))
            else: nw=1.0
            if len(self.frames)>=self.capacity:
                self.frames.sort(key=lambda x: x.weight-x.age*0.1)
                r=self.frames.pop(0); self.total_weight-=r.weight
            self.frames.append(Frame(vec,nw,sig,src)); self.total_weight+=nw
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
                    existing=[f for f in self.frames if (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig)==assoc_sig]
                    if existing:
                        for exf in existing:
                            self.total_weight-=exf.weight; exf.weight+=0.5; self.total_weight+=exf.weight
                    else:
                        base_vecs=[]
                        for f in self.frames:
                            fs=f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
                            if fs in (sa,sb): base_vecs.append(f.vec)
                        if len(base_vecs)<2: continue
                        total_w=sum(f.weight for f in self.frames if (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig) in (sa,sb))
                        assoc_vec=tuple(sum(f.vec[j]*f.weight for f in self.frames if (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig) in (sa,sb))/max(total_w,1) for j in range(_VEC_DIM))
                        if len(self.frames)>=self.capacity:
                            self.frames.sort(key=lambda x: x.weight); r=self.frames.pop(0); self.total_weight-=r.weight
                        self.frames.append(Frame(assoc_vec,weight=float(count),sig=assoc_sig)); self.total_weight+=float(count); self._assoc_frames+=1
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
                    self.frames.append(Frame((0.0,)*_VEC_DIM,weight=chain_w,sig=ms))
                    self.total_weight+=chain_w; self._chain_count+=1; formed+=1
    
    def self_observe(self):
        """Self-observation: system observes its own frame economy.
        Uses stable frame IDs (fid) for co-occurrence tracking.
        Chains form between frames that co-occur in self-observation."""
        self._self_observe_count+=1
        fids=[f.fid for f in self.frames if f.weight>2]
        feed_time=self._step_counter
        for fid in fids:
            self._window.append((f"fid_{fid}",feed_time,(0.0,)*_VEC_DIM))
            if len(self._window)>self._win_max:
                self._window.pop(0)
        for i in range(len(fids)):
            for j in range(i+1,len(fids)):
                ckey=tuple(sorted([f"fid_{fids[i]}",f"fid_{fids[j]}"]))
                self._cooccur[ckey]=self._cooccur.get(ckey,0)+1
        self._form_chains()
    
    def induction_clean(self):
        self.self_observe()  # observe before pruning
        for f in self.frames:
            self.total_weight-=f.weight
            if f.merged==0: f.weight*=0.80
            elif f.merged<3: f.weight*=0.95
            f.weight=max(1.0,f.weight)
            self.total_weight+=f.weight; f.age+=1
        self.frames.sort(key=lambda x: x.weight-x.age*0.05,reverse=True)
        half=max(1,len(self.frames)//2)
        for f in self.frames[half:]: self.total_weight-=f.weight
        self.frames=self.frames[:half]

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
        self._stress_accum=0.0; self._induction_threshold=0.6
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
            sig=f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
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
        self.frame_count+=1; self._input_count+=1
        if sig is None: sig=structural_signature(formula)
        self.memory.observe(symbol_vector(formula), sig)
        stress=self.memory.stress
        ind=self._induction_step(stress)
        return {"frame":self.frame_count,"mem":len(self.memory.frames),
                "eff":round(self.memory.efficiency,4),"stress":round(stress,4),
                "induction":ind,"thresh":self.memory._merge_thresh_val}
    
    def process_vec(self, vec, sig, src=""):
        """Process a pre-computed vector with signature (bypasses symbol_vector).
        For character-level processing where vectors must be distinct."""
        self.frame_count+=1; self._input_count+=1
        self.memory.observe(vec, sig, src)
        stress=self.memory.stress
        ind=self._induction_step(stress)
        return {"frame":self.frame_count,"mem":len(self.memory.frames),
                "eff":round(self.memory.efficiency,4),"stress":round(stress,4),
                "induction":ind,"thresh":self.memory._merge_thresh_val}
        induction_fired=False
        if self._stress_accum>self._induction_threshold:
            cd=self.frame_count-self._last_induction
            if cd>=15:
                self.memory.induction_clean()
                if self.vocab_mode: self.promote_to_vocab()
                self._stress_accum=0.0; self._last_induction=self.frame_count
                induction_fired=True
        return {"frame":self.frame_count,"mem":len(self.memory.frames),
                "eff":round(self.memory.efficiency,4),"stress":round(stress,4),
                "induction":induction_fired,"thresh":self.memory._merge_thresh_val}

    def evaluate_sig(self,sig):
        sp=set(sig.split("_"))
        sorted_w=sorted(f.weight for f in self.memory.frames)
        med=sorted_w[len(sorted_w)//2] if sorted_w else 1
        for f in self.memory.frames:
            if f.weight<med: continue
            fp=set(f.sig.split("_")); ratio=len(sp&fp)/min(len(sp),len(fp))
            if ratio>=0.75: return 2
        return 3

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
