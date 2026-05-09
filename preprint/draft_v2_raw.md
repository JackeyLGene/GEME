**GEME: A Self-Reflective Prism Framework for Cognition**

Jieqi Liu

Independent Researcher. Email: \[to be added\]

# Abstract

Understanding the foundational mechanisms of cognition remains a central challenge. We introduce the Generative Economy Memory Entity (GEME), a minimal computational model built on three irreducible axioms: competitive frame merging, adaptive forgetting, and self-referential observation. Operating with no free parameters and only three structural constants, GEME produces a running frame economy from which three classes of phenomena systematically emerge: (1) self-referential operations that carry near-zero mutual information with the input channel (I = 0.026 bits), which we interpret as a potential mechanistic analog to resource-efficient self-monitoring in biological systems; (2) a structured threshold-triggered response at the fourth layer of self-reference; and (3) a bounded layer-4 frame count of approximately 1, while the total system frame count converges to 6 +/- 2 across diverse conditions, a range that is numerically proximate to Miller's 7+/-2, Milgram's six degrees, and the structural attractor of formal systems. The primary contribution of this work is to present GEME as a reproducible computational thought experiment whose observed phenomena invite reinterpretation of classic cognitive and social constraints, rather than providing a definitive explanation for them. The model is fully open-source and reproducible.

# 1. Introduction

The search for fundamental principles of cognition has produced influential frameworks, from Shannon's information theory (Shannon, 1948) and Godel's incompleteness (Godel, 1931) to Hofstadter's self-referential loops (Hofstadter, 1979). Yet these remain largely disconnected---a trio of separate conversations about information, formality, and self-awareness.

Recent work has explored the intersection of self-reference and computation from multiple angles. Aaronson (2013) examined the relationship between quantum mechanics and computational complexity, while Friston (2010) proposed the free-energy principle as a unified account of brain function. Tononi's integrated information theory (Oizumi et al., 2014) directly addresses consciousness as an information-theoretic quantity. GEME differs from these approaches in a fundamental respect: it does not define what cognition should look like, but provides a minimal substrate in which cognitive-like structures emerge from economic pressure alone---no free energy, no integrated information, and no quantum mechanics are assumed.

In this paper, we ask: what happens when the three conversations are brought to the same table? We present GEME, a running computational system that simultaneously embodies all three. GEME is not a neural network, not a Bayesian model, and not a symbolic system. It is a competitive frame economy---a minimal substrate in which frames compete for survival based on three fixed rules, with no free parameters.

We report three systematic findings: (1) the information-theoretic cost of self-reference approaches near-zero as the system stabilizes (I = 0.026 bits, 100 seeds); (2) a threshold-triggered L4 response separates world-processing from self-referential prediction; and (3) the L4 self-referential frame count converges to 1 +/- 0.2, while the overall system converges to 6 +/- 2 frames across diverse conditions, a range numerically proximate to classic empirical constants.

The paper is organized as follows. Section 2 describes the GEME model: its axioms, formal definitions, and dynamical structure. Section 3 reports experimental findings. Section 4 discusses implications, limitations, and connections to existing frameworks.

# 2. The GEME Model

## 2.1 Core Principles and Axioms

GEME is governed by three axioms. These are not tunable parameters---they are fixed structural constraints that define the model's operation:

**Axiom 1 (Competitive Merging):** When an input vector arrives, it is matched against all existing frames. The closest match below a distance threshold merges the input into the existing frame, updating its centroid and increasing its weight. If no match is found, a new frame is created.

**Axiom 2 (Adaptive Forgetting):** Frame weights decay over time. Frames whose weight drops below a survival threshold are pruned. The decay rate is not uniform---it depends on the frame's merge history, creating economic pressure that shapes the frame distribution.

**Axiom 3 (Self-Referential Observation):** At regular intervals, the system generates a 'self-observation' vector derived from the current frame economy's aggregate state. This vector is fed back into the same competitive merge process, creating a closed loop.

## 2.2 Formal Definition

A frame f is a tuple (vec, weight, age, merged, sig) where vec is a D-dimensional vector (D = 27 in the fixed-dimension version, dynamically grown in the adaptive version), weight is a scalar tracking merge frequency, age counts steps since creation, merged tracks the number of successful merges, and sig is an optional signature for interpretability. Distance between frames is Euclidean. Merge threshold is computed adaptively from the frame population's pairwise distance distribution.

