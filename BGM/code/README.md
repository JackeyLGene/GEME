# BGM Experiments

> Building Bridge — cross-scale universal emergence from standard GEME primitives.

## Code Structure

| File | Purpose |
|------|---------|
| `geme.py` | Standard GEME kernel (copy from GEME v1.1, unmodified) |
| `bgm_core.py` | `GEMENet` — multi-GEME network container with G0 feedback |
| `bgm_experiment.py` | Experiment runner: Bach BWV 846 with/without G0 |
| `data/bwv846.py` | Hz-encoded Bach prelude data |
| `cat_on_mat_test.py` | Granularity test (deprecated after TEMPORAL_ANALYSIS.md) |
| `concept_hertz.py` | Initial Hz concept (deprecated) |
| `concept_hertz_full.py` | Full prelude test without G0 (deprecated) |

## Core Design

**GEME unchanged.** Always receives from environment. L6 = only output.

**G0 is a standard GEME.** Not a special component. Receives aggregated L6 from all units. Its self-observation vector feeds back as environmental context to each unit.

**Feedback = context modulation, not instruction.** G0 doesn't tell a unit "specialize in low frequencies." It provides a global state vector that shapes each unit's response to the same external input — analogous to contextual modulation in neural systems and quorum sensing in bacterial colonies.

## Experiments

### Experiment 1: Bach BWV 846 (this repo)

- 3 GEME units hearing Hz-encoded prelude
- 1 G0 unit aggregating L6, feeding back
- Ablation: remove G0 → units collapse to redundancy

### Experiment 2: Bacteria (planned)

- 16 GEME units in 4x4 grid
- No explicit G0 — only local neighbor communication
- Quorum-sensing emergent behavior

### Experiment 3: The Bridge (planned)

- Apply inter-GEME communication pattern from bacteria to Bach
- Verify statistical isomorphism via KS test

## Usage

```bash
python bgm_experiment.py
```

## Red Lines

- No LLM/AI/GPT mentions
- No third paper (External Engine) content
- All framework ideas attributed to Dennett
- "First brick-maker" writing stance

## References

- Dennett, D. (2017). *From Bacteria to Bach and Back*
- Felleman, D. J., & Van Essen, D. C. (1991). Distributed hierarchical processing in the primate cerebral cortex.
