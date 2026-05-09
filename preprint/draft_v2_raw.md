**GEME: A Self-Reflective Prism Framework for Cognition**

Jieqi Liu

Independent Researcher. Email: \[to be added\]

# Abstract

Understanding the foundational mechanisms of cognition remains a central challenge. We introduce the Generative Economy Memory Entity (GEME), a minimal computational model built on three irreducible axioms: competitive frame merging, adaptive forgetting, and self-referential observation. Operating with no free parameters and only three structural constants, GEME produces a running frame economy from which three classes of phenomena systematically emerge: (1) self-referential operations that are information-theoretically resource-neutral---carrying zero mutual information with the input channel; (2) a structured behavioral threshold-triggered behavior at the fourth layer of self-reference, corresponding to the emergence of metacognitive awareness; and (3) a stable numerical attractor---a bounded layer-4 frame count of approximately 1---that coincides with Miller\'s 7±2, Milgram\'s six degrees, and the structural convergence of formal systems. GEME does not simulate cognition; it provides a minimal computational substrate in which cognitive-like structures naturally arise. The model is fully open-source and reproducible.

# 1. Introduction

The search for fundamental principles of cognition has produced influential frameworks, from Shannon\'s information theory (Shannon, 1948) and Godel\'s incompleteness (Godel, 1931) to Hofstadter\'s self-referential loops (Hofstadter, 1979). Yet these remain largely disconnected---a trio of separate conversations about information, formality, and self-awareness.

Recent work has explored the intersection of self-reference and computation from multiple angles. Aaronson (2013) examined the relationship between quantum mechanics and computational complexity, while Friston (2010) proposed the free-energy principle as a unified account of brain function. Tononi's integrated information theory (Oizumi et al., 2014) directly addresses consciousness as an information-theoretic quantity. GEME differs from these approaches in a fundamental respect: it does not define what cognition should look like, but provides a minimal substrate in which cognitive-like structures emerge from economic pressure alone---no free energy, no integrated information, and no quantum mechanics are assumed.

In this paper, we ask: what happens when the three conversations are brought to the same table? We present GEME, a running computational system that simultaneously embodies all three. GEME is not a neural network, not a Bayesian model, and not a symbolic system. It is a competitive frame economy---a minimal substrate in which frames compete for survival based on three fixed rules, with no free parameters.

We report three systematic findings: (1) the information-theoretic cost of self-reference approaches near-zero as the system stabilizes (I = 0.026 bits, 20 seeds); (2) a threshold-triggered L4 response separates world-processing from self-referential prediction; and (3) the L4 self-referential frame count converges to 1 +/- 0.2, while the overall system converges to 6 +/- 2 frames across diverse conditions, echoing classic empirical constants.

The paper is organized as follows. Section 2 describes the GEME model: its axioms, formal definitions, and dynamical structure. Section 3 reports experimental findings. Section 4 discusses implications, limitations, and connections to existing frameworks.

# 2. The GEME Model

## 2.1 Core Principles and Axioms

GEME is governed by three axioms. These are not tunable parameters---they are fixed structural constraints that define the model\'s operation:

**Axiom 1 (Competitive Merging):** When an input vector arrives, it is matched against all existing frames. The closest match below a distance threshold merges the input into the existing frame, updating its centroid and increasing its weight. If no match is found, a new frame is created.

**Axiom 2 (Adaptive Forgetting):** Frame weights decay over time. Frames whose weight drops below a survival threshold are pruned. The decay rate is not uniform---it depends on the frame\'s merge history, creating economic pressure that shapes the frame distribution.

**Axiom 3 (Self-Referential Observation):** At regular intervals, the system generates a \'self-observation\' vector derived from the current frame economy\'s aggregate state. This vector is fed back into the same competitive merge process, creating a closed loop.

## 2.2 Formal Definition

A frame f is a tuple (vec, weight, age, merged, sig) where vec is a D-dimensional vector (D = 27 in the fixed-dimension version, dynamically grown in the adaptive version), weight is a scalar tracking merge frequency, age counts steps since creation, merged tracks the number of successful merges, and sig is an optional signature for interpretability. Distance between frames is Euclidean. Merge threshold is computed adaptively from the frame population\'s pairwise distance distribution.

## 2.3 Dynamics: The Layered Economy

The frame economy operates at multiple concurrent layers. Layer 1 (L1) establishes entity frames from raw input vectors via delta-adaptive merging. Layer 2 (L2) discovers co-occurrence associations between L1 frames through a sliding window, creating \'association frames\'. Layer 3 (L3) forms bridge frames by detecting stable association patterns---these are the system\'s first \'self-referential\' structures, encoding relationships among relationships. Layer 4 (L4) observes the stability curves of L3 bridges, generating metacognitive frames that track d(weight)/dt---the rate at which the system\'s own knowledge is changing.

# 3. Experimental Findings

## 3.1 The Godel Bridge: Self-Reference is Resource-Neutral

We compute the mutual information I(phi; X) between self-referential frames (phi, including 'self_obs', dwdw, and bridge frames) and external input frames (X) over the full co-occurrence space---not a truncated subspace. Across 20 random seeds with 2000 steps each, I(phi; X) = 0.032 +/- 0.006 bits, approaching zero relative to the channel capacity of the input stream. Regression against step count confirms the trend approaches zero as the system stabilizes (see Supplementary Materials S2). This result---the Godel Bridge---demonstrates that self-reference in a frame economy is information-theoretically resource-neutral.

