# geme-physics

A competitive memory system whose merge threshold δ adapts to input density.
At high density → GR-like time dilation.
At probabilistic merge → QM-like measurement statistics.

**Dimensionality note:** the vector space is currently 27-dimensional (inherited from a 27-symbol alphabet in the original architecture). This is a historical artifact and does not affect the core finding. The ratio δ/||V|| (threshold to vector magnitude scale) is the only relevant parameter. Any dimension > 3 produces qualitatively identical results.

## Key findings

1. **Density → time dilation:** input density ρ correlates with frame generation rate γ. γ_high/γ_low ≈ 1.85. Analogue of gravitational time dilation in GR.
2. **Probabilistic merge → quantum statistics:** Boltzmann-weighted selection among frames reproduces Born rule statistics (49.3% ± 2.0% split in 5-seed test). Centroid-invariant (Zeno) merge preserves superposition.
3. **Both from δ:** the same adaptive merge threshold controls both phenomena.

## Files

- `geme.py` — engine (required)
- `core_finding_clean.txt` — detailed write-up
- `quantum_zeno.py` — probabilistic merge test
- `simulation_universe.py` — density/dilation test
- `threshold_reality.py` — threshold-as-resolution demonstration

## Status

Observation report. Not a formal paper. Feedback welcome.
