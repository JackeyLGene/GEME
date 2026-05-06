# GEME — GO 阶段架构决策记录

**决策**: MemoryFrame 三层数据分离  
**日期**: 2026-05-03  
**影响**: 证明可见性基础设施

---

## 背景

PA 阶段 MemoryFrame 仅含：

```
Frame: {vec, weight, sig, age, merged}
  vec: [0.1, 0.3, ...]    ← 频次向量, 无括号
  sig: "conj_seg_seg"      ← 签名, 有括号结构
  src: 不存在              ← 原文丢失
```

ProofViewer 需要展示证明步骤原文，但 `src` 不存在。无法从 `vec` 或 `sig` 逆向还原原文。

## 决策

MemoryFrame 三字段分离：

```
Frame: {vec, weight, sig, src, age, merged}
  vec: [0.1, 0.3, ...]    ← 处理层: 粗聚类, 无括号
  sig: "conj_seg_seg"      ← 评估层: 签名匹配, 有括号结构
  src: "seg(A,B) ∧ ∠(A,B,C) ≡ ∠(D,E,F)"   ← 展示层: 人类可读原文
  
  处理层: 括号不重要 (聚类效率问题)
  评估层: 括号在签名中 (结构匹配)
  展示层: 括号在原文中 (人类可读)
```

## 影响

```
正向:
  ✓ ProofViewer 可展示原文, 括号自然存在
  ✓ 评估引擎不变 (sig + vec)
  ✓ 底层 GEME 架构无需修改

负向:
  ✗ 每帧多存一个字符串 (~100 bytes/帧)
  ✗ 需要将输入公式转为 src 字符串

代价: 极小 (100 bytes × 10-20 帧 = 1-2 KB)
```

## 写入变更

```
MemoryFrame.__init__:
  + self.src = ""

Memory.observe:
  合并时: src = "(" + src + ") ∧ (" + new_src + ")"  (链式合并)
  新建时: src = to_string(formula)

ProofViewer.view_chain:
  直接用 src 文本输出
```