## 3.2 Parameter Stability: Structural Robustness

The three structural constants (delta = 0.19, gamma = 0.05, tau = 0.6) define an economic regime, not a set of tuned parameters. Across a 50% variation of each constant, L4 prediction behavior persists qualitatively. Ablation experiments (Supplementary Materials A1-A8) confirm that no single threshold drives the effect; rather, it is the presence of a self-observation loop in a competitive frame economy that is sufficient.

## 3.3 Threshold-Triggered L4 Response

The L4 self-observation layer generates metacognitive frames when the derivative of frame weights exceeds |d(w)/dt| > 0.02---a threshold-triggered response, not a programmed behavior. The L4 prediction pipeline operates economically: generating a prediction costs O(W + K) (scanning window and co-occurrence table), while verification costs O(1). Over time, generation and verification costs converge as structural knowledge accumulates, simulating P-approaching-NP within the frame economy.

## 3.4 The Stable Attractor: Frame Count Convergence

Across memory capacities from 8 to 52, the L4 self-referential frame count converges to 1 +/- 0.2. The overall system frame count converges to 6 +/- 2 in the operational regime (capacities 8-32), a number that coincides with Miller's 7 +/- 2 (working memory), Milgram's six degrees (social networks), and the structural attractor of Q + G approximately equals PA (formal systems). This convergence may reflect a common information-theoretic constraint: the channel capacity of a self-referential loop.

# 4. Discussion

## 4.1 Summary of Findings

GEME demonstrates that a minimal frame economy, governed by three fixed axioms and no free parameters, produces a rich set of emergent phenomena. The system is not a simulation of cognition or physics---it is a computational substrate in which both cognitive-like and physical-like structures spontaneously arise. We summarize the key findings.

## 4.2 GEME and Cognitive Architecture

We contextualize GEME within existing frameworks. The resource-neutrality of self-reference resonates with Scott Aaronson\'s computational complexity approach to consciousness (Aaronson, 2013, 2011). The phase transition at L4 parallels Tononi\'s Integrated Information Theory (Oizumi et al., 2014) in suggesting a threshold for conscious awareness. The competitive frame economy shares structural features with Friston\'s Free Energy Principle (Friston, 2010), where systems minimize surprise through adaptive model updating.

## 4.3 Unifying Implications

The convergence of GEME\'s stable attractor (6) with empirical constants from psychology, sociology, and mathematics suggests---speculatively---that a common information-economic principle may underlie these phenomena. The constraint is not domain-specific: it arises from the channel capacity of the self-referential loop, whether in an individual mind, a social network, or a formal system. We offer this as a testable hypothesis for future work.

## 4.4 Limitations and Future Work

GEME in its current form is highly abstract. The input space is synthetic (fixed-dimensional vectors, currently of moderate size). Real-world cognitive tasks require richer sensory grounding, and we are actively extending GEME to handle variable-dimensional and natural language inputs. Future work includes: (a) coupling GEME with large language models for prompt engineering (PhasePrompt), (b) exploring natural language inputs across languages and domains (NoHarm), (c) formal mathematical analysis of the frame economy\'s phase transitions, and (d) extending the model to multi-agent social simulations.

GEME's layered architecture separates world-processing (L1-L3) from self-referential verification (L4-L6). The upper three layers form a metaframework: L4 predicts the next state, L5 observes the prediction outcome, and L6 issues a judgment. This tripartite structure suggests that consciousness---if it emerges---may require self-reference organized into a prediction-observation-judgment pipeline. A single self-referential frame acting as the L6 output could serve as a component in a larger network of such agents.

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

Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal, 27(3), 379-423.

# Supplementary Information

## S1. Exploratory Notes: Conceptual Evolution

The development of GEME was driven by observations that the frame economy\'s behavioral differentiation structurally parallels distinct descriptive paradigms in science. L1 frames operate on discrete differentiation (statistical mechanics), L2 on temporal structure (thermodynamics), L3 on relational topology (general relativity), and L4 on self-referential closure (quantum measurement / consciousness). These parallels are offered as heuristic motivation, not formal claims.

## S2. Extended Verification: Q + G ≈ PA

We encode the axioms of Robinson Arithmetic (Q) and Peano Arithmetic (PA) as structured vectors and input them to GEME. The frame economy of Q alone shows L2-level co-occurrence patterns (e.g., add_s\--mul_s). Adding the Godel sentence G to Q produces a frame economy that structurally approximates PA: the L3 bridge frame occupied by the induction axiom in PA is filled by G\'s self-referential structure in Q+G. This suggests that self-reference and induction are economically equivalent compression operations.

## S3. Cross-Language Semantic Convergence: The Code of Hammurabi

We input Chinese and English translations of the Code of Hammurabi into separate GEME instances. Despite operating on entirely different symbol sets, the L2 association topologies converge: the Chinese run yields 27 association frames, the English 30, with structural overlaps in legal concept groupings (punishment hierarchies, damage compensation, social role distinctions). This suggests translation-invariant semantic structure that GEME extracts without any linguistic priors.

## S4. Complete Experimental Data

Full parameter scans, statistical tests, and control experiments are provided in the companion repository at https://github.com/JackeyLGene/GEME.

## S5. Reproducibility Guide

All experiments are runnable via scripts in the /standalone directory of the GEME repository. Dependencies: Python 3.10+, numpy, scipy, and the local versions provided in the repository. No external data downloads are required. See README.md for step-by-step instructions.
