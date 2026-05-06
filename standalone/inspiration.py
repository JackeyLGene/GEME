# 灵感机制：从第5维分支世界拉帧到主时间线
import sys, math, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

print("="*55)
print("灵感实验：从第5维分支拉帧到主世界")
print("="*55)
print()

g = GEME(memory_cap=16); g.memory.quantum_mode = True
g.memory.preserve_sig = True; g.memory._merge_thresh_val = 0.8
g.memory._merge_dists = [0.8]*50; g._induction_threshold = 5.0

# 创建两个对立基帧（让后续输入产生分支）
va = [0.0]*_D27; va[0] = 1.0
vb = [0.0]*_D27; vb[5] = 1.0
g.process_vec(va, "A")
g.process_vec(vb, "B")

# 等距输入→触发分支
print("Phase 1: 注入等距输入 → 触发第5维分支")
for i in range(50):
    v = [0.0]*_D27
    v[0] = 0.5 + _r.gauss(0, 0.08)
    v[5] = 0.5 + _r.gauss(0, 0.08)
    g.process_vec(v, "s")

for i in range(30):
    v = [0.0]*_D27
    v[2] = 0.2 + _r.gauss(0, 0.05)
    g.process_vec(v, "s")

print(f"  主世界帧数: {len(g.memory.frames)}")

# 检查第5维分支
mv = g.memory._multiverse
print(f"  分支数: {len(mv)}")

# 找分支中存在的、主世界没有的"灵感帧"
main_sigs = set((f.sig_full or f.sig)[:20] for f in g.memory.frames)

# 注入灵感之前——先测试主世界对某种输入的响应基线
test_v = [0.0]*_D27; test_v[2] = 1.0
test_v[0] = 0.5
g2 = GEME(memory_cap=8); g2.memory.preserve_sig = True
g2.memory._chain_cooccur_thresh = 2; g2.memory._merge_dists = [0.3]*50
g2._induction_threshold = 3.0
for _ in range(100):
    g2.process_vec(test_v, "x")
baseline_frames = len(g2.memory.frames)
print(f"\nPhase 2: 基线(无灵感时处理test输入)→ {baseline_frames}帧")

# 注入灵感帧
print(f"\nPhase 3: 从分支拉帧 → 注入主世界")
inspired_frames = 0
for bi, (branch_frames, step, bid) in enumerate(mv[:5]):
    for f in branch_frames:
        s = (f.sig_full or f.sig)[:20]
        if s not in main_sigs and "A" not in s and "B" not in s:
            # 这是"灵感帧"——分支中有但主世界没有
            # 直接注入到主世界
            g.process_vec(f.vec, f"inspire_{bi}")
            main_sigs.add(s)
            inspired_frames += 1

print(f"  注入 {inspired_frames} 个灵感帧")
print(f"  注入后主世界帧数: {len(g.memory.frames)}")

# 测试灵感注入后——同一个输入的处理是否改变
g3 = GEME(memory_cap=8); g3.memory.preserve_sig = True
g3.memory._chain_cooccur_thresh = 2; g3.memory._merge_dists = [0.3]*50
g3._induction_threshold = 3.0

# 预注入灵感帧（模拟"灵光一闪"）
for bi, (branch_frames, step, bid) in enumerate(mv[:3]):
    for f in branch_frames[:2]:
        g3.process_vec(f.vec, f"insp_{bi}")

# 再输入测试信号
for _ in range(100):
    g3.process_vec(test_v, "x")

inspired_frames_out = len(g3.memory.frames)
print(f"\nPhase 4: 注入灵感后处理相同test输入→ {inspired_frames_out}帧 (基线{baseline_frames})")
diff = inspired_frames_out - baseline_frames
print(f"  灵感改变了感知: {'是(+' + str(diff) + '帧)' if diff != 0 else '否'}")
if diff > 0:
    print(f"  → 灵感扩增了感知维度—看世界更细了")
elif diff < 0:
    print(f"  → 灵感压缩了感知维度—看世界更结构化")

# 检查是否有"insp"帧和"x"帧的桥接
bridges = [f for f in g3.memory.frames if "insp" in (f.sig_full or f.sig)[:15] and "x" in (f.sig_full or f.sig)]
if bridges:
    print(f"  灵感-感知桥接帧: {len(bridges)}个")
    for br in bridges[:2]:
        w=int(br.weight); s=(br.sig_full or br.sig)[:35]
        print(f"    w={w} {s}")
    print("  ✓ 灵感和感知融合了")
