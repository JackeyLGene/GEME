================================================================================
  GEME V10 — Genetic Economy Memory Entity
  PA (Arithmetic) Code Review Package
================================================================================

  Author:     Liu Jieqi
  Date:       2026-05-04
  Inspired by: Hofstadter's GEB (1979) & Hebb's Organization of Behavior (1949)
  Status:     V10 — All self-reference endogenous

================================================================================
  PACKAGE CONTENTS
================================================================================

  1_Design_Philosophy.pdf
      Full design document: philosophy, architecture, innovations, baseline comparison.

  2_Core_Code.txt
      Concatenated core engine (geme_v6.py) with dependency summaries.

  3_Experimental_Reports.txt
      Ablation, hyperparameter sweep, statistical validation (Cohen's d), baseline.

  4_S4_Retired.txt
      Why external S4 was replaced by co-occurrence self-reference.

  README.txt (this file)

  test_data_example.py / .txt
      Minimal runnable test demonstrating add_comm emergence.

  v8_comprehensive_report.md
      Full experimental results (7 sections, ablation, hparam, IT paradox).

  v10_comprehensive_report.md (new)
      Baseline comparison (frequency, k-means) + Hebb citation + full stats.

  src/
      Minimal runnable source tree (language, q_axioms, entity, inference, etc.)

================================================================================
  QUICK START
================================================================================

  python test_data_example.py

  Expected: add_comm: S2 (emerged)

  Custom:
      from gira.phase6.geme_v6 import GEME
      e = GEME(memory_cap=10, cooccur_window=50, cooccur_thresh=0.25)
      e.process(formula)
      e.evaluate(target)  # returns 2 (S2) or 3 (S3)

================================================================================
  KEY FEATURES (V10)
================================================================================

  * Adaptive merge threshold (no hardcoded constants)
  * Association vectors = weighted avg of base frames
  * Chain vectors = weighted avg of association frames
  * Weight = compression contribution (count / mean)
  * Zero-axiom: Robinson Q only for evaluation backstop
  * Co-occurrence replaces external S4 (endogenous strange loop)
  * Frequency baseline comparison confirms GEME > naive counting

================================================================================
  RELATED WORK
================================================================================

  Hebb (1949): "Cells that fire together, wire together" — ancestor of co-occurrence.
  GEME extends Hebb with: structural merge, competitive induction, recursive chains.

  Hofstadter (1979): Strange-loop hypothesis — recursive self-reference in formal
  systems generates stratified meaning. GEME provides first computational realization.

================================================================================
  CONTACT
================================================================================

  This is a personal research project. No institutional affiliation.
================================================================================
