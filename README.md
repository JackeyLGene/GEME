# GEME — Generative Economy Memory Entity

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20059553.svg)](https://doi.org/10.5281/zenodo.20059553)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## A Prism, A Telescope

GEME is a minimal computational system built on three axioms:

1. **Competitive merging** — new input merges into the closest existing frame, or creates one
2. **Adaptive forgetting** — frames decay and are pruned under economic pressure
3. **Self-referential observation** — the system observes its own frame economy and feeds the observation back

Zero neural networks. Zero backpropagation. Zero free parameters. Three structural constants.

Shine any structured input through GEME and look at what emerges: quantized levels, time dilation, semantic convergence, self-referential prediction, anomaly detection. It is a prism — it decomposes information into frames and shows you the structure inside. It is a telescope — it points at things you already know and lets you see them differently.

No domain knowledge is programmed in. Everything that emerges is a property of the frame economy itself.

## Quick Start

```python
from geme import GEME, eq, fn, const
g = GEME(memory_cap=16)
# Process symbolic formulas
f = eq(fn("swap", const("1"), const("2")),
       fn("swap", const("2"), const("1")))
result = g.process_sig(f, structural_signature(f))
# Read all metrics
print(g.metrics())
```

No external dependencies. Python 3.8+ stdlib only.

---

## What Emerges

| Experiment | Observation | Invites |
|-----------|-------------|---------|
| Gödel Bridge | Self-reference carries near-zero mutual information with input | Information theory, formal systems |
| L4 Prediction | The system learns to predict the next input in a sequence | Cognitive science, anomaly detection |
| Consciousness Economy | Prediction costs ≈ verification costs in the frame economy | Computation complexity, P vs NP in self-referential systems |
| 22 Quantized Levels | A continuous circle is discretized into 22±2 frames | Physics, quantization |
| Time Dilation (1.85×) | Fast inputs produce fewer frames than slow ones | General relativity, time in frame economies |
| Born Rule (49.3%) | Equal-distance inputs merge probabilistically with 50/50 distribution | Quantum mechanics, measurement |
| Translation Invariance | Chinese and English texts converge to the same frame structure | Linguistics, semantics |
| Justice Structure (v6) | Social concepts (crime→punishment→class) produce identical L4 behavior across 3 scripts | Anthropology, social cognition |

---

## Structure

```
L1 ── L2 ── L3 ── L4 ── L5 ── L6
实体    关联    桥接    预测    元观测    统摄

(L1,L2,L3) = world processing — what is
(L4,L5,L6) = self-referential verification — what should be
```

---

## Repository

```
geme.py              — core engine
geme_dynamic.py      — dynamic vocabulary variant
docs/                — design spec, code audit, robustness report
standalone/          — 80+ validation experiments
preprint/            — paper drafts (CN/EN)
```

## Using It

Point GEME at your own data:

- Feed it legal texts and watch it discover structure across languages (`standalone/hammurabi_v3_cuneiform.py`)
- Feed it formal systems and watch Gödel sentences behave like induction axioms (`standalone/exp_godel_proof_test.py`)
- Feed it sensor data and watch it detect anomalies through L4 prediction

The companion paper describes the framework and observations. The code is the invitation.

## Protocol

Apache 2.0. All claims are empirically supported by reproducible experiments in the repository. Contributions, forks, and independent reproductions are welcome.

## Citation

```bibtex
@misc{liu2026geme,
  author = {Liu, Jieqi},
  title = {GEME: A Self-Reflective Prism Framework for Cognition},
  year = {2026},
  doi = {10.5281/zenodo.20059553}
}
```
