# GEME — Project Roadmap (Paper-Ready)

**Last updated**: 2026-05-04  
**Status**: V10 code frozen. Pre-submission optimization pending.

---

## Three Tracks Status

### Track 1: Code Completeness — ✓ DONE (V10)

```
Core engine (geme_v6.py): 288 lines
  Adaptive threshold (bootstrap from data)
  Association/chain vectors (weighted avg)
  Weight = compression contribution
  Zero-axiom design
  Fully endogenous self-reference (no S4)
```

### Track 2: Experimental Validity — ✓ MOSTLY DONE

```
[✓] PA emergence (add_comm consistent)
[✓] GO geometry concept network
[✓] Blation (3 conditions, with statistical tests)
[✓] Hyperparameter robustness (cap 4-16, window 30-80)
[✓] Zero-shot generalization
[✓] Negative control
[ ] Large-scale robustness matrix (postphoned to paper review)
    - cap=12+window=120 to cap=16+window=200
    - Expected: all stable, no fine-tuning required
    - Cost: ~12-16hr continuous run → not worth now
```

### Track 3: Framework Exploration — ✓ CORE COMPLETE

```
[✓] S0->L1->L2 hierarchy (weight ratio ~100:2:1)
[✓] Information theory paradox documented
[✓] Cohen's d=3.36 (large effect)
[✓] Hebbian reference
[ ] Paper structure — under philosophical design

Note: All experimental data requires human philosophical interpretation.
The system's value lies in organization, not compression.
Standard metrics cannot capture this — human reading is the only extraction method.
```

## Paper Components

```
1. Core engine design (philosophy + architecture)
2. PA experiments (ablation + robustness + stats)
3. GO experiments (concept emergence + hierarchy)
4. Comparison with Hebb / GEB / Free Energy
5. Methodology (zero-axiom, endogenous self-ref)
6. Discussion (information paradox, limitations)
```

## Milestones

```
[✓] V6.5: PA emergence (arithmetic)
[✓] Phase 6 GO: Geometry concept network
[✓] Recursive self-reference mechanism
[✓] Hofstadter correspondence (2026-05-04)
[✓] S4 retired (endogenous co-occurrence)
[✓] V8: Adaptive threshold, weighted vectors
[✓] V10: Complete endogenous, philosophical framing
[ ] Pre-submission: Large matrix + paper draft
```

## Key References

```
- Hebb (1949): "Organization of Behavior" — co-occurrence ancestor
- Hofstadter (1979): "Goedel, Escher, Bach" — strange-loop inspiration
- Friston (2024): Free Energy Principle — orthogonal comparison
