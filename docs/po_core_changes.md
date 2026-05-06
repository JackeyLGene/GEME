# Phase Ouroboros — Core Engine Changes

## Change 1: Co-occurrence Decay & Threshold (2026-05-04)

**Problem**: Co-occurrence decay (0.8x per step) prevented `count>=15` threshold
from ever being reached. Same-signature pairs were also excluded by `s1==s2: continue`.

**Solutions**:
- Removed decay (`self._cooccur[key]*=0.8`) — window size (max 80 entries) naturally bounds dictionary growth
- Changed `s1==s2: continue` to `id1==id2: continue` — different instances of same concept CAN co-occur
- Changed `count>=15` to `count>=max(5, total_steps*0.05)` — relative threshold

**Impact**: Phase 0 (mixed-stream classification) now confirmed.

## Change 2: Vector Table Expansion (2026-05-04)

**Problem**: `fn`/`const` fallback slots collapsed all custom function symbols into
the same vector dimension, losing symbol identity information.

**Solution**: Pre-expanded `_ALPHABET` with known experiment symbols:

| Slot | Domain | Symbols |
|------|--------|---------|
| 0-11 | PA | 0, 1, s, +, ×, =, forall, exists, x, y, z, sub |
| 12-14 | E1: Algebra | swap, pair, comm |
| 15-18 | E2: Induction | set, succ, empty, rank |
| 19-24 | E3: Spatial | point, line, shape, parallel, angle, triangle |
| 25-26 | Fallback | fn, const |

**Design intent**: The vector table is a pedagogical ladder (like teaching a child
basic color names). The cognitive unit does not know the table exists — it only
sees the frequency vectors. Future work may explore dynamic self-naming
(automatic dimension allocation for novel symbols).

## Change 3: `process_sig` Method Added (2026-05-04)

**Problem**: `process()` used PA-specific `compute_signature()` that doesn't
recognize custom function symbols (swap, succ, etc.).

**Solution**: Added `process_sig(formula, sig)` method that accepts an explicit
structural signature, bypassing `compute_signature()`.

**Impact**: Same GEME engine serves PA experiments (via `process`) and
Phase Ouroboros experiments (via `process_sig`).

## Change 4: Adaptive Threshold Floor (2026-05-04)

**Problem**: When all merge distances are 0 (identical vectors), median=0 leads to
`thresh=0`, which blocks all future merges (zero-deadlock).

**Solution**: `last_ok*0.5` floor on adaptive threshold.
Merge condition changed from `bd<thresh` to `bd<=thresh`.

**Impact**: Prevents deadlock in single-structure-type streams.

## Change 5: Association Frame Weighted Vector (2026-05-04)

**Problem**: Association frame vector fell back to all-zeros when >2 matching 
instance frames were found (e.g., 4 eq_swap_swap frames all match the same 
co-occurrence pair (eq_swap_swap, eq_swap_swap)).

**Solution**: Changed `len(base_vecs)==2` condition to `len(base_vecs)>=2`,
using weighted average of ALL matching frames:
  `assoc_vec = Σ(frame.vec × frame.weight) / Σ(frame.weight)`

**Impact**: Association frames now carry interpretable semantic vectors
(weighted concept centroids) regardless of matching frame count.

## Change 6: Chain Frame Cap (2026-05-04)

**Problem**: Chain frame creation (══) had no upper bound — any association
frame with weight>20 could trigger chains, causing combinatorial explosion
that filled memory with chain frames and evicted instance frames.

**Solution**: Added `max_chains` parameter (default=5) and `_chain_count`
tracker. Chain creation stops once `_chain_count >= max_chains`.

**Impact**: Memory remains balanced between instance/concept/chain layers.
Geometry experiments (E3) can set `max_chains=0` for pure association observation.
