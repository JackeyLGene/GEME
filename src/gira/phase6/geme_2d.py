"""
GEME 2D: two-dimensional stress via object vs self-reference coordinates.

  x = object coordinate  (Wittgenstein projection: signal density)
  y = self coordinate    (diagonalization projection: self-reference density)
  Stress = |y - x|       (dimension gap = breakthrough opportunity)

  Transition: |y - x| > threshold → system expands → new dimension.
"""
from __future__ import annotations
from typing import List, Dict
from dataclasses import dataclass, field
from collections import defaultdict

from gira.phase3.entity import QEntity
from gira.phase3.language import Formula, var, constant, eq, fn
from gira.phase4.pattern_tracker import compute_signature, PatternTracker
from gira.phase4.pattern_analyzer import PatternAnalyzer
from gira.phase4.induction_synthesizer import InductionSynthesizer, InductionRule


@dataclass
class Frame:
    """One GEME 2D frame."""
    frame: int
    formula_str: str
    x: float      # object coordinate
    y: float      # self-reference coordinate
    stress: float  # |y - x|
    cumulative: float


class GEME_2D:
    """GEM with 2D stress: object vs self-reference coordinate gap.
    
    x = normalized formula tree density (object space)
    y = same after diagonalization overlay (self-reference space)
    Stress = |y - x| per frame
    Cumulative stress with decay → transition when > threshold
    """
    
    def __init__(self, axioms=None, stress_threshold=0.35, decay=0.95):
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
        
        # 2D stress state
        self._stress_cumulative = 0.0
        self._decay = decay
        self._threshold = stress_threshold
        self.frame_count = 0
        self.system_level = 0
        self.frames: List[Frame] = []
        
        # Frequency / symbol tracking
        self._signature_freq: Dict[str, int] = defaultdict(int)
        self._symbol_usage: Dict[str, int] = defaultdict(int)
    
    # ============================================================
    # Coordinate computation
    # ============================================================
    
    def _formula_vector(self, formula):
        """v(F) = structural density vector (6 components)."""
        n = [0]; l = [0]; vv = [0]; c = [0]; f = [0]; q = [0]; d = [0]
        def walk(node, dp):
            if node is None: return
            n[0] += 1; d[0] = max(d[0], dp)
            k = getattr(node, 'kind', '')
            if k == "variable": vv[0] += 1; l[0] += 1
            elif k in ("constant", "numeral"): c[0] += 1; l[0] += 1
            elif k == "function": f[0] += 1
            elif k in ("forall", "exists"): q[0] += 1
            for a in getattr(node, 'args', []): walk(a, dp+1)
            if getattr(node, 'left', None): walk(node.left, dp+1)
            if getattr(node, 'right', None): walk(node.right, dp+1)
        walk(formula, 0)
        nn = max(n[0], 1)
        return (l[0]/nn, vv[0]/nn, c[0]/nn, f[0]/nn, q[0]/nn, d[0]/nn)
    
    def _vector_norm(self, v):
        """Normalize vector to scalar coordinate."""
        return sum(v) / len(v)
    
    def _object_coord(self, formula):
        """x = object space coordinate."""
        return self._vector_norm(self._formula_vector(formula))
    
    def _self_coord(self, formula):
        """y = self-reference space coordinate.
        
        Diagonalization: add self-reference overlay to formula tree.
        For PA: add a sub-node encoding = formula's own GN bit-length.
        """
        v = self._formula_vector(formula)
        # Add self-reference component: proportional to GN bits
        bits = formula.gn().bit_length()
        # Self-reference offset: larger GN → more self-reference potential
        self_offset = bits / (bits + 500.0)  # smooth (0,1)
        # Blend original vector with self-reference offset
        base = self._vector_norm(v)
        y = base * 0.5 + self_offset * 0.5
        return y
    
    # ============================================================
    # Core pipeline
    # ============================================================
    
    def process(self, formula):
        """One frame: compute x, y, stress, check transition."""
        self.frame_count += 1
        old_level = self.system_level
        
        sig = compute_signature(formula)
        self._signature_freq[sig] += 1
        
        for ch in str(formula):
            if ch.isalpha() or ch in "+=∀∃×s":
                self._symbol_usage[ch] += 1
        
        # ── 2D coordinates ──
        x = self._object_coord(formula)
        y = self._self_coord(formula)
        stress = abs(y - x)
        
        # ── Cumulative stress ──
        self._stress_cumulative = (self._decay * self._stress_cumulative
                                   + (1 - self._decay) * stress)
        
        # ── Record frame ──
        f = Frame(self.frame_count, str(formula)[:50], x, y, stress, self._stress_cumulative)
        self.frames.append(f)
        
        # ── Transition check ──
        if self._stress_cumulative > self._threshold:
            cooldown = self.frame_count - getattr(self, '_last_transition_frame', 0)
            if cooldown >= 30:
                self._transition()
        
        # ── Evaluate through QEntity ──
        S_F, reason = self.entity.inference.harm_operator.classifier.classify(
            formula, self.entity.inference.axioms, self.entity.inference.theorems)
        
        return {
            "frame": self.frame_count,
            "x": x, "y": y, "stress": stress,
            "cumulative": self._stress_cumulative,
            "S_F": S_F, "sig": sig, "reason": reason[:40],
        }
    
    def _transition(self):
        """2D transition: expand capacity, synthesize rules."""
        self.system_level += 1
        self._stress_cumulative = 0.0
        self._last_transition_frame = self.frame_count
        
        patterns = self.analyzer.analyze(self.tracker)
        if not patterns and self._signature_freq:
            patterns = self.analyzer.analyze_frequency_data(
                dict(self._signature_freq))
        
        if patterns:
            rules = self.synthesizer.synthesize_multiple(patterns)
            classifier = self.entity.inference.harm_operator.classifier
            for rule in rules:
                rname = rule.name()
                if rname in self._rule_names: continue
                if len(self.extracted_rules) >= self._max_rules: break
                classifier._rules.append(rule)
                self._rule_names.add(rname)
                self.extracted_rules.append(rule)
        
        self.tracker.clear()
    
    def evaluate(self, formula):
        S_F, reason = self.entity.inference.harm_operator.classifier.classify(
            formula, self.entity.inference.axioms, self.entity.inference.theorems)
        harm = 1.0 if S_F > self.system_level else 0.0
        return S_F, harm, reason
