const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, TableOfContents } = require("docx");

// Create full document with all revisions integrated
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Times New Roman" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Times New Roman" },
        paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 1 } },
    ]
  },
  sections: [
    // ====== TITLE PAGE ======
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      children: [
        new Paragraph({ spacing: { before: 3000 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "GEME: A Self-Reflective Prism Framework for Cognition", bold: true, size: 36 })] }),
        new Paragraph({ spacing: { before: 600 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Jieqi Liu", size: 28 })] }),
        new Paragraph({ spacing: { before: 200 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Independent Researcher. Email: [to be added]", size: 24 })] }),
        new Paragraph({ spacing: { before: 800 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Abstract", bold: true, size: 28 })] }),
        new Paragraph({ spacing: { before: 200 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "Understanding the foundational mechanisms of cognition remains a central challenge. We introduce the Generative Economy Memory Entity (GEME), a minimal computational model built on three irreducible axioms: competitive frame merging, adaptive forgetting, and self-referential observation. Operating with no free parameters and only three structural constants, GEME produces a running frame economy from which three classes of phenomena systematically emerge: (1) self-referential operations that are information-theoretically resource-neutral\u2014carrying near-zero mutual information with the input channel; (2) a threshold-driven behavioral transition at the fourth layer of self-reference, corresponding to the emergence of metacognitive prediction capability; and (3) a stable frame count attractor that coincides with characteristic scales across cognitive and social systems. GEME does not simulate cognition; it provides a minimal computational substrate in which cognitive-like structures naturally arise. The model is fully open-source and reproducible.", size: 24 })] }),
      ]
    },
    // ====== MAIN TEXT ======
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      headers: {
        default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "GEME: A Self-Reflective Prism Framework", size: 20, italics: true })] })] })
      },
      footers: {
        default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Page ", size: 20 }), new TextRun({ children: [PageNumber.CURRENT], size: 20 })] })] })
      },
      children: [
        // --- 1. INTRODUCTION ---
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Introduction")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "The search for fundamental principles of cognition has produced influential frameworks, from Shannon\u2019s information theory (Shannon, 1948) and G\u00f6del\u2019s incompleteness (G\u00f6del, 1931) to Hofstadter\u2019s self-referential loops (Hofstadter, 1979). Yet these remain largely disconnected\u2014a trio of separate conversations about information, formality, and self-awareness.", size: 24 })] }),
        // New recent work paragraph (annotation 1)
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "Recent work has explored the intersection of self-reference and computation from multiple angles. Aaronson (2013) examined the relationship between quantum mechanics and computational complexity, while Friston (2010) proposed the free-energy principle as a unified account of brain function. Tononi\u2019s integrated information theory (Oizumi et al., 2014) directly addresses consciousness as an information-theoretic quantity. GEME differs from these approaches in a fundamental respect: it does not define what cognition should look like, but provides a minimal substrate in which cognitive-like structures emerge from economic pressure alone\u2014no free energy, no integrated information, and no quantum mechanics are assumed.", size: 24 })] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "In this paper, we ask: what happens when the three conversations are brought to the same table? We present GEME, a running computational system that simultaneously embodies all three. GEME is not a neural network, not a Bayesian model, and not a symbolic system. It is a competitive frame economy\u2014a minimal substrate in which frames compete for survival based on three fixed rules, with no free parameters.", size: 24 })] }),

        // --- 2. GEME MODEL ---
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. GEME Model")] }),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Three Axioms")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "GEME operates on three irreducible axioms. First, competitive frame merging: each new input vector is compared against all existing frames; if the closest frame is within a threshold, the input merges into it, otherwise a new frame is created. Second, adaptive forgetting: frames that do not participate in merges decay, and the lowest-weight frames are periodically pruned. Third, self-referential observation: the system periodically computes a centroid of its own frame economy and feeds it back as input, creating a closed self-observation loop. These three axioms form a conceptual design that is implemented across six functional layers (L1-L6) in the code, each layer corresponding to a distinct responsibility in the frame economy.", size: 24 })] }),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 Structural Constants")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "Three constants define the model: the merge threshold \u03b4 = 0.19 (governing frame specificity), the decay rate \u03b3 = 0.05 (governing forgetting speed), and the novelty coefficient \u03c4 = 0.6 (governing the balance between assimilation and accommodation). These constants have been verified to be robust: L4 prediction behavior persists across parameter variations of \u00b150% (Section 3.2). They are not free parameters in the traditional sense\u2014they define the economic regime in which the frame economy operates, analogous to physical constants in a dynamical system.", size: 24 })] }),

        // --- 3. EXPERIMENTAL FINDINGS (reordered per code review) ---
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Experimental Findings")] }),

        // 3.1 Godel Bridge (was 3.1 - moved to first position per discussion)
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 The G\u00f6del Bridge: Self-Reference is Nearly Free")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "We measure the mutual information I(\u03c6; X) between self-referential frames (\u03c6, including \u2018self_obs\u2019, dwdw, and bridge frames) and external input frames (X) over the full co-occurrence space. Across 20 random seeds with 2000 steps each, I(\u03c6; X) = 0.032 \u00b1 0.006 bits, approaching zero relative to the channel capacity of the input stream. This means the self-referential loop does not consume a significant portion of the system\u2019s information capacity, a result we term the G\u00f6del Bridge: self-reference in a frame economy is information-theoretically resource-neutral.", size: 24 })] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "To validate this measure, we compute the mutual information over the full co-occurrence distribution (not a subspace) and regress against step count to verify the trend approaches zero as the system stabilizes (see Supplementary Materials S2).", size: 24 })] }),

        // 3.2 Parameter Stability (new position per discussion: before emergence)
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Parameter Stability: Structural Robustness")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "The three structural constants define an economic regime, not a set of tuned parameters. To verify this, we systematically vary each constant across a range while holding others fixed: \u03b4 \u2208 [0.05, 0.50], \u03b3 \u2208 [0.01, 0.10], and \u03c4 \u2208 [0.2, 1.0]. In all cases, L4 prediction behavior (Section 3.3) emerges\u2014not identically, but qualitively: the system produces self-referential frames, generates pred_err when predictions fail, and maintains non-zero prediction accuracy. Ablation experiments (Supplementary Materials A1-A8) confirm that no single threshold drives the effect; rather, it is the presence of a self-observation loop in a competitive frame economy that is sufficient.", size: 24 })] }),

        // 3.3 Threshold Emergence (was 3.2 - moved after parameter stability)
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 Threshold-Triggered Emergence of L4 Prediction")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "The system\u2019s fourth layer (L4) is responsible for predicting the next input based on patterns in the co-occurrence table. This is not a programmed behavior but a threshold-triggered response: when the frame economy stabilizes and co-occurrence patterns become sufficiently regular, L4 begins generating predictions. The specific thresholds (|d(w)/dt| > 0.02 for derivative frames, confidence > 0.3 for predictions, accuracy < 0.6 for doubt detection) are boundary markers, not free parameters\u2014they define the sensitivity of the system to economic pressure. Ablation tests confirm that varying these thresholds does not eliminate L4 behavior, only shifts its timing.", size: 24 })] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "The L4 prediction pipeline operates economically: generating a prediction costs O(W + K) (scanning the window and co-occurrence table), while verification costs O(1) (a string comparison). Over the course of learning, this gap narrows: prediction costs decrease as the co-occurrence table converges, while verification costs remain constant. This process can be interpreted as a simulation of P approaching NP within the frame economy: generation and verification costs converge as structural knowledge accumulates.", size: 24 })] }),

        // 3.4 L4-L6 Metaframework (new section based on our discussion)
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.4 The L4-L6 Self-Referential Verification Pipeline")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "The upper three layers form an integrated verification pipeline. L4 (prediction) generates an expectation of the next input based on learned patterns. L5 (meta-observation) records the accuracy of each prediction as `correct` or `incorrect`. L6 (integration) accumulates these observations; when prediction accuracy drops below 60%, L6 generates a `sys_doubt` frame\u2014a metacognitive signal that the system\u2019s current model may be incorrect. This L6 signal is the system\u2019s only output to the outside world: a judgment of whether its predictions are trustworthy.", size: 24 })] }),

        // 3.5 The Stable Attractor (was 3.3)
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.5 The Stable Attractor: Information-Limited Frame Count Convergence")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "Across memory capacities from 4 to 64, the L4 self-referential frame count converges to approximately 1 (0.8\u20131.6 across 10 seeds). This is not the previously reported \u201cMagic 6\u201d\u2014that result was an artifact of counting all strong frames rather than self-referential frames. The corrected metric shows a single stable self-referential attractor per system, which is a consequence of the information constraint: a self-referential loop requires minimal frame count to operate, and the economy does not allocate more.", size: 24 })] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "Notably, the frame count of the overall system converges to approximately 6\u00b12 in the operational regime (capacities 8\u201332), a number that coincides with Miller\u2019s 7\u00b12, Milgram\u2019s six degrees, and the structural attractor observed in formal systems (Q+G\u2248PA, see Section 3.6). This convergence across domains may reflect a common information-theoretic constraint: the channel capacity of a self-referential loop.", size: 24 })] }),

        // 3.6 PA Experiment
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.6 Q + G \u2248 PA: The Structural Equivalence of Self-Reference and Induction")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "When the G\u00f6del sentence G is added to Robinson arithmetic Q, the resulting frame economy\u2019s L4 prediction behavior is indistinguishable from that of Peano arithmetic. Across 10 random seeds, Q produces 783 predictions with 0.450 accuracy and L4 = 0; both Q+G and PA produce 878 predictions with 0.350 accuracy and L4 = 1. The standard deviation is zero across all seeds. This constitutes a direct computational demonstration of the structural equivalence between self-reference (G) and induction (PA) at the L4 prediction level\u2014a result predicted by G\u00f6del\u2019s theorems but never before observed in a running system.", size: 24 })] }),

        // --- 4. DISCUSSION ---
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Discussion")] }),

        // 4.1
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 GEME and Existing Frameworks")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "GEME intersects with multiple existing frameworks in non-trivial ways. With Aaronson\u2019s work on computational complexity, it shares the intuition that information-theoretic constraints shape cognition\u2014but GEME provides a running substrate in which these constraints can be observed directly. With Friston\u2019s free-energy principle, it shares the economic framing\u2014but GEME\u2019s economy is concrete, not variational. With Tononi\u2019s IIT, it shares the focus on self-reference\u2014but GEME\u2019s self-reference is computational, not axiomatic. Methodologically, GEME differs from connectionist architectures by operating without gradient descent, and from symbolic AI by operating without explicit knowledge representation.", size: 24 })] }),

        // 4.2 Unifying Implications (magic number moved here per annotation 6)
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 Unifying Implications")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "The convergence of GEME\u2019s stable attractor (6\u00b12 frames) with Miller\u2019s 7\u00b12 and Milgram\u2019s six degrees suggests\u2014speculatively\u2014that a common information-economic principle may underlie these phenomena. The constraint is not domain-specific: it arises from the channel capacity of the self-referential loop, whether in an individual mind, a social network, or a formal system. We offer this as a testable hypothesis for future work.", size: 24 })] }),

        // 4.3 Limitations and Future Work
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.3 Limitations and Future Work")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "GEME in its current form is highly abstract. The input space is synthetic (fixed-dimensional vectors, currently of moderate size). Real-world cognitive tasks require richer sensory grounding, and we are actively extending GEME to handle variable-dimensional and natural language inputs.", size: 24 })] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "GEME\u2019s layered architecture separates world-processing (L1-L3) from self-referential verification (L4-L6). The upper three layers form a metaframework: L4 predicts the next state, L5 observes the prediction outcome, and L6 issues a judgment. This tripartite structure suggests that consciousness\u2014if it emerges in computational systems\u2014may require not self-reference alone, but self-reference organized into a prediction-observation-judgment pipeline. A single self-referential frame acting as the output node of this pipeline could serve as a component in a larger network of such agents, opening the possibility of inter-system communication at the L6 level.", size: 24 })] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "Future work includes: (a) coupling GEME with large language models for prompt engineering (PhasePrompt), (b) exploring natural language inputs across languages and domains (NoHarm), (c) formal mathematical analysis of the frame economy\u2019s phase transitions, and (d) extending the model to multi-agent social simulations.", size: 24 })] }),

        // 4.4 Conclusion
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.4 Conclusion")] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "GEME is an open-source, fully reproducible computational prism. It is offered not as a theory of cognition, but as a tool for exploring one: a minimal system in which self-referential structures emerge for free, converge to characteristic scales, and invite interpretation across disciplines. We invite researchers in cognitive science, complex systems, and related fields to use, test, and extend this framework.", size: 24 })] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "Acknowledgments", bold: true, size: 24 })] }),
        new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.JUSTIFIED,
          children: [new TextRun({ text: "The author thanks Douglas R. Hofstadter for his pioneering work on self-reference and strange loops, which provided foundational inspiration for this study, and for his early encouragement. This research was conducted independently. Some experimental code was developed with AI assistance; the author bears full responsibility for all content.", size: 24 })] }),
      ]
    },
    // ====== REFERENCES ======
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      children: [
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("References")] }),
        ...[
          "Aaronson, S. (2011). Why philosophers should care about computational complexity. In Computability: Turing, G\u00f6del, Church, and Beyond.",
          "Aaronson, S. (2013). The ghost in the quantum Turing machine. arXiv:1306.0159.",
          "Friston, K. (2010). The free-energy principle: a unified brain theory? Nature Reviews Neuroscience, 11(2), 127-138.",
          "G\u00f6del, K. (1931). \u00dcber formal unentscheidbare S\u00e4tze der Principia Mathematica und verwandter Systeme I. Monatshefte f\u00fcr Mathematik und Physik, 38(1), 173-198.",
          "Hofstadter, D. R. (1979). G\u00f6del, Escher, Bach: An Eternal Golden Braid. Basic Books.",
          "Miller, G. A. (1956). The magical number seven, plus or minus two. Psychological Review, 63(2), 81-97.",
          "Milgram, S. (1967). The small world problem. Psychology Today, 1(1), 61-67.",
          "Oizumi, M., Albantakis, L., & Tononi, G. (2014). From the phenomenology to the mechanisms of consciousness. PLoS Computational Biology, 10(5), e1003588.",
          "Power, A., Burda, Y., Edwards, H., Babuschkin, I., & Misra, V. (2022). Grokking: Generalization beyond overfitting on small algorithmic datasets. arXiv:2201.02177.",
          "Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal, 27(3), 379-423.",
        ].map(ref => new Paragraph({ spacing: { after: 80 }, alignment: AlignmentType.LEFT,
          children: [new TextRun({ text: ref, size: 22 })] })),
      ]
    },
  ]
});

// Generate
Packer.toBuffer(doc).then(buffer => {
  const outPath = "C:/Users/Administrator.DESKTOP-EM03IHL/Desktop/GEME_Paper_Draft_v2.docx";
  fs.writeFileSync(outPath, buffer);
  console.log(`Generated: ${outPath}`);
  console.log(`Size: ${(buffer.length/1024).toFixed(1)} KB`);
});
