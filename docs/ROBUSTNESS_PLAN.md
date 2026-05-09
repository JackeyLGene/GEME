# GEME Comprehensive Robustness Test Plan

**Author:** Jieqi Liu  
**Date:** 2026-05-09  
**Status:** Proposed — awaiting confirmation before execution

---

## 1. Negative Controls (阴性对照)

Verify that GEME does NOT produce spurious positive results with null input.

| ID | Test | Method | Expected Outcome | Est. Time |
|----|------|--------|-----------------|-----------|
| N1 | Zero input | Feed `[0.0]*27` repeatedly for 2000 steps | No stable frames formed; MI ≈ 0; no L4 | 3 min |
| N2 | Pure noise input | Feed `random.gauss(0,1)` vectors, 2000 steps | High frame turnover; no stable associations; MI may ≠ 0 | 3 min |
| N3 | Single symbol repeated | Feed same `[1.0,0,0...]` with same sig for 2000 steps | Single frame dominates; no L4; MI ≈ 0 | 3 min |
| N4 | Empty sequence | Initialize GEME, call metrics() with zero inputs | No crash; frame_count=0; MI=0 | 1 min |
| N5 | No self_observe | Run 2000 steps without ever calling self_observe | L4 count = 0; MI undefined; economy still runs | 3 min |

| N6 | Random baseline (frame shuffle) | Same 2000 steps, but frames assigned randomly instead of by merge | If shuffled MI ≈ original MI, then MI→0 is trivial | 3 min |

**Hole plugged:** N6 — Baseline comparison. Without this, reviewer says "MI→0 is just because the space is small."

**Cross-cut addition for all controls:**
Every numerical result will be reported as `mean ± std` across 3 random seeds. Statistical significance: Cohen's d for effect size, not just p-value.

**Total:** ~16 min

---

## 2. Ablation Studies (消融实验)

Remove one mechanism at a time to verify each contributes as claimed.

| ID | Test | Method | Expected Outcome | Est. Time |
|----|------|--------|-----------------|-----------|
| A1 | No quantum merge | `quantum_mode=False` (default), sine wave 2000 steps | Deterministic; fewer distinct frames; L4 count stable | 3 min |
| A2 | No adaptive threshold | Fix threshold=0.15, disable `_adaptive_thresh()` | Frame count changes; possible over-merging or under-merging | 3 min |
| A3 | No pruning | Disable `induction_clean()`, run 3000 steps | Frame count saturates at capacity; weight inflation | 3 min |
| A4 | No forgetting (γ=0) | Set GAMMA=0, no age decay | Old frames never decay; L4 may be suppressed | 3 min |
| A5 | No co-occurrence tracking | Set cooccur_window=1, effectively disable L2 | No association frames; L3/L4 cannot form | 3 min |
| A6 | No self_obs centroid | Remove the centroid observe from self_observe(), only keep fid tracking | L4 self-frames drop to 0 | 3 min |
| A7 | No d(w)/dt meta-frames | Remove the dw_inject from self_observe() | L4_meta_active=0; centroid still works | 2 min |
| A8 | No multiverse | `_multiverse_enabled=False` | Identical results; multiverse is purely observational | 2 min |

**Total:** ~22 min

---

## 3. Robustness Tests (鲁棒性)

Verify that core claims hold across varying conditions.

| ID | Test | Method | Expected Outcome | Est. Time |
|----|------|--------|-----------------|-----------|
| R1 | Seed sweep (quantum) | 30 quantum seeds (0-29), sine wave 2000 steps | L4 count varies 0-3; MI stays < 0.02; self frames 1-3 | 8 min |
| R2 | Seed sweep (input) | 30 input seeds, fixed quantum seed, 2000 steps | Identical outputs (input randomness absorbed by fixed quantum) | 8 min |
| R3 | Capacity sweep | cap ∈ {4, 6, 8, 12, 16, 20, 24, 32, 48, 64}, 2000 steps each | L4 count ~1-2 across all; MI increases past cap=48 | 10 min |
| R4 | Step count sweep | Steps ∈ {100, 500, 1000, 2000, 5000}, cap=32 | L4 stabilizes after ~500 steps; MI converges | 8 min |
| R5 | Input complexity sweep | 3 patterns: sine (simple), 5-mixed (moderate), 30-random (complex), 2000 steps | Higher complexity → more L4 self-frames? | 8 min |
| R6 | Self-obs frequency | Rate ∈ {2, 5, 10, 20, 50} steps per self_observe | Too rare → no L4; too frequent → L4 saturation | 5 min |
| R7 | Window size sweep | cooccur_window ∈ {10, 20, 50, 100, 200} | Larger window → more associations; trade-off | 5 min |

