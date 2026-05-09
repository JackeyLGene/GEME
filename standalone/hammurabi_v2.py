"""
汉谟拉比法典 v2 — 分句级编码（人类认知窗口自然分割）
每个法律条款 = 一个输入帧（不是字符序列）
"""
import sys, math
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

# 分句版：每个条款独立一行
CN_CLAUSES = [
    "若人毁他人之目则毁其目",
    "若人折他人之骨则折其骨",
    "若人落他人之齿则落其齿",
    "若人杀他人之子则杀其子",
    "若人偷他人之牛则赔五倍",
    "若人伤他人之奴则赔其主",
    "若人骗他人之财则还其财",
    "若人筑墙不固压死人则偿命",
    "若人建房塌压死人则偿命",
    "若人医他人之眼愈则收费",
    "若人医他人之骨愈则收费",
    "若人医他人之齿愈则收费",
    "若人行窃被捕则处死",
    "若人窝藏逃奴则处死",
    "若人打他人之父则断其手",
    "若人骂他人之父则割其舌",
    "若人夺他人之田则还田",
    "若人坏他人之堤则赔堤",
    "若人盗他人之羊则赔十倍",
    "若人欺他人之妻则罚银",
    "若子打父则断其手",
    "若奴骂主则割其耳",
    "若人不还债则充为奴",
    "若人放火则处死",
]

EN_CLAUSES = [
    "if a man destroys the eye of another destroy his eye",
    "if a man breaks the bone of another break his bone",
    "if a man knocks out the tooth of another knock out his tooth",
    "if a man kills the son of another kill his son",
    "if a man steals the ox of another pay fivefold",
    "if a man injures the slave of another pay the owner",
    "if a man cheats another of property return the property",
    "if a builder builds a wall and it kills a man he shall die",
    "if a builder builds a house and it collapses he shall die",
    "if a physician heals a man's eye he shall be paid",
    "if a physician heals a man's bone he shall be paid",
    "if a physician heals a man's tooth he shall be paid",
    "if a thief is caught he shall be put to death",
    "if a man harbors a runaway slave he shall die",
    "if a man strikes his father cut off his hand",
    "if a man curses his father cut out his tongue",
    "if a man seizes another's field return the field",
    "if a man damages another's dike repair the dike",
]

def clause_to_vec(clause, dim=_D27):
    """条款→向量：字符频率编码（每个字符贡献 1/norm）"""
    v = [0.0] * dim
    if not clause:
        return v
    for ch in clause:
        idx = ord(ch) % dim
        v[idx] += 1.0
    norm = math.sqrt(sum(x*x for x in v))
    if norm > 0:
        v = [x / norm for x in v]
    return v

def run_hammurabi(label, clauses, n_cycles=120):
    g = GEME(memory_cap=32)
    g.memory.preserve_sig = True; g.memory.quantum_mode = True
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    g.memory.cooccur_thresh = 0.03
    
    for _ in range(n_cycles):
        for clause in clauses:
            v = clause_to_vec(clause)
            g.process_vec(v, clause[:8])
        # 每轮自指
        vs = [0.0]*_D27
        for j, f in enumerate(g.memory.frames[:min(len(g.memory.frames), _D27)]):
            vs[j] = f.weight / (sum(f.weight for f in g.memory.frames) or 1)
        g.process_vec(vs, 'self')
    
    assoc = [f for f in g.memory.frames if "──" in (f.sig_full or f.sig)]
    return g, assoc

print("="*60)
print("汉谟拉比 v2 — 分句级编码")
print("="*60)

g_cn, fn_cn = run_hammurabi("中文", CN_CLAUSES)
g_en, fn_en = run_hammurabi("英文", EN_CLAUSES)

m_cn = g_cn.metrics()
m_en = g_en.metrics()

print(f"\n中文: {len(fn_cn)} 关联帧 / {m_cn['frame_count']} 总帧")
print(f"英文: {len(fn_en)} 关联帧 / {m_en['frame_count']} 总帧")
print(f"结构差: {abs(len(fn_cn)-len(fn_en))} 帧")
print(f"\n中文L4: {m_cn['L4_frame_count']} 预测:{m_cn['pred_total']} 准确率:{m_cn['pred_accuracy']:.3f}")
print(f"英文L4: {m_en['L4_frame_count']} 预测:{m_en['pred_total']} 准确率:{m_en['pred_accuracy']:.3f}")

print(f"\n所有中文帧:")
for f in sorted(g_cn.memory.frames, key=lambda x:x.weight, reverse=True)[:8]:
    print(f"  w={int(f.weight):4d} m={f.merged:3d} {(f.sig_full or f.sig)[:22]}")
print(f"\n所有英文帧:")
for f in sorted(g_en.memory.frames, key=lambda x:x.weight, reverse=True)[:8]:
    print(f"  w={int(f.weight):4d} m={f.merged:3d} {(f.sig_full or f.sig)[:22]}")
