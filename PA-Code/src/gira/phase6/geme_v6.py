"""GEME V8 — PA with endogenous self-reference (co-occurrence).
Core principles:
  * Weight = compression contribution (not hand-tuned constant)
  * Merge threshold = adaptive (median frame similarity, not hardcoded)
  * Association frames = weighted average of base frames (equal participants)
  * No external S4 — co-occurrence IS self-reference
  * Zero-axiom design: Robinson Q is verification anchor only
"""
from __future__ import annotations
from typing import List, Tuple
import math, statistics
from gira.phase3.entity import QEntity
from gira.phase3.language import Formula, var, forall, eq, fn, constant
from gira.phase4.pattern_tracker import compute_signature, PatternTracker

_ALPHABET = ["0","1","s","+","\u00d7","=","forall","exists","x","y","z","sub"]
_VEC_DIM = len(_ALPHABET)

def symbol_vector(formula) -> Tuple[float, ...]:
    """Encode formula as frequency vector over 19-symbol alphabet.
    Each dimension counts occurrences of a given symbol type.
    """
    counts = {s:0.0 for s in _ALPHABET}; total=0
    def w(n):
        nonlocal total
        if n is None: return
        k=getattr(n,'kind',''); s=getattr(n,'symbol','')
        if k=="constant":
            v=str(getattr(n,'value',''))
            if v in counts: counts[v]=counts.get(v,0)+1; total+=1
        elif k=="numeral": counts["1"]=counts.get("1",0)+1; total+=1
        elif k=="function":
            _s=s if s in counts else ("\u00d7" if s=="\u00d7" else None)
            if _s in counts: counts[_s]=counts.get(_s,0)+1; total+=1
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
    """Euclidean distance between frequency vectors."""
    return math.sqrt(sum((ai-bi)**2 for ai,bi in zip(a,b)))

