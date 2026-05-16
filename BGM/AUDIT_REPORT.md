# BGM v0.5 审计报告

> 日期：2026-05-16
> 版本：v0.5 (7f1f9a6)
> 范围：论文 BGM_v0.5.md / bgm_core.py / 所有实验脚本

---

## 总体评估

论文 v0.5 相比 v0.4 有重大改进：解决型区分已撤回、添加了位置随机化控制、连续-离散原理作为基础原则提升到 §1、蟹道赋格作为 Coda。结构更严谨，断言更保守。

但存在两项可能需修正的数值差异，和两项文档不一致。

---

## 审计结果

### 类型 A：已确认一致 ✅

| 项目 | 位置 | 状态 |
|------|------|------|
| bgm_core.py 180 行，无核心修改 | 全文 | ✅ 干净，符合论文 §2.1 描述 |
| G0 禁用 → τ 收敛 | §3.4 | ✅ bgm_experiment.py 和 bgm_g0_pareto.py 均确认 |
| 桥的相变（步 23，0.300→1.000） | §3.3 | ✅ awakening_probe.py 确认 |
| α 悬崖（α=0.02 分化维持，α=0.00 坍缩） | §4.5 | ✅ bgm_bacteria_sensitivity.py 确认 |
| 桥不镜像梯度（r=-0.090） | §4.2 | ✅ bgm_bacteria.py 确认 |
| G0 全 τ 区间不锁（0.2-3.0） | §6.5 | ✅ bgm_g0_tau_scan.py 确认 |
| 记忆容量中性（cap=6-32 均产生分化）| §2.2 | ✅ bgm_g0_pareto.py 确认 |
| 调制速率无效（全部坍缩） | §2.2 | ✅ bgm_g0_pareto.py 确认 |
| 签名方案放大分化 2.2× | §2.2 | ✅ bgm_g0_pareto.py 确认（0.4848 / 0.2206 = 2.2×）|
| 论文列出的所有代码文件 | §程序 | ✅ 全部存在（代码目录 71 个 .py）|

### 类型 B：数值不一致 ⚠️

#### B1. g0_interval 帕累托最优值

**论文声称：** "g0_interval = 4 as the Pareto optimum — producing τ spread 74% above the default g0_interval = 1"（§2.2）

**审计结果（5 种子 × BWV 847 赋格 × 6 遍）：**
| gi | 均值 spread | 变化 |
|----|------------|------|
| 1 | 0.314 | 基线 |
| 3 | 0.427 | +36% |
| **4** | **0.469** | **+49%** |
| 5 | 0.415 | +32% |
| 8 | 0.388 | +24% |

**问题：** gi=4 确实是帕累托最优，但增益为 +49%，非 +74%。差值 25 个百分点。

**建议：** 将 §2.2 的 "74% above default" 修正为 "49% above default"。

#### B2. §3.2 声部事件 SR-eff 值

**论文声称（10 种子均值）：**
| 事件 | SR-eff |
|------|--------|
| STRETTO | 0.255 |
| EPISODE | 0.278 |
| CADENCE_dominant | 0.229 |
| CADENCE_tonic | 0.223 |

**审计结果（单种子 42，1 遍）：**
| 事件 | SR-eff |
|------|--------|
| STRETTO | 0.667 |
| EPISODE | 0.628 |
| CADENCE_dominant | 0.667 |
| CADENCE_tonic | 0.687 |

**问题：** 差异约 2.5-3×。论文值显著低于单种子实测值。
**可能原因：** 论文值可能来自 `bgm_cadence_randomized.py` 的变体间控制，而非原始赋格。如果是这样，§3.2 的表头应注明数据来源（"interleaved fugue variants, 10-seed mean"）。

**建议：** 验证 `bgm_cadence_randomized.py` 是否确实产生论文中报告的值。如确定，在表头注明数据来源。

---

### 类型 C：文档一致性 ⚠️

#### C1. bgm_g0_pareto.py 缺少 g0_interval 扫描

**论文 §2.2** 详细报告了 g0_interval 扫描结果（gi=4 为帕累托最优），但 `bgm_g0_pareto.py` 仅扫描 mem_cap、modulation rate 和 signature spectrum。g0_interval 数据来自内联实验（审计会话中），未封装为独立脚本。

**建议：** 将 g0_interval 扫描纳入 `bgm_g0_pareto.py`，或创建 `bgm_g0_interval_sweep.py`。

#### C2. 部分关键脚本为 `run_*` 命名

审计中产生的脚本以 `run_` 开头（`run_accel.py`, `run_gap_cap.py`, `run_g0tau_effect.py` 等）。这些支持 S11 但不属于论文引用的主脚本列表。不影响论文可复现性，但如被引用到预发材料中需注意命名统一。

---

### 类型 D：无需操作 ⚠️

#### D1. §3.1 使用 Score 编码而非 MIDI

**论文："Under BWV 847 Fugue (discrete score encoding, 6 passes)"**
审计确认：论文已明确标注数据来源。合规。

#### D2. Coda 蟹道赋格代码存在

`bgm_crab_canon.py` 存在且可运行。检查通过。

---

## 汇总

| 类别 | 项目数 | 通过 | 提醒 |
|------|--------|------|------|
| 已确认一致 | 10 | 10 | 0 |
| 数值不一致 | 2 | 0 | 2 |
| 文档一致性 | 2 | 0 | 2 |
| 无需操作 | 2 | 2 | 0 |

**行动项：**
1. §2.2: "74%" → "49%"（g0_interval 增益）
2. §3.2: 验证声部事件数值来源并标注
3. 将 g0_interval 扫描正式化到 `bgm_g0_pareto.py`
4. `run_*` 脚本案卷命名统一

论文核心主张在审计中均得到确认。v0.5 的修正方向（撤回解决型区分、添加位置控制、连续-离散原则）是正确的。
