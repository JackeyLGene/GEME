"""
GEME V5 — Irreducible residual stress (Cantor Gap dynamics).

  v = W-table vector (fixed-dim, symbol frequencies)
  v_pred = Bayesian mean from memory
  gap = |v - v_pred|

  The gap NEVER converges to 0 for structured formulas,
  because the fixed-dimension space cannot capture
  infinite structural variety.

  stress = cumulative(gap × freq_weight)
  transition when stress > threshold → capacity expansion → residual shrinks but reappears.
"""
from __future__ import annotations
from typing import List, Dict, Tuple
from collections import defaultdict, deque
import math

from gira.phase3.entity import QEntity
from gira.phase3.language import Formula
from gira.phase4.pattern_tracker import compute_signature, PatternTracker
from gira.phase4.pattern_analyzer import PatternAnalyzer
from gira.phase4.induction_synthesizer import InductionSynthesizer, InductionRule


# ============================================================
# W-table: each symbol has its own (0,1) coordinate
# ============================================================

# ============================================================
# W-table: fixed symbol alphabet → fixed-dimension vector
# ============================================================

_ALPHABET = [
    "0", "1", "s", "+", "\u00d7", "=", "forall", "exists",
    "x", "y", "z",
]
_VEC_DIM = len(_ALPHABET)

def symbol_vector(formula) -> Tuple[float, ...]:
    """Map formula to W-table: count per symbol / total leaf count, [0,1]."""
    counts = {s: 0.0 for s in _ALPHABET}
    total = 0
    def walk(node):
        nonlocal total
        if node is None: return
        k = getattr(node, 'kind', '')
        s = getattr(node, 'symbol', '')
        if k == "constant":
            v = str(getattr(node, 'value', ''))
            if v in counts: counts[v] += 1
            total += 1
        elif k == "numeral":
            counts["1"] += 1; total += 1
        elif k == "function":
            _s = s if s in counts else "\u00d7" if s == "\u00d7" else None
            if _s in counts: counts[_s] += 1
            total += 1
        elif k == "variable":
            if s in counts: counts[s] += 1
            total += 1
        elif k == "forall": counts["forall"] += 1; total += 1
        elif k == "exists": counts["exists"] += 1; total += 1
        if s == "=": counts["="] += 1; total += 1
        for a in getattr(node, 'args', []): walk(a)
        if getattr(node, 'left', None): walk(node.left)
        if getattr(node, 'right', None): walk(node.right)
    walk(formula)
    if total == 0: total = 1
    return tuple(counts[s] / total for s in _ALPHABET)


def vector_dist(a, b):
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


# ============================================================
# History model: Bayesian from sliding window
# ============================================================

# ============================================================
# GEME V5 — Cantor Gap dynamics
# ============================================================

class GEME:
    """Vector prediction gap → stress → transition."""
    
    def __init__(self, axioms=None, stress_threshold=3.0, window=15):
        if axioms is None:
            from gira.phase3.q_axioms import robinson_q
            axioms = robinson_q()
        self.entity = QEntity()
        self.entity.inference.axioms = axioms.copy()
        for a in axioms:
            if a not in self.entity.inference.theorems:
                self.entity.inference.theorems.append(a)
        
        self.tracker = PatternTracker()
        self.analyzer = PatternAnalyzer(min_frequency=3)
        self.synthesizer = InductionSynthesizer()
        self.extracted_rules: List[InductionRule] = []
        self._rule_names: set = set()
        self._max_rules = 10
        
        # Irreducible residual stress
        self._history = deque(maxlen=window)
        self._stress = 0.0
        self._threshold = stress_threshold
        self.frame_count = 0
        self.system_level = 0
        
        self._sig_freq: Dict[str, int] = defaultdict(int)
        self._concrete_samples: Dict[str, List[Formula]] = defaultdict(list)
        self._max_samples = 5
    
    def process(self, formula) -> dict:
        self.frame_count += 1
        
        S_F, reason = self.entity.inference.harm_operator.classifier.classify(
            formula, self.entity.inference.axioms, self.entity.inference.theorems)
        
        sig = compute_signature(formula)
        self._sig_freq[sig] += 1
        if self._sig_freq[sig] <= self._max_samples:
            self._concrete_samples[sig].append(formula)
        
        # ── Vector encoding ──
        v = symbol_vector(formula)
        
        # ── Bayesian prediction ──
        if len(self._history) == 0:
            v_pred = tuple(0.0 for _ in range(_VEC_DIM))
        else:
            ws = len(self._history)
            avg = [0.0] * _VEC_DIM
            for vec in self._history:
                for i, vi in enumerate(vec):
                    avg[i] += vi
            v_pred = tuple(a / ws for a in avg)
        
        # ── Irreducible gap ──
        gap = vector_dist(v, v_pred)
        
        # ── Observe ──
        self._history.append(v)
        
        # ── Irreducible residual stress ──
        # gap NEVER converges to 0: fixed-dim space cannot capture
        # infinite structural variety. δ = gap → irreducible.
        freq = self._sig_freq[sig]
        pressure = gap * min(1.0, freq / 10.0)
        self._stress += pressure
        
        # ── Transition ──
        if self._stress > self._threshold:
            cd = self.frame_count - getattr(self, '_last_trans', 0)
            if cd >= 20:
                self._transition()
        
        return {
            "frame": self.frame_count,
            "v": [round(vi, 3) for vi in v],
            "gap": round(gap, 4),
            "freq": freq,
            "pressure": round(pressure, 4),
            "stress": round(self._stress, 4),
            "S_F": S_F, "L_E": self.system_level,
            "sig": sig,
        }
    
    def _transition(self):
        old = self.system_level
        self.system_level += 1
        self._stress = 0.0
        self._last_trans = self.frame_count
        
        patterns = self.analyzer.analyze(self.tracker)
        if not patterns and self._sig_freq:
            patterns = self.analyzer.analyze_frequency_data(
                dict(self._sig_freq), dict(self._concrete_samples))
        
        if patterns:
            rules = self.synthesizer.synthesize_multiple(patterns)
            clf = self.entity.inference.harm_operator.classifier
            for rule in rules:
                rn = rule.name()
                if rn in self._rule_names: continue
                if len(self.extracted_rules) >= self._max_rules: break
                clf._rules.append(rule)
                self._rule_names.add(rn)
                self.extracted_rules.append(rule)
        self.tracker.clear()
    
    def evaluate(self, formula):
        S_F, _ = self.entity.inference.harm_operator.classifier.classify(
            formula, self.entity.inference.axioms, self.entity.inference.theorems)
        return S_F
