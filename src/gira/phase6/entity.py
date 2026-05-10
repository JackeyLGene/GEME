"""
GEME — the core observation instrument.

Stress is a VECTOR: (external, internal).
  external: L(F) > L(S) — "I don't understand this signal"
  internal: frequency/memory — "this pattern is inefficient"

Diagonalization happens EVERY FRAME — not conditionally.
Every formula has a self-reference degree ∈ [0,1].
Stress is the OUTPUT of diagonalization, not a condition for it.
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field
from collections import defaultdict

from gira.phase3.entity import QEntity
from gira.phase3.language import Formula
from gira.phase4.pattern_tracker import PatternTracker, compute_signature
from gira.phase4.pattern_analyzer import PatternAnalyzer
from gira.phase4.induction_synthesizer import InductionSynthesizer, InductionRule


@dataclass
class BoundaryRecord:
    """Record of a formula that triggered boundary (L3+)."""
    frame: int
    formula: Formula
    formula_str: str
    signature: str
    level: int
    reason: str


@dataclass
class EmergenceRecord:
    """Record of a formula that crossed the boundary (L3 -> L2-)."""
    frame: int
    formula_str: str
    old_level: int
    new_level: int


@dataclass
class StressVector:
    """Two-component stress: external and internal."""
    external: float = 0.0
    internal: float = 0.0
    
    def combined(self) -> float:
        return max(self.external, self.internal)
    
    def __str__(self):
        return f"E={self.external:.3f} I={self.internal:.3f}"


class GEME:
    """Core GEM instrument — formal system + observation layers.
    
    Each frame:
      1. classify formula → S(F) (signal level)
      2. diagonalize → self-reference degree
      3. compute external harm: S(F) > L(E)
      4. compute internal harm: 1 - 1/(1 + freq[signature])
      5. update (ext_stress, int_stress)
      6. if combined > threshold → transition + rule synthesis
      7. record emergence
    """
    
    def __init__(self, axioms: List[Formula] = None,
                 stress_threshold: float = 0.65,
                 min_frequency: int = 3):
        if axioms is None:
            from gira.phase3.q_axioms import robinson_q
            axioms = robinson_q()
        
        self.entity = QEntity()
        self.entity.inference.axioms = axioms.copy()
        for a in axioms:
            if a not in self.entity.inference.theorems:
                self.entity.inference.theorems.append(a)
        
        self.tracker = PatternTracker()
        self.analyzer = PatternAnalyzer(min_frequency=min_frequency)
        self.synthesizer = InductionSynthesizer()
        
        self.boundary_history: List[BoundaryRecord] = []
        self.emergence_history: List[EmergenceRecord] = []
        self.extracted_rules: List[InductionRule] = []
        self._rule_names: set = set()
        self._max_rules = 10
        
        # Frequency tracking for internal harm
        self._signature_freq: Dict[str, int] = defaultdict(int)
        # Concrete formula samples per signature (for real abstraction)
        self._concrete_samples: Dict[str, List[Formula]] = defaultdict(list)
        self._max_samples_per_sig = 5
        # Per-symbol usage tracking
        self._symbol_usage: Dict[str, int] = defaultdict(int)
        
        # Stress vector
        self._stress = StressVector()
        self._decay = 0.95
        self._alpha = 0.1
        
        self.entity.config["stress_threshold"] = stress_threshold
    
    @property
    def system_level(self) -> int:
        return self.entity.system_level
    
    @property
    def stress(self) -> float:
        return self._stress.combined()
    
    def stress_vector(self) -> Tuple[float, float]:
        return (self._stress.external, self._stress.internal)
    
    def process(self, formula: Formula) -> dict:
        """Feed one formula through the instrument.
        
        Per-frame pipeline:
          classify → diagonalize → harm → stress → transition check
        """
        old_level = self.system_level
        
        # ── 1. Classify (signal level) ──
        S_F, reason = self.entity.inference.harm_operator.classifier.classify(
            formula, self.entity.inference.axioms, self.entity.inference.theorems
        )
        
        # ── 2. Diagonalize: every frame, measure self-reference degree ──
        self_ref = self._diagonalize(formula, S_F)
        
        # ── 3. Compute signature and track frequency ──
        sig = compute_signature(formula)
        self._signature_freq[sig] += 1
        n = self._signature_freq[sig]
        # Store up to 5 concrete samples per signature for abstraction
        if n <= self._max_samples_per_sig:
            self._concrete_samples[sig].append(formula)
        
        # ── 4. Track symbol usage ──
        for ch in str(formula):
            if ch.isalpha() or ch in "+=∀∃×s":
                self._symbol_usage[ch] += 1
        
        # ── 5. Compute external and internal harm ──
        ext_harm = 1.0 if S_F > self.system_level else 0.0
        int_harm = 1.0 - (1.0 / (1.0 + n))
        combined = max(ext_harm, int_harm)
        
        # ── 6. Update stress vector ──
        self._stress.external = self._decay * self._stress.external + self._alpha * ext_harm
        self._stress.internal = self._decay * self._stress.internal + self._alpha * int_harm
        
        # ── 7. Update QEntity's stress (for transition mechanism) ──
        self.entity.stress_level = self._stress.combined()
        
        # ── 8. Record boundary ──
        is_boundary = S_F >= 3
        if is_boundary:
            self.tracker.record(formula, self.entity.frame_count, self.system_level)
            self.boundary_history.append(BoundaryRecord(
                frame=self.entity.frame_count,
                formula=formula,
                formula_str=str(formula)[:80],
                signature=sig,
                level=S_F,
                reason=reason,
            ))
        
        # ── 9. Update frame count ──
        self.entity.frame_count += 1
        
        # ── 10. Check transition: combined stress > threshold ──
        if combined > self.entity.config.get("stress_threshold", 0.65):
            cooldown = self.entity.frame_count - getattr(self.entity, '_last_transition_frame', 0)
            if cooldown >= self.entity.config.get("transition_cooldown", 50):
                self._execute_transition()
        
        # ── 11. Re-evaluate previous boundary formulas after transition ──
        if self.system_level > old_level:
            self._on_transition()
        
        return {
            "frame": self.entity.frame_count,
            "formula": str(formula)[:60],
            "S_F": S_F,
            "boundary": is_boundary,
            "system_level": self.system_level,
            "stress_ext": self._stress.external,
            "stress_int": self._stress.internal,
            "stress": combined,
            "self_ref": self_ref,
            "freq": n,
            "sig": sig,
            "reason": reason[:40],
        }
    
    def _diagonalize(self, formula: Formula, S_F: int) -> float:
        """Measure the self-reference degree of a formula. (Per-frame.)
        
        Diagonalization is NOT a conditional event.
        Every formula has some degree of self-reference:
          Ground:      0.0 (no reference)
          Eq ground:   0.1 (self-identity)
          Quantified:  0.3 (variable binding)
          V-quant over equation: 0.5 (partial self-map)
          Contains #:  0.8 (Godel numeral)
          S4 (Godel proposition): 1.0 (complete self-reference)
        """
        s = str(formula)
        if S_F == 4:
            return 1.0
        if "#" in s:
            return 0.8
        if "∀" in s or "∃" in s:
            return 0.5
        if formula.kind == "equation":
            return 0.1
        return 0.0
    
    def _execute_transition(self):
        """Execute a transition: L(E) += 1, reset stress, record."""
        self.entity.system_level += 1
        self.entity._last_transition_frame = self.entity.frame_count
        self._stress = StressVector()  # reset stress
        # Record transition
        if not hasattr(self.entity, 'transition_history'):
            self.entity.transition_history = []
        self.entity.transition_history.append(
            f"L{self.entity.system_level - 1}->L{self.entity.system_level}"
        )

    def _on_transition(self):
        """Handle system level increase — synthesize rules.
        
        Two paths:
          [A] L3+ patterns from PatternTracker (standard)
          [B] L1 frequency patterns from signature data (concrete→abstract)
        
        Path [B] is the key to concrete→∀ emergence:
          When all training is L1 ground instances, the tracker is empty
          but signature frequency has accumulated. Analyze frequency data
          directly to find compression candidates.
        """
        patterns = self.analyzer.analyze(self.tracker)
        
        # Fallback: if no L3 patterns, use L1 frequency data
        if not patterns and self._signature_freq:
            patterns = self.analyzer.analyze_frequency_data(
                dict(self._signature_freq),
                dict(self._concrete_samples),
            )
        
        if not patterns:
            return
        
        rules = self.synthesizer.synthesize_multiple(patterns)
        
        classifier = self.entity.inference.harm_operator.classifier
        for rule in rules:
            rname = rule.name()
            if rname in self._rule_names:
                continue
            if len(self.extracted_rules) >= self._max_rules:
                break
            
            classifier._rules.append(rule)
            self._rule_names.add(rname)
            self.extracted_rules.append(rule)
        
        self.tracker.clear()
    
    def evaluate(self, formula: Formula) -> Tuple[int, float, str]:
        """Evaluate a formula through the current system. Returns (S_F, harm, reason)."""
        S_F, reason = self.entity.inference.harm_operator.classifier.classify(
            formula, self.entity.inference.axioms, self.entity.inference.theorems
        )
        harm = 1.0 if S_F > self.system_level else 0.0
        return S_F, harm, reason
    
    def symbol_usage_report(self) -> Dict[str, int]:
        """Return aggregated symbol usage statistics."""
        return dict(self._symbol_usage)
    
    def signature_report(self) -> Dict[str, int]:
        """Return signature frequency statistics."""
        return dict(self._signature_freq)
    
    def summary(self) -> str:
        """Human-readable summary of current state."""
        lines = [
            f"GEME State:",
            f"  Level: L(E) = {self.system_level}",
            f"  Stress: E={self._stress.external:.3f} I={self._stress.internal:.3f}",
            f"  Boundary records: {len(self.boundary_history)}",
            f"  Extracted rules: {len(self.extracted_rules)}",
            f"  Top signautres: {len(self._signature_freq)} types",
        ]
        for sig, cnt in sorted(self._signature_freq.items(), key=lambda x: -x[1])[:3]:
            lines.append(f"    {sig}: {cnt}")
        for r in self.extracted_rules:
            tmpl = str(r.predicate_template)[:50] if r.predicate_template else "N/A"
            lines.append(f"    - {r.name()}: {tmpl}")
        return "\n".join(lines)
