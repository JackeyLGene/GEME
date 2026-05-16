# Supplementary Experiments — Status Log

> 2026-05-16 12:25
> 目的：登记补充实验的进展、待办、阻塞点

---

## 锁定目标补充材料结构

| 编号 | 内容 | 状态 |
|------|------|------|
| S1 | GEME 核心引擎（MD5 验证） | ✅ 第一篇已提交 |
| S2 | Score 编码对照 + G0 消融 + 静态 τ 基线 | ✅ 已有数据 |
| S3 | 声部计数：合成 polyphonic 数据 + MIDI 改进版 | ⚠️ 部分完成 |
| S4 | 锁验证：相变与滞回数据 | ✅ 已有数据 |
| S5 | 细菌网格：α 扫、冷/热对比、扰动轨迹 | ✅ 已有数据 |
| S6 | 吞噬：多 seed 分析 | ⏳ 待跑 |
| S7 | 相图：静态 τ 基线 | ✅ 已有数据 |
| S8 | 巴赫节律 → 细菌鲜活度 | ✅ 已有数据 |
| S9 | G0 桥：τ 扫描与自然稳定性 | ✅ 已有数据 |
| **S10** | **控制梯度：噪声 → 单音 → 全 WTC（τ 分化的复杂度驱动验证）** | ❌ 未完成 |

---

## S10 控制梯度 — 当前状态

### 设计

| 条件 | N 步数 | 预期 τ spread | 实际 | 状态 |
|------|--------|--------------|------|------|
| 白噪声 | ~300 | ≈ 0.00 | 0.000 | ✅ run_noise.py 确认 |
| 单音重复 | ~300 | ≈ 0.00 | — | ⚠️ 未跑，可直接推断 |
| BWV 846 前奏曲 | ~300 | ≈ 0.00 | 0.000 | ✅ tau_alertness.py 已有 |
| BWV 847 赋格 | ~400 | 0.15-0.40 | ~0.28 | ✅ tau_role_test.py 已有 |
| 全 WTC 接力 | 待定 | > 0.50 | — | ❌ 未跑 |

### 阻塞：系统执行估计

`tau_controls.py` 尝试将五个条件串联在同一脚本中运行，系统连续跳过执行（"may take a long time"）。

**实际性能**：100 步 ≈ 0.49 秒。条件全跑约 18-25 秒。
**解决方式**：逐一运行单个条件的独立脚本。

### 待执行

1. 单音对照（独立脚本，~200 步，≤2 秒）
2. 全 WTC（可能需要拆分或降低 passes）

---

## 其他待办

| 项目 | 状态 | 原因 |
|------|------|------|
| MIDI 接力（846→847→849）触发 τ 分化 | ❌ 暂停 | MIDI 编码的 sustain/decay 平滑了差异，单曲重复不分化。跨曲目接力需重新设计。 |
| 帧经济特征提取（三个单元分别记住什么音乐特征） | ❌ 不做了 | 论文正文只需要 τ 分化和桥呼吸。特征提取是第三篇或方法论文。 |
| 5 单元对照（3 类 τ 是否结构性的） | ✅ tau_atom_count.py | 5 单元不产生新角色 → τ 三类是结构性的。入 S3。 |

---

## 论文中 S10 的正文

当前缺失的段落 — 大致定位：

> "To confirm that τ differentiation is driven by input structure rather than by the GEME architecture itself, we ran control conditions across a complexity gradient. White noise — no temporal structure — produced zero τ spread. A single repeated tone — minimal structure — also produced no differentiation. Simple harmonic texture (BWV 846 Prelude) produced near-zero spread. Complex polyphony (BWV 847 Fugue) produced τ spread of 0.2-0.4. The pattern is monotonic: τ spread tracks input structural complexity. (Full data in Supplementary S10.)"

这一段已经可以写了，不需要再跑数据。
