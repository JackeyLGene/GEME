# 输入"直觉"：从L3注入指导，观察L1感知变化
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

g = GEME(memory_cap=16); g.memory.preserve_sig = True
g.memory._chain_cooccur_thresh = 2; g.memory._merge_dists = [0.3]*50
g._induction_threshold = 3.0

# Phase 1: 建立直觉（L3的意义结构）——"危险" = {dark, fast, loud}
print('Phase 1: 建立直觉(L3意义结构) - "危险"概念')
vdark=[0.0]*_D27; vdark[0]=1.0; vdark[1]=0.3  # dark
vfast=[0.0]*_D27; vfast[5]=1.0; vfast[6]=0.3  # fast
vloud=[0.0]*_D27; vloud[10]=1.0; vloud[11]=0.3  # loud

for _ in range(300):
    g.process_vec(vdark, "dark")
    g.process_vec(vfast, "fast")
    g.process_vec(vloud, "loud")

# 此时GEME已形成{fast, dark, loud}之间的──关联 = "危险"概念

# 构建L3投影向量
bridge_frames = [f for f in g.memory.frames if "──" in (f.sig_full or f.sig)]
if bridge_frames:
    proj = [0.0]*_D27
    total = sum(f.weight for f in bridge_frames)
    for f in bridge_frames:
        for d in range(_D27):
            proj[d] += f.vec[d] * f.weight / total
    
    print(f"  直觉投影向量构建完成({len(bridge_frames)}个关联帧)")
    print(f"  主分量: [{proj[0]:.3f}, {proj[5]:.3f}, {proj[10]:.3f}]")
else:
    proj = [0.0]*_D27

# Phase 2: 注入直觉——不输入危险相关，看GEME是否更敏感
print(f"\nPhase 2: 注入直觉——L3投影调制L1阈值")
# 先测量基线阈值
baseline_thresh = g.memory._merge_thresh_val

# 输入一个模棱两可的信号（既有点dark又有点像别的）
v_ambiguous = [0.0]*_D27; v_ambiguous[0] = 0.5; v_ambiguous[7] = 0.5

# 不使用直觉时的处理
g_plain = GEME(memory_cap=16); g_plain.memory.preserve_sig = True
g_plain.memory._chain_cooccur_thresh = 2
g_plain.memory._merge_dists = [0.3]*50; g_plain._induction_threshold = 3.0
for _ in range(100):
    g_plain.process_vec(v_ambiguous, "ambig")
plain_frames = len([f for f in g_plain.memory.frames if "ambig" in (f.sig_full or f.sig)[:10]])
print(f"  无直觉: {plain_frames}个模糊输入帧")

# 使用直觉（L3投影到L1）
g_int = GEME(memory_cap=16); g_int.memory.preserve_sig = True
g_int.memory._chain_cooccur_thresh = 2
g_int.memory._merge_dists = [0.3]*50; g_int._induction_threshold = 3.0

# 先用直觉结构预训练L3
for _ in range(100):
    g_int.process_vec(vdark, "dark")
    g_int.process_vec(vfast, "fast")
    g_int.process_vec(vloud, "loud")

# 手动调制阈值(模拟L3→L1投影: dark→敏感)
g_int.memory._merge_thresh_val *= 1.5  # 直觉"关注dark"→提高阈值→更容易合并
for _ in range(100):
    g_int.process_vec(v_ambiguous, "ambig")
int_frames = len([f for f in g_int.memory.frames if "ambig" in (f.sig_full or f.sig)[:10]])
print(f"  有直觉: {int_frames}个模糊输入帧(阈值被直觉调制)")

# Phase 3: 直接输入"直觉帧"
print(f"\nPhase 3: 直接输入直觉帧——L3不依赖L1")
# 在GEME中，"直觉"就是L3帧直接进入帧经济
g3 = GEME(memory_cap=8); g3.memory.preserve_sig = True
g3.memory._chain_cooccur_thresh = 2; g3.memory._merge_dists = [0.3]*50
g3._induction_threshold = 3.0

# 直接注入L3帧（模拟"直觉"作为独立输入源）
for i in range(200):
    if i % 2 == 0:
        g3.process_vec(proj, "intuition")  # L3投影作为输入
    else:
        g3.process_vec(v_ambiguous, "ambig")  # 真实感知

print(f"  混合直觉+感知: {len(g3.memory.frames)}帧总")
l3like = [f for f in g3.memory.frames if "intuition" in (f.sig_full or f.sig)]
print(f"  直觉帧数: {len(l3like)}")
if l3like:
    top = sorted(l3like, key=lambda x: x.weight, reverse=True)[0]
    s=(top.sig_full or top.sig)[:30]
    print(f"  直觉帧: w={int(top.weight)} {s}")

print(f"\n结论：直觉可以是输入——来自更高层的帧直接进入帧经济。")
print(f"  这和感官输入在同一个经济中竞争和合并。")
print(f"  第六感 = 更高维度的帧被系统当作输入处理。")
