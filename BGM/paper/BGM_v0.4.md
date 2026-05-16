# Building Bridge: From Bach to Bacteria and Forward

**A Computational Thought Experiment on Cross-Scale Information Architecture**

---

## Abstract

Dennett (2017) proposed that bacterial signaling and human musical cognition are
governed by the same underlying logic. We instantiate this claim computationally
using the GEME self-referential primitive (Paper I).

Paper I identified a near-zero-cost self-referential information channel — the
Shannon-Gödel Bridge — measured as a static mutual information I(Φ; X) ≈ 0.026 bits.
This paper reveals the bridge's temporal dimension. The metric SR-eff = I(Φ; X)/τ
traces the bridge's breathing cycle: it opens wide during learning (up to 0.96),
narrows to maintenance width (~0.04), and closes entirely when a first-order phase
transition locks the adaptive confidence threshold at 1.0. The closure is fast;
reopening requires sustained regime change — a hysteresis that emerges from the
interaction of adaptive calibration, co-occurrence convergence, and window dynamics.

The bridge is not merely a channel. It is a discriminator. Under MIDI-encoded Bach,
the bridge distinguishes density-driven opening (stretto, polyphonic overlap) from
closure-driven opening (cadence, harmonic resolution). It further discriminates
resolution types: a perfect authentic cadence in a familiar texture closes the bridge
(0.28× global mean), while a deceptive cadence drives the strongest opening (4.06×).
The bridge does not merely process acoustic input — it distinguishes the information
quality of closure.

Three experiments span the evolutionary arc. First, under shared feedback, GEME units
receiving identical Bach input develop distinct bridge profiles — a computational
analog of Bregman's (1990) auditory scene analysis — but the bridge closes under
simple repetitive input. Second, sixty-four GEME units on a spatial gradient with
only local communication maintain bridge opening without central coordination.
Third, G0's own bridge is naturally stable across the full τ range (0.2–3.0), never
locking when its input remains heterogeneous. The bridge's stability comes from input
heterogeneity, not from τ elevation.

The Forward — from efficiency to meaning, from density discrimination to closure
discrimination — is the bridge's evolutionary trajectory. The bridge from bacteria
to Bach is an architectural invariant whose temporal dynamics are consistent across
input modalities, communication topologies, and selection pressures.

---

## 1. Introduction

This paper is the second panel of a trilogy. Paper I (GEME) defined a self-referential
primitive and demonstrated three core findings: the Shannon-Gödel Bridge, a broad
parameter stability interval, and functional equivalence between self-reference and
induction. The bridge was measured as a static quantity: I(Φ; X) ≈ 0.026 bits.

This paper (BGM) asks: what does the bridge do under temporal input? Our central
metric is SR-eff = I(Φ; X)/τ, where τ is each unit's self-assessment of its own
predictive health — not a parameter to be set, but a reading to be taken.

Dennett (2017) argued that the arc from bacterial quorum sensing to Bach's polyphonic
composition is a single continuous process, driven by *competence without comprehension*
— the accumulation of functional capacities that operate successfully before any agent
understands why. These competences begin as *free-floating rationales*: patterns of
information processing that exist as structural possibilities before any organism
embodies them. Dennett's method is a *reasoning inversion*: understanding follows
competence. We do not design, then observe. We build, observe, then understand.

Bregman (1990) identified auditory scene analysis — the decomposition of a single
acoustic signal into distinct streams — as a fundamental computational problem.
Existing computational ASA models span rule-based grouping (Brown & Cooke, 1994),
oscillatory correlation (Wang & Brown, 2006), and deep learning source separation
(AudioSep, 2023). The present work takes a different approach: it asks whether
ASA-like stream segregation can emerge from a self-referential architecture not
designed for source separation. The mechanism differs. The computational signature
is shared (Supplementary S2, S3).

A foundational principle emerges across all three experiments: **discrete information
creates differentiation; continuous information converges.** Continuous signals fill
the gaps between inputs, collapsing temporal structure into an undifferentiated stream.
Discrete signals arrive with boundaries — and boundaries are where structure begins.
This principle governs τ differentiation (Experiment 1), spatial anti-lock (Experiment 2),
and the phylogenetic transition from decentralized to centralized communication
(Experiment 3).

