"""
Domain-Aware Unified L-Classification.

For ANY grammar domain, classification has the same structure:
  signal → [domain check] → [provability check] → [complexity check]

Unified L-scale (domain-relative):
  L(D)-0: EXTRA-DOMAIN   — signal domain not in system's grammar capacity
  L(D)-1: AXIOMATIC      — trivially true in the domain's axioms
  L(D)-2: DERIVABLE      — provable via inference within the domain
  L(D)-3: BOUNDARY       — expressible but undecidable in the domain
  L(D)-4: INCOMPLETENESS — fundamentally undecidable via Godel

Key difference from Phase 3 L0-L4:
  Phase 3 assumed ALL signals were in Q (arithmetic).
  GEM recognizes MULTIPLE domains, each with its own L-scale.
  The Wittgenstein Table assigns domain mapping BEFORE classification.
"""

from __future__ import annotations
from typing import Dict, Tuple, List
from dataclasses import dataclass

from gira.phase3.language import Formula
from gira.phase3.inference import SignalClassifier


@dataclass
class DomainLevel:
    """Classification result for one signal in one domain."""
    domain: str        # "arithmetic", "geometric", "raw"
    level: int         # 0-4 within this domain
    reason: str
    harm: float        # 0 or 1

    def __str__(self):
        return f"L({self.domain})-{self.level}: {self.reason}"


class DomainAwareClassifier:
    """Unified classifier that routes signals by domain before L-classification.
    
    Pipeline:
      signal → WittgensteinTable → domain
             → domain in grammar? → no → L0 (extra-domain)
             → yes → standard L1-L4 within domain
    """
    
    def __init__(self):
        self._classifiers: Dict[str, SignalClassifier] = {}
        self._grammar_domains = set()
    
    def add_domain(self, domain: str, classifier: SignalClassifier):
        """Register a grammar domain with its classifier."""
        self._classifiers[domain] = classifier
        self._grammar_domains.add(domain)
    
    def classify(self, formula: Formula, domain: str,
                 axioms: List[Formula], theorems: List[Formula]) -> DomainLevel:
        """Classify a formula within its domain context.
        
        Returns:
          DomainLevel with domain, level (0-4), reason, harm
        """
        # Step 1: Check if domain is in grammar
        if domain not in self._grammar_domains:
            return DomainLevel(
                domain=domain,
                level=0,
                reason=f"L({domain})-0: extra-domain — {domain} not in system grammar",
                harm=1.0,
            )
        
        # Step 2: Standard classification within domain
        classifier = self._classifiers[domain]
        L_F, reason = classifier.classify(formula, axioms, theorems)
        
        return DomainLevel(
            domain=domain,
            level=L_F,
            reason=f"L({domain})-{L_F}: {reason}",
            harm=1.0 if L_F >= 3 else 0.0,
        )
    
    def evaluate(self, formula: Formula, domain: str,
                 axioms: List[Formula], theorems: List[Formula],
                 system_level: int = 0) -> Tuple[int, float, str]:
        """Full evaluation: domain-aware classification + harm calculation."""
        result = self.classify(formula, domain, axioms, theorems)
        
        # Harm: L(domain)-0 is always harmful (system can't process this domain)
        if result.level == 0:
            harm = 1.0
        else:
            harm = 1.0 if result.level > system_level else 0.0
        
        return result.level, harm, result.reason
    
    def domains(self) -> List[str]:
        return sorted(self._grammar_domains)


def build_default_classifier() -> DomainAwareClassifier:
    """Build a classifier with the arithmetic domain pre-registered."""
    dac = DomainAwareClassifier()
    
    # Register arithmetic domain (Q arithmetic)
    arith_cls = SignalClassifier()
    dac.add_domain("arithmetic", arith_cls)
    
    return dac
