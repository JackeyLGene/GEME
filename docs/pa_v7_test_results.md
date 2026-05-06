# GEME V7 — PA Comprehensive Test Results

## E1: Experiment Matrix

## E2: Co-occurrence Threshold Sweep

## E3: Zero-shot Generalization

## E4: Negative Control (no S2)

## Summary: V6 (external S4) vs V7 (endogenous co-occurrence)

| Aspect | V6 (external S4) | V7 (co-occurrence) |
|--------|------------------|--------------------|
| Self-reference source | Pre-coded Godel formula | Endogenous sliding window |
| Association discovery | None | Co-occurrence → L1 frames |
| Inference chains | None | Shared element → L2 chains |
| S4 requirement | External injection | 0 external dependencies |
| Code complexity | 178 lines | ~200 lines (same Memory) |
| add_comm (E1) | ~35% (with S4) | Varies with threshold |
| assoc frames | 0 | Observed (1 in neg ctrl) |
| chain frames | 0 | Observed (0 in neg ctrl) |