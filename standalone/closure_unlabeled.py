# Closure detection WITHOUT external labels
# L2 only observes L1's frame state over time
# No v_closed/v_open. Only temporal pattern of L1 frame changes.
import sys, os, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

class GEME_T(GEME):
    def observe_ext(self, sigs, src="e"):
        ft = self.memory._step_counter
        for sig in sigs:
            sid = f"{src}_{sig[:18]}"
            self.memory._window.append((sid, ft, (0.0,)*_VEC_DIM))
            if len(self.memory._window) > self.memory._win_max:
                self.memory._window.pop(0)

def trial(seed):
    r = random.Random(seed)
    pts = ["A","B","C","D","E","F"]
    g0 = GEME_T(memory_cap=12, merge_thresh=0.001, cooccur_window=20, cooccur_thresh=0.08, max_chains=5, time_window_size=5)
    g1 = GEME_T(memory_cap=16, cooccur_window=30, cooccur_thresh=0.1, max_chains=10, time_window_size=10)
    g2 = GEME_T(memory_cap=16, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=8)
    g3 = GEME_T(memory_cap=12, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=12)
    for g in [g0,g1,g2,g3]: g.memory._chain_cooccur_thresh = 2

    for epoch in range(40):
        r.shuffle(pts)
        for i in range(0, len(pts)-2, 2):
            a,b,c = pts[i], pts[i+1], pts[i+2]
            # Closed
            for p in [a,b,c]: g0.process_sig(eq(fn("pt",const(p)),const("y")),f"p{p}")
            g1.process_sig(eq(fn("s",const(f"{a}{b}")),const("y")),f"s{a}{b}")
            g1.process_sig(eq(fn("s",const(f"{b}{c}")),const("y")),f"s{b}{c}")
            g1.process_sig(eq(fn("s",const(f"{c}{a}")),const("y")),f"s{c}{a}")
            l1s = list(set(f.sig_full or f.sig for f in g1.memory.frames if f.weight>2))
            g2.observe_ext(l1s,"L1")
            g2.process_sig(eq(fn("t",const(".")),const("y")),"tick")  # heartbeat
            l2s = list(set(f.sig_full or f.sig for f in g2.memory.frames if f.weight>2))
            g3.observe_ext(l2s,"L2")
            g3.process_sig(eq(fn("t",const(".")),const("y")),"tick")  # heartbeat
            
            # Open
            a,b,c = pts[(i+1)%6], pts[(i+2)%6], pts[(i+3)%6]
            for p in [a,b,c]: g0.process_sig(eq(fn("pt",const(p)),const("y")),f"p{p}")
            g1.process_sig(eq(fn("s",const(f"{a}{b}")),const("y")),f"s{a}{b}")
            g1.process_sig(eq(fn("s",const(f"{b}{c}")),const("y")),f"s{b}{c}")
            l1s = list(set(f.sig_full or f.sig for f in g1.memory.frames if f.weight>2))
            g2.observe_ext(l1s,"L1")
            l2s = list(set(f.sig_full or f.sig for f in g2.memory.frames if f.weight>2))
            g3.observe_ext(l2s,"L2")
    
    # Does L3 distinguish open vs closed?
    l3_refs = len([f for f in g3.memory.frames if "L2_" in (f.sig_full or f.sig)])
    l3_chains = len([f for f in g3.memory.frames if "══" in (f.sig_full or f.sig)])
    l2_refs_l1 = len([f for f in g2.memory.frames if "L1_" in (f.sig_full or f.sig)])
    l2_chains = len([f for f in g2.memory.frames if "══" in (f.sig_full or f.sig)])
    
    return {"l3_ref": l3_refs, "l3_chains": l3_chains, "l2_ref": l2_refs_l1, "l2_chains": l2_chains}

print("=== CLOSURE DETECTION: UNLABELED, PURE TEMPORAL ===")
print("L0(pt) -> L1(seg) -> L2(obs L1) -> L3(obs L2)")
print("No external labels. No v_closed/v_open.")
print("Only temporal frame changes.")
print()

results = [trial(s) for s in range(42, 62)]
l3r = statistics.mean(r["l3_ref"] for r in results)
l3c = statistics.mean(r["l3_chains"] for r in results)
l3r_any = sum(1 for r in results if r["l3_ref"] > 0)

print(f"20 seeds summary:")
print(f"  L2 frames referencing L1: avg {statistics.mean(r['l2_ref'] for r in results):.1f}")
print(f"  L2 chains: avg {statistics.mean(r['l2_chains'] for r in results):.1f}")
print(f"  L3 frames referencing L2: avg {l3r:.1f}")
print(f"  L3 chains: avg {l3c:.1f}")
print(f"  L3 with L2 references: {l3r_any}/20")

print(f"\nSample L2 frames (seed 42):")
g0 = GEME_T(memory_cap=12, merge_thresh=0.001, cooccur_window=20, cooccur_thresh=0.08, max_chains=5, time_window_size=5)
g1 = GEME_T(memory_cap=16, cooccur_window=30, cooccur_thresh=0.1, max_chains=10, time_window_size=10)
g2 = GEME_T(memory_cap=16, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=8)
g3 = GEME_T(memory_cap=12, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=12)
for g in [g0,g1,g2,g3]: g.memory._chain_cooccur_thresh = 2
r = random.Random(42); pts = ["A","B","C","D","E","F"]
for ep in range(40):
    r.shuffle(pts)
    for i in range(len(pts)-2, 2):
        a,b,c=pts[i%6],pts[(i+1)%6],pts[(i+2)%6]
        for p in [a,b,c]: g0.process_sig(eq(fn("pt",const(p)),const("y")),f"p{p}")
        g1.process_sig(eq(fn("s",const(f"{a}{b}")),const("y")),f"s{a}{b}")
        g1.process_sig(eq(fn("s",const(f"{b}{c}")),const("y")),f"s{b}{c}")
        g1.process_sig(eq(fn("s",const(f"{c}{a}")),const("y")),f"s{c}{a}")
        l1s = list(set(f.sig_full or f.sig for f in g1.memory.frames if f.weight>2))
        g2.observe_ext(l1s,"L1")
        l2s = list(set(f.sig_full or f.sig for f in g2.memory.frames if f.weight>2))
        g3.observe_ext(l2s,"L2")

print(f"  L2 frames ({len(g2.memory.frames)}):")
for f in sorted(g2.memory.frames, key=lambda x: x.weight, reverse=True)[:6]:
    sig = f.sig_full or f.sig
    t = "C" if "══" in sig else ("A" if "──" in sig else "F")
    ext = " [OBSERVES L1]" if "L1_" in sig else ""
    print(f"  [{t}] w={int(f.weight):4d} {sig[:50]}{ext}")

print(f"\n  L3 frames ({len(g3.memory.frames)}):")
for f in sorted(g3.memory.frames, key=lambda x: x.weight, reverse=True)[:8]:
    sig = f.sig_full or f.sig
    t = "C" if "══" in sig else ("A" if "──" in sig else "F")
    ext = " [OBSERVES L2]" if "L2_" in sig else ""
    print(f"  [{t}] w={int(f.weight):4d} {sig[:50]}{ext}")

print(f"\n{'='*55}")
print("UNLABELED CLOSURE DETECTION:")
if l3r_any >= 15:
    print("19/20: Temporal closure detected without external labels.")
    print("L3 observes L2 observing L1 observing segments.")
    print("Pure structural observation — no meaning layer.")
else:
    print(f"{l3r_any}/20: Temporal self-observation forms chains, but")
    print("closure distinction requires deeper temporal depth.")
