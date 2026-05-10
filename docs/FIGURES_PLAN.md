# Figures Plan

## 正文

| Figure | 内容 | 数据来源 |
|--------|------|---------|
| Fig 1 | GEME架构图：L1-L6分层管道（输入→实体→关联→桥接→预测→元观测→统摄→输出） | 概念图（手工绘制） |
| Fig 2 | 哥德尔桥：MI随步数的收敛曲线（20种子，2000步，阴影=±1σ） | claim_confirmation.json |
| Fig 3 | 参数稳定性：δ/γ/τ三参数扫描热图，映射L4预测是否存在 | 需新建 run_parameter_sweep.py |
| Fig 4 | L4阈值响应：d(w)/dt > 0.02时触发dwdw帧 | 已有数据 |
| Fig 5 | 帧数收敛：容量8-52下L4=1，系统=6±2 | phase3_robustness.json |
| Fig 6 | Q+G≈PA：三条件（Q/Q+G/PA）的L4/预测数/准确率柱状图+误差线 | statistical_tests.json |
| Fig 7 | 概念关系图：GEME三定理+Aaronson/Friston/Tononi/Hofstadter之间的映射 | 概念图 |

## 补充材料

| Figure | 内容 | 数据来源 |
|--------|------|---------|
| S-Fig 1 | S1六层壁垒实验的输出图 | standalone/s1_demo_experiments.py |
| S-Fig 2 | 几何/Tarski对比柱状图（绝对几何 vs 平行 vs Tarski） | test_geometry_tarski.py |
| S-Fig 3 | 汉谟拉比三语收敛：CN/EN/CUN的L2关联帧重叠Venn图 | hammurabi_v3数据 |

## 需新建的实验（数据未生成）

1. **run_parameter_sweep.py**：δ∈[0.05,0.50], γ∈[0.01,0.10], τ∈[0.2,1.0]的网格扫描→确认L4预测存在区间
2. **run_fig2_mi_curve.py**：MI随步数的逐点记录（非单点均值）
3. **run_fig5_capacity_sweep.py**：容量4-64的精细扫描（当前只有8个点）
