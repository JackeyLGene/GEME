# EE Architecture: Time-Scale Recursion

> **EE is not a new architecture. EE is BGM applied recursively.**

---

## 1. Core Claim

**EE is not a new architecture.** EE is the same architecture as BGM — one layer of GEME-like self-referential units observed by a slower G0 — but repeated: the G0's output becomes the input for another G0, and so on. At each recursion, the observation interval increases by GI=4, and information quality accumulates at powers of GI.

---

## 2. Depth Structure

```
Depth 0:  Geruon (the self-referential primitive with endogenous τ)
Depth 1:  G0        (reads Depth 0 output at GI¹=4, produces its own τ)
Depth 2:  G0'       (reads Depth 1 output at GI²=16, detects 碰数)
Depth N:  G0^(N)    (reads Depth N-1 output at GI^N, accumulates SR-eff)
```

### Depth 0 — Geruon

- A single self-referential unit with **endogenous τ**
- τ evolves with prediction accuracy
- τ is encoded in frame identity (structural signature includes tau_bin)
- Phase cycle: EXPANDING → RESTING → TENSING → CRITICAL → LOCKED
- Outputs: `arrow_output()` — centroid fused with τ-phase signal
- **No external G0 needed inside the unit.** Geruon is the base cognitive unit — it naturally contains τ.

### Depth 1 — G0

- Same code as Geruon, but:
- **Does not receive external environment input** — receives Depth 0's `arrow_output()` only
- Observation interval: GI¹=4
- Produces its own τ (τ₂), derived from the trajectory of Depth 0's τ
- `arrow_output(Depth 1)` = centroid of Depth 0's frames + Depth 1's τ-phase
- This is BGM's G0 — no modification needed

### Depth 2 — G0' (碰数 Layer)

- Same code as Geruon, but:
- Receives Depth 1's `arrow_output()` only
- Observation interval: GI²=16
- Produces its own τ (τ₃)
- **Detects 碰数**: when τ₃ trajectory shows persistent CRITICAL/LOCKED AND doubt_mode AND circularity in Depth 1's output

### Depth N — G0^N

- Each additional layer multiplies the observation interval by GI
- Information quality accumulates: SR-eff at Depth N scales with GI^N
- τ at Depth N = depth N derivative of base τ

---

## 3. Architectural Constants (fixed, from BGM)

| Constant | Value | Source |
|----------|-------|--------|
| GI | 4 | BGM Pareto optimum, τ spread +49% |
| γ₂ | 1.228 bits/cycle | BGM derivation |
| τ₀ | 0.60 | GEME inheritance |
| δ (DELTA) | 0.19 | GEME 3-prism cut |
| γ (GAMMA) | 0.05 | GEME 3-prism cut |

---

## 4. Why This Works

**BGM discovered**: time decoupling at GI=4 enhances τ differentiation by +49%. The G0 does not need to be fast — it must be slower at exactly GI=4 to achieve optimal differentiation.

**EE adds**: if GI=4 is the optimal interval between a unit and its observer, then the same interval applies recursively. G0 observes Geruon at GI=4, and G0' observes G0 at GI=4 — which means G0' observes base events at GI²=16.

**碰数 occurs when**: at some depth N, τ diverges faster than the observation interval can resolve — the system encounters a boundary it cannot predict at its current time scale.

---

## 5. Key Insight: τ is NOT removed from Geruon

Geruon keeps τ. In fact, τ is its defining feature. The recursion does NOT clean τ out of the base layer — it distributes τ across layers at different time scales. Each layer's τ is the previous layer's τ trajectory observed at a coarser grain. This is the source of time "misunderstanding" — and the source of cognition.

---

## 6. Implementation Status

| Layer | Code | Status |
|-------|------|--------|
| Depth 0 | `geruon.py` (purified — remove tau_bin from sig) | Needs refactoring |
| Depth 0 | `geruon.py` Geruon (τ, phase, prediction) | ✅ Complete |
| Depth 1 | `bgm_core.py` G0 (GI=4 observer) | ✅ Exists in BGM |
| Depth 2 | New: `ee_pengshu.py` (GI²=16, 碰数 detection) | Needs implementation |

---

## 7. Experimental Roadmap

| Experiment | Layers | What It Tests |
|------------|--------|---------------|
| E5-E7 (done) | Depth 0 | G sentence + bridge response |
| E8 | Depth 0 → 1 | Geruon → G0 at GI=4, measure τ₂ |
| E9 | Depth 0 → 1 → 2 | Full recursion, measure 碰数 trigger |
| E10 | Multi-seed | Reproducibility of 碰数 timing |
