# EE Architecture Audit Report (M1)

> 日期：2026-05-17
> 范围：geruon.py (2099 行) / precip_test.py / 与三大公设 + 梯度场哲学的一致性
> 审计方式：代码逐行审查 + 运行验证

---

## 1. 哲学一致性

| 公设 | 评分 | 核心代码 | 说明 |
|------|------|---------|------|
| 生成第一性 | ⭐⭐⭐⭐⭐ | `_update_tau()`, `phase`, `arrow_output()` | τ 内生演化 + 相位呼吸完整 |
| 信息-观测构成性 | ⭐⭐⭐⭐ | StructuralSig, 碰数检测, MI | 好——input() 字符串分支有退化 |
| 自指生成模式 | ⭐⭐⭐⭐⭐ | circularity, doubt, 沉淀, self_observe | 高阶自指全套实现 |

## 2. 梯度场方向一致性

| 组件 | 状态 | 说明 |
|------|------|------|
| BiasField | ✅ 完整 | L360-465, deposit/blend_into/seed_frames |
| arrow_output() | ✅ 完整 | L1421-1444, centroid + phase 融合 |
| SharedField | ✅ 独立文件 | shared_field.py, 5 单元 τ spread=0.191 |
| phase_output() | ✅ Legacy 标注 | 建议使用 arrow_output() |
| **vocab_mode** | ⚠️ 保留调试 | 已标注 DEPRECATED, 不参与核心流程 |

## 3. 已修正的问题

| # | 问题 | 文件 | 修正 |
|---|------|------|------|
| 1 | `enrich_codex()` 调用了不存在的方法 | precip_test.py:33 | → `enrich()` |
| 2 | `from geme import _VEC_DIM, _ALPHABET` 不存在的导入 | precip_test.py:4 | 移除，使用显式 SYMBOLS |
| 3 | `input()` 字符串分支使用 `ord(ch)` 回退编码 | geruon.py:1553-1558 | 移除 ord 回退，仅保留 novelty 注册 |
| 4 | 自测代码依赖 `_ALPHABET`（7 处引用）| geruon.py:1960-2030 | 全部替换为 `_TEST_SYMS` |
| 5 | `process_sig()` 未标记 deprecated | geruon.py:1463 | 添加 DEPRECATED 文档 |
| 6 | `evaluate_sig()` 未标记 deprecated | geruon.py:1730 | 添加 DEPRECATED 文档 |
| 7 | `enable_vocab()` 未标记 deprecated | geruon.py:1704 | 添加 DEPRECATED 文档 |

## 4. 保留的调试工具

| 项目 | 状态 | 理由 |
|------|------|------|
| vocab_mode | DEPRECATED 但保留 | 人类可读的翻译口——调试时查看系统内部状态 |
| phase_output() | Legacy 标注 | Bacteria 邻居通信兼容性 |
| process_sig() | DEPRECATED 标注 | GEME formula 语言兼容性 |

## 5. 自测结果

| 测试 | 结果 | 说明 |
|------|------|------|
| S1 StructuralSig 确定性 | ✅ | 同结构→同 gid，不同结构→不同 gid |
| S2 循环检测 | ⚠️ 2-cycle=False | StructuralSig 不可变，真 2-cycle 需要 A 引用 B 时 B 已存在——已知限制 |
| S3 GeruonFrame 签名 | ✅ | 自动哥德尔签名生成 |
| T0 vec_dim 灵活性 | ✅ | 8/16/32 全部正常 |
| T1 τ 演化 | ✅ | 19 次相位转换，相位序列完整 |
| T2 τ 分化 | ⚠️ 三单元 spread=0 | 同输入同种子→无分化——同 BGM 的 G0 消融结果 |
| T3 相位编码 | ✅ | 最小相间距离 1.414，vec_dim≥16 时良好 |
| T4 锁检测 | ✅ | 相位序列完整，τ 有波动 |
| T5 相位可区分性 | ✅ | 所有相位 distinct |
| T6 循环追踪 | ✅ | 12 帧全部有 struct_sig，circular refs 检测存在 |
| T7 Codex 跨代 | ✅ | Gen0→Gen1→Gen2 传递正常 |
| T8 Codex 锚 | ✅ | Codex-only 模式维持桥开放 |
| T9 碰数检测 | ⚠️ 0 事件 | 五条件检测器存在，但自然循环引用未出现 |

## 6. 剩余问题

| # | 问题 | 严重性 | 建议处理时间 |
|---|------|--------|------------|
| P1 | StructuralSig 不可变导致真圆形引用不能自发产生 | 设计层 | P2 递归深度实验中解决 |
| P2 | 碰数检测器始终未触发（五条件同时满足极难） | 实验层 | 构造自指输入序列触发 |
| P3 | I(Φ;X)=0（所有自测中）| 观测层 | Φ/X 分区共现结构未建立——BGM 桥未在 Geruon 中出现 |
| P4 | GI≈1（L0→L1 无时间解耦）| 实验层 | 需引入跨层时间解耦机制 |

---

*所有已修正的 bug 已通过 precip_test.py 和 geruon.py 自测验证通过。*
*梯度场方向已清理，vocab_mode 保留为调试口但已标注 DEPRECATED。*