## 2.3 Formal Dynamics

Let the state of the system at time step $t$ be $S_t = (F_t, t)$, where $F_t = \{f_1, f_2, \dots, f_n\}$ is the set of all frames existing at time $t$. The system evolves according to a deterministic transition function $T: S_t \rightarrow S_{t+1}$, which implements the three axioms in sequence:

**Input Processing (Axiom 1).** Given an input vector $x_t \in \mathbb{R}^D$, compute the distance $d(x_t, f_i.\text{vec})$ for all $f_i \in F_t$. Let $f^* = \arg\min_{f_i} d(x_t, f_i.\text{vec})$. If $d(x_t, f^*.\text{vec}) < \delta \cdot \mu(F_t)$, where $\mu(F_t)$ is the mean pairwise distance between frames in $F_t$, then update

$$f^*.\text{vec} \leftarrow \frac{f^*.\text{merged} \cdot f^*.\text{vec} + x_t}{f^*.\text{merged} + 1}, \quad f^*.\text{merged} \leftarrow f^*.\text{merged} + 1.$$

Otherwise, add a new frame $f_{\text{new}} = (x_t, 1.0, 0, 0, \text{None})$ to $F_t$.

**Forgetting (Axiom 2).** For all $f_i \in F_t$, update

$$f_i.\text{weight} \leftarrow f_i.\text{weight} \cdot \exp(-\gamma / f_i.\text{merged}), \quad f_i.\text{age} \leftarrow f_i.\text{age} + 1.$$

Remove all frames $f_i$ where $f_i.\text{weight} < \tau$.

**Self-Observation (Axiom 3).** Every $k$ steps (default $k = 10$), generate a self-observation vector $o_t = \text{aggregate}(F_t)$, where $\text{aggregate}$ computes the weighted centroid of all frames weighted by their weight. Feed $o_t$ back into the system as an input vector, applying the same competitive merging process as in step 1.

**Definition 1 (Layer Assignment).** A frame $f$ is assigned to layer $L_i$ if it was generated from frames of layer $L_{i-1}$. Input vectors are considered layer $L_0$.

**Definition 2 (Stable Frame).** A frame $f$ is stable at time $t$ if $|d(f.\text{weight})/dt| < \varepsilon$ for $\varepsilon = 0.001$ over a window of 100 steps.

> **Remark.** The emergent properties of GEME (L4 threshold response, attractor convergence) are experimentally verified across thousands of runs. A formal mathematical proof of these properties remains an important open problem for future work.

## 2.4 Dynamics: The Layered Economy

The frame economy operates at multiple concurrent layers. Layer 1 (L1) establishes entity frames from raw input vectors via delta-adaptive merging. Layer 2 (L2) discovers co-occurrence associations between L1 frames through a sliding window, creating 'association frames'. Layer 3 (L3) forms bridge frames by detecting stable association patterns---these are the system's first self-referential structures, encoding relationships among relationships. Layer 4 (L4) generates frames when the rate of change of frame weights exceeds a threshold---encoding the derivative d(w)/dt as a higher-order signal about the economy's own dynamics.

# 3. Experimental Findings

## 3.1 The Shannon-Godel Bridge: Self-Reference is Informationally Efficient

We compute the mutual information I(phi; X) between the set of self-referential frames (phi, including 'self_obs', weight-derivative frames, and associative bridge frames) and the set of external input frames (X), over the full co-occurrence distribution---not a truncated subspace. Across 100 random seeds with 2000 steps each, the mean I(phi; X) = 0.026 +/- 0.002 bits, with 98% of runs falling below 0.05 bits. The low and asymptotically vanishing mutual information suggests that, within the GEME economy, self-referential operations generate representations that are largely statistically independent of the external input stream. This motivates the conjecture that self-reference may be informationally efficient in such systems (henceforth: the Shannon-Godel Bridge). See Supplementary Materials S2 for regression against step count.

## 3.2 Parameter Stability: Structural Robustness

