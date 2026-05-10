# LLM-related experiments: PhasePrompt + Grokking

## PhasePrompt

Tests whether self-referential (G) prompting improves LLM reasoning.

| File | Description |
|------|-------------|
| phaseprompt_v3_final.json | v3: True self-ref prompt "recall what you know" |
| phaseprompt_night.json | v1: Weak G prompt "focus on..." |
| phaseprompt_v2.py | Original G prompt: "[self-ref] identify type→apply rules→compute" |

Key finding: G alone does NOT improve accuracy (8-11% vs 10% bare).
G helps only when combined with structure (CoT+G=10% vs CoT=17%).
Self-reference in LLMs requires structural scaffolding, not magic sentences.

## Grokking

Tests whether G-sentence accelerates grokking (sudden generalization).

| File | Description |
|------|-------------|
| grokking_clean.json | Power et al. framework, 30% data, 2-layer transformer |
| grokking_results.json | v1: 50% data, grokked at 130 steps |
| grokking_v2_results.json | v2: 10-20% data, regression test |

Key finding: In 2-layer setting with 50% data, G condition showed
higher retention after weight decay collapse (0.749 vs 0.279).
G helps structural memory persist through forgetting phases.

## Running

Scripts in this directory require `../code/geme.py` (GEME engine).
PhasePrompt scripts also require: torch, transformers, datasets (Pythia-1.4b).