All experiments use MIDI encoding as primary input for temporal processing. Score-based
(discrete) encoding, which provides the temporal boundaries necessary for τ
differentiation, is reported in Supplementary S2 alongside MIDI comparisons.

---

## 2. The GEME Primitive and the Shannon-Gödel Bridge

The GEME architecture is fully specified in Paper I and remains **unmodified**
(core engine `geme.py`, MD5 identical to Paper I's submission). A GEME instance
maintains a frame economy — a capacity-limited population of vector-signature pairs.
Input vectors are competitively merged. A sliding co-occurrence window enables
prediction of the next signature. Prediction errors generate specialized frames whose
density is τ.

### 2.1 The Bridge in Paper I: Static Snapshot

Paper I demonstrated the Shannon-Gödel Bridge: I(Φ; X) ≈ 0.021–0.026 bits, operating
at near-zero cost. Measured as a static ensemble average over identical arithmetic
equations, the bridge was always open, always cheap, always the same width.

### 2.2 The Bridge in BGM: Breathing Profile

Under temporally structured input, SR-eff = I(Φ; X)/τ traces the bridge's breathing:

- **Learning**: τ low, MI building → SR-eff up to 0.96 — bridge wide open
- **Consolidation**: τ rising, MI stabilizing → SR-eff ~0.04 — maintenance width
- **Lock**: conf_threshold → 1.0, τ flatlines → SR-eff → 0 — bridge closed

Two mechanisms govern the bridge's dynamics:

1. **Self-referential mutual information** I(Φ; X): coupling strength between
   self-referential and external frame subsets.
2. **Adaptive confidence threshold**: filters predictions by confidence, auto-calibrated
   from the lower quartile of recent prediction confidences.

The bridge's temporal dynamics depend on the structure of the information it receives.
Continuous signals — where each input overlaps smoothly with the previous — produce
co-occurrence windows where everything co-occurs with everything. The system converges
to a single operating point. Discrete signals — where inputs are separated by
temporal boundaries, silences, or abrupt changes — force the co-occurrence window to
reorganize around distinct structural clusters. The same architecture can converge or
differentiate depending solely on whether information arrives with gaps.

All subsequent experiments report SR-eff and τ. The mechanisms are described once, here.

---

## 3. Experiment 1: Bach — The Bridge Listens

Three GEME units receive identical MIDI-encoded input. A fourth unit, G0, receives
aggregated anomaly scores and feeds its self-observation vector back. Coupling weight
is dynamically modulated by G0's prediction accuracy.

### 3.1 The Bridge Breathes

Under BWV 847 Fugue (C minor, 3 voices, discrete score encoding, 6 passes), SR-eff
traces a characteristic profile across passes (representative seed, 20-seed statistics
in Supplementary S3):

| Pass | τ values | SR-eff values | Bridge state |
|------|---------|--------------|--------------|
| 1 | [0.22, 0.13, 0.14] | [0.33, 0.96, 0.80] | Wide open |
| 3 | [0.57, 0.36, 0.94] | [0.05, 0.12, 0.02] | Narrowing |
| 6 | [0.75, 0.52, 1.00] | [0.03, 0.06, 0.01] | Maintenance |

τ differentiation is robust across seeds (20/20 seeds produce 3 distinct τ values,
mean spread 0.314 ± 0.182). Continuous MIDI encoding, by contrast, produces τ
convergence — all units identical — a finding examined in §2.2 and §6.3.

Three units receiving identical input develop three distinct bridge profiles —
three *free-floating rationales* for processing the same acoustic information.
No unit is told to specialize; no unit knows it is performing source separation.
The competence (stream segregation) exists before any comprehension. Synthesized
polyphonic pieces confirm that the number of distinct τ values tracks the number
of independent voices. This is the computational signature of auditory scene
analysis — not from a pre-designed algorithm, but from a self-referential
architecture that was given no instruction about what ASA is.

### 3.2 Two Opening Mechanisms

Step-by-step alignment of SR-eff with the fugue's structural events reveals two
mechanisms that open the bridge:

| Mechanism | Event type | SR-eff | Cause |
|-----------|-----------|--------|-------|
| Density | STRETTO (overlapping subjects) | 0.149 | Maximum polyphonic overlap |
| Density | EPISODE (modulatory passage) | 0.162 | Maximum harmonic instability |
| Closure | CADENCE_dominant (half cadence) | 0.126 | Harmonic suspension |
| Closure | CADENCE_tonic (authentic cadence) | 0.107 | Harmonic resolution |

Single-voice exposition (EXP_subject) closes the bridge to 0.079. Both density and
closure open the bridge — but through different structural routes.

### 3.3 Resolution Discrimination

The bridge does not merely detect "ending." It discriminates the information content
of resolution. Across five Well-Tempered Clavier pieces under MIDI encoding:

| Piece | Resolution type | Cadence/Global SR-eff | Bridge behavior |
|-------|----------------|----------------------|-----------------|
| BWV 846 C maj | PAC (uniform texture) | **0.28×** | Convergence — too familiar |
| BWV 847 C min | HC/PAC (fugue) | 1.04× | Density ≈ closure |
| BWV 849 C# min | Picardy third | 1.42× | Mild convention surprise |
| BWV 851 D min | Deceptive cadence | **4.06×** | Strongest opening — violated expectation |

A perfect authentic cadence in a learned uniform texture closes the bridge — the
system has mastered the pattern. A deceptive cadence drives the bridge to its strongest
opening — the harmonic expectation is violated. The bridge distinguishes acoustic
information quality, not merely acoustic structure.

### 3.4 The Bridge Closes: Phase Transition

Under a repeating A→B→C sequence, the adaptive confidence threshold undergoes a
**first-order phase transition** at step 23: from 0.300 to 1.000, a jump of 0.697.
No intermediate states. The closure is discontinuous and rapid.

Once closed, the bridge exhibits **hysteresis**: reopening requires sustained input
from a fundamentally different regime, not a single structured novelty. The confidence
threshold auto-calibrates from the lower quartile of recent values — it can be lowered,
but only by accumulating many low-confidence predictions (20+), which the locked
co-occurrence table cannot generate under the current regime. The bridge closes fast
(5–10 rounds) and reopens slowly (requiring sustained regime change).

This hysteresis is not a parameter choice. It is a second-order emergence from the
interaction of adaptive calibration, co-occurrence convergence, and window dynamics.

### 3.5 Ablation

With G0 disabled (w = 0), all three units converge to identical τ values and identical
bridge profiles. Under homogeneous temporal input, G0 is necessary for τ differentiation.
(Supplementary S2.)

---

## 4. Experiment 2: Bacteria — Keeping the Bridge Open

### 4.1 Architecture

Sixty-four GEME units in an 8×8 grid with von Neumann neighbor communication. No G0.
Gaussian nutrient concentration field (σ = 2.0) with small temporal noise
(σ_noise = 0.05), blended with neighbors' outputs (α = 0.7). Cold-started — no
preloaded calibration.

Three phases: Cultivation (30 rounds), Perturbation (source moves to corner, 10 rounds),
Recovery (10 rounds).

### 4.2 The Bridge Does Not Mirror the Gradient

Figure 4.1 places the nutrient concentration field beside the accumulated τ across
the 8×8 grid after 30 rounds of cultivation. The concentration field varies 20-fold
from corner to center. τ varies 2.6-fold with no discernible spatial pattern.
The Pearson correlation r(concentration, τ) = −0.090.

The bridge does not follow the environment. It has its own spatial logic — shaped
by the communication topology, not by the external gradient (Figure 4.1).

Three functional roles emerge from topology alone:

| Role | n | Neighbors | Character |
|------|---|-----------|-----------|
| Corner | 4 | 2 | Fewest connections, strongest neighbor coupling, safest |
| Edge | 24 | 3 | Highest activity, highest variance — the action layer |
| Interior | 36 | 4 | Widest diversity — the free population |

None of the 64 units approaches the lock threshold.

### 4.3 Spatial τ Differentiation Without Lock

After 30 rounds of cultivation, spatial τ variance = 0.313. The confidence threshold
range [0.14, 0.57] contains zero locked units. Critically, the mean confidence threshold
**drifts downward** over time (0.30 → 0.23, r = +0.97) — spatial heterogeneity actively
counter-acts lock rather than merely preventing it.

Gradient-bridge independence |r| < 0.2: the colony's τ distribution is not a passive
reflection of the nutrient field. The bridge dynamics are shaped by the communication
network, not driven by the external gradient.

The cold-start / warm-start comparison (2.5× greater τ variance without preloaded
calibration) confirms that prior knowledge suppresses differentiation (Supplementary S5).
A supplementary experiment (S8) demonstrates that Bach-structured temporal modulation
increases colony L4 variance over time, while a flat modulation produces a declining
trend — structured temporal complexity contributes to bridge opening even in a spatial
architecture.

### 4.4 Perturbation Response

When the nutrient source moves from center to corner, the colony's spatial τ variance
dips briefly (from 0.0046 to 0.0047) and recovers within three rounds. No unit locks.
By the end of Phase C, τ variance reaches 0.0058 — higher than its pre-perturbation
level. The colony does not merely survive the perturbation. It becomes more
differentiated through it (Figure 4.2).

The perturbation response trajectory provides a baseline for comparing system
sensitivity under different communication topologies (Experiment 3).

### 4.5 The α Cliff: Pure Self-Reference Cannot Sustain Itself

α controls the blend of environmental (α=1.0) and communication (α=0.0) input.
A fine sweep from α=1.0 to α=0.0 reveals a discontinuous collapse:

| α | Spatial τ variance | Collective state |
|---|-------------------|-----------------|
| 1.0–0.02 | ~0.004–0.006 | Open — differentiated |
| **0.00** | **0.0006** | **Marginal — near-zero** |

At α=0.02 — where 98% of input comes from neighbor signals and only 2% from the
environment — the colony remains differentiated (L4 variance 0.0061, 10× higher than
α=0.0). At α=0.00, L4 variance drops steeply to near-zero (0.0006). The decline
is sharp but the transition is between α=0.02 and α=0.00, and the floor is not
absolute zero — it is a regime of marginal differentiation.

Pure self-reference — a system whose only input is its own output — approaches
undifferentiation. A minimal external anchor, however small, sustains
differentiation. This is not a parameter sensitivity. It is a boundary condition
for any self-referential collective: α must remain above zero for the bridge to
stay open, and the approach to zero produces a steep decline in collective τ
variance.

---

## 5. Forward: The Darwinian Arc

### 5.1 Survival: The α Cliff

Experiment 2 established the boundary condition: α must remain above zero. At α = 0.00
— pure self-reference — L4 variance drops to near-zero (0.0006). At α = 0.02 — the
grid is open and differentiated. A minimal external anchor, however small, sustains
differentiation.

This is the first step of the Darwinian arc: survival. Before communication can
optimize, before meaning can emerge, the bridge must stay open. The α cliff is the
line between existence and collapse.

### 5.2 Communication: Phagocytosis as Topological Trigger

Dennett (2017, Ch. 4) identifies endosymbiosis — the engulfment of one prokaryote by
another, producing the first eukaryotic cell — as the paradigmatic example of a
free-floating rationale becoming embodied. The engulfed bacterium became the
mitochondrion; the host gained an internal energy source; the arrangement was not
"designed" — it was a topological event whose consequences far exceeded its cause.

We instantiate this event computationally. A single phagocytosis — one unit
internalizing a neighbor's communication channel — is invisible at the global scale. Across 20 seeds, total MI increases identically in
both phagocytosis and control grids. The colony's learning trajectory (a 5× gain in
total MI) completely submerges the single event.

