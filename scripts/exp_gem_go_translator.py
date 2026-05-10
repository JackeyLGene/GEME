"""
GEME GO — Interactive translation layer with path finding.
"""
import sys, os, random
sys.path.insert(0, r'G:\GEME\src')
from gira.phase3.language import *
from gira.phase6.geme_go import GEME
OUT=r'g:\GEME\docs\go_tri';os.makedirs(OUT,exist_ok=True)
_rnd=random.Random(42)
A,B,C,D,E,F,G,H,I,J,K,L=[var(c) for c in "ABCDEFGHIJKL"]
tri_pool=[(A,B,C),(D,E,F),(G,H,I),(J,K,L)]

class ProofTranslator:
    def __init__(self,geme):
        self.e=geme
        self.targets=[]
    def get_network(self):
        assocs={}
        for f in self.e.memory.frames:
            sig=f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
            if not "──" in sig: continue
            parts=sig.split("──")
            a,b=parts[0][:25],parts[1][:25]
            assocs[(a,b)]=f.weight;assocs[(b,a)]=f.weight
        return assocs
    def _match(self,target,key):
        if target=="△"and"△"in key:return True
        if target=="∥"and"parallel"in key:return True
        if target=="∠"and"angle"in key:return True
        if target=="SEG"and"seg"in key:return True
        return target in key
    def _label(self,s):
        if"triangle"in s or"△"in s:return"△"
        if"parallel"in s:return"∥"
        if"angle"in s:return"∠"
        if"seg"in s:return"SEG"
        return s[:4]
    def evaluate_path(self):
        net=self.get_network()
        res=[]
        for i in range(len(self.targets)-1):
            a,b=self.targets[i],self.targets[i+1]
            bw=0
            for(k1,k2),w in net.items():
                if self._match(a,k1)and self._match(b,k2):bw=max(bw,w)
                if self._match(a,k2)and self._match(b,k1):bw=max(bw,w)
            res.append((a,b,bw,bw>=25))
        return res
    def feed_gap(self,gap):
        a,b,_,_=gap
        t1,t2=_rnd.choice(tri_pool),_rnd.choice(tri_pool)
        while t2==t1:t2=_rnd.choice(tri_pool)
        data=[]
        # feed all 4 concept types to saturate all associations
        for _ in range(10):
            data.append(eq(fn("seg",t1[_rnd.randint(0,2)],t1[(_rnd.randint(0,2)+1)%3]),
                           fn("seg",t2[_rnd.randint(0,2)],t2[(_rnd.randint(0,2)+1)%3])))
        for _ in range(10):
            i=_rnd.randint(0,2)
            data.append(eq(fn("angle",t1[(i+1)%3],t1[i],t1[(i+2)%3]),
                           fn("angle",t2[(i+1)%3],t2[i],t2[(i+2)%3])))
        for _ in range(10):
            data.append(eq(fn("parallel",t1[0],t1[1]),fn("parallel",t2[0],t2[1])))
        for _ in range(10):
            data.append(eq(fn("△",t1[0],t1[1],t1[2]),fn("△",t2[0],t2[1],t2[2])))
        _rnd.shuffle(data)
        for f in data:self.e.process(f)
        return f"fed {len(data)} items to strengthen {a}-{b}"
    def run_proof(self,path_labels,rounds=8):
        self.targets=list(path_labels)
        print(f"\n  Target: {' → '.join(self.targets)}")
        for rnd in range(rounds):
            status=self.evaluate_path()
            all_strong=all(s[3] for s in status)
            ps=" → ".join(f"{s[0]}(w={s[2]:.0f},{'✓'if s[3]else'?'})"for s in status)
            print(f"  R{rnd+1}: {ps}")
            if all_strong:
                return self.final_proof()
            gap=min(status,key=lambda x:x[2])
            if gap:self.feed_gap(gap)
        return self.final_proof()
    def final_proof(self):
        status=self.evaluate_path()
        min_w=min(s[2] for s in status)
        all_s=all(s[3] for s in status)
        lines=[f"\n{'='*55}",f"  PROOF: {' → '.join(self.targets)}",'='*55,
               f"  Confidence: {min_w:.0f}/31  {'✓ COMPLETE'if all_s else'· INCOMPLETE'}"]
        rules={
            ("SEG","∠"):"Segment equality defines angle correspondence",
            ("∠","∥"):"Corresponding angles indicate parallel lines",
            ("∥","△"):"Parallel lines determine triangle properties",
            ("SEG","∥"):"Segment relations define parallel construction",
            ("SEG","△"):"Segments form the sides of a triangle",
            ("∠","△"):"Angle properties classify triangles",
            ("∠","SEG"):"Angle definition references segments",
            ("∥","SEG"):"Parallel lines cut by transversal create segments",
            ("∥","∠"):"Parallel lines create equal corresponding angles",
            ("△","SEG"):"Triangle edges are segments",
            ("△","∠"):"Triangle has interior angles",
            ("△","∥"):"Triangle orientation relates to parallel",
        }
        for i in range(len(self.targets)-1):
            a,b=self.targets[i],self.targets[i+1]
            w=0
            for s in status:
                if s[0]==a and s[1]==b:w=s[2];break
            rule=rules.get((a,b),"logical relationship")
            lines.append(f"\n  Step {i+1}: {a} → {b}")
            lines.append(f"    {rule}")
            lines.append(f"    link weight: {w:.0f} (threshold: 25)")
        lines.append(f"\n{'='*55}")
        return "\n".join(lines)

# ── Run ──
print("="*55)
print("  GEME GO — Interactive Proof Translator")
print("="*55)
e=GEME(axioms=[],memory_cap=12,merge_thresh=0.75,cooccur_window=80,cooccur_thresh=0.30)
print("\n  Seeding: 600 random assertions")
for step_i in range(600):
    t1,t2=_rnd.choice(tri_pool),_rnd.choice(tri_pool)
    while t2==t1:t2=_rnd.choice(tri_pool)
    st=_rnd.choice(["seg","angle","parallel","triangle"])
    if st=="seg":i=_rnd.randint(0,2);f=eq(fn("seg",t1[i],t1[(i+1)%3]),fn("seg",t2[i],t2[(i+1)%3]))
    elif st=="angle":i=_rnd.randint(0,2);f=eq(fn("angle",t1[(i+1)%3],t1[i],t1[(i+2)%3]),fn("angle",t2[(i+1)%3],t2[i],t2[(i+2)%3]))
    elif st=="parallel":f=eq(fn("parallel",t1[0],t1[1]),fn("parallel",t2[0],t2[1]))
    else:f=eq(fn("△",t1[0],t1[1],t1[2]),fn("△",t2[0],t2[1],t2[2]))
    e.process(f)
t=ProofTranslator(e)
print(f"  Frames: {len(e.memory.frames)}")
result=t.run_proof(["SEG","∠","∥","△"])
print(result)
print(f"\n  Final frames: {len(e.memory.frames)}")
print("="*55)
