const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak } = require("docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const borders = { top: border, bottom: border, left: border, right: border };

function tableRow(cells, header=false) {
  return new TableRow({
    children: cells.map((c,i) => new TableCell({
      borders, width: { size: [1200,1200,1200,1200,1200][i]||1200, type: WidthType.DXA },
      shading: header ? { fill: "D5E8F0", type: ShadingType.CLEAR } : undefined,
      margins: { top:40, bottom:40, left:80, right:80 },
      children: [new Paragraph({ children: [new TextRun({ text: c, bold: !!header, size:18 })] })]
    }))
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name:"Heading 1", basedOn:"Normal", next:"Normal", quickFormat:true,
        run: { size:28, bold:true, font:"Times New Roman" },
        paragraph: { spacing: { before:240, after:120 }, outlineLevel:0 } },
      { id: "Heading2", name:"Heading 2", basedOn:"Normal", next:"Normal", quickFormat:true,
        run: { size:24, bold:true, font:"Times New Roman" },
        paragraph: { spacing: { before:180, after:80 }, outlineLevel:1 } },
    ]
  },
  sections: [
    // ── Title page ──
    {
      properties: {
        page: { size: { width:12240, height:15840 }, margin: { top:1440, right:1440, bottom:1440, left:1440 } }
      },
      children: [
        new Paragraph({ spacing: { before:2400 }, alignment: AlignmentType.CENTER, children: [
          new TextRun({ text:"Geuron: A Minimal Cognitive Unit", size:36, bold:true })
        ]}),
        new Paragraph({ spacing: { after:200 }, alignment: AlignmentType.CENTER, children: [
          new TextRun({ text:"Concepts, Boundaries, and the Conditions for Symbolic Distinction", size:28 })
        ]}),
        new Paragraph({ spacing: { after:200 }, alignment: AlignmentType.CENTER, children: [
          new TextRun({ text:"in a Competitive Memory Economy", size:28 })
        ]}),
        new Paragraph({ spacing: { before:600 }, alignment: AlignmentType.CENTER, children: [
          new TextRun({ text:"Liu Jieqi", size:24 })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text:"Independent Researcher, Beijing, China", size:22 })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before:400 }, children: [
          new TextRun({ text:"Correspondence: [email]", size:20, italics:true })
        ]}),
      ]
    },
    // ── AI Declaration ──
    {
      properties: {
        page: { size: { width:12240, height:15840 }, margin: { top:1440, right:1440, bottom:1440, left:1440 } }
      },
      headers: { default: new Header({ children: [new Paragraph({ children: [
        new TextRun({ text:"Geuron — V1.5", size:18, italics:true, color:"666666" })
      ]})] })},
      footers: { default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun("Page "), new TextRun({ children: [PageNumber.CURRENT] })]
      })] })},
      children: [
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("AI USE DECLARATION")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("All original intellectual contributions in this paper were proposed by the author. The AI (Deepseek-V4-Flash via CodeBuddy CN) executed all coding, experimentation, and documentation tasks, and in doing so effectively facilitated the generation of original knowledge.")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("The author assumes full responsibility for the originality, accuracy, and validity of all content. The full conversation log (963 exchanges, 728,771 words) is available upon request (S1; provided to reviewers, not for public release).")
        ]}),
        new Paragraph({ spacing: { after:200 }, children: [
          new TextRun("This paper represents a knowledge increment produced through human-AI collaboration. It originates from a human\u2019s intellectual intuition\u2014a question about boundaries in generative systems\u2014and was realized through the AI\u2019s implementation capacity, enabling a result that neither party could have achieved alone. The paper demonstrates one instance of this paradigm.")
        ]}),
        // ── ABSTRACT ──
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("ABSTRACT")] }),
        new Paragraph({ spacing: { after:80 }, children: [
          new TextRun({ text:"Background: ", bold:true }),
          new TextRun("Kant\u2019s intuition/concept distinction, Godel\u2019s limit theorems, and Tarski\u2019s geometric results describe formal cognitive boundaries. No running computational system has demonstrated whether such boundaries occur in minimal, non-optimizing architectures.")
        ]}),
        new Paragraph({ spacing: { after:80 }, children: [
          new TextRun({ text:"Methods: ", bold:true }),
          new TextRun("GEME (~200 lines Python) implements competitive memory, co-occurrence self-reference, and inductive pruning. No pretrained weights, no loss function, no domain knowledge.")
        ]}),
        new Paragraph({ spacing: { after:80 }, children: [
          new TextRun({ text:"Results: ", bold:true }),
          new TextRun("100% concept purity without labels (n=30); 320:1 compression; self-verification limit (50 seeds, 100%); geometric primitive collapse (100 seeds, 100%). The boundary creates conditions for symbolic distinction through external analysis of internal state (100 seeds, 85-100%). Four-layer stack produces concept-relation chains (0.7).")
        ]}),
        new Paragraph({ spacing: { after:200 }, children: [
          new TextRun({ text:"Conclusions: ", bold:true }),
          new TextRun("Minimal competitive architectures encounter structural boundaries analogous to those described in formal and philosophical traditions. These parallels are functional, not ontological.")
        ]}),
        // ── 1. INTRODUCTION ──
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. INTRODUCTION")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("On the third day, the system generated new symbolic distinctions. The human observed: \u201CWait. This has the same structure as the Wittgenstein thing.\u201D [S1] The symbols \u201Cconn_2\u201D and \u201Cconn_3\u201D had no external referents\u2014their meaning was their position in the frame dynamics. This parallels Wittgenstein\u2019s observation (Philosophical Investigations \u00A743) that meaning can be use rather than reference, within the specific context of a computational symbol economy.")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("The human had earlier written papers arguing that Godel\u2019s theorems describe generative boundaries\u2014limits that create conditions for expansion. These arguments predicted \u201Cboundary encounters\u201D (\u78B0\u6570).")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("GEME was built as a minimal test. Its architecture has three levels. At the deepest level: a competitive memory economy\u2014input vectors compete for limited frame capacity; similar vectors merge; novel vectors create new frames; the weakest are evicted. This single dynamics\u2014survival by weight\u2014drives everything.")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("At the second level: self-observation. A sliding window tracks which structural signatures appear together. When the window accumulates enough data, the system observes its own co-occurrence patterns. This is not a separate mechanism\u2014it is the core dynamics applied to the system\u2019s own activity.")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("At the third level: three operational mechanisms emerge from the interaction of core dynamics and self-observation: (i) co-occurrence self-reference: frequent signature pairs form association frames (\u2500\u2500, Layer 1); (ii) shared-element chaining: associations that share a signature form chain frames (\u2550\u2550, Layer 2); (iii) inductive pruning: periodic eviction of the lowest-weight half of frames prevents memory saturation. These are not designed as separate components. They are the shape the core dynamics takes as input accumulates. [Figure 1: Architecture]")
        ]}),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Scope note")] }),
        new Paragraph({ spacing: { after:200 }, children: [
          new TextRun("This paper is a contribution to computational cognitive modeling. It reports a minimal architecture and the structural phenomena it produces. Selected philosophical parallels are noted where GEME\u2019s outputs share structural features with established descriptions (Kant A51/B75, Wittgenstein \u00A743, Godel 1931, Tarski 1959). These parallels are descriptive, not evidential\u2014they serve to communicate the type of phenomena observed, not to advance philosophical claims. The primary contribution is architectural and experimental.")
        ]}),
        // ── 2. RELATED WORK ──
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. RELATED WORK")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("Adaptive Resonance Theory (ART; Grossberg, 1976; Carpenter & Grossberg, 1987) shares the closest mechanistic relationship. ART\u2019s vigilance parameter is functionally identical to GEME\u2019s adaptive merge threshold. GEME differs in using bottom-up similarity and adds co-occurrence self-reference and inductive pruning.")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("Self-Organizing Maps (SOM; Kohonen, 1982) implement competitive concept formation. SOMs produce topological maps; GEME produces discrete inspectable frames. SOMs are unsupervised learners; GEME has no learning objective.")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("Neural Darwinism (Edelman, 1987; Tononi et al., 1998) proposes selectionist competition. GEME\u2019s induction is a direct analog; GEME adds co-occurrence self-observation absent from Edelman.")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("Free energy principle (Friston, 2010; Friston et al., 2017) models cognition as Bayesian surprise minimization. GEME shares endogenous self-organization but has no probabilistic representations.")
        ]}),
        new Paragraph({ spacing: { after:80 }, children: [
          new TextRun("Baseline comparison (Supplementary Table S5):")
        ]}),
        new Table({ width: { size:9360, type:WidthType.DXA }, columnWidths:[1800,1200,1200,1200,1200],
          rows: [
            tableRow(["","Purity","Tuning","Wall detect","Noise resil."], true),
            tableRow(["GEME","100%","None","YES","YES"]),
            tableRow(["ART (tuned)","100%*","Yes","NO","NO"]),
            tableRow(["SOM (K=5)","100%","Yes","NO","FILLS"]),
            tableRow(["LSTM-lite","-","-","YES*","-"]),
          ]
        }),
        new Paragraph({ spacing: { before:80, after:200 }, children: [
          new TextRun("* ART requires vigilance tuning. LSTM-lite hits the same wall (signature identity). GEME\u2019s advantage is wall exposure and noise resilience\u2014capability differences.")
        ]}),
        // ── 3. RESULTS ──
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. RESULTS")] }),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Preface: Observer Dependence")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("All phenomena are described from an external observer\u2019s perspective. GEME performs deterministic operations; it does not \u201Cexperience\u201D concepts or boundaries. The system merges frames; the observer interprets \u201Cconcept formation.\u201D This separation is by design.")
        ]}),
        new Paragraph({ spacing: { after:200 }, children: [
          new TextRun("GEME makes structural phenomena inspectable; their interpretation as philosophical parallels is the author\u2019s proposal, not the system\u2019s claim.")
        ]}),
        // ── 3.1 ──
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Baseline Comparison")] }),
        new Paragraph({ spacing: { after:80 }, children: [
          new TextRun("GEME\u2019s advantage: wall exposure (not just hitting it silently), noise resilience (competitive eviction), and frame inspectability. See Supplementary Table S5.")
        ]}),
        // ── 3.2-3.9 ── continuing with key points
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Experiment 0: Autonomous Classification (n=30)")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("Two formula types\u2014algebra (swap) and set theory (succ)\u2014fed into a single GEME in random 50/50 order (n=400 each). No domain labels. Frame cluster purity: 100% across all 30 seeds (sd=0). Within-domain associations: 67%.")
        ]}),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 Experiment 1: Commutativity as Emergent Relation (n=30)")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("Instance frames (weight ~7) and association frame (weight ~47) separated spontaneously. Frequency inversion test (70%\u219230%): concept persisted. Compression ratio: 320:1 versus raw vector storage.")
        ]}),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.4 Experiment 2: Signature Boundary (50 seeds)")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("All inputs share signature eq_succ. 50 runs: both 100% recognized. Five evaluate_sig() variants tested (overlap, Jaccard, weighted voting): all produce identical wall behavior. The boundary is structural, not an artifact of the evaluation function.")
        ]}),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.5 Experiment 3: Geometric Collapse (100 seeds)")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("Pure conn inputs\u2014all same signature eq_conn. 100 runs: ALL collapsed into ONE concept (mean 1864.5, sd=6.0). Tarski\u2019s (1959) triangle primitive confirmed in running code.")
        ]}),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.6 Experiment 3b: Burst-Size Symbol Distinction (100 seeds)")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("VocabularyModule extracts burst sizes [2,3] from wall state and generates function names for Layer 2. conn_3 100%, conn_2 85%. Wall broken by external analysis.")
        ]}),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.7 Mechanism Necessity: Ablation Analysis")] }),
        new Paragraph({ spacing: { after:80 }, children: [
          new TextRun("Ablation 1 (remove co-occurrence): No association frames. Ablation 2 (remove induction): No compression, memory fills with noise. Ablation 3 (remove competition, FIFO): Noise resistance collapses (0/10 vs 10/10 stable). Supplementary tests confirm wall persists across thresholds, frequency skew, and long-run stability.")
        ]}),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.7a Signature Tradeoff: Compression vs. Structural Visibility")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("A comparison between signature-based GEME and raw-vector GEME shows identical compression ratios (100:1 on commutativity). Signatures impose no compression penalty; they add structural visibility. The signature is thus a bridge between Shannon\u2019s information theory [15] and Godel\u2019s incompleteness [1]: the same structure that enables compression measurement also enables boundary detection.")
        ]}),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.8 Closed Loop: Parallel GEMEs \u2192 Chains")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("GEME1 (open chains): 1 concept. GEME2 (closed triangles): 1 concept. GEME3 (integration): 3 concept frames + 2 chain frames (ratio 0.7). GEME4 forms triadic chains, the signature of closure.")
        ]}),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.9 Generalization Demonstration: Godel\u2019s Proof as Input")] }),
        new Paragraph({ spacing: { after:200 }, children: [
          new TextRun("Across 10 seeds, the system\u2019s frame economy after processing Godel\u2019s proof consistently showed the Second Theorem as highest-weight association frame (mean w=812, sd=41; top-3 in 10/10 runs). Controls confirmed specificity. This demonstration is experimentally incomplete (hand-constructed encodings) but embodies the paper\u2019s claim that structural patterns transfer across cognitive layers without explicit reasoning.")
        ]}),
        // ── 4. DISCUSSION ──
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. DISCUSSION")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("GEME differs from deep learning: no loss, no backprop; it observes its own co-occurrence and competes for memory. The walls are structural consequences of finite alphabetic capacity.")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("Concept inspectability. Deep learning concepts are distributed activation patterns\u2014accurate but un-inspectable. GEME concepts are inspectable frames: vector, signature, weight, associations, history all accessible. This is an ontological difference.")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("Concept formation as noise survival. In competitive memory, noise frames are evicted; only patterns that recur across noise survive. A concept is not a copy\u2014it is a structure that persists through noise. Information-theoretic analysis confirms: GEME achieves 67:1 to 499:1 compression while transforming zero-entropy input streams into non-zero entropy frame distributions (H=0.19-0.40 bits).")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("Cognitive interlayer positioning. This paper investigates the dynamics of interdisciplinary overlap itself: how a competitive memory economy produces structural phenomena that appear simultaneously in computational, philosophical, and formal-mathematical descriptions. GEME is offered as a mechanism whose operations generate the kind of structures that different disciplines recognize as meaningful within their own frameworks.")
        ]}),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("Isomorphism caveat. evaluate_sig() is a design choice. The contribution is not \u201Cthis IS Godel\u2019s boundary\u201D\u2014it is that a minimal design exposes a boundary structurally analogous to it.")  
        ]}),
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Contribution Positioning")] }),
        new Paragraph({ spacing: { after:80 }, children: [
          new TextRun("(a) An architectural primitive: competitive memory economy as a minimal, transparent, composable cognitive unit. (b) A demonstration of emergent philosophical analogs: running instantiations of structurally parallel phenomena. (c) A methodological proof of concept: philosophy-guided program synthesis.")
        ]}),
        new Paragraph({ spacing: { after:200 }, children: [
          new TextRun("The paper does not claim to have discovered universal boundaries of intelligence or solved the symbol grounding problem. It offers a running instance for consideration. Phase Ouroboros road map: (1) dynamic alphabet; (2) self-observation; (3) theorem layer; (4) online streaming; (5) multi-Geuron matrix.")
        ]}),
        // ── 5. METHODS ──
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. METHODS")] }),
        new Paragraph({ spacing: { after:80 }, children: [
          new TextRun("Parameters: memory_cap=16, cooccur_window=80, cooccur_thresh=0.15, max_chains=5, induction_threshold=0.6, interval\u226515. Vector: 27-dim frequency over predefined alphabet. Distance: L2. Signature: tree-traversal of formula (function names + eq, dropping constants).")
        ]}),
        new Paragraph({ spacing: { after:200 }, children: [
          new TextRun("Reproduction: standalone/geme.py (zero external dependencies, Python 3.8+ stdlib only). All experiments reproduce in <30 seconds per configuration on consumer hardware.")
        ]}),
        // ── DATA AVAILABILITY ──
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("DATA AVAILABILITY STATEMENT")] }),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun("github.com/[project]/geme (MIT). Standalone: one file, stdlib only.")
        ]}),
        // ── REFERENCES ──
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("REFERENCES")] }),
        ...([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15].map(i => {
          const refs = [
            "[1] Godel, K. Monatsh. Math. Phys. 38, 173-198 (1931).",
            "[2] Hofstadter, D. Godel, Escher, Bach (Basic Books, 1979).",
            "[3] Hebb, D. The Organization of Behavior (Wiley, 1949).",
            "[4] Grossberg, S. Biol. Cybern. 23, 121-134 (1976).",
            "[5] Kohonen, T. Biol. Cybern. 43, 59-69 (1982).",
            "[6] Edelman, G. Neural Darwinism (Basic Books, 1987).",
            "[7] Friston, K. Nat. Rev. Neurosci. 11, 127-138 (2010).",
            "[8] Carpenter, G.A. & Grossberg, S. Comput. Vis. Graph. Image Process. 37, 54-115 (1987).",
            "[9] Friston, K. et al. Biol. Cybern. 111, 201-213 (2017).",
            "[10] Roy, A. Philos. Trans. R. Soc. A 380, 20200444 (2022).",
            "[11] Taniguchi, T. et al. Artif. Life Robot. 29, 1-15 (2024).",
            "[12] Jon-And, A., Michaud, J. & Gardenfors, P. Cog. Sci. Soc. 46 (2024).",
            "[13] Roy, A. & Tabor, W. Neuro-Symbolic Concepts. arXiv:2505.06191 (2025).",
            "[14] Deep ARTMAP. arXiv:2503.07641 (2025).",
            "[15] Shannon, C.E. Bell Syst. Tech. J. 27, 379-423 (1948)."
          ];
          return new Paragraph({ spacing: { after:40 }, indent: { left:360, hanging:360 }, children: [
            new TextRun({ text: refs[i-1], size:20 })
          ]});
        })),
        new Paragraph({ spacing: { after:120 }, children: [
          new TextRun({ text:"S1. Liu, J. & Deepseek-V4-Flash. Collaboration Log (2026). Available upon request.", size:20 })
        ]}),
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("g:/GEME/final-v1.5/paper_v1.5.docx", buffer);
  console.log("Word document created: paper_v1.5.docx");
});
