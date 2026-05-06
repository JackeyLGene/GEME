# GEM Architecture v2 — Recursive Self-Observation

**Milestone: GEM Framework Complete · Layer 2 Design · 2026-05-03**

---

## 1. The Full Cognitive Loop

```
Human (consciousness) ──[generates]──▶ Translatable Language (Wittgenstein Table)
                                              │
                                        Digital (1D: GN/UTF)
                                              │
                                    ┌─────────┴──────────┐
                                    │  GEME (3 operations) │
                                    │                       │
                                    │ ① Readability Mapping │── domain + signature
                                    │ ② Diagonal Transforms │── self-reference
                                    │ ③ Training Evaluation │── boundary + harm + emergence
                                    └─────────┬──────────┘
                                              │
                                        Emergence (digital patterns)
                                              │
                                    ┌─────────┴──────────┐
                                    │  Layer 2 GEME       │
                                    │  (algebraic/geometric│
                                    │   interpretation)    │
                                    └─────────┬──────────┘
                                              │
                                        Readable Theorem
                                              │
Human (understands) ◀────── Translatable Language ◀──────┘

GEME is not an agent. It is an observation instrument.
The human is at both ends of the loop.
```

## 2. Recursive Architecture (Key Innovation)

```
Layer 1 GEME (Language):
  Raw signals → Wittgenstein Table → L(raw)-0 clustering
  → Output: structural clusters {α, β, γ, ...} with relation patterns

Layer 2 GEME (Algebraic/Geometric):
  Layer 1 clusters as INPUT → encoded as formal patterns
  → Discovers provable relations between clusters
  → Human reads: "α∘β = β∘α" (cluster α commutes with cluster β)

The human cannot read Layer 1 directly.
The algebraic layer translates structural emergence into readable theorems.
This IS recursive self-observation — GEME observing GEME.
```

## 3. Unified Domain-Aware L-Scale

```
L(D)-0: EXTRA-DOMAIN   — domain not in grammar (growth seed)
L(D)-1: AXIOMATIC      — trivially true
L(D)-2: DERIVABLE      — requires inference
L(D)-3: BOUNDARY       — expressible, not provable (emergence trigger)
L(D)-4: INCOMPLETENESS — fundamentally undecidable
```

## 4. Variable Architecture — Layer Distinction

```
Layer 3: Language (GEME 6.3 — future work)
  ─────────────────────────────────────────
  Variables: NOT pre-given — must emerge from signal structure
  "The system creates 'x' when it needs a placeholder
   for a category it has discovered"
  Truly open-ended emergence

Layer 2: Geometry (GEME 6.2 — framework ready)
  ─────────────────────────────────────────
  Variables: pre-given as field coordinates
  Points and lines are domain objects, not abstract variables
  Variables range over the field, not universal quantification

Layer 1: Q Arithmetic (GEME 6.1 — active)
  ─────────────────────────────────────────
  Variables: pre-given in FOL (first-order logic) 
  var("x"), forall, exists, eq — language primitives
  Like Chomsky's innate language faculty:
    the CAPACITY for variables is pre-given
    but the SPECIFIC USE (e.g. commutativity) is discovered
    through compression of repeated concrete patterns

Key distinction from LLMs:
  LLMs: variables are statistical embeddings — no formal binding
  GEME: variables are FOL bindings — syntactically constrained
  This is why GEME can detect formal boundaries (L3) but LLMs cannot.
```

## 5. Layer Selection — Why M1 (Q + FOL) Is Optimal

```
Available layers for formal arithmetic:

  M0 (pure arithmetic):
    [0, 1, s, +]           no ∀, no formula structure
    Can express: "1+2=3"
    Cannot express: L3 boundary, cannot detect ⨀
    → Too weak. Boundary invisible.

  M1 (Q + FOL) ← GEME:
    [0, s, +, ×, ∀, ∃, =]  minimal undecidable grammar
    Can express: all Q theorems + L3 undecidable propositions
    Variables: minimal pre-given (like Chomsky's innate faculty)
    Discovery: SPECIFIC USE of variables (commutativity pattern)
    → Just right. Boundary visible, emergence authentic.

  M2 (PA = Q + induction schema):
    Can express: all PA theorems
    But: induction schema already encodes "how to generalize"
    Discovery would be: "I already had the rule, didn't I?"
    → Too strong. Emergence becomes trivial.

  M3 (ZFC set theory):    
    Can express: everything
    But: discoverable patterns confounded with set existence axioms
    → Too powerful. Emergence is drowned.

GEME chose M1 because it is the MINIMAL layer that:
  1. Can express undecidable propositions (L3 boundary)
  2. Has variables as language primitives (not emergent — honest)
  3. Does NOT have pre-given induction (emergence is real)
  4. Forces the system to DISCOVER compression patterns,
     not inherit them from the axiom layer

This is the "poverty of stimulus" argument in computational form:
  - The capacity for variables is innate (FOL)
  - The specific law (commutativity) is discovered from limited data
  - Discovery is real because the law was NOT in the axioms
```

## 7. Core Components

| Component | File | Role |
|:---|:---|:---|
| WittgensteinTable | `phase6/wittgenstein.py` | Translation: external → domain + signature |
| DomainAwareClassifier | `phase6/domain_classifier.py` | Domain-routed L(D)-level |
| GEME | `phase6/entity.py` | Observation instrument (3 operations) |
| GEMReporter | `phase6/reporter.py` | Human-readable pipeline output |

## 8. Three Sandboxes

| # | Sandbox | Domain | Truth Source | Layer |
|:---:|:---|:---|:---|:---:|
| 6.1 | PA | arithmetic | Q axioms | 1 |
| 6.2 | Geometry | geometric | Tarski algebra | 1 |
| 6.3 | Language | raw | none (pure structure) | 1 |

**Layer 2**: Algebraic GEME receiving Layer 1 output → theorem generation

## 6. Research Program

```
Completed:
  Phase 1-4: Closed emergence (concept verification)
  GEME Framework: Table + Classifier + Entity + Reporter
  Recursive Architecture Design

In Progress:
  Geometry sandbox (Tarski encoding)
  Language sandbox (full emergence pipeline)
  Layer 2 (algebraic interpretation of Layer 1 output)

Future:
  LLM-as-binary-feedback language training
  GEME recursive self-observation experiments
  Paper: GEME as concluding piece
```
