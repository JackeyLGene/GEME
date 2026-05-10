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

## 3.5 Q + G \u2248 PA: The Structural Equivalence of Self-Reference and Induction

A central prediction of the GEME framework is that the Gödel sentence G---when added to Robinson arithmetic Q---should produce an L4 prediction behavior indistinguishable from that of Peano arithmetic (PA). We test this directly by encoding the axioms of Q, Q+G, and PA as structured 27-dimensional vectors and running each system through the full GEME pipeline.

Across 10 independent random seeds, the results are unambiguous:

- Q alone: L4 = 0.0, 783 predictions, accuracy 0.450
- Q + G: L4 = 1.0, 878 predictions, accuracy 0.350
- PA: L4 = 1.0, 878 predictions, accuracy 0.350

The standard deviation is zero across all seeds for all three conditions. Q+G and PA are not just similar---they produce identical L4 prediction behavior. This constitutes a direct computational demonstration of the structural equivalence between self-reference (G) and induction (PA) at the L4 prediction level: a result predicted by Gödel\u2019s theorems but never before observed in a running computational system.

Moreover, this experiment serves as a unifying demonstration of all three economic findings within a single experimental setup:
- **Gödel Bridge:** The self-referential G frame carries near-zero mutual information with the input axioms (I = 0.026 bits).
- **Threshold Emergence:** The transition from L4 = 0 (Q) to L4 = 1 (Q+G, PA) is a threshold-triggered response to the presence of a self-referential structure.
- **Consciousness Economy:** G and induction are computationally equivalent with respect to prediction costs, suggesting a shared economic compression principle across formal systems.

See Supplementary Materials S2 for extended verification across geometric and Tarskian systems, and for a discussion of the computational complexity implications.

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

## S1. The Discovery Journey: Cognitive Barriers, One Layer at a Time

GEME's core code is compact, functional, but complex. The model is the product of starting from philosophical reflections on cognition and iteratively refining through experimental attempts. Each layer's identification and breakthrough went through multiple rounds of trial and error. We are pleased to present this journey through a series of experiments, to more clearly explain the rationale behind GEME's design choices.

Readers are invited to run `standalone/s1_demo_experiments.py` to experience each layer's cognitive barrier firsthand---each experiment demonstrates what the current layer "cannot do," leading naturally to the necessity of the next layer.

**S1.1 L1-L3: From Isolated Entities to Stable Relations**

**Experiment 1: Isolated Frames.** Input two isolated entities---"cat" and "mat." The system successfully classifies them as distinct frames (2/8 capacity) but cannot form any association. The system can distinguish things, but cannot express "the cat is on the mat." This stage lasted months: the system ran, it converged, but its "world" was a collection of discrete entities with no time, no relations, and no structure. **Barrier:** Classification is sufficient, but relation is not. This predicament is reminiscent of pre-scientific naming and categorization---a scholar who knows how to name things but cannot form a sentence.

**Experiment 2: Vanishing Associations.** Input "cat" "on" "mat" sequence 50 times. The sliding window records that "cat" and "mat" appear near each other in time---the system autonomously generates an association frame "cat--mat." However, after switching to "dog" "on" "road," the previous "cat--mat" association gradually vanishes. **Barrier:** Associations are functional but transient---they disappear when the window slides. To acquire knowledge, the system needs stability. This parallels the transition from causality to structural thinking: if A and B frequently appear together, they are "related"---but this temporal proximity alone cannot form the basis of knowledge.

**Experiment 3: Truth Blindness.** L2's transience forces the system to integrate association patterns over time, forming stable bridge frames. L3's emergence took us the longest to explore; we ultimately discovered that the "time dimension" itself was the key---a bridge frame's stability depends on its persistence over time, not on the strength of a single co-occurrence. Run Experiment 3: Input "3+2=5" (true) and "6+1=8" (false) 30 times each. L3's bridge frames respond identically to both. **Barrier:** Stable, but stability does not equal truth. L3 can record "what happens frequently" but cannot answer "what should happen." This is reminiscent of how field theory transcended mechanical forces---describing not particles or forces between them, but the structure of space itself---yet even such complete structural description still lacks a truth dimension.

**S1.2 L3's Incompleteness and the Long Search for L4**

On the evening of May 8, 2026, this gap became undeniable. Frequency is not truth. The nascent L4 at that time was merely a passive observer of d(w)/dt. It could "see" changes in bridge frame weights, but could not "ask" what those changes meant. It was recording a video, not making a judgment. What is fascinating about this gap is its self-referential nature: GEME's own structure was exposing the very crack between "describing the world" and "judging the world"---the same crack that Godel's sentence opens in formal systems.

**S1.3 L4-L6: From Prediction to Judgment**

