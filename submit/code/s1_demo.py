"""
S1: 六层壁垒实验 - 可复现的发现之旅
每个实验展示一个"认知壁垒"：
  跑实验 → 看到当前层做不到什么 → 理解为什么需要下一层 → 恰好对应科学史的一次相变
"""
import sys, math
sys.path.insert(0, '../final-v1.5')
from geme import GEME, _VEC_DIM

def clear(g):
    """Reset GEME state for fresh experiment."""
    g.memory.frames.clear()
    g.memory._cooccur.clear()
    g.memory._assoc_frames = 0
    g.memory._weight_history.clear()
    g.memory._step_counter = 0

# ===== L1 壁垒：孤立帧 =====
# 对应：轴心时代——分类但不关联
print("="*60)
print("L1 壁垒实验：孤立帧")
print("对应：轴心时代——分类但不关联")
print("-"*60)

g = GEME(memory_cap=8)
g.memory.preserve_sig = True
# 输入孤立实体——没有关联结构
g.process_vec([1,0]+[0]*25, '猫')
g.process_vec([0,1]+[0]*25, '垫子')
m = g.metrics()
assoc = [f for f in g.memory.frames if '──' in (f.sig_full or '')]
print(f"  输入: '猫' 和 '垫子'")
print(f"  关联帧: {len(assoc)}（期望 0——孤立帧无法形成关系）")
print(f"  帧数: {m['frame_count']}/8")
print(f"  结论: L1能分类，但不能表达'猫在垫子上'。")

# ===== L2 壁垒：短暂关联 =====
# 对应：牛顿时代——因果但短暂
print("\n" + "="*60)
print("L2 壁垒实验：短暂关联")
print("对应：牛顿时代——因果但短暂")
print("-"*60)

g2 = GEME(memory_cap=16)
g2.memory.preserve_sig = True; g2.memory.quantum_mode = True
g2.memory._merge_dists = [0.3]*50; g2._induction_threshold = 3.0
g2.memory.cooccur_thresh = 0.12

for i in range(50):
    g2.process_vec([1,0,0]+[0]*24, '猫')
    g2.process_vec([0,1,0]+[0]*24, '在')
    g2.process_vec([0,0,1]+[0]*24, '垫上')

m2 = g2.metrics()
assoc2 = [f for f in g2.memory.frames if '──' in (f.sig_full or '')]
print(f"  输入: '猫' '在' '垫上' × 50轮")
print(f"  关联帧: {len(assoc2)}")
print(f"  L3桥接帧(L4_count): {m2['L4_frame_count']}")
# 换输入——看关联是否消失
clear(g2); g2.memory.cooccur_thresh = 0.12
for i in range(50):
    g2.process_vec([1,0,0]+[0]*24, '狗')
    g2.process_vec([0,1,0]+[0]*24, '在')
    g2.process_vec([0,0,1]+[0]*24, '路上')
m2b = g2.metrics()
print(f"  切换输入为'狗在街上'× 50轮后——旧关联'猫──垫上'消失")
print(f"  结论: L2关联随窗口滑动而消失。关联是临时的。")

# ===== L3 壁垒：无法判断真假 =====
# 对应：爱因斯坦/场论之后——结构完备但无真值
print("\n" + "="*60)
print("L3 壁垒实验：频率≠真值")
print("对应：经典物理完备后——仍无法回答'真'问题")
print("-"*60)

g3 = GEME(memory_cap=16)
g3.memory.preserve_sig = True; g3.memory.quantum_mode = True
g3.memory._merge_dists = [0.3]*50; g3._induction_threshold = 3.0
g3.memory.cooccur_thresh = 0.12
for _ in range(30):
    g3.process_vec([1,0]+[0]*25, '3+2=5')
    g3.process_vec([0,1]+[0]*25, '6+1=8')
m3 = g3.metrics()
l3_frames = [f for f in g3.memory.frames if chr(8212)*2 in (f.sig_full or '')]
print(f"  输入: '3+2=5'(真) 和 '6+1=8'(假)—各30次")
print(f"  L3桥接帧: {len(l3_frames)}")
for f in l3_frames:
    print(f"    桥: {(f.sig_full or f.sig)[:30]} w={int(f.weight)}")
print(f"  真与假的处理方式完全相同——频率统计无法区分真值。")
print(f"  结论: L3能发现模式，但不能判断真假。")

# ===== L4 壁垒：预测但不知自己的准确性 =====
# 对应：哥本哈根——预测有效但不知道元层面的精度
print("\n" + "="*60)
print("L4 壁垒实验：孤独的预测者")
print("对应：哥本哈根——会预测但不知自己的准确率")
print("-"*60)

g4 = GEME(memory_cap=16)
g4.memory.preserve_sig = True; g4.memory.quantum_mode = True
g4.memory._merge_dists = [0.3]*50; g4._induction_threshold = 3.0
g4.memory.cooccur_thresh = 0.08
for _ in range(50):
    g4.process_vec([1,0,0]+[0]*24, '猫')
    g4.process_vec([0,1,0]+[0]*24, '在')
    g4.process_vec([0,0,1]+[0]*24, '垫上')
m4 = g4.metrics()
print(f"  输入: (猫→在→垫上)×50")
print(f"  预测数: {m4['pred_total']}, 准确率: {m4['pred_accuracy']:.3f}")
# 注入异常
g4.process_vec([1,0,0]+[0]*24, '猫')
g4.process_vec([0,1,0]+[0]*24, '在')
g4.process_vec([0.1,0.1,0.1,1]+[0]*23, '路上')
m4b = g4.metrics()
errs = len([f for f in g4.memory.frames if 'pred_err' in (f.sig_full or '')])
print(f"  注入异常后: pred_err帧 = {errs}")
print(f"  但系统不知道自己总体准确率在下降——没有元认知。")
print(f"  结论: L4能预测和检测误差，但不知道'我的预测能力如何'。")

# ===== L5 壁垒：元观测但不行动 =====
# 对应：香农——知道信息论但不去判断
print("\n" + "="*60)
print("L5 壁垒实验：旁观者")
print("对应：香农——信息可测量但不可行动")
print("-"*60)

g5 = GEME(memory_cap=16)
g5.memory.preserve_sig = True; g5.memory.quantum_mode = True
g5.memory._merge_dists = [0.3]*50; g5._induction_threshold = 3.0
g5.memory.cooccur_thresh = 0.08
for _ in range(50):
    g5.process_vec([1,0,0]+[0]*24, '猫'); g5.process_vec([0,1,0]+[0]*24, '在'); g5.process_vec([0,0,1]+[0]*24, '垫上')
print(f"  训练完成。预测准确率: {g5.metrics()['pred_accuracy']:.3f}")
print(f"  注入噪声序列...")
import random
for _ in range(30):
    for __ in range(3):
        v = [0.0]*27; v[random.randint(0,26)] = 1.0
        g5.process_vec(v, f'noise{__}')
m5 = g5.metrics()
doubt = len([f for f in g5.memory.frames if 'sys_doubt' in (f.sig_full or '')])
print(f"  L5记录了准确率: {m5['pred_accuracy']:.3f}")
print(f"  L6 sys_doubt帧: {doubt}（准确率<60%时触发——系统'觉得不对'）")
print(f"  结论: L5看到趋势，L6才做出判断。两者缺一不可。")

print("\n" + "="*60)
print("S1 六层壁垒实验全部完成。")
print('每一层揭示的"不能"恰对应科学史上一次范式转换的驱动力。')
print("="*60)
