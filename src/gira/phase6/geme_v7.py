"""GEME V7 — Weight regularization + Dynamic signatures + S4 semantics."""
from __future__ import annotations
from typing import List, Tuple
from collections import defaultdict
import math, random
from gira.phase3.entity import QEntity
from gira.phase3.language import Formula, var, forall, eq, fn, constant
from gira.phase4.pattern_tracker import compute_signature, PatternTracker

_ALPHABET = ["0","1","s","+","\u00d7","=","forall","exists","x","y","z","sub"]
_VEC_DIM = len(_ALPHABET)

def symbol_vector(formula) -> Tuple[float, ...]:
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
    return math.sqrt(sum((ai-bi)**2 for ai,bi in zip(a,b)))

def sig_edit(s1,s2):
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
    __slots__=("vec","weight","sig","age","merged")
    def __init__(self,vec,weight=1.0,sig=""):
        self.vec=vec; self.weight=weight; self.sig=sig[:30]; self.age=0; self.merged=0

class Memory:
    def __init__(self,capacity=10,merge_thresh=0.15,max_weight=100.0,s4_derive=True):
        self.frames=[]; self.capacity=capacity; self.merge_thresh=merge_thresh
        self.max_weight=max_weight; self.s4_derive=s4_derive
        self.total_weight=0.0; self.signature_pool=set()

    def observe(self,vec,sig):
        bi,bd=-1,float('inf')
        for i,f in enumerate(self.frames):
            d=vec_dist(vec,f.vec)
            if d<bd: bd=d; bi=i
        if bi>=0 and bd<self.merge_thresh:
            f=self.frames[bi]; self.total_weight-=f.weight
            f.vec=tuple((f.vec[j]*f.weight+vec[j])/(f.weight+1) for j in range(len(vec)))
            f.weight=min(self.max_weight,f.weight+1.0)
            f.merged+=1
            # Dynamic signature discovery
            combined="_".join(sorted(set(f.sig.split("_")+sig.split("_"))))
            if len(combined.split("_"))<=8: f.sig=combined[:30]
            self.total_weight+=f.weight
        else:
            nw=1.0+5.0*min(1.0,bd/max(self.merge_thresh,0.001)) if bi>=0 else 1.0
            nw=min(self.max_weight,nw)
            if len(self.frames)>=self.capacity:
                self.frames.sort(key=lambda x: x.weight)
                r=self.frames.pop(0); self.total_weight-=r.weight
            self.frames.append(Frame(vec,nw,sig)); self.total_weight+=nw

    def induction_clean(self):
        """Selective decay: unmerged frames decay, merged frames preserved."""
        for f in self.frames:
            self.total_weight-=f.weight
            if f.merged==0: f.weight*=0.80  # noise: heavy decay
            elif f.merged<3: f.weight*=0.95 # weak pattern: light decay
            f.weight=max(1.0,min(self.max_weight,f.weight))
            self.total_weight+=f.weight
            f.age+=1
        self.frames.sort(key=lambda x: x.weight-x.age*0.05, reverse=True)
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
    @property
    def rule_count(self):
        if not self.frames: return 0
        avg=self.total_weight/len(self.frames)
        return sum(1 for f in self.frames if f.weight>avg*2)
    @property
    def s4_ratio(self):
        tw=self.total_weight or 1
        return sum(f.weight for f in self.frames if "fn" in f.sig or "sub" in f.sig)/tw


class GEME:
    def __init__(self,axioms=None,mem_cap=10,merge_thresh=0.15,max_weight=100.0,s4_derive=True):
        if axioms is None:
            from gira.phase3.q_axioms import robinson_q; axioms=robinson_q()
        self.entity=QEntity()
        self.entity.inference.axioms=axioms.copy()
        ax_strs={str(a) for a in axioms}
        self.entity.inference.theorems=[a for a in self.entity.inference.theorems if str(a) in ax_strs]
        self.memory=Memory(capacity=mem_cap,merge_thresh=merge_thresh,max_weight=max_weight,s4_derive=s4_derive)
        self._stress_accum=0.0; self._induction_threshold=0.6
        self.frame_count=0; self.system_level=0; self._last_induction=0

    def process(self,formula) -> dict:
        self.frame_count+=1
        S_F,_=self.entity.inference.harm_operator.classifier.classify(
            formula,self.entity.inference.axioms,self.entity.inference.theorems)
        sig=compute_signature(formula)
        self.memory.observe(symbol_vector(formula),sig)
        stress=self.memory.stress; self._stress_accum+=stress*0.1
        induction_fired=False
        if self._stress_accum>self._induction_threshold:
            cd=self.frame_count-self._last_induction
            if cd>=15: self.memory.induction_clean(); self._stress_accum=0.0; self._last_induction=self.frame_count; induction_fired=True
        return {
            "frame":self.frame_count,"mem":len(self.memory.frames),
            "rules":self.memory.rule_count,"eff":round(self.memory.efficiency,4),
            "util":round(self.memory.utilization,4),"stress":round(stress,4),
            "accum":round(self._stress_accum,4),"S_F":S_F,"L_E":self.system_level,
            "sig":sig[:20],"induction":induction_fired,"s4_r":round(self.memory.s4_ratio,3),
        }

    def evaluate(self,formula):
        sig=compute_signature(formula); sp=set(sig.split("_"))-{"forall"}
        if not self.memory.frames:
            S_F,_=self.entity.inference.harm_operator.classifier.classify(
                formula,self.entity.inference.axioms,self.entity.inference.theorems)
            return S_F
        sorted_w=sorted(f.weight for f in self.memory.frames)
        median=sorted_w[len(sorted_w)//2]; min_survive=max(median,2.0)
        for f in self.memory.frames:
            if f.weight<min_survive: continue
            fp=set(f.sig.split("_")); ratio=len(sp&fp)/min(len(sp),len(fp))
            if ratio>=0.75: return 2
        S_F,_=self.entity.inference.harm_operator.classifier.classify(
            formula,self.entity.inference.axioms,self.entity.inference.theorems)
        return S_F

    def emergence_score(self,sig):
        tp=set(sig.split("_")); best=0
        for f in self.memory.frames:
            fp=set(f.sig.split("_")); ratio=len(tp&fp)/min(len(tp),len(fp))
            if ratio>=0.75 and f.weight>best: best=f.weight
        sorted_w=sorted(f.weight for f in self.memory.frames)
        med=sorted_w[len(sorted_w)//2] if sorted_w else 1
        return best>=med, best/med