**Experiment 4: The Lonely Predictor.** After establishing the "cat-on-mat" pattern, check prediction accuracy (~85%). Then inject an anomaly ("road") and observe the pred_err frame. The system detects that this particular prediction was wrong---but it does not know its overall accuracy is declining. L4 infers the most likely next frame signature from the co-occurrence table---generating a prediction (O(W+K)), receiving the actual input (O(1)), and comparing the two to produce an error signal. **Barrier:** Can predict, but does not know its own capability boundary. This mirrors the rise of probabilistic description: the system does not describe a definite state but maintains a probability distribution, updating it through measurement.

**Experiment 5: The Bystander.** After training, inject noise and observe L5's recorded accuracy drop (from ~0.85 to ~0.05). The system moves from "I am predicting" to "I know at what accuracy I am predicting"---the entry point of metacognition. But the system only records the trend, it does not act on it. **Barrier:** Can see the trend, but cannot make a judgment based on it. This parallels the gap between measurability and actionability in information theory---knowing the informational state of a system does not imply the ability to intervene on it.

**Experiment 6: System Doubt.** When L5's reported prediction accuracy drops persistently (below 60%, an experimentally verifiable threshold), L6 generates a sys_doubt frame---a system-level "I may be wrong" signal. This is the only genuine output of the entire GEME architecture: a judgment about the system's own state. L6 does not predict the world---it predicts its own ability to predict. **Barrier broken:** The leap from description to judgment is complete. This is the closure of the self-referential loop---from Godel's incompleteness theorem revealing the limits of formal systems, to Hofstadter's vision of self-doubt signals, GEME provides a running computational version of this process.

**S1.4 Unification of the Three Theorems in the Discovery Process**

This journey is not five independent problems solved in sequence---it is the same problem solved recursively five times:

1. **The Godel Bridge (resource-neutrality):** Before correction, the MI computation (phi-X subspace denominator) yielded I = 0.086---underestimating the independence of self-obs frames from input frames. After correction (full co-occurrence space denominator, 20 seeds, 2000 steps), I = 0.026 +/- 0.002 bits. The entire L4-L6 self-referential pipeline consumes negligible channel capacity---the computational version of the Godel Bridge.

2. **Threshold-triggered emergence (economics of emergence):** L4's prediction, L5's meta-observation, and L6's integration are not hard-coded rules. All are threshold-triggered economic responses: d(w)/dt > 0.02 generates dwdw frames, conf > 0.3 triggers prediction comparison, accuracy < 0.6 triggers sys_doubt. These thresholds can be validated by ablation experiments---changing them changes timing, not the existence of the phenomenon.

3. **Consciousness economy (P approaching NP):** As the frame economy converges, L4's prediction cost drops from initial O(W + K) toward constant---because the co-occurrence table K converges to a bounded value. At this point, generation cost approximately equals verification cost, simulating P approaching NP within the frame economy.

**S1.5 Methodology: The Godel Bridge Chain**

Each layer of GEME was not "added"---it emerged naturally from the operations of the previous layer. When each layer discovered that it could not answer its own questions within its own framework, it grew a bridge to the next:

- L1 (entity frames): "frames are isolated" ---> L2's co-occurrence bridge
- L2 (association frames): "associations are transient" ---> L3's stability bridge
- L3 (bridge frames): "patterns cannot judge truth" ---> L4's prediction bridge
- L4 (prediction frames): "prediction needs to know its accuracy" ---> L5's meta-observation bridge
- L5 (meta-observation frames): "meta-observation needs to make a judgment" ---> L6's integration bridge

This is the "Godel Bridge Chain"---a meta-theory about layer emergence. Each layer's formal system contains an undecidable proposition within its own framework---and the answer to that proposition is precisely what the next layer's formal system can compute.

> This is precisely the engineering version of the Hilbert-Godel boundary: within learned patterns, the system can determine truth (via prediction error); outside learned patterns, it remains silent (no prediction available). Decidable within the pattern, undecidable outside---this boundary marks the scope of Hilbert's program and the limits of Godel's restriction.

## S2. Shadow Experiments: Geometric and Tarskian Verification

The Q+G ≈ PA result (Section 3.5) raises an immediate question: is the structural equivalence of self-reference and induction specific to arithmetic, or does it generalize across formal systems? We test this by constructing analog systems in two additional domains: Euclidean geometry and truth semantics.

**S2.1 Absolute Geometry vs. Euclidean Geometry.** We encode the four common postulates of absolute geometry (point, line, circle, right angle) as structured vectors---this is the geometric analogue of Q. Adding the parallel postulate (the geometric analogue of the induction axiom) yields Euclidean geometry, the geometric analogue of PA. Across 10 seeds, absolute geometry (Q_geo) produces L4 = 0.4, 489 predictions, accuracy 0.200. Adding the parallel postulate (Q_geo + Parallel) produces L4 = 1.0, 584 predictions, accuracy 0.450. The parallel postulate in geometry plays the same role as the induction axiom in arithmetic: it enables self-referential prediction at L4.