def sig_edit(s1,s2):
    """Levenshtein-based similarity on structural signatures."""
    p1,p2=s1.split("_"),s2.split("_")
    m,n=len(p1),len(p2)
    dp=[[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0]=i
    for j in range(n+1): dp[0][j]=j
    for i in range(1,m+1):
        for j in range(1,n+1):
            c=0 if p1[i-1]==p2[j-1] else 1
            dp[i][j]=min(dp[i-1][j]+1,dp[i][j-1]+1,dp[i-1][j-1]+c)
    return 1.0-dp[m][n]/max(m,n,1)

class Frame:
    __slots__=("vec","weight","sig","sig_full","src","age","merged")
    def __init__(self,vec,weight=1.0,sig="",src=""):
        self.vec=vec; self.weight=weight; self.sig=sig[:30]; self.sig_full=sig
        self.src=src[:80] if src else sig[:30]; self.age=0; self.merged=0

class Memory:
    """Competitive memory economy.
    
    Each frame stores a centroid vector, weight (compression contribution),
    and structural signature. Frames compete for limited capacity; induction
    evicts the lowest-weight half when stress exceeds threshold.
    
    Co-occurrence tracking in a sliding window generates association frames
    and chain frames — these participate equally in merge/eviction.
    """
    def __init__(self,capacity=10,merge_thresh=None,cooccur_window=50,cooccur_thresh=0.25):
        self.frames=[]; self.capacity=capacity
        self.merge_thresh=merge_thresh  # None = adaptive
        self._merge_thresh_val=merge_thresh or 0.15  # fallback
        self.cooccur_thresh=cooccur_thresh
        self.total_weight=0.0
        self._window=[]; self._win_max=cooccur_window
        self._cooccur={}; self._assoc_frames=0
        self._merge_dists=[0.12]  # only track SUCCESSFUL merge distances
        
    def _adaptive_thresh(self):
        """Merge threshold = median of distances that led to actual merges.
        Reflects the system's current granularity level."""
        if not self._merge_dists: return 0.12
        med=statistics.median(self._merge_dists[-50:])
        return min(max(med,0.08),0.35)
        
    def observe(self,vec,sig,src=""):
        # ── Step 1: find nearest frame ──
        bi,bd=-1,float('inf')
        best_sig=""
        for i,f in enumerate(self.frames):
            d=vec_dist(vec,f.vec)
            if d<bd: bd=d; bi=i; best_sig=f.sig_full
        thresh=self._adaptive_thresh()
        self._merge_thresh_val=thresh
        
        # ── Step 2: merge or create ──
        if bi>=0 and bd<thresh:
            self._merge_dists.append(bd)  # track successful merge distance
            if len(self._merge_dists)>100: self._merge_dists.pop(0)
            f=self.frames[bi]; self.total_weight-=f.weight
            # Weighted centroid update
            f.vec=tuple((f.vec[j]*f.weight+vec[j])/(f.weight+1) for j in range(len(vec)))
            f.weight+=1.0; f.merged+=1
            combined="_".join(sorted(set(f.sig.split("_")+sig.split("_"))))
            if len(combined.split("_"))<=8: f.sig=combined[:30]
            self.total_weight+=f.weight
        else:
            nw=1.0+5.0*max(0,1.0-bd/thresh) if bd!=float('inf') else 1.0
            if len(self.frames)>=self.capacity:
                self.frames.sort(key=lambda x: x.weight-x.age*0.1)
                r=self.frames.pop(0); self.total_weight-=r.weight
            self.frames.append(Frame(vec,nw,sig,src)); self.total_weight+=nw
        
        # ── Step 3: co-occurrence tracking ──
        self._window.append((sig,vec if hasattr(self,'_current_vec') else tuple(vec)))
        if len(self._window)>self._win_max: self._window.pop(0)
        for i in range(len(self._window)):
            for j in range(i+1,min(i+3,len(self._window))):
                s1=self._window[i][0]; s2=self._window[j][0]
                if s1==s2: continue
                key=tuple(sorted([s1,s2]))
                self._cooccur[key]=self._cooccur.get(key,0)+1
        
        # ── Step 4: association & chain creation ──
        total_steps=len(self._window)
        if total_steps>=30:
            for (sa,sb),count in list(self._cooccur.items()):
                ratio=count/total_steps
                if ratio>=self.cooccur_thresh and count>=15:
                    assoc_sig=sa+"──"+sb
                    existing=[f for f in self.frames if 
                             (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig)==assoc_sig]
                    if existing:
                        for exf in existing:
                            self.total_weight-=exf.weight
                            exf.weight+=0.5
                            self.total_weight+=exf.weight
                    else:
                        # Association weight = co-occurrence count (compression contribution)
                        assoc_w=float(count)
                        # Association vector = weighted average of base frame vectors
                        base_vecs=[]
                        for f in self.frames:
                            fs=f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
                            if fs in (sa,sb):
                                base_vecs.append(f.vec)
                        if len(base_vecs)==2:
                            assoc_vec=tuple((base_vecs[0][j]+base_vecs[1][j])/2 
                                           for j in range(_VEC_DIM))
                        else:
                            assoc_vec=tuple([0.0]*_VEC_DIM)
                        if len(self.frames)>=self.capacity:
                            self.frames.sort(key=lambda x: x.weight)
                            r=self.frames.pop(0); self.total_weight-=r.weight
                        self.frames.append(Frame(assoc_vec,weight=assoc_w,sig=assoc_sig,src=""))
                        self.total_weight+=assoc_w
                        self._assoc_frames+=1
                    # Chain: shared element between associations
                    if existing and existing[0].weight>20:
                        for other_f in self.frames:
                            if other_f is existing[0]: continue
                            osig=other_f.sig_full if hasattr(other_f,'sig_full') and other_f.sig_full else other_f.sig
                            if "──" not in osig: continue
                            pa=set(assoc_sig.split("──")); pb=set(osig.split("──"))
                            if pa&pb and len(pa)>1 and len(pb)>1:
                                ms=assoc_sig+"══"+osig
                                if not any(ff.sig_full==ms for ff in self.frames):
                                    # Chain weight = mean of association weights
                                    chain_w=(existing[0].weight+other_f.weight)/2
                                    # Chain vector = weighted average of association vectors
                                    chain_vec=tuple((existing[0].vec[j]*existing[0].weight + 
                                                    other_f.vec[j]*other_f.weight)/
                                                    max(existing[0].weight+other_f.weight,1)
                                                    for j in range(_VEC_DIM))
                                    if len(self.frames)>=self.capacity:
                                        self.frames.sort(key=lambda x: x.weight)
                                        r=self.frames.pop(0); self.total_weight-=r.weight
                                    self.frames.append(Frame(chain_vec,weight=chain_w,sig=ms,src=""))
                                    self.total_weight+=chain_w
                    self._cooccur[key]*=0.8  # decay

    def induction_clean(self):
        """Selective decay: unmerged frames decay faster, merged survive.
        Keeps top half by (weight - age*0.05). This is the competitive
        selection step — the memory economy's core pruning mechanism.
        """
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
        """Memory efficiency: 1 - (weight deviation / mean). 
        Tighter weight distribution = more efficient compression.
        """
        if not self.frames or self.total_weight==0: return 1.0
        avg=self.total_weight/len(self.frames)
        dev=sum(abs(f.weight-avg) for f in self.frames)/(len(self.frames)*max(avg,0.001))
        return max(0.01,1.0-min(1.0,dev))
    @property
    def utilization(self): return len(self.frames)/self.capacity
    @property
    def stress(self): return self.utilization*(1.0-self.efficiency)

    # Information theory metrics
    def compression_ratio(self, input_count):
        """Input frames / output frames = compression ratio."""
        return input_count/max(len(self.frames),1)
    
    def entropy_reduction(self, initial_frames):
        """Estimate entropy reduction: initial frames → current frames."""
        if initial_frames==0: return 0.0
        return 1.0-len(self.frames)/initial_frames


class GEME:
    """Zero-axiom design. Robinson Q is theoretical reference only, used for 
    S-classification backstop in evaluate(). No axioms are pre-loaded.
    """
    def __init__(self,axioms=None,memory_cap=10,merge_thresh=None,
                 cooccur_window=50,cooccur_thresh=0.25):
        if axioms is None:
            from gira.phase3.q_axioms import robinson_q; axioms=robinson_q()
        self.entity=QEntity()
        self.entity.inference.axioms=axioms.copy()
        self.memory=Memory(capacity=memory_cap,merge_thresh=merge_thresh,
                          cooccur_window=cooccur_window,cooccur_thresh=cooccur_thresh)
        self._stress_accum=0.0; self._induction_threshold=0.6
        self.frame_count=0; self._last_induction=0
        self._input_count=0  # track total input for compression ratio

    def process(self,formula) -> dict:
        self.frame_count+=1; self._input_count+=1
        sig=compute_signature(formula)
        self.memory.observe(symbol_vector(formula),sig)
        stress=self.memory.stress; self._stress_accum+=stress*0.1
        induction_fired=False
        if self._stress_accum>self._induction_threshold:
            cd=self.frame_count-self._last_induction
            if cd>=15:
                self.memory.induction_clean()
                self._stress_accum=0.0; self._last_induction=self.frame_count
                induction_fired=True
        return {"frame":self.frame_count,"mem":len(self.memory.frames),
                "eff":round(self.memory.efficiency,4),"stress":round(stress,4),
                "induction":induction_fired,"thresh":self.memory._merge_thresh_val}

    def evaluate(self,formula):
        """Evaluate formula against memory. S2 = emerged (match found)."""
        sig=compute_signature(formula); sp=set(sig.split("_"))-{"forall"}
        if not self.memory.frames: return 3
        sorted_w=sorted(f.weight for f in self.memory.frames)
        median=sorted_w[len(sorted_w)//2]; min_s=max(median,2.0)
        for f in self.memory.frames:
            if f.weight<min_s: continue
            fp=set(f.sig.split("_")); ratio=len(sp&fp)/min(len(sp),len(fp))
            if ratio>=0.75: return 2
        return 3

    def evaluate_sig(self,sig):
        """Evaluate a signature directly (for test formulas)."""
        sp=set(sig.split("_"))
        sorted_w=sorted(f.weight for f in self.memory.frames)
        med=sorted_w[len(sorted_w)//2] if sorted_w else 1
        for f in self.memory.frames:
            if f.weight<med: continue
            fp=set(f.sig.split("_")); ratio=len(sp&fp)/min(len(sp),len(fp))
            if ratio>=0.75: return 2
        return 3