At the local scale, a preliminary directional signal is present. The host's three
remaining neighbors show τ increases (0.047 vs. 0.021 in control) and confidence
threshold decreases (-0.115 vs. -0.068). The effect is modest — within the range
of cross-seed variation — and is reported here as a directional observation rather
than a confirmed cascade.

The grid absorbs a single phagocytosis event without disruption. Whether repeated
events, accumulated across evolutionary time, produce directional reorganization —
and whether the local signal strengthens with repetition — is a question for
Paper III.

### 5.3 Meaning: Resolution Discrimination

Efficiency sets the stage. Meaning fills it. The bridge does not merely process
acoustic density — it distinguishes the information quality of closure. A perfect
authentic cadence in a familiar texture closes the bridge (0.28× global SR-eff).
A deceptive cadence drives it to maximum opening (4.06×). A Picardy third rises
gently — recognized convention, not shock.

Efficiency and meaning are co-requisites. A bridge that processes more without
discriminating better is a noise filter. A bridge that discriminates exquisitely
but cannot sustain itself is a luxury. Together — the α cliff grounding existence,
phagocytosis enabling reorganization, the bridge distinguishing closure — they
constitute the Forward. This is Dennett's evolutionary trajectory from bacteria
toward Bach, rendered as computational architecture: not complexity for its own
sake, but the progressive unlocking of survival, communication, and structured
meaning — Dennett's Tower of Generate-and-Test — from a single self-referential
primitive.