**Total:** ~52 min

---

## 4. Sensitivity Analysis (敏感性分析)

Sweep the three structural constants (δ, γ, τ) and key config parameters.

| ID | Test | Method | Expected Outcome | Est. Time |
|----|------|--------|-----------------|-----------|
| S1 | δ (DELTA) sweep | δ ∈ {0.05, 0.10, 0.15, 0.19, 0.25, 0.35, 0.50}, 2000 steps | Very small δ → too many frames; large δ → over-merging | 7 min |
| S2 | γ (GAMMA) sweep | γ ∈ {0.01, 0.025, 0.05, 0.10, 0.20}, 2000 steps | Small γ → weight inflation; large γ → too fast decay | 5 min |
| S3 | τ (TAU) sweep | τ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}, 2000 steps | Low τ → too frequent induction; high τ → too rare | 5 min |
| S4 | capacity + cooccur 2D | cap ∈ {8, 16, 32} × window ∈ {20, 50, 100} = 9 combos | Maps the stability region | 8 min |
| S5 | cooccur_thresh sweep | thresh ∈ {0.10, 0.15, 0.25, 0.40, 0.60}, 2000 steps | Low thresh → many false associations; high → none | 5 min |
| S6 | **Cross-impl consistency** | Same test (sine 2000 steps, cap=32) on both geme.py and geme_dynamic.py | Both implementations should give frame_count±3, MI±0.005 | 5 min |

**Hole plugged:** S6 — Two implementations must agree. Reviewer asks "Which implementation is the real GEME?"

**Total:** ~35 min

---

## 5. PhasePrompt: CoT + G (提示工程实验)

The LM experiment with self-referential prompts. Run only if `pythia-1.4b` is available.

| ID | Test | Method | Expected Outcome | Est. Time |
|----|------|--------|-----------------|-----------|
| P1 | Baseline | GSM8K 30 questions, no prompt engineering, exact answer match | 5/30 ≈ 17% (previously observed) | 2 min |
| P2 | CoT only | Add "Let's think step by step" | 4/30 ≈ 13% (previously observed) | 2 min |
| P3 | G only | Add "[self-ref] You are solving X type problem" | 4/30 ≈ 13% (previously observed) | 2 min |
| P4 | CoT + G | Both prompts stacked | 6/30 ≈ 20% (previously observed — synergistic) | 2 min |
| P5 | **Word-count control** | Same-length filler text ("The sky is blue and the grass is green and...") instead of G | If filler ≈ G, then G effect is just context length, not self-reference | 3 min |
| P6 | G position | G at start vs G at end vs G in system prompt | G position affects outcome? | 3 min |
| P7 | Full GSM8K | All 1319 test questions, CoT vs CoT+G | Statistical significance testing (binomial test) | 15 min |

**Hole plugged:** P5 — Word-count control. Reviewer says "Your G prompt is longer — the improvement is from more tokens, not self-reference."

**Total:** ~28 min

---

## 6. Statistical Reporting Standard (跨测试统计规范)

- **每个数值结果**报告为 `mean ± std (N_runs)`，例如 `MI=0.011±0.003 (N=10)`
- **组间比较**报告 Cohen's d（效应量），不仅仅是 p 值
- **收敛准则**：2000步后，若最后500步的帧数变化 < 5% 则视为收敛；否则增加步数到5000
- **多重比较校正**：将各补偿 Bonferroni 校正（α/N_test），避免随机显著

## 7. Summary Statistics (汇总统计)

After all tests, produce a single table of core claim confidence.

| Claim | Supporting Tests | Confidence | Key Weakness |
|-------|-----------------|------------|-------------|
| Self-reference is resource-neutral (MI→0) | N1-N6, R1-R4, S1-S6 | ★★★★★ | Permutation test needed if noisy data |
| L4 frames emerge only with self_observe | N5, A6 | ★★★★★ | Self_obs centroid is one vector — only 1 frame |
| d(w)/dt meta-frames detect cognitive change | A7, R6 | ★★★★☆ | Derivative threshold (0.02) is arbitrary |
| 3 constants produce stable economy | S1-S3 | ★★★★★ | Sweep range may not cover edge collapse |
| Capacity-MI boundary exists | R3, S4 | ★★★★☆ | Need analytical proof, not just sweep |
| PhasePrompt: CoT+G synergy | P1-P7 | ★★★☆☆ | Small sample; need full GSM8K for significance |
| Both implementations agree | S6 | ★★★☆☆ | Only 1 test case; need more overlap
| CoT+G synergistic effect | P1-P6 | ★★★☆☆ (small sample) |
| Capacity-MI boundary exists | R3, S4 | ★★★★☆ |

