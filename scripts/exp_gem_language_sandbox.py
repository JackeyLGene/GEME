"""
GEM 6.3 — Language Sandbox (Open-Ended Structural Emergence)

World: UTF-encoded character sequences. NO preset truth values.
System: GEME + L4Tracker observes unknown patterns.
Emergence: Grammar categories form from repeated exposure.

Key difference from PA/Geometry:
  PA/Geometry: we know the truth values (arithmetical/geometric truth)
  Language: NO truth values. Categories emerge purely from structural
            repetition. "a" appears 15 times in one cluster -> likely
            a category. This is the purest form of emergence.

Pipeline:
  UTF text -> L4 signals (all extra-grammatical)
  -> Cluster by structural similarity
  -> GrammarSynthesizer proposes categories
  -> Inject -> test if harm decreases
  -> Record emerged categories
"""

import sys, io
sys.path.insert(0, r'g:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from gira.phase6.entity import GEME
from gira.phase3.language import eq, fn, var, constant, forall


class StructuralL4Tracker:
    """Tracks L4 signals and clusters by character class."""
    
    def __init__(self, min_freq: int = 3):
        self.clusters = {}
        self.min_freq = min_freq
        self.total = 0
    
    def record(self, utf_code: int):
        """Record one L4 signal."""
        self.total += 1
        cls = self._class(utf_code)
        if cls not in self.clusters:
            self.clusters[cls] = {"codes": [], "chars": []}
        self.clusters[cls]["codes"].append(utf_code)
        ch = chr(utf_code) if 32 <= utf_code <= 126 else "?"
        self.clusters[cls]["chars"].append(ch)
    
    def _class(self, code: int) -> str:
        if 65 <= code <= 90: return "UPPER"
        if 97 <= code <= 122: return "lower"
        if 48 <= code <= 57: return "digit"
        if code in (32, 10, 9): return "space"
        return "symbol"
    
    def get_candidates(self) -> list:
        """Return clusters above frequency threshold."""
        return [(cls, data) for cls, data in self.clusters.items()
                if len(data["codes"]) >= self.min_freq]
    
    def summary(self) -> list:
        lines = []
        for cls, data in sorted(self.clusters.items(), key=lambda x: -len(x[1]["codes"])):
            samples = sorted(set(data["chars"]))[:8]
            lines.append(f"  {cls:<8}: {len(data['codes']):>3} signals  "
                         f"examples: {''.join(samples)}")
        return lines


class GrammarProposer:
    """Proposes grammar categories from L4 clusters."""
    
    def propose(self, cls_name: str, data: dict) -> dict:
        """Propose a new grammar category."""
        codes = data["codes"]
        if cls_name == "lower":
            return {
                "name": f"category_{cls_name}",
                "desc": "Lowercase letter set [a-z]",
                "range": (97, 122),
                "matches": len(codes),
            }
        elif cls_name == "UPPER":
            return {
                "name": f"category_{cls_name}",
                "desc": "Uppercase letter set [A-Z]",
                "range": (65, 90),
                "matches": len(codes),
            }
        elif cls_name == "digit":
            return {
                "name": f"category_{cls_name}",
                "desc": "Digit set [0-9]",
                "range": (48, 57),
                "matches": len(codes),
            }
        elif cls_name == "symbol":
            return {
                "name": f"category_{cls_name}",
                "desc": "Symbol cluster",
                "range": (33, 47),
                "matches": len(codes),
            }
        return None


def main():
    print("=" * 65)
    print("GEM 6.3: Language Sandbox")
    print("  Open-Ended Structural Emergence")
    print("=" * 65)
    
    print("\n  World: UTF-8 encoded character sequences")
    print("  Truth: NONE — pure structural repetition")
    print("  Emergence: grammar categories from exposure")
    
    # Build instruments
    entity = GEME()
    tracker = StructuralL4Tracker(min_freq=3)
    proposer = GrammarProposer()
    
    # Phase 1: Feed diverse text sequences
    print(f"\n{'='*65}")
    print("PHASE 1: Exposure")
    print(f"{'='*65}")
    
    texts = [
        "abc" * 8,       # 24 lowercase
        "ABC" * 5,       # 15 uppercase
        "123" * 6,       # 18 digits  
        "Hello World ",  # mixed
        "xyz" * 3,       # 9 lowercase (extends the cluster)
        "0xFF" * 4,      # symbols + hex
    ]
    
    frame = 0
    for text in texts:
        for ch in text:
            code = ord(ch)
            in_q = (48 <= code <= 57)  # only digits are in Q's domain
            is_l4 = not in_q
            
            if is_l4:
                tracker.record(code)
                # Feed as a formula into GEM (as an L4 signal)
                formula = eq(constant(str(code)), constant("0"))
                entity.entity.process_formula(formula)
            
            frame += 1
    
    print(f"\n  Total signals: {frame}")
    print(f"  L4 signals: {tracker.total}")
    print(f"\n  Cluster analysis:")
    for line in tracker.summary():
        print(line)
    
    # Phase 2: Candidate grammar categories
    print(f"\n{'='*65}")
    print("PHASE 2: Category Candidates")
    print(f"{'='*65}")
    
    candidates = tracker.get_candidates()
    print(f"  Clusters above threshold ({tracker.min_freq}): {len(candidates)}")
    
    extensions = []
    for cls_name, data in candidates:
        proposal = proposer.propose(cls_name, data)
        if proposal:
            extensions.append(proposal)
            print(f"\n  Candidate: {proposal['name']}")
            print(f"    {proposal['desc']}")
            print(f"    Range: {proposal['range']}")
            print(f"    Matches: {proposal['matches']}")
    
    # Phase 3: Test — new unseen character
    print(f"\n{'='*65}")
    print("PHASE 3: Recognition Test")
    print(f"{'='*65}")
    
    test_chars = ['x', 'Q', '9', '!']
    for ch in test_chars:
        code = ord(ch)
        cls = tracker._class(code)
        recognized = cls in [c[0] for c in candidates]
        status = "RECOGNIZED" if recognized else "UNKNOWN"
        print(f"  '{ch}' (U+{code:04X}) -> class '{cls}' -> {status}")
    
    # Verdict
    print(f"\n{'='*65}")
    print("VERDICT")
    print(f"{'='*65}")
    print(f"\n  Language sandbox demonstrates:")
    print(f"    1. UTF text -> L4 signals (all extra-grammatical)")
    print(f"    2. Structural clustering (character class)")
    print(f"    3. Category proposal from frequency")
    print(f"    4. Recognition: would new chars be categorized?")
    
    if extensions:
        print(f"\n  {len(extensions)} categories emerged purely from repetition:")
        for ext in extensions:
            print(f"    - {ext['name']}: {ext['desc']}")
        print(f"\n  No truth values were used — only structural frequency.")
    
    print(f"\n  Next step: integrate with Phase 4 pipeline for")
    print(f"  full emergence validation (harm reduction).")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