---

## 6. Discussion

### 6.1 The Bridge Is Alive

Paper I measured the Shannon-Gödel Bridge as a static constant. This paper reveals
the bridge as a dynamic structure whose breathing profile includes two opening
mechanisms (density, closure), phase transitions (first-order lock, second-order
hysteresis), and discriminatory capacity (resolution types). The bridge is not a pipe.
It is a lung. The interval between breaths is not silence. It is the breath.

### 6.2 The Evolutionary Arc

- **Bach**: G0 opens the bridge through τ differentiation. Under simple input, the
  bridge closes — a first-order phase transition with hysteresis.
- **Bacteria**: No G0 needed. Spatial heterogeneity keeps the bridge open across
  all 64 positions.
- **Forward**: Efficiency (phagocytosis) and meaning (resolution discrimination)
  are co-requisites. The bridge both processes more and distinguishes better.

### 6.3 Discrete Information Creates Differentiation

A principle cuts across all three experiments: **continuous information converges.
Discrete information differentiates.**

In Experiment 1, τ differentiation is observed under discrete score encoding — where
symbolic chord changes are separated by metrical beats. Continuous MIDI signals, with
their sustain overlap filling temporal gaps, suppress differentiation: all units
converge to identical τ values. Discrete information arrives with boundaries, and
boundaries are where different frame economies can develop distinct temporal structures.
The same three-unit GEME architecture that differentiates under score encoding
converges to redundancy under continuous MIDI — not because of any parameter
difference, but because continuous information does not provide the gaps that
differentiation requires.

