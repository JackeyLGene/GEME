# S4 Retired — External Self-Reference Replaced by Endogenous Co-occurrence

**Date**: 2026-05-04  
**Phase**: PA → GO unification  
**Status**: SIGNFICANT ARCHITECTURAL SIMPLIFICATION

---

## What Changed

```
PA V6 (V6.5):          external Godel S4 injection
PA V7 (current):       co-occurrence sliding window (replaces S4)
GO (Phase 6):          co-occurrence sliding window (shared mechanism)
```

## Why

V6 proved: "self-reference helps emergence" (S4 raised emergence from 17% to 35%).  
V7 proves: "self-reference is endogenous co-occurrence, no external injection needed."

The sliding window co-occurrence mechanism (developed in GO for concept linking) incidentally provides the same self-referential pressure that S4 was designed for — but naturally, without any hand-coded Godel numbering.

## What Was Lost

```
Concept              Status
────────────────────────────────────────────
sub(GN(F), 17, GN(F))     REMOVED from all experiments
Godel number encoding     REMOVED from alphabet
S4 signal injection       REMOVED from test protocols
S4 vs no-S4 control       NO LONGER MEANINGFUL

Impact on codebase:
  geme_v6.py: S4-related code REMOVED (replaced by co-occurrence)
  Only ~20 lines removed, architecture simplified
```

## What Was Gained

```
                     V6 (external S4)      V7 (co-occurrence)
────────────────────────────────────────────────────────────
add_comm emergence     35%                    100% (all conditions)
mul_comm emergence     17%                    100% (with training)
assoc frames           0                      9-10
chain frames           0                      4-5
zero-shot              S2                     S2 (unchanged)
negative control       S3                     S3 (correct)
code complexity        178 lines              ~200 lines (shared with GO)
```

## Philosophical Significance

```
S4 was a "hack" — a hand-crafted self-referential formula that proved
a principle but couldn't scale.

Co-occurrence is a "mechanism" — a general operation that any data stream
naturally generates, without special engineering.

The unification of PA and GO under a single co-occurrence mechanism
confirms: strange loops are not constructed — they are discovered.
```

## Files Updated

```
src/gira/phase6/geme_v6.py   — V7 (co-occurrence replaces S4)
docs/milestone_go_complete.md  — Referenced
docs/project_roadmap.md       — Track 1 marked complete
```
