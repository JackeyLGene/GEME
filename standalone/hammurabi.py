# 汉谟拉比法典翻译不变性测试
# 3800年前的法律——GEME能否从不同语言中提取同一结构？
import sys, math
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

cn = "若人毁他人之目则毁其目若人折他人之骨则折其骨若人落他人之齿则落其齿"
en = "if a man destroys the eye of another man they shall destroy his eye if he breaks the bone of another they shall break his bone"

g_cn = GEME(memory_cap=32)
g_cn.memory.preserve_sig = True; g_cn.memory.quantum_mode = True
g_cn.memory._merge_dists = [0.3]*50; g_cn._induction_threshold = 3.0

g_en = GEME(memory_cap=32)
g_en.memory.preserve_sig = True; g_en.memory.quantum_mode = True
g_en.memory._merge_dists = [0.3]*50; g_en._induction_threshold = 3.0

for _ in range(300):
    for ch in cn: 
        v=[0.0]*_D27; v[ord(ch)%_D27]=1.0; g_cn.process_vec(v, ch)
    for ch in en: 
        v=[0.0]*_D27; v[ord(ch)%_D27]=1.0; g_en.process_vec(v, ch)

fn_cn = [f for f in g_cn.memory.frames if "──" in (f.sig_full or f.sig)]
fn_en = [f for f in g_en.memory.frames if "──" in (f.sig_full or f.sig)]
print(f"汉谟拉比跨语言测试")
print(f"中文关联帧: {len(fn_cn)}/32, 英文关联帧: {len(fn_en)}/32")
print(f"结构收敛: {'相同结构' if abs(len(fn_cn)-len(fn_en))<=3 else '结构差异'}")
