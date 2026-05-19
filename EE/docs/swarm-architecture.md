# Geruon Swarm — Parallel Training + Codex Integration

**Goal:** N Geruon instances process different cultural streams in parallel. Their Codex/BiasField outputs integrate into a shared pool.

## Architecture

```
                       ┌──────────────┐
                       │  Input Divider │
                       └──────┬───────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
     ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
     │ Stream A │        │ Stream B │        │ Stream C │
     │   (MIDI) │        │  (text)  │        │   (midi)  │
     └────┬────┘        └────┬────┘        └────┬────┘
          │                   │                   │
     ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
     │Geruon A │        │Geruon B │    ... │Geruon N │
     └────┬────┘        └────┬────┘        └────┬────┘
          │(K=0.5)           │(K=10)            │(K=100)
          │                   │                   │
          └──────────────┬───┴───────────────────┘
                         │
                    ┌────▼─────┐
                    │  Shared   │
                    │ BiasField │
                    │ + Codex   │
                    └──────────┘
```

## Integration Modes

| Mode | Frequency | Use Case |
|------|-----------|----------|
| **Per-step** | Every `GI=4` steps | Tight coupling, real-time cultural exchange |
| **Per-generation** | After each data cycle | Loose coupling, standard M4 mode |
| **On-boundary** | When any Geruon triggers 碰数 | Asymmetric sharing — only "interesting" moments propagate |

## Code Pattern

```python
class Swarm:
    def __init__(self, n_workers=4, streams=None):
        self.workers = [
            Geruon(vec_dim=27, memory_cap=16, kappa_tau=K_LENSES[i % 3])
            for i in range(n_workers)
        ]
        self.shared_bias = BiasField(vec_dim=27)
        self.shared_codex = Codex.empty(name="swarm", vec_dim=27)
    
    def step(self, steps=500):
        for step in range(steps):
            for i, worker in enumerate(self.workers):
                vec, sig = self.streams[i][step % len(self.streams[i])]
                worker.process_vec(vec, sig)
                if step % 16 == 0:  # Integration interval
                    self.shared_bias.deposit(worker.arrow_output())
```

## Benefit over sequential M4

- **Cultural diversity**: N Geruons on N different cultural streams simultaneously — not one Geruon on one stream for N passes.
- **τ differentiation**: Fast lens (κ=0.5) and slow lens (κ=10) train on different data — their τ trajectories naturally diverge, enriching the shared BiasField more than if both trained on the same stream.
- **Fault tolerance**: If one Geruon enters D5 lock, others continue feeding diverse structure to the shared field.

## Implementation

This is a wrapper class — not a kernel modification. Geruon is already stateless enough (τ memory is internal per instance) that wrapping N instances in a Swarm class requires ~50 lines of new code. No changes to geruon.py.
