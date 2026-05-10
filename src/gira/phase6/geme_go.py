"""
GEME GO — Geometry phase. SAS → ASA → SSS chain emergence.
"""
from __future__ import annotations
from typing import List, Tuple
import math
from gira.phase3.entity import QEntity
from gira.phase3.language import Formula, Term, constant

# ── Geometric alphabet (18 chars) ──
_ALPHABET = [
    "A","B","C","D","E","F",
    "seg","angle","triangle",
    "equiv","conj","impl",
    "lparen","rparen","comma","dot",
    "point","line",
]
_VEC_DIM = len(_ALPHABET)

_ALPHABET += ["△"]  # triangle symbol for axiom encoding

def formula_source(f) -> str:
    """Convert formula tree to standard geometric notation.
    
    angle(A,B,C) = angle at vertex B with arms BA, BC → ∠B
    seg(A,B) = segment AB → AB
    △(A,B,C) = triangle ABC → △ABC
    """
    if f is None: return ""
    k = getattr(f, 'kind', '')
    s = getattr(f, 'symbol', '')
    if k in ("constant",): return str(getattr(f, 'value', ''))
    if k == "variable": return str(getattr(f, 'symbol', ''))
    if k == "function":
        pts = "".join(formula_source(a) for a in getattr(f, 'args', []))
        if s == "seg": return pts
        if s == "angle":
            # 3-arg form only: angle(A,B,C) = vertex at B → ∠ABC
            args = [formula_source(a) for a in getattr(f, 'args', [])]
            if len(args) == 3: return f"∠{''.join(args)}"
            return f"∠{pts}"
        if s == "△": return f"△{pts}"
        return f"{s}({pts})"
    if k == "equation":
        return f"({formula_source(f.left)} ≡ {formula_source(f.right)})"
    if k == "conjunction":
        return f"({formula_source(f.left)} ∧ {formula_source(f.right)})"
    if k == "implication":
        return f"({formula_source(f.left)} → {formula_source(f.right)})"
    return str(f)

def symbol_vector(formula) -> Tuple[float, ...]:
    counts = {s:0.0 for s in _ALPHABET}; total=0
    def w(n):
        nonlocal total
        if n is None: return
        k=getattr(n,'kind',''); s=getattr(n,'symbol','')
        if k in ("constant","variable"):
            if s in counts: counts[s]=counts.get(s,0)+1; total+=1
        elif k=="function":
            if s in counts: counts[s]=counts.get(s,0)+1; total+=1
        elif k=="equation": counts["equiv"]=counts.get("equiv",0)+1; total+=1
        elif k=="conjunction": counts["conj"]=counts.get("conj",0)+1; total+=1
        elif k=="implication": counts["impl"]=counts.get("impl",0)+1; total+=1
        if getattr(n,'left',None): w(n.left)
        if getattr(n,'right',None): w(n.right)
    w(formula)
    if total==0: total=1
    return tuple(counts[s]/total for s in _ALPHABET)

def vec_dist(a,b):
    return math.sqrt(sum((ai-bi)**2 for ai,bi in zip(a,b)))

def structural_signature(formula) -> str:
    """Generate formula structure tree signature (no variable names)."""
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
        elif k=="variable": pass  # skip variable names
        else: pass  # skip constants
        if getattr(n,'left',None): walk(n.left)
        if getattr(n,'right',None): walk(n.right)
    walk(formula)
    return "_".join(parts) if parts else "empty"

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

# ── MemoryFrame with src field ──
class Frame:
    __slots__=("vec","weight","sig","src","age","merged","sig_full")
    def __init__(self,vec,weight=1.0,sig="",src=""):
        self.vec=vec; self.weight=weight; self.sig=sig[:40]; self.sig_full=sig; self.src=src[:120]
        self.age=0; self.merged=0

