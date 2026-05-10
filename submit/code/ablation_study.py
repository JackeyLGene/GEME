"""
Ablation study v3: Two-phase experiment.
Phase 1 (train): clean input → system reaches healthy accuracy
Phase 2 (stress): noise injection → accuracy drops → doubt may activate

Only after Phase 1 has established healthy accuracy (> HEALTHY_ACC_THRESHOLD)
can we meaningfully test whether DOUBT_ON_THRESHOLD and DOUBT_OFF_THRESHOLD
function as designed. A system that was never healthy cannot "doubt" itself.
"""
import sys, math
sys.path.insert(0, '.')
from geme import GEME, _VEC_DIM, GAMMA, TAU
import random


def run_two_phase(train_steps=400, stress_steps=400,
                  noise_frac=0.5, trials=10, **overrides):
    """Phase 1: train on clean patterns. Phase 2: inject noise.
    Returns doubt activation rate and per-phase metrics."""
    import geme as gm

    orig = {}
    for k, v in overrides.items():
        orig[k] = getattr(gm, k, None)
        setattr(gm, k, v)

    results = []
    for seed in range(trials):
        rng = random.Random(seed * 317 + 29)
        g = GEME(memory_cap=12, cooccur_window=60)
        g.memory.preserve_sig = True
        g.memory.quantum_mode = True

        # Phase 1: clean training
        for t in range(train_steps):
            idx = t % 5
            v = [0.0] * _VEC_DIM
            v[idx] = 1.0
            v[(idx + 2) % _VEC_DIM] = 0.4
            g.process_vec(v, f"pat_{idx}")
            if t % 20 == 19:
                g.memory.induction_clean()

        # Capture post-training metrics
        m1 = g.metrics()
        phase1_acc = m1.get('pred_accuracy', 0.0)
        phase1_preds = m1.get('pred_total', 0)
        was_healthy = phase1_acc > gm.HEALTHY_ACC_THRESHOLD

        # Phase 2: noise injection
        for t in range(stress_steps):
            if rng.random() < noise_frac:
                v = [rng.random() for _ in range(_VEC_DIM)]
                norm = math.sqrt(sum(x*x for x in v))
                if norm > 0:
                    v = [x/norm for x in v]
                g.process_vec(v, 'noise')
            else:
                idx = t % 5
                v = [0.0] * _VEC_DIM
                v[idx] = 1.0
                v[(idx + 2) % _VEC_DIM] = 0.4
                g.process_vec(v, f"pat_{idx}")
            if t % 20 == 19:
                g.memory.induction_clean()

        m2 = g.metrics()
        results.append({
            'phase1_acc': phase1_acc,
            'phase1_preds': phase1_preds,
            'was_healthy': was_healthy,
            'phase2_acc': m2.get('pred_accuracy', 0.0),
            'doubt': m2.get('doubt_mode', False),
            'doubt_final': m2.get('doubt_mode', False),
            'L4': m2.get('L4_frame_count', 0),
            'frames': m2.get('frame_count', 0),
        })

    for k, v in orig.items():
        if v is not None:
            setattr(gm, k, v)

    n = len(results)
    return {
        'phase1_acc': sum(r['phase1_acc'] for r in results) / n,
        'healthy_rate': sum(1 for r in results if r['was_healthy']) / n,
        'phase2_acc': sum(r['phase2_acc'] for r in results) / n,
        'doubt_frac': sum(1 for r in results if r['doubt']) / n,
        'L4': sum(r['L4'] for r in results) / n,
        'frames': sum(r['frames'] for r in results) / n,
    }