In Experiment 2, the α cliff demonstrates the same principle at the colony scale.
Continuous communication (α = 0, pure L6 echo) collapses all τ variance to zero.
A discrete environmental anchor (α > 0, each position a distinct concentration)
maintains differentiation. The boundary between identical and distinct is the
boundary between continuous and discrete.

In Experiment 3, phagocytosis internalizes a continuous broadcast — removing it
from the shared channel — and the remaining discrete environmental signals grow
cleaner. The efficiency gain is not from adding information but from removing
continuity that masks discreteness.

Information needs boundaries. Differentiation begins in gaps. This is not a
limitation of the GEME architecture. It is a statement about information itself.

### 6.4 τ Is Not a Parameter

Paper I presented τ = 0.60 as a core constant. Under temporal input, τ reveals itself
as an internally generated variable. The dynamic coupling formula τ_i = τ₀ × (MI₀ / MI_i)
retains τ₀ as an anchor inherited from Paper I's Pareto-optimal parameter set — τ is
not eliminated but repositioned: from a global constant to a unit-level variable whose
value is determined by each unit's prediction history. This transformation mirrors
Dennett's internalization of competences.

### 6.5 G0's Bridge: Naturally Stable

G0's bridge never locks across the full τ range (0.2–3.0). Its input — aggregated
L6 from differentiated units — is inherently heterogeneous. The bridge's stability
comes from input heterogeneity, not from τ elevation. The τ = 3.0 setting inherited
from GEMENet initialization has no effect on G0's lock resistance: conf_threshold
remains stable at ~0.30 across the entire τ range. G0 does not need protection
because its input is already diverse.

