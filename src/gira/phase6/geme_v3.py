"""
GEME V3 — Wittgenstein Table as primary encoding. No GN.

  x = object coordinate  (W-table projection of formula symbols)
  y = self coordinate    (W-table projection of formula's OWN signature)
  Stress = |y - x|       (gap: what it is vs how it classifies itself)

  Transition: accumulated gap > threshold → system expands
"""
from __future__ import annotations
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict

from gira.phase3.entity import QEntity
from gira.phase3.language import Formula
from gira.phase4.pattern_tracker import compute_signature, PatternTracker
from gira.phase4.pattern_analyzer import PatternAnalyzer
from gira.phase4.induction_synthesizer import InductionSynthesizer, InductionRule


# ============================================================
# Wittgenstein Table — symbol coordinate assignment
# ============================================================

# Each PA symbol gets a (0,1) coordinate based on its information role
# Numbers: near 0 (ground)
# Operators: near 0.3-0.4
# Relations: near 0.6
# Quantifiers: near 0.7-0.8
# Variables: near 0.9-1.0

def _symbol_coord(sym: str) -> float:
    """W-table coordinate for a PA symbol."""
    if sym.isdigit():
        return 0.05 + (int(sym) % 10) * 0.005
    mapping = {
        "s": 0.15, "+": 0.30, "\u00d7": 0.35,
        "=": 0.60, "forall": 0.75, "exists": 0.72,
        "x": 0.90, "y": 0.93, "z": 0.96,
    }
    return mapping.get(sym, 0.50)


def _leaf_coords(formula) -> List[float]:
    """Extract W-table coordinates from all leaf nodes in formula tree."""
    coords = []
    def walk(node):
        if node is None: return
        k = getattr(node, 'kind', '')
        s = getattr(node, 'symbol', '')
        v = getattr(node, 'value', None)
        if k == "variable":
            coords.append(_symbol_coord(s))
        elif k == "constant":
            coords.append(_symbol_coord(str(v)))
        elif k == "numeral":
            coords.append(_symbol_coord(str(v)[:6]))  # truncated
        elif k == "function":
            coords.append(_symbol_coord(s))
        for a in getattr(node, 'args', []): walk(a)
        if getattr(node, 'left', None): walk(node.left)
        if getattr(node, 'right', None): walk(node.right)
    walk(formula)
    return coords if coords else [0.50]


def object_coord(formula) -> float:
    """x = mean W-table coordinate of formula's symbol leaves."""
    cs = _leaf_coords(formula)
    return sum(cs) / len(cs)


def signature_coord(signature: str) -> float:
    """y = W-table coordinate of formula's structural signature.
    
    The signature describes WHAT the formula IS, structurally.
    This is the "self" coordinate — the formula classified itself.
    The gap between x and y is the self-reference tension.
    """
    # Signature components map to W-table regions
    parts = signature.split("_")
    coords = []
    for p in parts:
        if "equation" in p or "forall" in p or "exists" in p:
            coords.append(0.60)  # relational/binding
        elif "add" in p or "mul" in p or "swap" in p or "comm" in p:
            coords.append(0.35)  # structural operator
        else:
            coords.append(0.50)
    return sum(coords) / len(coords) if coords else 0.50


@dataclass
class Frame2D:
    frame: int
    x: float
    y: float
    gap: float
    cumulative: float


class GEME_V3:
    """W-table based 2D GEM instrument."""
    
    def __init__(self, axioms=None, gap_threshold=0.25, decay=0.95):
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
        
        self._cumulative = 0.0
        self._decay = decay
        self._threshold = gap_threshold
        self.frame_count = 0
        self.system_level = 0
        
        self._sig_freq: Dict[str, int] = defaultdict(int)
        self._symbol_count: Dict[str, int] = defaultdict(int)
        self._concrete_samples: Dict[str, List[Formula]] = defaultdict(list)
        self._max_samples = 5
    
    def process(self, formula) -> dict:
        self.frame_count += 1
        old_level = self.system_level
        
        sig = compute_signature(formula)
        self._sig_freq[sig] += 1
        n = self._sig_freq[sig]
        if n <= self._max_samples:
            self._concrete_samples[sig].append(formula)
        
        for ch in str(formula):
            self._symbol_count[ch] = self._symbol_count.get(ch, 0) + 1
        
        # 2D coordinates
        x = object_coord(formula)
        y = signature_coord(sig)
        gap = abs(y - x)
        
        self._cumulative = self._decay * self._cumulative + (1 - self._decay) * gap
        
        S_F, reason = self.entity.inference.harm_operator.classifier.classify(
            formula, self.entity.inference.axioms, self.entity.inference.theorems)
        
        # Transition
        if self._cumulative > self._threshold:
            cd = self.frame_count - getattr(self, '_last_transition', 0)
            if cd >= 20:
                self._transition()
        
        return {
            "frame": self.frame_count,
            "sig": sig, "x": x, "y": y, "gap": gap,
            "cumul": self._cumulative,
            "S_F": S_F, "L_E": self.system_level,
        }
    
    def _transition(self):
        self.system_level += 1
        self._cumulative = 0.0
        self._last_transition = self.frame_count
        
        patterns = self.analyzer.analyze(self.tracker)
        if not patterns and self._sig_freq:
            patterns = self.analyzer.analyze_frequency_data(
                dict(self._sig_freq),
                dict(self._concrete_samples),
            )
        
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
        S_F, reason = self.entity.inference.harm_operator.classifier.classify(
            formula, self.entity.inference.axioms, self.entity.inference.theorems)
        harm = 1.0 if S_F > self.system_level else 0.0
        return S_F, harm, reason
    
    @property
    def stress(self):
        return self._cumulative
