# 第5维测试：GEME的多世界演化
# 量子合并时，未选中的候选帧保存为分支——独立演化
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM

_r = random.Random(42)

print("="*55)
print("第5维测试：GEME多世界演化")
print("="*55)

g = GEME(memory_cap=10); g.memory.quantum_mode = True
g.memory.preserve_sig = True; g.memory._merge_thresh_val = 0.8
g.memory._merge_dists = [0.8]*50

# 先创建两个对立的基帧——使后续输入有多个候选
va = [0.0]*_VEC_DIM; va[0] = 1.0
vb = [0.0]*_VEC_DIM; vb[5] = 1.0
g.process_vec(va, "a")
g.process_vec(vb, "b")

# 然后在中间注入等距输入——触发分支
print("\n注入等距输入（在a和b之间）：")
for i in range(30):
    v = [0.0]*_VEC_DIM
    v[0] = 0.5 + _r.gauss(0, 0.05)
    v[5] = 0.5 + _r.gauss(0, 0.05)
    g.process_vec(v, "in")

mv = g.memory._multiverse
print(f"\n多世界分支数: {len(mv)}")
for i, (frames, step, bid) in enumerate(mv[:5]):
    ws = [f.weight for f in frames]
    avg_w = statistics.mean(ws) if ws else 0
    # 看帧经济中的签名
    sigs = set((f.sig_full or f.sig)[:15] for f in frames)
    print(f"  分支{i}: 来自step{step}, {len(frames)}帧, 均w={avg_w:.0f} {sigs}")

# 继续输入，让分支各自演化
print("\n继续输入100步——分支各自演化：")
for i in range(100):
    t = i * 0.01
    v = [0.0]*_VEC_DIM; v[0] = math.cos(t*2)*0.5+0.5; v[5] = math.sin(t*2)*0.5+0.5
    g.process_vec(v, "in")

mv = g.memory._multiverse
print(f"演化后分支数: {len(mv)}")
if mv:
    ws = [f.weight for f in mv[0][0]]
    frame_0 = len(mv[0][0])
    print(f"  分支0: {frame_0}帧, 均w={statistics.mean(ws):.0f}")
if len(mv) > 1:
    ws2 = [f.weight for f in mv[1][0]]
    frame_1 = len(mv[1][0])
    print(f"  分支1: {frame_1}帧, 均w={statistics.mean(ws2):.0f}")
    print(f"  帧数差: {abs(frame_0 - frame_1)}")
    # 权重分布差
    if frame_0 > 0 and frame_1 > 0:
        min_f = min(frame_0, frame_1)
        w_diff = sum(abs(mv[0][0][i].weight - mv[1][0][i].weight) for i in range(min_f)) / min_f
        print(f"  权重分布差: {w_diff:.2f} (越大→分支差异越大)")

print("\n✓ 第5维多世界机制运行中" if len(mv) > 0 else "✗ 未产生分支")
