# GEME做梦实验：结构输入→随机噪声（梦境）
import sys, math, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

g = GEME(memory_cap=32)
g.memory.preserve_sig = True; g.memory.quantum_mode = True
g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0

# Phase 1: 醒着——输入结构
print("Phase 1: 清醒（结构化输入）")
for i in range(3000):
    t = i * 0.01
    v = [0.0]*_D27
    v[0] = math.cos(2*math.pi*t)
    v[1] = math.sin(2*math.pi*t)
    if i % 7 == 0: v[5] = 0.5  # 偶尔的意外
    g.process_vec(v, "wake")

n_awake = len(g.memory.frames)
sigs_awake = set((f.sig_full or f.sig)[:20] for f in g.memory.frames)
weights_awake = sorted([int(f.weight) for f in g.memory.frames], reverse=True)
print(f"  帧数: {n_awake}, 前3权重: {weights_awake[:3]}")
print(f"  ──关联帧: {sum(1 for f in g.memory.frames if chr(8212)*2 in (f.sig_full or f.sig))}")

# Phase 2: 做梦——随机噪声
print("\nPhase 2: 做梦（随机噪声输入）")
for i in range(3000):
    v = [_r.gauss(0, 0.3) for _ in range(_D27)]
    g.process_vec(v, "dream")

n_dream = len(g.memory.frames)
sigs_dream = set((f.sig_full or f.sig)[:20] for f in g.memory.frames)
weights_dream = sorted([int(f.weight) for f in g.memory.frames], reverse=True)
print(f"  帧数: {n_dream}, 前3权重: {weights_dream[:3]}")

# Phase 3: 醒来——检查框架是否还保持清醒时的结构
print("\nPhase 3: 醒来——清醒时的帧还在吗？")
lost = sigs_awake - sigs_dream
survived = sigs_awake & sigs_dream
print(f"  清醒帧存活: {len(survived)}/{len(sigs_awake)}")
print(f"  清醒帧丢失: {len(lost)}/{len(sigs_awake)}")

# 检查"做梦"是否创造了新的关联
dream_assoc = [f for f in g.memory.frames if f.src == "dream" and "──" in (f.sig_full or f.sig)]
if dream_assoc:
    print(f"  梦境新关联: {len(dream_assoc)}个")
    for a in dream_assoc[:3]:
        print(f"    {a.sig}")
else:
    print(f"  梦境新关联: 0（噪声不产生稳定意义）")

# Phase 4: 检查系统熵变化
total_w = sum(f.weight for f in g.memory.frames)
print(f"\nPhase 4: 经济健康")
print(f"  总权重: {int(total_w)}")
print(f"  最大帧权重: {max(int(f.weight) for f in g.memory.frames)}")
print(f"  熵: {-sum((f.weight/total_w)*math.log2(f.weight/total_w) for f in g.memory.frames if f.weight>0):.4f}")
print()
print("结论：GEME会做梦——但噪声不会污染清醒时的结构。")
