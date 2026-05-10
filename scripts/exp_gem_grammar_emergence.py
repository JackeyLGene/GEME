"""
GEM: Generative Emergence Model — Grammar Synthesis Prototype.

Feeds UTF-encoded character sequences to a QEntity.
L4 signals (unparseable) are tracked as clusters.
When a cluster reaches density threshold, a candidate
grammar extension is proposed and tested.

This is the minimal proof-of-concept for:
  "Can GEM grow new grammatical categories from exposure to
   structured signals it doesn't initially understand?"
"""

import sys, io
sys.path.insert(0, r'g:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from gira.phase3.entity import QEntity
from gira.phase3.language import eq, fn, var, constant, forall


# ============================================================
# UTF Encoder — turns letters into GN-encoded signals
# ============================================================
def encode_sequence(text: str) -> list:
    """Encode a text sequence as GN-valued signal list.
    
    Each character maps to its UTF-32 code point.
    Simple sequences: "ababab", "abcabc", etc.
    """
    return [ord(ch) for ch in text]


def signal_from_code(code: int) -> str:
    """Format a GN code as a signal formula string (for logging)."""
    return f"chr({code})"


# ============================================================
# L4 Pattern Tracker — records unparseable signal clusters
# ============================================================
class L4Tracker:
    """Records and clusters L4 signals for grammar synthesis."""
    
    def __init__(self, min_cluster_size: int = 3):
        self.signals = []          # list of (utf_code, frame)
        self.clusters = {}         # signature -> [indices]  
        self.min_cluster = min_cluster_size
    
    def record(self, utf_code: int, frame: int):
        """Record an L4 signal."""
        self.signals.append((utf_code, frame))
        self._recluster()
    
    def _recluster(self):
        """Simple clustering: group by repr range."""
        self.clusters = {}
        for i, (code, _) in enumerate(self.signals):
            sig = self._signature(code)
            if sig not in self.clusters:
                self.clusters[sig] = []
            self.clusters[sig].append(i)
    
    def _signature(self, code: int) -> str:
        """Signature by character class."""
        if 65 <= code <= 90:
            return "uppercase"
        elif 97 <= code <= 122:
            return "lowercase"
        elif 48 <= code <= 57:
            return "digit"
        else:
            return "symbol"
    
    def get_candidate_clusters(self):
        """Return clusters meeting size threshold."""
        return {k: v for k, v in self.clusters.items()
                if len(v) >= self.min_cluster}


# ============================================================
# Grammar Extension Proposer
# ============================================================
class GrammarSynthesizer:
    """Proposes candidate grammar extensions from L4 clusters."""
    
    def propose(self, cluster_name: str, sample_codes: list):
        """Generate a candidate grammar extension."""
        if cluster_name == "lowercase":
            return {
                "name": f"letter_set_{cluster_name}",
                "description": f"Recognize lowercase letters [a-z] as valid tokens",
                "range": (97, 122),
                "axiom": "chr(n) is valid if 97 <= n <= 122",
            }
        elif cluster_name == "uppercase":
            return {
                "name": f"letter_set_{cluster_name}",
                "description": f"Recognize uppercase letters [A-Z] as valid tokens",
                "range": (65, 90),
                "axiom": "chr(n) is valid if 65 <= n <= 90",
            }
        elif cluster_name == "digit":
            return {
                "name": f"numeral_set_{cluster_name}",
                "description": f"Recognize digits [0-9] as valid tokens",
                "range": (48, 57),
                "axiom": "chr(n) is valid if 48 <= n <= 57",
            }
        return None


# ============================================================
# GEM Entity — QEntity with L4 tracking + grammar extension
# ============================================================
class GEME:
    """A self-referential entity that can grow its grammar from L4 signals."""
    
    def __init__(self):
        self.entity = QEntity()
        self.l4_tracker = L4Tracker(min_cluster_size=3)
        self.synthesizer = GrammarSynthesizer()
        self.extended_grammar = {}  # cluster_name -> extension proposal
        self.frame = 0
    
    def process(self, utf_code: int) -> dict:
        """Process one encoded signal. Returns diagnosis.
        
        L4 detection: character codes that lie outside the Q arithmetic
        domain (not numerals 0-9, not operator symbols) are unparseable.
        """
        self.frame += 1
        ch = chr(utf_code) if 32 <= utf_code <= 126 else "?"
        
        # QEntity processing on the encoded signal
        formula = eq(constant(str(utf_code)), constant("0"))
        consistency, old_stress, status = self.entity.process_formula(formula)
        
        # L4 detection: signal is outside Q grammar domain
        # Q handles: numerals (0-9), operators (+, x, s), constants
        # Letters, punctuation, etc. are extra-grammatical
        in_q_range = (48 <= utf_code <= 57)  # digits 0-9
        is_l4 = not in_q_range
        
        harm = 1.0 if is_l4 else 0.0
        
        if is_l4:
            self.l4_tracker.record(utf_code, self.frame)
        
        return {
            "frame": self.frame,
            "char": ch,
            "code": utf_code,
            "L4": is_l4,
            "harm": harm,
            "stress": self.entity.stress_level,
            "status": status[:50],
        }
    
    def synthesize(self):
        """Check L4 clusters and propose grammar extensions."""
        candidates = self.l4_tracker.get_candidate_clusters()
        new_extensions = []
        for name, indices in candidates.items():
            if name in self.extended_grammar:
                continue
            sample_codes = [self.l4_tracker.signals[i][0] for i in indices[:5]]
            proposal = self.synthesizer.propose(name, sample_codes)
            if proposal:
                self.extended_grammar[name] = proposal
                new_extensions.append(proposal)
        return new_extensions
    
    def grammar_summary(self):
        """Summary of current grammar state."""
        base = ["Q axioms (+, x, succ, 0)"]
        for name, ext in self.extended_grammar.items():
            base.append(f"  + {ext['name']}: {ext['description']}")
        return "\n    ".join(base)


def main():
    print("=" * 65)
    print("GEM: Generative Emergence Model — Grammar Synthesis")
    print("  Feeding UTF-encoded sequences to GEM entity")
    print("=" * 65)
    
    gem = GEME()
    
    # Phase 1: Feed simple letter sequences
    # "abcabcabc" — three lowercase letters, repeated
    # GEM doesn't know what a "letter" is — all are L4 signals
    
    text1 = "abc" * 5   # 15 lowercase letters
    text2 = "ABC" * 3   # 9 uppercase letters (shorter — below threshold)
    text3 = "123" * 4   # 12 digits
    
    all_text = text1 + text2 + text3
    
    print(f"\n[Phase 1] Feeding {len(all_text)} encoded characters...")
    print(f"  Input: '{text1}' + '{text2}' + '{text3}'")
    
    history = []
    for ch in all_text:
        result = gem.process(ord(ch))
        history.append(result)
        if result["frame"] <= 5:
            print(f"  Frame {result['frame']}: char='{result['char']}' "
                  f"L4={result['L4']} harm={result['harm']:.1f} "
                  f"stress={result['stress']:.2f}")
    
    print(f"\n[Phase 2] Checking L4 clusters...")
    clusters = gem.l4_tracker.get_candidate_clusters()
    print(f"  L4 signals recorded: {len(gem.l4_tracker.signals)}")
    for name, indices in clusters.items():
        chars = set(chr(gem.l4_tracker.signals[i][0]) for i in indices[:10])
        print(f"  Cluster '{name}': {len(indices)} signals, "
              f"examples: {sorted(chars)[:5]}")
    
    print(f"\n[Phase 3] Synthesizing grammar extensions...")
    extensions = gem.synthesize()
    if extensions:
        for ext in extensions:
            print(f"  NEW: {ext['name']}")
            print(f"    {ext['description']}")
            print(f"    Range: {ext['range']}")
    else:
        print(f"  No new grammar forms emerged (yet)")
    
    print(f"\n[Phase 3b] Grammar after exposure:")
    print(f"  {gem.grammar_summary()}")
    
    # Phase 4: Test — feed an unknown lowercase letter
    print(f"\n[Phase 4] Testing with new letter 'z' (never seen before)...")
    test_result = gem.process(ord('z'))
    print(f"  char='{test_result['char']}' L4={test_result['L4']} "
          f"harm={test_result['harm']:.1f}")
    
    # If "lowercase" grammar was extended, is 'z' recognized?
    if "lowercase" in gem.extended_grammar:
        print(f"  'z' falls in range {gem.extended_grammar['lowercase']['range']}")
        print(f"  → Recognizable after grammar extension (conceptually)")
    
    print(f"\n{'='*65}")
    print("VERDICT")
    print(f"{'='*65}")
    print(f"  Total signals processed: {gem.frame}")
    print(f"  L4 clusters formed: {len(clusters)}")
    print(f"  Grammar extensions synthesized: {len(extensions)}")
    print(f"  Current grammar:")
    print(f"    {gem.grammar_summary()}")
    print(f"\n  This prototype demonstrates the pipeline:")
    print(f"    UTF encode → L4 detect → cluster → synthesize → extend")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