### 6.6 Biological Correspondence

Jayakumar et al. (2021): spontaneous QS segregation without central coordination
(parallel to spatial τ variance). Popat et al. (2012): removing a QS node changes
collective productivity (parallel to phagocytosis). Scribner et al. (2022): nutrient
environment selects for coexisting strategies (parallel to α-ablation). These are
not validations — they indicate architectural universality.

### 6.7 Limitations and EE Hook

Computational thought experiment. Limitations: unit counts of 3 and 64; uniform
27-dimensional encoding; instantaneous communication without signal accumulation.

**6. Higher-order bridge limitation.** G0's bridge is naturally stable across the
full τ range when its input remains heterogeneous (§6.5). This paper examines a
single layer of self-referential observation (G0 monitoring three units). The
recursive structure — a bridge monitoring bridges, at arbitrary depth — remains
unexplored. Whether higher-order self-referential channels maintain the same
natural stability, and whether stability degrades with depth, are open questions
for Paper III (External Engine).

---

## Supplementary Information

**S1.** GEME core engine — identical to Paper I submission (MD5 verified).

**S2.** Input encoding and temporal structure. Score vs. MIDI comparison. Gap insertion
experiment: discrete boundaries enable τ differentiation. Connection to Bregman's
temporal proximity principle.

**S3.** τ differentiation controls and voice tracking. White noise, single tone, and
excess-unit controls. Voice count experiment (1–5 voices). τ count ≥ voice count.
Computational signature of auditory scene analysis.

**S4.** Lock verification: phase transition (step 23, first-order) and hysteresis data.

**S5.** Bacteria grid: α-sweep, cold/warm start, perturbation trajectories, position
sensitivity, neighbor coupling.

**S6.** Phagocytosis: multi-seed local cascade analysis.

**S7.** Phase portrait: static τ baseline for comparison.

**S8.** Bach rhythm → Bacteria aliveness: temporal structure from the fugue modulates
colony τ variance.

**S9.** G0 bridge: τ scan (0.2–3.0) and natural stability data.

**S10.** Cross-condition isomorphism: KS test conf_threshold distributions.

All experiments reproducible with Python 3.8+ stdlib, zero external dependencies.
Core engine `geme.py` MD5: 0025C508BDBDB386E9A5EB72081995B7 (identical to Paper I).
Key scripts: `bgm_bach_pipeline.py`, `bgm_bacteria.py`, `bgm_phagocytosis_v2.py`,
`bgm_wtc_full.py`, `bgm_midi_gap_test.py`, `bgm_voice_validation.py`,
`bgm_tau_multiseed.py`, `bgm_structural_analysis.py`, `bgm_g0_tau_scan.py`.
Figures: `fig_input_vs_tau.png` (4.1), `fig_perturbation.png` (4.2).

---

## References

- Barraud, N., et al. (2009). *J. Bacteriol.*, 191(23), 7333-7342.
- Bregman, A. S. (1990). *Auditory Scene Analysis*. MIT Press.
- Brown, G. J., & Cooke, M. (1994). Computational auditory scene analysis.
  *Computer Speech and Language*, 8(4), 297-336.
- Dennett, D. C. (2017). *From Bacteria to Bach and Back*. W. W. Norton.
- Hofstadter, D. R. (1979). *Gödel, Escher, Bach*. Basic Books.
- Jayakumar, P., et al. (2021). *bioRxiv*, 2021.03.22.436499.
- Liu, X., et al. (2023). AudioSep: Separate Anything You Describe. *arXiv:2308.05037*.
- Popat, R., et al. (2012). *Proc. R. Soc. B*, 279, 4765-4771.
- Scribner, M. R., et al. (2022). *J. Bacteriol.*, 204(2), e00444-21.
- Wang, D. L., & Brown, G. J. (2006). *Computational Auditory Scene Analysis*.
  IEEE Press / Wiley.
- Williams, H., Nicolson, A., & Green, T. (2024). Applying Marr's framework to
  auditory scene analysis. *Frontiers in Neuroscience*, 18, 1352247.
