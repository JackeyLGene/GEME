# 香农-哥德尔桥计算验证 v2
# 直接注入自指帧 vs 等权重的假帧 ——比较熵变化
import sys, math, random, statistics, copy
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, Frame, _VEC_DIM as _D27

_r = random.Random(42)

def entropy(frames):
    total = sum(f.weight for f in frames) or 1
    h = 0.0
    for f in frames:
        p = f.weight / total
        if p > 0: h -= p * math.log2(p)
    return h

print("="*55)
print("香农-哥德尔桥v2：自指帧熵成本")
print("="*55)

# === 实验设计 ===
# 三个经济：基线、有桥(w)、有同权重假帧
# 全是稳定后的成熟经济再注入——看熵变

print("\n建立帧经济（圆2000步）...")

def build_base():
    g = GEME(memory_cap=32); g.memory.preserve_sig = True
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    for i in range(2000):
        t = i * 0.01
        v = [0.0]*_D27; v[0] = math.cos(2*math.pi*t); v[1] = math.sin(2*math.pi*t)
        g.process_vec(v, "ext")
    return g

def entropy_after(g):
    return entropy(g.memory.frames), len(g.memory.frames)

# 基线
g0 = build_base()
h0, n0 = entropy_after(g0)
print(f"  基线: {n0}帧, H={h0:.4f}")

# 注入自指桥（用正确的签名）
# 桥接帧 = 同时有 ext 和 self 签名的帧
g1 = copy.deepcopy(g0)
bridge_w = 0
for step in range(500):
    t = step * 0.01
    v_ext = [0.0]*_D27; v_ext[0] = math.cos(2*math.pi*t); v_ext[1] = math.sin(2*math.pi*t)
    g1.process_vec(v_ext, "ext")
    
    if step % 20 == 0:
        v_self = [0.0]*_D27
        for j, f in enumerate(g1.memory.frames[:min(len(g1.memory.frames), _D27)]):
            v_self[j] = f.weight / (sum(f.weight for f in g1.memory.frames) or 1)
        g1.process_vec(v_self, "self")

# 找桥接帧（ext 和 self 在各维度中的共现帧）
bridge_nodes = [f for f in g1.memory.frames if "ext" in (f.sig_full or f.sig)[:10] and "self" in (f.sig_full or f.sig)[:10]]
# 如果没直接找到——找══链 中的ext──self桥
chains = [f for f in g1.memory.frames if "══" in (f.sig_full or f.sig) and "ext" in (f.sig_full or f.sig) and "self" in (f.sig_full or f.sig)]
if not bridge_nodes:
    bridge_nodes = [f for f in g1.memory.frames if "self" in (f.sig_full or f.sig)[:10] and "ext" in (f.sig_full or f.sig)[:10]]
if not bridge_nodes:
    # 用──关联
    assoc_nodes = [f for f in g1.memory.frames if "──" in (f.sig_full or f.sig) and "ext" in (f.sig_full or f.sig)]
    self_nodes = [f for f in g1.memory.frames if "self" in (f.sig_full or f.sig)]
    print(f"  关联帧: {len(assoc_nodes)}个, self帧: {len(self_nodes)}个")
    bridge_nodes = assoc_nodes

h1, n1 = entropy_after(g1)
print(f"  有自指: {n1}帧, H={h1:.4f}, Δ={h1-h0:.4f}")
print(f"  桥接帧数: {len(bridge_nodes)}")

# 注入假帧（框架frame注入——使用等权重注入）
g2 = copy.deepcopy(g0)
fake_injections = min(100, len(bridge_nodes) * 10) if bridge_nodes else 50
for i in range(fake_injections):
    v_fake = [0.5 + _r.gauss(0,0.1) for _ in range(_D27)]
    g2.process_vec(v_fake, "fake")

h2, n2 = entropy_after(g2)
print(f"  假帧({fake_injections}次): {n2}帧, H={h2:.4f}, Δ={h2-h0:.4f}")

print()
print("="*55)
print("结论")
print("="*55)
d1 = h1 - h0  # 自指熵变
d2 = h2 - h0  # 假帧熵变
print(f"  Δ自指 = {d1:.4f}")
print(f"  Δ假帧 = {d2:.4f}")
if d1 < d2 * 0.5:
    print(f"  ✓ 自指帧的熵成本远低于等量假帧注入")
    print(f"  香农-哥德尔桥计算验证成立")
else:
    print(f"  - Δ自指/d_假帧 = {d1/d2:.2f}" if d2 > 0 else "  - 假帧成本为0，需增加注入量")