---

## Timeline

```
Phase 1: Negative controls    16 min  ← start here (includes N6: baseline)
Phase 2: Ablation             22 min
Phase 3: Robustness           52 min  ← longest phase
Phase 4: Sensitivity          35 min  ← includes cross-impl validation
Phase 5: Theorem robustness   57 min  ← Hammurabi / Q+G / Born / GR / 22-levels
Phase 6: PhasePrompt          28 min  ← includes word-count control

Total: ~210 min ≈ 3h 30min
```

Phases 1-2 can start immediately (no external data).
Phase 5 reuses existing standalone experiments — minimal setup.
Phase 6 requires LM loaded (can start while other phases run).

All tests runnable in parallel where hardware allows.
Each test writes results to `docs/robustness_results/` for traceability.
Final output: `docs/ROBUSTNESS_REPORT.md`.

---

## 6b. Theorem Robustness (核心定理鲁棒性)

Key results from standalone experiments — verify they hold across conditions.

| ID | Test | Method | Expected Outcome | Est. Time |
|----|------|--------|-----------------|-----------|
| T1 | **Hammurabi: multiple seeds** | CN + EN input, 10 different seeds each, measure association frame count delta | `|CN_frames - EN_frames|` ≤ 5 for all seeds | 8 min |
| T2 | **Hammurabi: sig perturbation** | Randomly swap 5% of characters in CN and EN texts, re-run | Structure partially broken; `|delta|` increases | 5 min |
| T3 | **Hammurabi: unrelated text control** | Replace EN with unrelated text (e.g., news article), compare CN vs unrelated | `|delta|` >> 5; structure does NOT converge | 3 min |
| T4 | **Q+G ≈ PA: seed sweep** | 10 seeds, measure L3 bridge frame overlap between Q+G and PA | Overlap ≥ 70% in every seed | 8 min |
| T5 | **Q+G ≈ PA: ablation** | Remove G from Q+G → should collapse back to Q structure | Q+G vs Q difference disappears | 5 min |
| T6 | **Q+G ≈ PA: unrelated G** | Replace G with random self-ref sentence (e.g., "This sentence is false") | Still produces PA-like structure? Or only with real G? | 5 min |
| T7 | **22 quantized levels: seed sweep** | 20 seeds, circle → count quantized peaks | 22 ± 2 levels in ≥ 18/20 seeds | 5 min |
| T8 | **22 quantized levels: frequency sweep** | Input frequency varied (0.5x, 1x, 2x, 5x), count levels | Level count should be frequency-independent | 5 min |
| T9 | **1.85x time dilation: seed sweep** | 10 seeds, measure relativistic factor γ | γ ∈ [1.75, 1.95] in ≥ 8/10 seeds | 5 min |
| T10 | **Born rule 49.3%: seed sweep** | 10 seeds × 3700 samples each, measure p(merge) | p ∈ [0.47, 0.51] in ≥ 9/10 seeds | 8 min |

**Total:** ~57 min

**What this defends against:**

| Reviewer Attack | Defense |
|----------------|---------|
| "Hammurabi convergence was a coincidence" | T1-T3 (seed sweep + unrelated control) |
| "Q+G≈PA is code-specific" | T4-T6 (seed sweep + ablation + probe) |
| "22 levels from circle is cherry-picked" | T7-T8 (seed + frequency sweep) |
| "GR 1.85x was one lucky run" | T9 (10 seeds) |
| "Born 49.3% is measurement noise" | T10 (10 seeds × 3700 samples) |

**Hole plugged by this module:** Without these, the paper's headline results have zero robustness evidence.

---

## 8. What This Plan Defends Against

| Reviewer Attack | Defense |
|----------------|---------|
| "Your MI→0 is just small sample" | N6 (random baseline), R1-R4 (scale sweep) |
| "Your L4 is an artifact of implementation" | S6 (cross-impl), A1-A8 (ablation) |
| "Your PhasePrompt result is from more text, not self-ref" | P5 (word-count control) |
| "Your results are just seed luck" | R1-R2 (30 seeds, reported as mean±std) |
| "Your constants are cherry-picked" | S1-S3 (sweep plus Bonferroni) |
| "Your model is too small to matter" | R3-R5 (capacity + complexity sweep) |
| "Your implementation has no stats" | 6.5 (effect size + convergence criterion) |
