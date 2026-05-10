GEME — Geuron Emergent Memory Engine
======================================
V1.5 | 2026-05-05 | Author: Liu Jieqi
======================================

FILES:

Manuscript:
  paper_en.txt              — English (3,410 words, v1.5)
  paper_cn.txt              — Chinese translation

Mathematics + Statistics:
  statistical_analysis.py   — p-values, 95% CIs (all p<0.001)
  supplementary_tables.txt  — Tables S1-S7

Core engine (Python 3.8+, stdlib only):
  geme.py                   — GEME engine (~200 lines)
  run_all_experiments.py    — one-shot reproduction

Baselines:
  baseline_quantitative.py  — GEME vs ART vs SOM
  baseline_fair.py          — ART tuned + LSTM-lite
  ablation_complete.py      — fixed threshold, frequency skew, long-run
  fifo_ablation.py          — competitive vs FIFO comparison
  eval_sensitivity.py       — 5 variants, wall persists in all

Demonstrations:
  exp_godel_growth.py       — GEME reads Godel's proof
  exp_godel_controls.py     — 3-condition: full / theorem-only / random
  info_theory.py            — compression ratios, frame entropy
  signature_tradeoff.py     — signature vs raw-vector: same compression

Support:
  glossary.txt / gir_summary.txt
  review_ai_strict.txt / reference_assessment.txt

Word:
  create_docx.js            — node create_docx.js

======================================
NOTES:
- All experiments: <30s per config on consumer hardware
- Seeds: 42-91 (Exp 2), 42-141 (Exp 3)
- Statistical tests: binomial, all p<0.001