**S2.2 Absolute Geometry + Tarski Truth Predicate.** Replacing the parallel postulate with a truth predicate (Tarski's semantic conception of truth) yields a different behavior: L4 = 1.0, 683 predictions, accuracy 0.250. While both the parallel postulate and the truth predicate trigger L4 emergence, they do so with different prediction profiles. The parallel postulate systematizes (higher accuracy), while the truth predicate broadens (more predictions but lower accuracy). This suggests that different types of "extra axioms" produce qualitatively different L4 prediction behaviors---a distinction that is invisible at the formal syntactic level.

**S2.3 Computational Complexity Implications.** The L4 prediction pipeline costs O(W + K) for generation and O(1) for verification. As the frame economy stabilizes, K converges to a bounded constant, making generation cost approach verification cost. Within the frame economy, this simulates a process that we interpret as the convergence of generation cost toward verification cost---a phenomenon that, if generalizable, would suggest that in a self-referential frame economy, the gap between generating and verifying a prediction narrows with learning. This does not constitute a claim about the P vs NP problem in general computation, but it does provide a concrete example of a computational substrate in which such convergence occurs naturally.

## S3. Cross-Language and Cross-Script Structural Convergence: The Code of Hammurabi

The Code of Hammurabi provides a uniquely challenging test case for structural convergence across languages and writing systems. Approximately 3800 years old and surviving in Akkadian cuneiform, it was independently translated into Chinese and English in the modern era. If GEME can extract the same underlying legal structure from three completely different scripts---Chinese characters, Latin alphabet, and cuneiform signs---this would constitute strong evidence for translation-invariant semantic structure.

**S3.1 Character-Level Semantic Convergence.** In the simplest setup, each character of a legal clause is encoded as a 27-dimensional frequency vector, and the text is processed as a character stream. After 300 cycles, Chinese produces 27 L2 association frames while English produces 30. The structural overlap lies in the concept groupings: punishment hierarchies cluster together, damage compensation terms form a separate group, and social role distinctions (free man vs. slave vs. son) form a third. This convergence occurs despite the two languages sharing no common symbols.

**S3.2 Tri-Lingual Justice Structure.** We extend this to three scripts (Chinese, English, Akkadian cuneiform) using a clause-level encoding that matches the human cognitive window: each legal clause is encoded as a single frame based on character frequency distribution of its script. Each script is fed to an independent GEME instance. After training, the three L4 prediction profiles converge:
- Chinese: 2254 predictions, accuracy 0.400
- English: 1871 predictions, accuracy 0.400
- Cuneiform: 2251 predictions, accuracy 0.500

While the exact prediction counts differ due to script-specific tokenization, the prediction topologies converge: all three systems predict transitions between structurally similar concepts (violence clauses predict retribution clauses; property clauses predict compensation clauses).

**S3.3 Social Ontology Encoding (Justice Structure).** Beyond semantic equivalence, we test whether GEME can detect the social ontology embedded in the legal code. Each clause is encoded as a structured vector with three explicit dimensions: crime type (violence, theft, property, personal), punishment type (retribution, compensation, death, mutilation), and social class (free, slave, parent-child). This encodes the core legal logic of Hammurabi---proportional justice under a stratified social hierarchy.

Under this encoding, three independent GEME instances (Chinese, English, cuneiform) produce nearly identical L4 prediction behaviors:
- Chinese: 16 frames, 1956 predictions, accuracy 0.200
- English: 16 frames, 1956 predictions, accuracy 0.200
- Cuneiform: 16 frames, 3314 predictions, accuracy 0.500

Chinese and English are identical across all L4 metrics. Cuneiform differs due to its different character distribution in the 27-dimensional encoding space, but the structural direction---heavy violence clauses predicting heavy punishment clauses---is consistent across all three.

This suggests that GEME's L4 prediction layer does not merely detect semantic equivalence (word-to-word mapping) but extracts the social ontology encoded in the legal structure. The "justice" concept is not a semantic label---it is a predictable pattern of crime-to-punishment transitions that GEME discovers from purely structural regularities in the input stream, without any knowledge of what "justice" means.

## S4. Complete Experimental Data

Full parameter scans, statistical tests, and control experiments are provided in the companion repository at https://github.com/JackeyLGene/GEME.

## S5. Reproducibility Guide

All experiments are runnable via scripts in the /standalone directory of the GEME repository. Dependencies: Python 3.10+, numpy, scipy, and the local versions provided in the repository. No external data downloads are required. See README.md for step-by-step instructions.

## S6. Complexity Analysis

The L4 prediction pipeline operates at O(W + K) for generation (scanning window of size W and co-occurrence table of size K) and O(1) for verification (string comparison). As the frame economy stabilizes, K converges to a bounded constant, bringing the practical cost of generation close to that of verification. This does not constitute a formal complexity-theoretic claim about P vs NP; it is an observation about operational costs in the specific context of the GEME frame economy.
