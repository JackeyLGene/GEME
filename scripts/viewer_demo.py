"""ProofViewer — SAS triangle congruence, correct geometric notation."""
import sys
sys.path.insert(0, r'G:\GEME\src')
from gira.phase3.language import *
from gira.phase6.geme_go import GEME
from gira.phase6.proof_viewer import ProofViewer

A,B,C,D,E,F = [var(c) for c in "ABCDEF"]

# SAS: (AB≡DE ∧ ∠A≡∠D ∧ AC≡DF) → △ABC ≡ △DEF
SAS = impl(
    conj(conj(eq(fn("seg",A,B),fn("seg",D,E)),
              eq(fn("angle",B,A,C),fn("angle",E,D,F))),
         eq(fn("seg",A,C),fn("seg",D,F))),
    eq(fn("△",A,B,C),fn("△",D,E,F)))

# ASA: (∠A≡∠D ∧ AB≡DE ∧ ∠B≡∠E) → △ABC ≡ △DEF
ASA = impl(
    conj(conj(eq(fn("angle",B,A,C),fn("angle",E,D,F)),
              eq(fn("seg",A,B),fn("seg",D,E))),
         eq(fn("angle",A,B,C),fn("angle",D,E,F))),
    eq(fn("△",A,B,C),fn("△",D,E,F)))

# SSS: (AB≡DE ∧ BC≡EF ∧ CA≡FD) → △ABC ≡ △DEF
SSS = impl(
    conj(conj(eq(fn("seg",A,B),fn("seg",D,E)),
              eq(fn("seg",B,C),fn("seg",E,F))),
         eq(fn("seg",C,A),fn("seg",F,D))),
    eq(fn("△",A,B,C),fn("△",D,E,F)))

for label, axiom, extra, rounds in [
    ("run01 — axiom only", SAS, [], 0),
    ("run02 — axiom + ASA x50", SAS, [ASA]*50, 50),
    ("run03 — axiom + ASA x100 + SSS x5", SAS, [ASA]*100 + [SSS]*5, 105),
]:
    e = GEME(axioms=[axiom], memory_cap=8, merge_thresh=0.75)
    v = ProofViewer(e)
    for f in extra: e.process(f)
    p = v.save_run()
    # Print first line of axiom
    import os
    with open(p, 'r', encoding='utf-8') as fh: first = fh.readline()
    print(f"{label}: {os.path.basename(p)}")
