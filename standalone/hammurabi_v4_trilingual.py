"""
汉谟拉比 v4 — 三语混排，同一石板
(毁目)(eye)(𒅆)(折骨)(bone)(𒀠)...
GEME从混排中自己发现：三种文字指向同一概念
"""
import sys, math
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

# 同一块石板：每个法律概念三种文字并列
SLAB = [
    ("毁目","eye","𒅆"),
    ("折骨","bone","𒀠"),
    ("落齿","tooth","𒍣"),
    ("杀子","son","𒌉"),
    ("偷牛","ox","𒄞"),
    ("伤奴","slave","𒀴"),
    ("骗财","cheat","𒋻"),
    ("医眼","heal_eye","𒋗𒅆"),
    ("医骨","heal_bone","𒋗𒀠"),
    ("医齿","heal_tooth","𒋗𒍣"),
    ("行窃","steal","𒋻𒁺"),
    ("打父","strike","𒀜𒁕"),
    ("骂父","curse","𒅗𒆷"),
    ("夺田","seize","𒀀𒊮"),
    ("坏堤","dike","𒋗𒉄"),
    ("放火","arson","𒉏"),
]

def concept_to_vec(text, dim=_D27):
    """文字→向量：字符归一化频率"""
    v = [0.0] * dim
    for ch in text:
        v[ord(ch) % dim] += 1.0
    norm = math.sqrt(sum(x*x for x in v))
    if norm > 0:
        v = [x / norm for x in v]
    return v

g = GEME(memory_cap=32)
g.memory.preserve_sig = True; g.memory.quantum_mode = True
g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
g.memory.cooccur_thresh = 0.05

# 混排：每个概念三种文字连在一起
# 认知窗口 ≈ 3-5个单元，同概念的三种文字必然落在同一窗口内
for _ in range(200):
    for cn, en, cun in SLAB:
        g.process_vec(concept_to_vec(cn), cn[:4])
        g.process_vec(concept_to_vec(en), en[:4])
        g.process_vec(concept_to_vec(cun), "cun")
    # 自指
    vs=[0.0]*_D27
    for j,f in enumerate(g.memory.frames[:min(len(g.memory.frames),_D27)]):
        vs[j]=f.weight/(sum(f.weight for f in g.memory.frames) or 1)
    g.process_vec(vs,'self')

m = g.metrics()
assoc = [f for f in g.memory.frames if chr(8212)*2 in (f.sig_full or f.sig)]
print("="*60)
print("汉谟拉比 v4 — 三语混排石板")
print("="*60)
print(f"\n总帧: {m['frame_count']}  关联帧: {len(assoc)}")
print(f"L4: {m['L4_frame_count']}  预测: {m['pred_total']}  准确率: {m['pred_accuracy']:.3f}")
print(f"\n跨语言关联桥（CN──EN/CUN）:")
for f in assoc[:10]:
    sig = f.sig_full or f.sig
    # 检查是否跨语言
    has_cn = any(c in sig for c in "毁折落杀偷伤骗医行打骂夺坏放")
    has_en = any(c in sig for c in "eyebonetoothsonox")
    has_cun = 'cun' in sig
    marker = ""
    if has_cn and has_en: marker = " [CN↔EN]"
    elif has_cn and has_cun: marker = " [CN↔CUN]"
    elif has_en and has_cun: marker = " [EN↔CUN]"
    elif has_cn: marker = " [CN]"
    elif has_en: marker = " [EN]"
    print(f"  w={int(f.weight):4d} {sig[:35]}{marker}")

# 统计跨语言关联桥的比例
cn_en = sum(1 for f in assoc if any(c in (f.sig_full or f.sig) for c in "毁折落杀偷伤骗医行打骂夺坏放")
            and any(c in (f.sig_full or f.sig) for c in "eyebonetoothsonox"))
cn_cun = sum(1 for f in assoc if any(c in (f.sig_full or f.sig) for c in "毁折落杀偷伤骗医行打骂夺坏放")
            and 'cun' in (f.sig_full or f.sig))
en_cun = sum(1 for f in assoc if any(c in (f.sig_full or f.sig) for c in "eyebonetoothsonox")
            and 'cun' in (f.sig_full or f.sig))
total_cross = cn_en + cn_cun + en_cun
print(f"\n跨语言关联桥统计:")
print(f"  CN↔EN: {cn_en}桥  CN↔CUN: {cn_cun}桥  EN↔CUN: {en_cun}桥")
print(f"  总计跨语言桥: {total_cross}/{len(assoc)} ({total_cross/max(len(assoc),1)*100:.0f}%)")
