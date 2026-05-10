"""
GEM Reporter — presents the full emergence pipeline to the human observer.

GEM is not an agent. It's an instrument.
The human observes the pipeline, not asks it questions.

Output structure:
  [1] Input Space — what was fed to the system
  [2] Boundary Map — what triggered L3+
  [3] Emergence Log — what crossed the boundary
  [4] Rule Catalog — what the system synthesized
  [5] Signature Atlas — structural clusters with frequency
"""

from __future__ import annotations
from typing import List, Dict, Tuple
from dataclasses import dataclass, field

from gira.phase3.language import Formula


@dataclass
class GEMReport:
    """Complete observation report from one GEM session."""
    title: str
    
    # Phase 1: Input
    input_formulas: List[Tuple[str, str, int]] = field(default_factory=list)
    # (name, formula_str, initial_level)
    
    # Phase 2: Boundary
    boundary_records: List[Tuple[str, str, int]] = field(default_factory=list)
    # (name, signature, frequency)
    
    # Phase 3: Emergence
    emergence_records: List[Tuple[str, int, int, str]] = field(default_factory=list)
    # (name, old_level, new_level, formula_str)
    
    # Phase 4: Rules
    extracted_rules: List[Tuple[str, str]] = field(default_factory=list)
    # (rule_name, template_str)
    
    # Phase 5: Signatures
    signatures: Dict[str, int] = field(default_factory=dict)
    # signature -> frequency
    
    # Timeline
    transitions: List[Tuple[int, int]] = field(default_factory=list)
    # (frame, new_level)
    
    def render(self) -> str:
        """Render a human-readable report."""
        sep = "=" * 65
        lines = [sep, self.title.center(65), sep]
        
        # Input Space
        lines.append(f"\n  {'INPUT SPACE':^55}")
        lines.append(f"  {'Name':<16} {'Initial L':<12} Formula")
        lines.append(f"  {'-'*55}")
        for name, fstr, level in self.input_formulas:
            marker = "BOUNDARY" if level >= 3 else "in-grammar"
            lines.append(f"  {name:<16} L{level:<11} {fstr[:35]} [{marker}]")
        
        # Boundary Map  
        lines.append(f"\n  {'BOUNDARY MAP':^55}")
        lines.append(f"  {'Signature':<40} {'Count':<8}")
        lines.append(f"  {'-'*50}")
        for sig, count in sorted(self.signatures.items(), key=lambda x: -x[1]):
            lines.append(f"  {sig:<40} {count:<8}")
        
        # Emergence Log
        if self.emergence_records:
            lines.append(f"\n  {'EMERGENCE LOG':^55}")
            lines.append(f"  {'Name':<16} {'Old':<6} {'New':<6} {'Formula'}")
            lines.append(f"  {'-'*55}")
            for name, old, new, fstr in self.emergence_records:
                lines.append(f"  {name:<16} L{old:<5} L{new:<5} {fstr[:35]}")
        else:
            lines.append(f"\n  No emergence observed in this session.")
        
        # Rule Catalog
        if self.extracted_rules:
            lines.append(f"\n  {'RULE CATALOG':^55}")
            for rname, tmpl in self.extracted_rules:
                lines.append(f"  {rname}")
                lines.append(f"    {tmpl[:55]}")
        
        # Timeline
        if self.transitions:
            lines.append(f"\n  {'TRANSITION TIMELINE'}")
            for frame, level in self.transitions:
                lines.append(f"    Frame {frame}: L(E) -> {level}")
        
        lines.append(f"\n{sep}")
        lines.append("  Observer: pattern recognition belongs to the human.".center(65))
        lines.append("  This instrument only makes structures visible.".center(65))
        lines.append(sep)
        
        return "\n".join(lines)


class GEMReporter:
    """Builds a GEMReport from session data."""
    
    def __init__(self, title: str):
        self.report = GEMReport(title=title)
    
    def record_input(self, name: str, formula: Formula, level: int):
        self.report.input_formulas.append((name, str(formula)[:80], level))
    
    def record_boundary(self, signature: str, count: int):
        self.report.signatures[signature] = count
    
    def record_emergence(self, name: str, old_level: int, new_level: int, formula: Formula):
        self.report.emergence_records.append((name, old_level, new_level, str(formula)[:80]))
    
    def record_rule(self, rule_name: str, template_str: str):
        self.report.extracted_rules.append((rule_name, template_str))
    
    def record_transition(self, frame: int, new_level: int):
        self.report.transitions.append((frame, new_level))
    
    def render(self) -> str:
        return self.report.render()
