"""
MI Experiment: measure I(phi; X) across independent seeds.
Uses current code (adaptive conf threshold, derived constants, fixed Unicode).
Each seed: independent quantum random, 2000 steps, structured formula input.
"""
import sys, math, json
sys.path.insert(0, '.')
from geme import GEME, eq, fn, const, structural_signature

def run_mi_experiment(n_seeds=20, steps=2000, memory_cap=32, seed_offset=0):
    """Run GEME for `steps` with `n_seeds` independent seeds.
    Returns list of I(phi;X) values and full metrics per seed."""
    import random as _rnd
    results = []

    for seed_idx in range(n_seeds):
        seed = seed_idx * 101 + seed_offset
        rng = _rnd.Random(seed)

        g = GEME(memory_cap=memory_cap, cooccur_window=60)
        g.memory.preserve_sig = True
        g.memory.quantum_mode = True

        for t in range(steps):
            # Generate structured formula input (replicating original experimental design)
            a = str(rng.randint(0, 9))
            b = str(rng.randint(0, 9))
            f = eq(fn("swap", const(a), const(b)),
                   fn("swap", const(b), const(a)))
            sig = structural_signature(f)
            g.process_sig(f, sig)

            # Periodic induction
            if t % 20 == 19:
                g.memory.induction_clean()

        m = g.metrics()
        mi = m.get('I(phi;X)', 0.0)
        results.append({
            'seed': seed,
            'MI': mi,
            'frames': m.get('frame_count', 0),
            'L4': m.get('L4_frame_count', 0),
            'preds': m.get('pred_total', 0),
            'accuracy': m.get('pred_accuracy', 0.0),
            'efficiency': m.get('efficiency', 0.0),
            'conf_threshold': m.get('conf_threshold', 0.0),
        })

    return results


def report(name, results):
    """Pretty-print MI experiment results."""
    mi_vals = [r['MI'] for r in results]
    n = len(mi_vals)
    mean_mi = sum(mi_vals) / n
    var_mi = sum((x - mean_mi)**2 for x in mi_vals) / (n - 1) if n > 1 else 0
    std_mi = var_mi ** 0.5
    sorted_mi = sorted(mi_vals)
    ci_low = sorted_mi[int(n * 0.025)] if n >= 40 else mean_mi - 2.0 * std_mi / (n**0.5)
    ci_high = sorted_mi[int(n * 0.975)] if n >= 40 else mean_mi + 2.0 * std_mi / (n**0.5)
    pct_below_005 = sum(1 for x in mi_vals if x < 0.05) / n * 100

    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  n = {n}")
    print(f"  MI  = {mean_mi:.6f} +/- {std_mi:.6f}")
    print(f"  95% CI = [{ci_low:.6f}, {ci_high:.6f}]")
    print(f"  min = {min(mi_vals):.6f}  max = {max(mi_vals):.6f}")
    print(f"  % < 0.05 = {pct_below_005:.1f}%")
    print(f"  all values: {[round(x,6) for x in sorted_mi]}")

    # Also show auxiliary metrics
    l4_vals = [r['L4'] for r in results]
    pred_vals = [r['preds'] for r in results]
    print(f"  L4: mean={sum(l4_vals)/n:.1f}, range=[{min(l4_vals)},{max(l4_vals)}]")
    print(f"  Preds: mean={sum(pred_vals)/n:.0f}")

    return {
        'n': n,
        'mean': round(mean_mi, 6),
        'std': round(std_mi, 6),
        '95CI': [round(ci_low, 6), round(ci_high, 6)],
        'min': round(min(mi_vals), 6),
        'max': round(max(mi_vals), 6),
        'pct_below_0.05': round(pct_below_005, 1),
        'all': [round(x, 6) for x in sorted_mi],
    }


if __name__ == '__main__':
    print("GEME Mutual Information Experiment")
    print("I(phi; X) across independent random seeds")

    # Run 20-seed quick test
    r20 = run_mi_experiment(n_seeds=20, steps=2000)
    summary_20 = report("20 seeds, 2000 steps", r20)

    # Run 100-seed full test (takes longer)
    print("\n  Running 100 seeds (this takes a few minutes)...")
    r100 = run_mi_experiment(n_seeds=100, steps=2000, seed_offset=500)
    summary_100 = report("100 seeds, 2000 steps", r100)

    # Save results
    output = {
        'MI_20seeds': summary_20,
        'MI_100seeds': summary_100,
    }
    out_path = 'g:/GEME/submit/data/mi_results_updated.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")