class Memory:
    def __init__(self,capacity=10,merge_thresh=0.15,cooccur_window=50,cooccur_thresh=0.4):
        self.frames=[]; self.capacity=capacity
        self.merge_thresh=merge_thresh; self.total_weight=0.0
        # ── Association (co-occurrence) mechanism ──
        self._window=[]   # ring buffer of recent sigs+src
        self._win_max=cooccur_window
        self._cooccur_thresh=cooccur_thresh
        self._cooccur={}  # {(sig_a,sig_b): count, ...}
        self._assoc_frames=0  # counter for created association frames
    def observe(self,vec,sig,src):
        bi,bd=-1,0.0
        for i,f in enumerate(self.frames):
            d=sig_edit(sig,f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig)
            if d>bd: bd=d; bi=i
        if bi>=0 and bd>=self.merge_thresh:
            f=self.frames[bi]; self.total_weight-=f.weight
            f.vec=tuple((f.vec[j]*f.weight+vec[j])/(f.weight+1) for j in range(len(vec)))
            f.weight+=1.0; f.merged+=1
            # Keep src concise: abbreviate merged instances
            f.src = src[:60]  # keep last src, not chain
            combined="_".join(sorted(set(f.sig.split("_")+sig.split("_"))))
            if len(combined.split("_"))<=10: f.sig=combined[:40]
            self.total_weight+=f.weight
        else:
            nw=1.0+5.0*max(0.0,1.0-bd/max(self.merge_thresh,0.001)) if bi>=0 else 1.0  # lower similarity → higher weight
            if len(self.frames)>=self.capacity:
                self.frames.sort(key=lambda x: x.weight-x.age*0.1)
                r=self.frames.pop(0); self.total_weight-=r.weight
            self.frames.append(Frame(vec,nw,sig,src)); self.total_weight+=nw
        # ── Co-occurrence: track which sigs appear together ──
        self._window.append((sig,src))
        if len(self._window)>self._win_max: self._window.pop(0)
        # Count co-occurrence pairs in window
        for i in range(len(self._window)):
            for j in range(i+1,min(i+3,len(self._window))):  # only close pairs
                s1=self._window[i][0]; s2=self._window[j][0]; src1=self._window[i][1]; src2=self._window[j][1]
                if s1==s2: continue
                key=tuple(sorted([s1,s2]))
                self._cooccur[key]=self._cooccur.get(key,0)+1
        # Detect: has a pair co-occurred enough to indicate association?
        total_steps=len(self._window)
        if total_steps>=30:  # need minimum window
            for (sa,sb),count in list(self._cooccur.items()):
                ratio=count/total_steps
                if ratio>=self._cooccur_thresh and count>=20:  # require absolute+relative
                    assoc_sig=sa+"──"+sb
                    # Dedup: check if same link exists (exact match, NOT substring in chain)
                    existing=[f for f in self.frames if 
                             (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig) == assoc_sig]
                    if existing:
                        for exf in existing:
                            self.total_weight-=exf.weight
                            exf.weight+=0.5
                            self.total_weight+=exf.weight
                    else:
                        # Capacity guard for side-effect creations
                        if len(self.frames) >= self.capacity:
                            self.frames.sort(key=lambda x: x.weight)
                            r=self.frames.pop(0)
                            self.total_weight-=r.weight
                        assoc_vec=tuple([0.0]*len(_ALPHABET))
                        self.frames.append(Frame(assoc_vec,weight=10.0,sig=assoc_sig,src=f"[co-occur: {sa[:15]} × {sb[:15]}]"))
                        self.total_weight+=10.0
                        self._assoc_frames+=1
                    # ── RECURSIVE SELF-REFERENCE ──
                    # Any two frames sharing base elements → link frame.
                    # Level 1: input frames → ── links (concepts)
                    # Level 2: links with shared element → ══ links (chains)
                    # Level N: same mechanism, N levels of self-reference
                    if existing and existing[0].weight > 30:
                        for other_f in self.frames:
                            if other_f is existing[0]: continue
                            osig = other_f.sig_full if hasattr(other_f,'sig_full') and other_f.sig_full else other_f.sig
                            if "──" not in osig: continue
                            parts_a = set(assoc_sig.split("──"))
                            parts_b = set(osig.split("──"))
                            shared = parts_a & parts_b
                            if shared and len(parts_a) > 1 and len(parts_b) > 1:
                                ms = assoc_sig + "══" + osig
                                exists = any(ff.sig_full == ms for ff in self.frames)
                                if not exists:
                                    if len(self.frames) >= self.capacity:
                                        self.frames.sort(key=lambda x: x.weight)
                                        r=self.frames.pop(0)
                                        self.total_weight-=r.weight
                                    mvec = tuple([0.0]*len(_ALPHABET))
                                    self.frames.append(Frame(mvec, weight=15.0, sig=ms,
                                        src=f"[chain: {assoc_sig[:15]}══{osig[:15]}]"))
                                    self.total_weight += 15.0
                    self._cooccur[key]*=0.8
    
    def induction_clean(self,chain=None):
        for f in self.frames:
            self.total_weight-=f.weight
            if f.merged==0: f.weight*=0.80
            elif f.merged<3: f.weight*=0.95
            f.weight=max(1.0,f.weight)
            self.total_weight+=f.weight; f.age+=1
        # Promoted frames: never evict (axioms, high-weight)
        promoted=[f for f in self.frames if f.weight>=20 or (f.merged==0 and len(self.frames)<3)]
        others=[f for f in self.frames if f not in promoted]
        others.sort(key=lambda x: x.weight-x.age*0.05,reverse=True)
        keep=promoted+others[:max(1,self.capacity//2-len(promoted))]
        for f in self.frames:
            if f not in keep: self.total_weight-=f.weight
        self.frames=keep

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

# ── ProofChain (from proof_viewer) ──
from gira.phase6.proof_viewer import ProofChain

class GEME:
    def __init__(self,axioms=None,memory_cap=10,merge_thresh=0.15,
                 cooccur_window=50,cooccur_thresh=0.4):
        self.entity=QEntity()
        self.entity.inference.axioms=list(axioms or [])
        self.entity.inference.theorems=[]
        self.memory=Memory(capacity=memory_cap,merge_thresh=merge_thresh,
                          cooccur_window=cooccur_window,cooccur_thresh=cooccur_thresh)
        self.chain=ProofChain()
        self._stress_accum=0.0; self._induction_threshold=0.6
        self.frame_count=0; self._last_induction=0
        # Pre-load axioms
        for a in (axioms or []):
            src=formula_source(a)
            vec=symbol_vector(a)
            sig=structural_signature(a)
            self.memory.observe(vec,sig,src)
        # Initial snapshot
        self.chain.snapshot(self.memory.frames, self.frame_count)

    def process(self,formula) -> dict:
        self.frame_count+=1
        sig=structural_signature(formula)
        src=formula_source(formula)
        vec=symbol_vector(formula)
        self.memory.observe(vec,sig,src)
        stress=self.memory.stress; self._stress_accum+=stress*0.1
        induction_fired=False
        if self._stress_accum>self._induction_threshold:
            cd=self.frame_count-self._last_induction
            if cd>=15:
                self.memory.induction_clean(self.chain)
                self._stress_accum=0.0; self._last_induction=self.frame_count
                induction_fired=True
        # Snapshot after induction
        if induction_fired or self.frame_count % 30 == 0:
            self.chain.snapshot(self.memory.frames, self.frame_count)
        return {
            "frame":self.frame_count,"mem":len(self.memory.frames),
            "eff":round(self.memory.efficiency,4),
            "util":round(self.memory.utilization,4),"stress":round(stress,4),
            "accum":round(self._stress_accum,4),
            "sig":sig[:30],"induction":induction_fired,
        }

    def evaluate(self,formula):
        sig=structural_signature(formula)
        if not self.memory.frames: return 3
        sorted_w=sorted(f.weight for f in self.memory.frames)
        median=sorted_w[len(sorted_w)//2]; min_s=max(median,2.0)
        for f in self.memory.frames:
            if f.weight<min_s: continue
            fs=f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
            d=sig_edit(sig, fs)
            if d>=0.70: return 2
        return 3

    def emergence_score(self,sig):
        tp=set(sig.split("_"));best=0
        fs=self.memory.frames
        med=sorted(f.weight for f in fs)[len(fs)//2] if fs else 1
        for f in fs:
            fp=set(f.sig.split("_"));ratio=len(tp&fp)/min(len(tp),len(fp))if fp else 0
            if ratio>=0.75 and f.weight>best: best=f.weight
        return best>=med,best/max(med,1)
    
    def emergence_report(self):
        """Show all frames in memory with weight status."""
        lines=["  MEMORY STATE"]
        for i,f in enumerate(self.memory.frames):
            med=sum(ff.weight for ff in self.memory.frames)/len(self.memory.frames) if self.memory.frames else 0
            em="E" if f.weight>=med else " "
            lines.append(f"  [{i}] w={f.weight:.1f} {em}  {f.src[:60]}")
        lines.append("")
        lines.append(self.chain.view())
        lines.append("")
        # Check emergence
        targets=[("SAS→ASA",f"seg_equiv_angle_equiv_impl"),
                 ("ASA→SSS",f"seg_equiv_seg_equiv_impl")]
        for nm,sig in targets:
            S=self.evaluate(None) if False else 3
            lines.append(f"  CHECK: {nm}")
        return "\n".join(lines)
