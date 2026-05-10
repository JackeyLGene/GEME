"""Vocabulary Module: monitors a GEME's memory, detects wall conditions, 
and generates new alphabet entries for downstream GEMEs.

This sits between perception layers (GEME1/2, which hit walls) and
integration/theorem layers (GEME3/G4, which need expanded vocabulary).

Architecture:
  Input → GEME1/2 → frames → VocabularyModule → new alphabet → GEME3/G4
                                   ↑
                                   └── monitors walls ──┘

This module makes vocabulary generation endogenous — no script-level bridge.
"""
from __future__ import annotations
import math

class VocabularyModule:
    """Observes a GEME memory and generates alphabet extensions."""
    
    def __init__(self, min_wall_weight=50, min_frames=2):
        self.min_wall_weight = min_wall_weight
        self.min_frames = min_frames
        self.generated_vocab = {}  # {burst_size: function_name}
        
    def analyze(self, memory) -> dict:
        """Analyze memory state for wall conditions. Returns generated vocabulary."""
        if not memory.frames:
            return {}
            
        frames = sorted(memory.frames, key=lambda x: x.weight, reverse=True)
        
        # ── Step 1: Detect wall condition ──
        # Wall = all high-weight frames share the same semantic signature
        top_frames = [f for f in frames if f.weight >= self.min_wall_weight]
        if len(top_frames) < self.min_frames:
            return {}  # Not enough signal
        
        sigs = set()
        for f in top_frames:
            fs = f.sig_full if hasattr(f, 'sig_full') and f.sig_full else f.sig
            sigs.add(fs)
        
        # If all top frames collapsed to the same sig — wall detected
        if len(sigs) <= 1:
            return self._extract_vocabulary(top_frames, memory)
        
        # ── Step 2: Check if frames from separate GEMEs share patterns ──
        # This catches cross-GEME walls (GEME1 + GEME2 both hit conn)
        common_parts = None
        for fs in sigs:
            parts = set(fs.replace("──","_").replace("══","_").split("_"))
            if common_parts is None:
                common_parts = parts
            else:
                common_parts &= parts
        
        if common_parts and len(common_parts) >= 1:
            return self._extract_vocabulary(top_frames, memory)
            
        return {}
    
    def _extract_vocabulary(self, top_frames, memory) -> dict:
        """Generate new vocabulary entries from wall condition."""
        # Extract content word from highest-weight frame
        best_sig = ""
        max_w = 0
        for f in top_frames:
            if f.weight > max_w:
                max_w = f.weight
                best_sig = f.sig_full if hasattr(f, 'sig_full') and f.sig_full else f.sig
        
        parts = best_sig.replace("──","_").replace("══","_").split("_")
        content_word = ""
        for p in parts:
            if p not in ("eq","and","impl","empty","forall","yes") and len(p) >= 2:
                content_word = p
                break
        
        if not content_word:
            return {}
        
        # Detect burst sizes from window
        window_entries = getattr(memory, '_window', [])
        runs = []
        run = 0
        for entry in window_entries:
            sig = entry[0] if isinstance(entry, tuple) else ""
            if content_word in sig:
                run += 1
            else:
                if run >= 2:
                    runs.append(run)
                run = 0
        if run >= 2:
            runs.append(run)
        
        burst_sizes = list(set(runs)) if runs else [2, 3]
        
        # Generate vocabulary
        vocab = {}
        for bs in burst_sizes:
            fn_name = content_word + "_" + str(bs)
            vocab[bs] = fn_name
        
        self.generated_vocab = vocab
        return vocab
    
    def get_formulas(self, burst_data: dict) -> list:
        """Convert vocabulary + data into formulas for downstream GEME.
        
        burst_data: {function_name: [list_of_instances]}
        Returns: [(formula, signature), ...] ready for process_sig
        """
        from gira.phase3.language import eq, fn, constant as Const
        from gira.phase6.geme_go import structural_signature
        
        formulas = []
        for fn_name, instances in burst_data.items():
            for inst in instances:
                f = eq(fn(fn_name, Const(inst)), Const("yes"))
                formulas.append((f, structural_signature(f)))
        return formulas
    
    @property
    def has_generated(self) -> bool:
        return len(self.generated_vocab) > 0
    
    @property
    def vocabulary(self) -> dict:
        return self.generated_vocab
