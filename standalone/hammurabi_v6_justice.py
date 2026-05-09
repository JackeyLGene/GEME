"""
汉谟拉比 v6 — 正义结构编码
每个法律条款编码为 (犯罪类型, 惩罚类型, 社会层级) 三元组
三部石板三种辞汇——同一正义结构——GEME能否重合？
"""
import sys, math
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

# 法律的三维结构：(犯罪类型, 惩罚类型, 社会层级)
# 犯罪: 0=暴力, 1=盗窃, 2=财产, 3=人身
# 惩罚: 0=同态, 1=赔偿, 2=死刑, 3=残害
# 阶层: 0=自由人, 1=奴隶, 2=亲子
LAWS = [
    # (cn, en, cun, crime, punish, class)
    ("毁他人之目","destroy his eye","𒅆𒋗", 0,0,0),
    ("折他人之骨","break his bone","𒀠𒋗",0,0,0),
    ("落他人之齿","knock out his tooth","𒍣𒋗",0,0,0),
    ("偷他人之牛","steal an ox","𒄞𒋻",1,1,0),
    ("伤他人之奴","injure a slave","𒀴",0,1,1),
    ("骗他人之财","cheat of property","𒋻𒋗",2,1,0),
    ("杀他人之子","kill his son","𒌉𒌉",3,0,0),
    ("窝藏逃奴","harbor a runaway","𒁁𒀴",1,2,0),
    ("打他人之父","strike his father","𒀜𒁕",0,3,2),
    ("偷他人之羊","steal a sheep","𒇻𒋻",1,1,0),
    ("放火","commit arson","𒉏𒉏",2,2,0),
    ("夺他人之田","seize a field","𒀀𒊮𒋻",2,1,0),
    ("不还债","default on debt","𒆥𒋻",2,1,0),
    ("骂他人之父","curse his father","𒀜𒅗𒆷",3,3,2),
    ("打他人之子","strike his son","𒌉𒁕",0,0,2),
    ("毁他人之田","destroy a field","𒀀𒊮𒇻",2,1,0),
]

def justice_to_vec(crime, punish, cls, dim=_D27):
    """正义编码：三维→27维向量"""
    v = [0.0]*dim
    v[crime]=1.0; v[3+punish]=1.0; v[6+cls]=1.0
    return v

def train_justice(concepts, label):
    g=GEME(memory_cap=16); g.memory.preserve_sig=True; g.memory.quantum_mode=True
    g.memory._merge_dists=[0.3]*30; g._induction_threshold=3.0; g.memory.cooccur_thresh=0.05
    for _ in range(200):
        for cn, en, cun, crime, punish, cls in concepts:
            v = justice_to_vec(crime, punish, cls)
            g.process_vec(v, (en if label=='en' else cn if label=='cn' else cun)[:4])
        vs=[0.0]*_D27
        for j,f in enumerate(g.memory.frames[:min(len(g.memory.frames),_D27)]):
            vs[j]=f.weight/(sum(f.weight for f in g.memory.frames) or 1)
        g.process_vec(vs,'self')
    m = g.metrics()
    preds = {}
    for cn, en, cun, crime, punish, cls in concepts[:8]:
        v = justice_to_vec(crime, punish, cls)
        g.process_vec(v, (en if label=='en' else cn if label=='cn' else cun)[:4])
        p, c = g.memory.predict_next()
        preds[(crime,punish,cls)] = (p, c)
    return g, m, preds

print("="*65)
print("汉谟拉比 v6 — 正义结构跨语言不变性")
print("同一条社会结构→三种辞汇→L4预测是否重合")
print("="*65)

g_cn, m_cn, p_cn = train_justice(LAWS, "cn")
g_en, m_en, p_en = train_justice(LAWS, "en")
g_cun, m_cun, p_cun = train_justice(LAWS, "cun")

print(f"\n{'':>15} {'总帧':>6} {'L4':>4} {'预测':>6} {'准确率':>8}")
print('-'*48)
print(f"{'中文':>15} {m_cn['frame_count']:>6d} {m_cn['L4_frame_count']:>4d} {m_cn['pred_total']:>6d} {m_cn['pred_accuracy']:>8.3f}")
print(f"{'英文':>15} {m_en['frame_count']:>6d} {m_en['L4_frame_count']:>4d} {m_en['pred_total']:>6d} {m_en['pred_accuracy']:>8.3f}")
print(f"{'楔形':>15} {m_cun['frame_count']:>6d} {m_cun['L4_frame_count']:>4d} {m_cun['pred_total']:>6d} {m_cun['pred_accuracy']:>8.3f}")

# 比较L4预测的犯罪类型→惩罚类型映射
print(f"\n正义结构映射 (犯罪→惩罚→阶层):")
print(f"{'犯罪类型':>8} {'中文预测':>15} {'英文预测':>15} {'楔形预测':>15}")
print('-'*58)
crime_names = ["暴力","盗窃","财产","人身"]
for (crime,punish,cls), cn_pred in sorted(p_cn.items())[:8]:
    en_pred = p_en.get((crime,punish,cls),("?",0))[0]
    cun_pred = p_cun.get((crime,punish,cls),("?",0))[0]
    print(f"{crime_names[crime]:>8}  {str(cn_pred)[:12]:>15}  {str(en_pred)[:12]:>15}  {str(cun_pred)[:12]:>15}")
