# D_H收敛验证：自指帧的熵变化随系统规模增大是否趋于零
import sys, math, copy, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = __import__("random").Random(42)

def entropy(frames):
    total = sum(f.weight for f in frames) or 1
    h = 0.0
    for f in frames: p = f.weight/total; h -= p*math.log2(p) if p>0 else 0
    return h

def test_at_capacity(cap, ext_steps=None):
    s = ext_steps or cap * 60
    g = GEME(memory_cap=cap); g.memory.preserve_sig = True
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    for i in range(s):
        t = i*0.01; v=[0.0]*_D27; v[0]=math.cos(2*math.pi*t); v[1]=math.sin(2*math.pi*t)
        g.process_vec(v, "ext")
    h0 = entropy(g.memory.frames); n0 = len(g.memory.frames)
    
    g2 = copy.deepcopy(g)
    for step in range(500):
        t = step*0.01; v=[0.0]*_D27; v[0]=math.cos(2*math.pi*t); v[1]=math.sin(2*math.pi*t)
        g2.process_vec(v, "ext")
        if step % 20 == 0:
            vs = [0.0]*_D27
            for j,f in enumerate(g2.memory.frames[:min(len(g2.memory.frames),_D27)]):
                vs[j] = f.weight/(sum(f.weight for f in g2.memory.frames) or 1)
            g2.process_vec(vs, "self")
    
    h1 = entropy(g2.memory.frames); n1 = len(g2.memory.frames)
    dh = h1 - h0
    bridges = [f for f in g2.memory.frames if "ext" in (f.sig_full or f.sig)[:10] and "self" in (f.sig_full or f.sig)[:10]]
    return cap, n0, n1, h0, h1, dh, len(bridges)

print("D_H 收敛测试：memory_cap 8 -> 128")
print(f"{'cap':>4} {'n0':>4} {'n1':>4} {'H0':>8} {'H1':>8} {'D_H':>8} {'桥':>4}")
for cap in [8, 16, 32, 64, 128]:
    _, n0, n1, h0, h1, dh, br = test_at_capacity(cap)
    print(f"{cap:4} {n0:4} {n1:4} {h0:8.4f} {h1:8.4f} {dh:8.4f} {br:4}")
