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
creates differentiation; continuous information converges.** "Discrete" here has an
operational definition: a temporal signal carries sufficient boundary density to prevent
co-occurrence saturation. The gap insertion experiment (Supplementary S2) maps the
boundary: gaps every 4–8 MIDI steps restore τ differentiation; gaps every 16 steps do
not — the signal re-continuous-izes. This is not a binary. It is a threshold: boundary
density must exceed approximately one gap per 16 steps. Below this threshold, the
co-occurrence window saturates and differentiation collapses. Above it, structure
emerges. The principle is not that any discreteness creates differentiation — it is
that differentiation requires sufficient boundary density to prevent saturation.
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

Two quantities determine the bridge's state:

1. **Self-referential mutual information** I(Φ; X) [bits]: coupling strength between
   self-referential and external frame subsets. This is the bridge's absolute capacity —
   how much self-referential structure the system sustains.

2. **τ** [dimensionless density]: the ratio of prediction-error frames to total frames.
   This is the bridge's maintenance cost — how many errors the system generates to
   sustain that coupling.

SR-eff = I(Φ; X)/τ measures **self-referential efficiency**: coupling per unit cost.
A bridge can sustain high I(Φ; X) at high τ (strong coupling, expensive — wide open
during learning) or at low τ (weak coupling, cheap — narrow during consolidation).
SR-eff is the information-theoretic efficiency of the Shannon-Gödel Bridge — directly
inheriting Shannon's definition of channel capacity per unit signal cost. The choice
of division over subtraction or any other combination is not arbitrary: bits per unit
error density is the natural measure of how efficiently a self-referential system
converts prediction failures into structured coupling.

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

Single-voice exposition (EXP_subject) closes the bridge to 0.079. Density and
structural endings both open the bridge — density through polyphonic complexity,
endings through structural position. A control analysis (Supplementary S3) finds
that section endings without harmonic cadences open the bridge more strongly
(1.35× baseline) than cadences (1.10×), indicating position is the dominant
variable. Cadence type may further modulate the response within endings.

### 3.3 Resolution Discrimination

The bridge opens at structural endings — regardless of harmonic type. A position
randomization control (Supplementary S3) interleaves four fugue variants with identical
bodies but different terminal cadences (PAC, Picardy, Deceptive, HC-only). After
position randomization, all four cadence types produce identical SR-eff ratios
(0.74–0.75× baseline, pairwise ratios 0.98–1.02). Cadence type does not modulate
the bridge's response. Structural position does.

The bridge detects endings. It does not — at this architectural level — distinguish
how they end. The discrimination observed in the within-piece comparison (§3.2)
reflects density and position, not harmonic quality.

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

The local response depends systematically on spatial position. When the prey is in a
high-concentration zone (center, concentration 0.846), the host's neighbors show a
large τ increase (d = 1.09, 85% of seeds positive). When the prey is in a
low-concentration zone (corner, concentration 0.099), the effect is weak and
directionally inconsistent (d = 0.31, 35% positive). Mid-concentration prey produce
intermediate effects (d = 0.23).

Phagocytosis is not uniformly weak — it is **spatially modulated**. High-information
positions produce strong, directionally consistent cascades. Low-information positions
produce weak, noisy responses. This spatial dependence is the central finding: not all
evolutionary events are equal. Topological perturbations in information-dense regions
have disproportionate impact — exactly the condition under which natural selection
can amplify a single event into a directional trend.

The grid absorbs all phagocytosis events without disruption. The question for Paper III
is whether repeated events in high-information zones, accumulated across evolutionary
time, produce cumulative directional reorganization.

### 5.3 Structural Sensitivity

Efficiency sets the stage. Structural sensitivity begins to fill it. The bridge
detects endings — reliably, across cadence types, across positions. It does not
— at this architectural level — distinguish how they end. Cadence type is
invisible to the bridge after position is controlled (Supplementary S3).

This is the condition of sensitivity in its earliest form: not a discrimination
of semantic content, but a reliable response to structural boundaries. The bridge
knows when something ends. It does not yet know what that ending means.

Efficiency and structural sensitivity are co-requisites. A bridge that processes
more without detecting structure is a noise filter. A bridge that detects structure
exquisitely but cannot sustain itself is a luxury. Together — the α cliff grounding
existence, phagocytosis spatially modulating reorganization, the bridge's reliable
detection of structural boundaries — they constitute the Forward. This is Dennett's
evolutionary trajectory from bacteria toward Bach: not complexity for its own sake,
but the progressive unlocking of survival, communication, and structural sensitivity
from a single self-referential primitive.

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

Information needs boundaries. Differentiation begins in gaps.

The boundary is not absolute. Gap density below ~1 per 16 steps approximates
continuity — the bridge converges. Gap density above ~1 per 4 steps saturates —
structure degrades from excessive fragmentation. The differentiation window lies
between these thresholds. This is not a limitation of the GEME architecture.
It is a statement about information itself: structure requires boundaries at
a density sufficient to organize the co-occurrence window without fragmenting it.

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