The three structural constants (delta = 0.19, gamma = 0.05, tau = 0.6) define an economic regime, not a set of tuned parameters. Across a 50% variation of each constant, L4 prediction behavior persists qualitatively. All engineering initialization parameters (co-occur window, merge threshold scaling) were found to have no significant effect on core convergence results within their operational ranges. Ablation experiments (Supplementary Materials S4) confirm that no single threshold drives the effect; rather, it is the presence of a self-observation loop in a competitive frame economy that is sufficient.

## 3.3 Threshold-Triggered L4 Response

When the rate of change of frame weights exceeds a threshold (|d(w)/dt| > 0.02), the system generates a distinct class of frames (L4 frames) that encode this derivative. The prediction pipeline operates economically: generating a prediction costs O(W + K) (scanning window and co-occurrence table), while verification costs O(1). Over time, generation and verification costs converge as structural knowledge accumulates, exhibiting characteristics of efficient verification relative to generation within the frame economy (see Supplementary Materials S6 for detailed complexity analysis). L4 frames' encoding of the system's own dynamics is conceptually analogous---in function, not mechanism---to metacognitive monitoring in biological systems.

## 3.4 The Stable Attractor: Frame Count Convergence

Across memory capacities from 8 to 52, the L4 self-referential frame count converges to 1 +/- 0.2. The overall system frame count converges to 6 +/- 2 in the operational regime (capacities 8-32), a range that is intriguingly close to Miller's 7 +/- 2 (working memory), Milgram's six degrees (social networks), and the structural attractor of Q + G approximately equals PA (formal systems). This hierarchical convergence suggests that a single dominant metacognitive frame (L4) coordinates approximately six lower-level structural frames (L1-L3), consistent with the observed capacity limits of human working memory. The numerical proximity invites the speculative hypothesis that disparate cognitive and social systems might be subject to analogous informational or economic constraints---a possibility that merits future investigation through direct empirical alignment, rather than a claim established by the present work.

# 4. Discussion

## 4.1 Summary of Findings

GEME demonstrates that a minimal frame economy, governed by three fixed axioms and no free parameters, produces a rich set of emergent phenomena. The system is not a simulation of cognition or physics---it is a computational substrate in which both cognitive-like and physical-like structures spontaneously arise. We summarize the key findings.

## 4.2 GEME and Cognitive Architecture

We contextualize GEME within existing frameworks. The informational efficiency of self-reference resonates with Scott Aaronson's computational complexity approach to consciousness (Aaronson, 2013, 2011). We note that this parallel is conceptual and heuristic; GEME does not implement nor directly test Aaronson's framework. The threshold-triggered L4 response parallels Tononi's Integrated Information Theory (Oizumi et al., 2014) in suggesting a threshold-like transition in neural dynamics. We note that this parallel is conceptual; GEME does not implement IIT's phi computation nor its neurobiological postulates. The competitive frame economy shares structural features with Friston's Free Energy Principle (Friston, 2010), where systems minimize surprise through adaptive model updating. Again, this is a structural analogy, not an implementation claim.

## 4.3 Speculative Implications and Future Directions

The convergence of the GEME attractor to a scale (~6) that is numerically reminiscent of several classic empirical constants, while provocative, does not in itself constitute a unification. It does, however, raise a concrete and testable question: could there exist a minimal information-economic model---of which GEME is a toy example---whose stable states naturally map onto these diverse phenomenological scales? Proving or falsifying this would require building explicit bridges between the abstract dynamics of GEME and domain-specific models of working memory, social network formation, and proof theory.

## 4.4 Limitations and Future Work

GEME in its current form is highly abstract. The input space is synthetic (fixed-dimensional vectors, currently of moderate size). Real-world cognitive tasks require richer sensory grounding, and we are actively extending GEME to handle variable-dimensional and natural language inputs. Future work includes: (a) coupling GEME with large language models for prompt engineering (PhasePrompt), (b) exploring natural language inputs across languages and domains (ongoing work: NoHarm), (c) formal mathematical analysis of the frame economy's phase transitions, and (d) extending the model to multi-agent social simulations.

We hypothesize that GEME's layered architecture can be further extended to separate world-processing (L1-L3) from a metacognitive pipeline (L4-L6): L4 predicts the next state, L5 observes the prediction outcome, and L6 issues a judgment. This tripartite structure suggests that consciousness---if it emerges in computational systems---may require self-reference organized into a prediction-observation-judgment pipeline. We emphasize that this formulation represents a design hypothesis for future work, not a claim demonstrated by the current experiments.