def two_phase_sweep(name, chosen_mult, mult_range, param_key, derive_fn):
    print(f"\n{'='*70}")
    print(f"  {name}")
    print(f"  Chosen: mult={chosen_mult} -> value={derive_fn(chosen_mult):.4f}")
    print(f"{'='*70}")
    print(f"{'mult':>6} {'value':>8} {'p1_acc':>7} {'healthy':>8} {'p2_acc':>7} {'doubt':>7} {'L4':>5} {'frames':>7}")
    print("-" * 60)

    doubt_rates = []
    for mult in mult_range:
        val = derive_fn(mult)
        m = run_two_phase(trials=10, **{param_key: val})
        doubt_rates.append(m['doubt_frac'])
        marker = " <<<" if abs(mult - chosen_mult) < 0.001 else ""
        dflag = " DOUBT" if m['doubt_frac'] > 0 else ""
        print(f"{mult:6.2f} {val:8.4f} {m['phase1_acc']:7.3f} {m['healthy_rate']:7.0%} "
              f"{m['phase2_acc']:7.3f} {m['doubt_frac']:6.0%} {m['L4']:5.1f} "
              f"{m['frames']:7.1f}{marker}{dflag}")

    # Find transition
    transitions = []
    for i in range(1, len(doubt_rates)):
        if abs(doubt_rates[i] - doubt_rates[i-1]) > 0.1:
            transitions.append((mult_range[i-1], mult_range[i],
                                doubt_rates[i-1], doubt_rates[i]))

    if transitions:
        print(f"\n  Transition boundaries:")
        for m1, m2, d1, d2 in transitions:
            print(f"    mult {m1:.2f}->{m2:.2f}: doubt {d1:.0%}->{d2:.0%}")

        chosen_near_transition = any(
            abs(chosen_mult - m1) < 0.1 or abs(chosen_mult - m2) < 0.1
            for m1, m2, _, _ in transitions
        )
        if chosen_near_transition:
            print(f"  [WARN] Chosen ({chosen_mult}) is near a transition boundary")
        else:
            print(f"  [OK] Chosen ({chosen_mult}) is within a stable plateau")
    else:
        if all(d == 0 for d in doubt_rates):
            print(f"\n  All 0% doubt (system never enters doubt)")
        elif all(d == 1.0 for d in doubt_rates):
            print(f"\n  All 100% doubt (system always enters doubt)")
        elif all(d > 0 for d in doubt_rates):
            print(f"\n  Doubt activated at ALL multipliers (robust to multiplier choice)")
        print(f"  [OK] No sharp transition -> multiplier choice is robust")

    return doubt_rates


if __name__ == '__main__':
    print("GEME Ablation Study v3 -- Two-Phase (Train then Stress)")
    print("Phase 1: 400 steps clean -> system learns to predict")
    print("Phase 2: 400 steps with 50% noise -> accuracy drops -> doubt may fire")

    # Baseline: do systems reach healthy accuracy in Phase 1?
    baseline = run_two_phase(trials=10)
    print(f"\n  Baseline: p1_acc={baseline['phase1_acc']:.3f}, "
          f"healthy={baseline['healthy_rate']:.0%}, "
          f"p2_acc={baseline['phase2_acc']:.3f}, "
          f"doubt={baseline['doubt_frac']:.0%}")

    # ---- DOUBT_ON_THRESHOLD ----
    # doubt activates when acc < DOUBT_ON_THRESHOLD AND system was previously healthy
    two_phase_sweep(
        "DOUBT_ON_THRESHOLD = TAU * mult  (chosen mult=1.0, val=0.60)",
        chosen_mult=1.0,
        mult_range=[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0],
        param_key='DOUBT_ON_THRESHOLD',
        derive_fn=lambda m: TAU * m
    )

    # ---- HEALTHY_ACC_THRESHOLD ----
    # doubt precondition: system must have been above this to trigger doubt on drop
    two_phase_sweep(
        "HEALTHY_ACC_THRESHOLD = 1.0 - GAMMA * mult  (chosen mult=4.0, val=0.80)",
        chosen_mult=4.0,
        mult_range=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 15.0],
        param_key='HEALTHY_ACC_THRESHOLD',
        derive_fn=lambda m: 1.0 - GAMMA * m
    )

    # ---- DOUBT_OFF_THRESHOLD ----
    # once in doubt, accuracy must exceed this to exit
    # Note: in our 400-step stress phase, the system may not have time to recover
    # We test: does the threshold affect WHETHER doubt persists?
    two_phase_sweep(
        "DOUBT_OFF_THRESHOLD = 1.0 - GAMMA * mult  (chosen mult=3.0, val=0.85)",
        chosen_mult=3.0,
        mult_range=[1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0],
        param_key='DOUBT_OFF_THRESHOLD',
        derive_fn=lambda m: 1.0 - GAMMA * m
    )

    # ---- DW_THRESHOLD ----
    # controls L4 meta-observation: does weight change rate affect L4 frame count?
    two_phase_sweep(
        "DW_THRESHOLD = GAMMA * mult  (chosen mult=0.4, val=0.02)",
        chosen_mult=0.4,
        mult_range=[0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 2.0],
        param_key='DW_THRESHOLD',
        derive_fn=lambda m: GAMMA * m
    )

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print("For each derived constant:")
    print("  - If doubt-frac transitions at a SPECIFIC multiplier -> the exact")
    print("    multiplier matters (load-bearing, not robust to perturbation)")
    print("  - If doubt-frac is STABLE across a WIDE RANGE -> the multiplier")
    print("    sits in a plateau (robust, any nearby value works equally well)")
    print("  - For DOUBT_ON: the multiplier should be at a natural separation")
    print("    between high-accuracy (Phase 1) and low-accuracy (Phase 2) regimes")
    print("=" * 70)
