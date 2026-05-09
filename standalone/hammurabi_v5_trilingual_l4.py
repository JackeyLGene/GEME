"""
汉谟拉比 v5 — 三块石板，三个GEME，同一结构
GEME_A读中文 → L4预测"A→B"
GEME_B读英文 → L4预测"eye→bone"  
GEME_C读楔形 → L4预测"𒅆→𒀠"
三组预测拓扑是否收敛？
"""
import sys, math
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

# 同一套概念，三种书写形式
CONCEPTS_CN = ["毁目","折骨","落齿","杀子","偷牛","伤奴","骗财","医眼"]
CONCEPTS_EN = ["eye", "bone", "tooth","son", "ox",  "slave","cheat","heal"]
CONCEPTS_CUN = ["𒅆","𒀠","𒍣","𒌉","𒄞","𒀴","𒋻","𒋗"]

def text_to_vec(text, dim=_D27):
    v=[0.0]*dim
    for ch in text: v[ord(ch)%dim]+=1.0
    norm=math.sqrt(sum(x*x for x in v))
    return [x/norm for x in v] if norm>0 else v

def train_geme(concepts, label):
    g=GEME(memory_cap=16); g.memory.preserve_sig=True; g.memory.quantum_mode=True
    g.memory._merge_dists=[0.3]*30; g._induction_threshold=3.0; g.memory.cooccur_thresh=0.05
    for _ in range(200):
        for c in concepts:
            g.process_vec(text_to_vec(c), c[:4])
        vs=[0.0]*_D27
        for j,f in enumerate(g.memory.frames[:min(len(g.memory.frames),_D27)]):
            vs[j]=f.weight/(sum(f.weight for f in g.memory.frames) or 1)
        g.process_vec(vs,'self')
    # 预测拓扑：每个概念后预测什么
    pred_map = {}
    for c in concepts[:6]:
        # 用该概念向量做输入，检查L4预测结果
        g.process_vec(text_to_vec(c), c[:4])
        pred, conf = g.memory.predict_next()
        pred_map[c[:4]] = (pred, conf)
    return g, pred_map

print("="*60)
print("汉谟拉比 v5 — 三石板·三GEME·L4预测拓扑")
print("="*60)

g_cn, map_cn = train_geme(CONCEPTS_CN, "中文")
g_en, map_en = train_geme(CONCEPTS_EN, "英文")
g_cun, map_cun = train_geme(CONCEPTS_CUN, "楔形")

print(f"\n{'输入':>10}  {'中文预测':>15}  {'英文预测':>15}  {'楔形预测':>15}")
print("-"*60)
for i, (cn, en, cun) in enumerate(zip(CONCEPTS_CN[:6], CONCEPTS_EN[:6], CONCEPTS_CUN[:6])):
    pred_cn, cnf_cn = map_cn.get(cn[:4], ("?",0))
    pred_en, cnf_en = map_en.get(en[:4], ("?",0))
    pred_cun, cnf_cun = map_cun.get(cun[:4], ("?",0))
    pc = (pred_cn or "?")[:12] if pred_cn else "?"
    pe = (pred_en or "?")[:12] if pred_en else "?"
    pcun = (pred_cun or "?")[:12] if pred_cun else "?"
    print(f"{cn:>6}/{en:>4}/{cun:>2}  {pc:>15}  {pe:>15}  {pcun:>15}")

# 计算三者的预测拓扑一致性
# 比较预测是否都指向序列中"下一个"概念
next_cn = [CONCEPTS_CN[i+1][:4] if i+1<len(CONCEPTS_CN) else "" for i in range(6)]
next_en = [CONCEPTS_EN[i+1][:4] if i+1<len(CONCEPTS_EN) else "" for i in range(6)]
next_cun = [CONCEPTS_CUN[i+1][:4] if i+1<len(CONCEPTS_CUN) else "" for i in range(6)]

match_cn = sum(1 for i in range(6) if next_cn[i] and map_cn.get(CONCEPTS_CN[i][:4],("",0))[0] and next_cn[i] in (map_cn.get(CONCEPTS_CN[i][:4],("",0))[0] or ""))
match_en = sum(1 for i in range(6) if next_en[i] and map_en.get(CONCEPTS_EN[i][:4],("",0))[0] and next_en[i] in (map_en.get(CONCEPTS_EN[i][:4],("",0))[0] or ""))
match_cun = sum(1 for i in range(6) if next_cun[i] and map_cun.get(CONCEPTS_CUN[i][:4],("",0))[0] and next_cun[i] in (map_cun.get(CONCEPTS_CUN[i][:4],("",0))[0] or ""))

print(f"\n预测指向'下一个概念'次数:")
print(f"  中文: {match_cn}/6  英文: {match_en}/6  楔形: {match_cun}/6")
print(f"  三语言预测拓扑一致性: {'✓ 收敛' if match_cn==match_en and match_en==match_cun else '结构差异'}")
