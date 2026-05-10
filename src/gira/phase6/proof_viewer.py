"""
ProofViewer — Weight stability chain (temporal cross-section).
Proof = weight maturation, not logical deduction.
"""
from __future__ import annotations
from typing import List, Dict, Tuple
import os, datetime

class Section:
    """A temporal snapshot of memory at a given frame."""
    __slots__ = ("frame","items")
    def __init__(self, frame: int, items: List[Tuple[str,float]]):
        self.frame = frame
        self.items = items  # [(src, weight), ...]

class ProofChain:
    def __init__(self):
        self.sections: List[Section] = []
        
    def snapshot(self, frames_list: List, frame_count: int):
        """Take a snapshot: record all current frames with weights."""
        items = [(f.src, f.weight) for f in frames_list]
        self.sections.append(Section(frame_count, items))
    
    def stability(self, src_prefix: str, min_weight: float = 5.0) -> bool:
        """Check if a pattern is stable (weight above threshold for 2+ sections)."""
        above = 0
        for sec in reversed(self.sections[-3:]):  # last 3 sections
            for s,w in sec.items:
                if src_prefix in s and w >= min_weight:
                    above += 1
                    break
        return above >= 2


class ProofViewer:
    def __init__(self, geme_instance):
        self.g = geme_instance
        self.rid = _next_rid()
    
    def view(self) -> str:
        m = self.g.memory
        med = sorted(f.weight for f in m.frames)[len(m.frames)//2] if m.frames else 0
        mw = max(f.weight for f in m.frames) if m.frames else 1
        chain = self.g.chain
        
        lines = ["="*60, f"  Proof Viewer — Run #{self.rid}", "="*60]
        lines.append(f"\n── Current Memory ──")
        lines.append(f"  occupied: {len(m.frames)}/{m.capacity}  stress: {m.stress:.4f}  median: {med:.1f}")
        for i, f in enumerate(sorted(m.frames, key=lambda x: x.weight, reverse=True)):
            em = "[E]" if f.weight >= med else "[.]"
            bar = "#" * max(1, int(f.weight / mw * 30)) + "." * max(0, 30 - max(1, int(f.weight / mw * 30)))
            lines.append(f"  [{i}] {em} w={f.weight:5.1f}  {f.src}")
            lines.append(f"       {bar}")
        
        lines.append(f"\n── Weight History ({len(chain.sections)} snapshots) ──")
        if not chain.sections:
            lines.append("  [no snapshots]")
        else:
            # Show last 5 sections
            for sec in chain.sections[-5:]:
                lines.append(f"  @frame {sec.frame}:")
                for s,w in sec.items:
                    bar = "#" * max(1, int(w / mw * 20)) + "." * max(0, 20 - max(1, int(w / mw * 20)))
                    lines.append(f"    w={w:5.1f} {bar}  {s}")
        
        lines.append(f"\n── Stability ──")
        # Check each unique pattern
        seen = set()
        for sec in chain.sections:
            for s,w in sec.items:
                prefix = s[:30] if len(s) > 30 else s
                if prefix in seen: continue
                seen.add(prefix)
                stable = chain.stability(s[:20], 5.0)
                status = "STABLE" if stable else "unst"
                lines.append(f"  [{status}] w={w:5.1f}  {s}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def save_run(self, out_dir: str = None) -> str:
        out_dir = out_dir or r'g:\GEME\docs'
        ts = datetime.datetime.now().strftime("%H%M%S")
        fn = f"proof_run{self.rid:02d}_{ts}.txt"
        p = os.path.join(out_dir, fn)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(self.view())
        return p

_g_counter = 0
def _next_rid(): global _g_counter; _g_counter += 1; return _g_counter
