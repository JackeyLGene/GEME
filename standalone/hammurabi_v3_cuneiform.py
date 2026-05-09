"""
汉谟拉比法典 v3 — 三种书写系统：中文、英文、楔形文字
同一套法律——三种完全不同的符号系统——
GEME能否跨语系收敛到同一结构？
"""
import sys, math
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27
import random

# 同一套法律——三种编码
# 概念序列（法律的核心语义结构）
CONCEPTS = [
    ("毁目","eye","𒅆"),
    ("折骨","bone","𒀠"),
    ("落齿","tooth","𒍣"),
    ("杀子","son","𒌉"),
    ("偷牛","ox","𒄞"),
    ("伤奴","slave","𒀴"),
    ("骗财","cheat","𒋻"),
    ("塌墙","wall","𒂍"),
    ("塌房","house","𒂍𒋾"),
    ("医眼","heal_eye","𒅆𒋗"),
    ("医骨","heal_bone","𒀠𒋗"),
    ("医齿","heal_tooth","𒍣𒋗"),
    ("行窃","steal","𒋻𒁺"),
    ("窝藏","harbor","𒁁"),
    ("打父","strike_father","𒀜𒁕"),
    ("骂父","curse_father","𒀜𒅗𒆷"),
    ("夺田","seize_field","𒀀𒊮"),
    ("坏堤","damage_dike","𒋗𒉄"),
    ("盗羊","steal_sheep","𒇻𒋻"),
    ("欺妻","deceive_wife","𒈗𒊩"),
    ("不还债","debt","𒆥𒋻"),
    ("放火","arson","𒉏"),
]

def encode_clause(concept, dim=_D27):
    """概念→向量：用概念名称的字符哈希编码"""
    v = [0.0] * dim
    for ch in concept:
        idx = ord(ch) % dim
        v[idx] += 1.0
    norm = math.sqrt(sum(x*x for x in v))
    if norm > 0:
        v = [x / norm for x in v]
    return v

# 三种语言用不同签名（完全不同）但相同概念编码
CN_CLAUSES = [(c[0], "cn_"+c[0][:4]) for c in CONCEPTS]
EN_CLAUSES = [(c[1], "en_"+c[1][:4]) for c in CONCEPTS]
CUN_CLAUSES = [(c[2], "cun_"+str(i)[:4]) for i, c in enumerate(CONCEPTS)]

def run_lang(label, clauses, n_cycles=100):
    g = GEME(memory_cap=32)
    g.memory.preserve_sig = True; g.memory.quantum_mode = True
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    g.memory.cooccur_thresh = 0.01
    
    for _ in range(n_cycles):
        for concept, sig in clauses:
            v = encode_clause(concept)
            g.process_vec(v, sig)
        vs = [0.0]*_D27
        for j, f in enumerate(g.memory.frames[:min(len(g.memory.frames), _D27)]):
            vs[j] = f.weight / (sum(f.weight for f in g.memory.frames) or 1)
        g.process_vec(vs, 'self')
    
    assoc = [f for f in g.memory.frames if chr(8212)*2 in (f.sig_full or f.sig) or chr(9711)*2 in (f.sig_full or f.sig)]
    return len(assoc), g

print("="*65)
print("汉谟拉比 v3 — 三种书写系统")
print("中文/英文/楔形文字 → 同一语义结构？")
print("="*65)

cn_a, g_cn = run_lang("中文", CN_CLAUSES)
en_a, g_en = run_lang("英文", EN_CLAUSES)
cun_a, g_cun = run_lang("楔形文字", CUN_CLAUSES)

m_cn = g_cn.metrics(); m_en = g_en.metrics(); m_cun = g_cun.metrics()

print(f"\n{'':>15} {'关联帧':>8} {'总帧':>6} {'L4':>4} {'预测':>6} {'准确率':>8}")
print("-"*55)
print(f"{'中文':>15} {cn_a:>8d} {m_cn['frame_count']:>6d} {m_cn['L4_frame_count']:>4d} {m_cn['pred_total']:>6d} {m_cn['pred_accuracy']:>8.3f}")
print(f"{'英文':>15} {en_a:>8d} {m_en['frame_count']:>6d} {m_en['L4_frame_count']:>4d} {m_en['pred_total']:>6d} {m_en['pred_accuracy']:>8.3f}")
print(f"{'楔形文字':>15} {cun_a:>8d} {m_cun['frame_count']:>6d} {m_cun['L4_frame_count']:>4d} {m_cun['pred_total']:>6d} {m_cun['pred_accuracy']:>8.3f}")

max_a = max(cn_a, en_a, cun_a)
min_a = min(cn_a, en_a, cun_a)
print(f"\n结构收敛：关联帧数极差 = {max_a - min_a} (相差{((max_a-min_a)/max(max_a,1)*100):.0f}%)")
print(f"结论：{'√ 三种书写系统结构收敛' if max_a-min_a <= 5 else '结构差异较大'}")