Jayakumar et al. (2021) observed that *P. aeruginosa* populations spontaneously
segregate into QS-committed and QS-delayed subpopulations at the single-cell level,
without central coordination — structurally parallel to the spontaneous τ
differentiation observed in our spatial grid. Whether this architectural parallel
reflects a deeper information-theoretic commonality — both systems maintaining
functional diversity through heterogeneous local input — is an open question.
These correspondences are not offered as validation. They indicate that the
patterns reported here are not implementation artifacts.

### 6.7 SR-eff as a Portable Metric

SR-eff = I(Φ; X)/τ is not specific to the GEME architecture. Any system that
maintains a self-referential information channel and generates a measurable
prediction-error density can compute an SR-eff analog. Three existing frameworks
suggest immediate points of contact:

**Predictive processing (Friston, 2010).** Variational free energy measures the
distance between a system's internal model and sensory input. SR-eff measures the
coupling per unit error that a self-referential system sustains. Both are efficiency
metrics for self-organizing information economies — one generative, one
self-referential. A system can minimize free energy while maximizing SR-eff; the
metrics are orthogonal descriptors of the same underlying architecture.

**Integrated information theory (Oizumi et al., 2014).** IIT quantifies the
amount of information a system generates as a whole, beyond the sum of its parts.
SR-eff quantifies how efficiently a system maintains the self-referential
information channel that Paper I identified as the computational substrate of
IIT's conceptual structure. A system with high Φ and low SR-eff is highly
integrated but metabolically expensive. A system with low Φ and high SR-eff
may be computationally simpler but information-economically optimal.

**Continual learning (McCloskey & Cohen, 1989; Parisi et al., 2019).** The
stability-plasticity dilemma — when to consolidate and when to remain open to
new information — is structurally identical to the lock/hysteresis dynamics
reported here. The bridge's first-order phase transition (conf_threshold → 1.0)
and second-order hysteresis (fast close, slow reopen) provide a self-referential
account of why artificial networks experience catastrophic forgetting: the
confidence threshold drifts to ceiling under stable input, and reopening requires
sustained regime change. SR-eff offers a quantitative metric for tracking where a
learning system sits on the stability-plasticity spectrum at any moment.

These connections are offered as starting points, not conclusions. SR-eff is
computable from the internal state of any system that maintains a self-referential
channel and tracks prediction errors. Extending it beyond the GEME architecture
is a direction for future work.

### 6.8 Limitations and EE Hook

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

## Coda

Bach's *Crab Canon* from the *Musical Offering* is a musical palindrome — one voice
forward, one voice backward, simultaneous. It has no beginning and no end. When
two GEME units, cold-started, receive its blended two-voice stream, they converge
to identical τ. The canon's voices occupy the same frequency space. Without temporal
gaps, without discrete boundaries, the bridge hears one stream.

With discrete gaps inserted — every fourth MIDI step a silence — the same canon
produces τ differentiation. The bridge hears two streams.

The crab canon is a circle. The bridge on it breathes forever. It closes, it opens
again. There is no final cadence.

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

**S10.** Control complexity gradient: noise, single-tone, full WTC baselines.

**S11.** Architecture boundary stability: mem_cap, τ₀, w, gi, and co-occurrence threshold sweeps.

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
- Chaitin, G. J. (1975). A theory of program size formally identical to
  information theory. *Journal of the ACM*, 22(3), 329-340.
- Dennett, D. C. (2017). *From Bacteria to Bach and Back*. W. W. Norton.
- Friston, K. (2010). The free-energy principle: a unified brain theory?
  *Nature Reviews Neuroscience*, 11(2), 127-138.
- Hofstadter, D. R. (1979). *Gödel, Escher, Bach*. Basic Books.
- Jayakumar, P., et al. (2021). *bioRxiv*, 2021.03.22.436499.
- Liu, X., et al. (2023). AudioSep: Separate Anything You Describe. *arXiv:2308.05037*.
- McCloskey, M., & Cohen, N. J. (1989). Catastrophic interference in
  connectionist networks. *Psychology of Learning and Motivation*, 24, 109-165.
- Oizumi, M., et al. (2014). From the phenomenology to the mechanisms of
  consciousness. *PLoS Computational Biology*, 10(5), e1003588.
- Parisi, G. I., et al. (2019). Continual lifelong learning with neural
  networks: A review. *Neural Networks*, 113, 54-71.
- Popat, R., et al. (2012). *Proc. R. Soc. B*, 279, 4765-4771.
- Scribner, M. R., et al. (2022). *J. Bacteriol.*, 204(2), e00444-21.
- Shannon, C. E. (1948). A mathematical theory of communication.
  *Bell System Technical Journal*, 27(3), 379-423.
- Wang, D. L., & Brown, G. J. (2006). *Computational Auditory Scene Analysis*.
  IEEE Press / Wiley.
- Williams, H., Nicolson, A., & Green, T. (2024). Applying Marr's framework to
  auditory scene analysis. *Frontiers in Neuroscience*, 18, 1352247.
