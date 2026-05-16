# Submit 包检查报告

> 2026-05-16
> 检查内容：g:\GEME\BGM\submit\BGM_v0.6.md + 代码 + 图表 + 补充材料

---

## ✅ 已修正的问题（对比 paper/BGM_v0.5.md）

| 问题 | v0.5 | v0.6 submit | 状态 |
|------|------|-------------|------|
| g0_interval 增益 | 74% | 49% | ✅ 已修 |
| §3 标题 "Listens" | "The Bridge Listens" | "The Bridge Responds" | ✅ 已修 |
| §3.2 表值来源 | 无说明 | "10 seeds × 3 passes; Pass 1 drives peaks" | ✅ 已加注 |
| §5 实验权重 | 与§3-4同级 | 新增 exploratory 声明 | ✅ 已加注 |
| §6.1 r=+0.964 | 无警告 | 新增自相关警告 | ✅ 已修 |
| §6.3 原则定位 | "foundational principle" | "recovers Shannon (1948)" | ✅ 已修 |
| §3.1 "FFR"使用 | 无映射 | 现为 "temporal integration windows" + 丹内特映射 | ✅ 已修 |
| Coda "hears" | "bridge hears two streams" | "bridge responds to" | ✅ 已修 |
| 参考文献 | 17篇 | 20篇 | ✅ 已扩展 |

---

## ⚠️ 剩余问题

### 1. §3.2 4.06× 声称与位置控制结论的表面矛盾（中等）

**位置：** §3.2 L244-L250

**当前文本：**
```
The bridge detects endings. It does not distinguish how they end — but in
ecological musical contexts, cadence type and structural position are not
independent. A deceptive cadence at the expected structural close drives the
bridge to its strongest opening (4.06×) because the bridge anticipated closure
and was forced to remain open.
```

**问题：** 刚说完"all cadence types produce identical SR-eff ratios... when position is controlled"，立即说"deceptive cadence drives 4.06×"。这是两个实验条件——随机化 vs 真实音乐。但读者会在同一段内看到矛盾。需要明确标注 4.06× 的数据来源（例如"Measured in the unaltered fugue from Experiment 1, where position and cadence are naturally confounded"）。

**建议：** 加一句 "The 4.06× is measured in the unaltered fugue (Experiment 1), where position and cadence are naturally confounded."

### 2. §1 L75-83 重复段落（小）

**位置：** §1 L74-83

**问题：** 编辑遗留。`"the signal re-continuous-izes (pending multi-seed confirmation). the signal re-continuous-izes. This is not a binary..."` 同一行出现了两次。

**建议：** 删去重复行。

### 3. submit/code 缺少部分实验脚本（小）

**论文列出但 submit/code 无的脚本：**
- `bgm_voice_validation.py` ✅ 存在
- `bgm_tau_multiseed.py` ✅ 存在
- `bgm_wtc_full.py` ✅ 存在
- `bgm_cadence_randomized.py` ✅ 存在
- `bgm_structural_analysis.py` ✅ 存在
- `bgm_bach_pipeline.py` ✅ 存在

论文列出的脚本全部存在。提交码目录也包含额外脚本（如 `bgm_gamma2_measure.py`, `bgm_gravity_constant.py`, `bgm_three_layer.py`）——这些来自今日深度探索，不属于提交范畴。无问题。

### 4. 图表无正文引用（小）

§4.2 写道 "Figure 4.1 places the nutrient concentration field beside the accumulated τ"——但正文未显式引用 [图 1]。如提交 Word 版本（.docx），需手动插入图引用。

### 5. §6.6 和 §2.2 数值一致（已确认）

§2.2: "49% above default" ✅
§6.6: "49% above default" ✅
两者一致。

---

## ✅ 已确认一致

| 项目 | 状态 |
|------|------|
| geme.py MD5 | ✅ 0025C508BDBDB386E9A5EB72081995B7 |
| 图文件 | ✅ 5张 PNG 存在 |
| 补充材料 S2 | ✅ 有 markdown 文档 |
| 补充材料 S3 | ✅ 有 markdown 文档 |
| 论文脚本列表 | ✅ 全部存在于 submit/code |
