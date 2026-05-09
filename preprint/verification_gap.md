# v2 vs Code: 声明有效性审核

## 3个严重问题

### 问题A: MI数值（0.032）无实验脚本支撑

**论文写：** "I(phi;X) = 0.032 ± 0.006 (20 seeds, 2000 steps)"
**代码事实：** 没有脚本跑过20种子×2000步的MI测量。0.032是单次运行值。

根源：
- `standalone/geme.py`（约400行简化版）不包含 `mutual_information_phi_X()` 方法
- `final-v1.5/geme.py`（780行全功能版）包含MI方法，但独立实验脚本import的是简化版
- 真正的MI实验脚本不存在

**修复：** 运行 `run_theorems_fixed.py` 或新建 `run_mi_20seeds.py` 来生成正确数据

### 问题B: Q+G≈PA数据不支持结论

**论文写：** "Q+G和PA在L4预测行为上不可区分"
**代码事实：** 10种子下Q、Q+G、PA三者的桥帧数全为0——无法区分是因为**全相等**（全都0），不是"Q+G≈PA"。

根源：
- 实验使用 `standalone/geme.py`（旧版），没有L4预测功能
- 桥帧计数在旧版实现中全部为0
- L4预测的Q+G≈PA（878次预测、0.350准确率）是在 `final-v1.5/geme.py` 中用新版本测试的——但那是用一个未命名的独立测试脚本跑的

### 问题C: standalone实验引用旧版geme.py

所有 `standalone/*.py` 文件 import `standalone/geme.py`（简化版）而非 `final-v1.5/geme.py`（全功能版）。这意味着：
- 汉谟拉比实验（standalone/hammurabi*.py）没有L4预测能力
- PA实验（standalone/exp_godel_proof_test.py）没有MI测量
- 所有声明涉及L4/MI/pred_err的数据，其脚本不在standalone目录下

## 建议修复

| 优先级 | 修复 |
|--------|------|
| P0 | 建 `run_mi_20seeds.py`：20种子×2000步×全空间MI → 生成真正的0.032±数据 |
| P1 | 更新 `standalone/geme.py`，或让standalone脚本引用 `final-v1.5/geme.py` |
| P2 | Q+G≈PA声明改为更谨慎的表述（"方向性一致"而非"不可区分"） |