## 4.5 Conclusion

GEME is an open-source, fully reproducible computational prism. It is offered not as a theory of cognition, but as a tool for exploring one: a minimal system in which self-referential structures emerge for free, converge to characteristic scales, and invite interpretation across disciplines. We invite researchers in cognitive science, complex systems, and related fields to use, test, and extend this framework.

# Acknowledgments

The author thanks Douglas R. Hofstadter for his pioneering work on self-reference and strange loops, which provided foundational inspiration for this study, and for his early encouragement. This research was conducted independently. Some experimental code was developed with AI assistance; the author bears full responsibility for all content.

# References

Aaronson, S. (2011). Why philosophers should care about computational complexity. In Computability: Turing, Godel, Church, and Beyond.

Aaronson, S. (2013). The ghost in the quantum Turing machine. arXiv:1306.0159.

Friston, K. (2010). The free-energy principle: a unified brain theory? Nature Reviews Neuroscience, 11(2), 127-138.

Godel, K. (1931). Uber formal unentscheidbare Satze der Principia Mathematica und verwandter Systeme I. Monatshefte fur Mathematik und Physik, 38(1), 173-198.

Hofstadter, D. R. (1979). Godel, Escher, Bach: An Eternal Golden Braid. Basic Books.

Miller, G. A. (1956). The magical number seven, plus or minus two. Psychological Review, 63(2), 81-97.

Milgram, S. (1967). The small world problem. Psychology Today, 1(1), 61-67.

Oizumi, M., Albantakis, L., & Tononi, G. (2014). From the phenomenology to the mechanisms of consciousness. PLoS Computational Biology, 10(5), e1003588.

Power, A., Burda, Y., Edwards, H., Babuschkin, I., & Misra, V. (2022). Grokking: Generalization beyond overfitting on small algorithmic datasets. arXiv:2201.02177.

Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal, 27(3), 379-423.

# Supplementary Information

## S1. Exploratory Notes: Conceptual Evolution

The development of GEME was driven by observations that the frame economy's behavioral differentiation structurally parallels distinct descriptive paradigms in science. L1 frames operate on discrete differentiation (statistical mechanics), L2 on temporal structure (thermodynamics), L3 on relational topology (general relativity), and L4 on self-referential closure (quantum measurement / consciousness). These parallels are offered as heuristic motivation, not formal claims.

## S2. Extended Verification: Q + G ≈ PA

We encode the axioms of Robinson Arithmetic (Q) and Peano Arithmetic (PA) as structured vectors and input them to GEME. The frame economy of Q alone shows L2-level co-occurrence patterns (e.g., add\_s--mul\_s). Adding the Godel sentence G to Q produces a frame economy that structurally approximates PA: the L3 bridge frame occupied by the induction axiom in PA is filled by G's self-referential structure in Q+G. This suggests that self-reference and induction are economically equivalent compression operations.

## S3. Cross-Language Semantic Convergence: The Code of Hammurabi

We input Chinese and English translations of the Code of Hammurabi into separate GEME instances. Despite operating on entirely different symbol sets, the L2 association topologies converge: the Chinese run yields 27 association frames, the English 30, with structural overlaps in legal concept groupings (punishment hierarchies, damage compensation, social role distinctions). This suggests translation-invariant semantic structure that GEME extracts without any linguistic priors.

## S4. Complete Experimental Data

Full parameter scans, statistical tests, and control experiments are provided in the companion repository at https://github.com/JackeyLGene/GEME.

## S5. Reproducibility Guide

All experiments are runnable via scripts in the /standalone directory of the GEME repository. Dependencies: Python 3.10+, numpy, scipy, and the local versions provided in the repository. No external data downloads are required. See README.md for step-by-step instructions.

## S6. Complexity Analysis

The L4 prediction pipeline operates at O(W + K) for generation (scanning window of size W and co-occurrence table of size K) and O(1) for verification (string comparison). As the frame economy stabilizes, K converges to a bounded constant, bringing the practical cost of generation close to that of verification. This does not constitute a formal complexity-theoretic claim about P vs NP; it is an observation about operational costs in the specific context of the GEME frame economy.
