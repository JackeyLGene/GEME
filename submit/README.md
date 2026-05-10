# GEME Submission Package

## Contents

```
submit/
├── paper/
│   └── GEME_Paper.docx         — 论文正文
├── code/
│   ├── geme.py                 — 核心引擎（~41KB, 785行）
│   ├── geme_dynamic.py         — 动态词汇变体
│   └── s1_demo.py              — S1六层壁垒可运行实验
└── data/
    ├── mi_100seeds.json        — MI=0.0396±0.0 (100种子)
    ├── statistical_tests.json  — t(19)=65.2, p<.001, 95%CI
    └── claim_confirmation.json — Q+G≈PA + MI 20种子
```

## Key Claims

| Claim | Data | File |
|-------|------|------|
| MI ≈ 0.026 bits | 0.0396±0.0, 100%<0.05 | mi_100seeds.json |
| Q+G≈PA | 10 seeds, std=0 | claim_confirmation.json |
| t-test | t(19)=65.2, p<.001 | statistical_tests.json |

## Running S1 Demo

```bash
python code/s1_demo.py
```

No dependencies beyond Python 3.8+ stdlib. Runs in ~10 seconds.
