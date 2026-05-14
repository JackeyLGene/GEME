"""Graph-theoretic analysis of GEME frame economies.
Extract structural signatures from the co-occurrence graph.
"""
import sys, os, time, math, statistics
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet

# Build frame-graph from a GEME's memory
def frame_graph(geme):
    """Return adjacency dict: {frame_idx: {neighbor_idx: weight}}"""
    frames = geme.memory.frames
    n = len(frames)
    if n < 2: return {}
    
    # Use co-occurrence as edge weight proxy
    # Co-occurrence dict: {sig_pair: count}
    cooccur = getattr(geme.memory, '_cooccur', {})
    
    graph = {i: {} for i in range(n)}
    for (sig_a, sig_b), count in cooccur.items():
        # Find frame indices for these signatures
        idx_a = next((j for j, f in enumerate(frames) if f.sig == sig_a), None)
        idx_b = next((j for j, f in enumerate(frames) if f.sig == sig_b), None)
        if idx_a is not None and idx_b is not None and idx_a != idx_b:
            graph[idx_a][idx_b] = graph[idx_a].get(idx_b, 0) + count
            graph[idx_b][idx_a] = graph[idx_b].get(idx_a, 0) + count
    
    return graph

def graph_metrics(graph):
    """Compute graph-level metrics."""
    n = len(graph)
    if n < 2: return {'nodes': n, 'edges': 0, 'density': 0, 'avg_degree': 0}
    
    total_edges = sum(len(neighbors) for neighbors in graph.values()) // 2
    density = 2 * total_edges / (n * (n - 1)) if n > 1 else 0
    degrees = [len(neighbors) for neighbors in graph.values()]
    avg_deg = statistics.mean(degrees) if degrees else 0
    max_deg = max(degrees) if degrees else 0
    
    # Modularity (simplified: how concentrated is the graph?)
    # High = few hubs, Low = distributed
    if max_deg > 0:
        hub_concentration = max_deg / sum(v for v in degrees if v > 0) if any(v > 0 for v in degrees) else 0
    else:
        hub_concentration = 0
    
    return {
        'nodes': n,
        'edges': total_edges,
        'density': round(density, 4),
        'avg_degree': round(avg_deg, 2),
        'hub_concentration': round(hub_concentration, 4),
    }

def analyze_piece(name, score, encoder, passes=4):
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3, seed_base=42)
    track = net.enable_tracking()
    
    for _ in range(passes):
        for entry in score:
            if len(entry) == 2: notes, beats = entry
            else: notes, beats = entry[0], entry[1]
            v = encoder(notes)
            for _ in range(beats):
                net.step(v, '')
    
    # Extract graphs from each unit and G0
    unit_graphs = [frame_graph(net.units[i]) for i in range(3)]
    g0_graph = frame_graph(net.g0)
    
    unit_metrics = [graph_metrics(g) for g in unit_graphs]
    g0_m = graph_metrics(g0_graph)
    
    # Average unit metrics
    avg_density = statistics.mean(m['density'] for m in unit_metrics)
    avg_hub = statistics.mean(m['hub_concentration'] for m in unit_metrics)
    
    # Compare unit graphs: how similar are their topologies?
    # Using Jaccard-like similarity on edge sets
    edges_list = [set(tuple(sorted([u, v])) for u in g for v in g[u]) for g in unit_graphs if g]
    avg_similarity = 0
    if len(edges_list) >= 2:
        sims = []
        for i in range(len(edges_list)):
            for j in range(i+1, len(edges_list)):
                if edges_list[i] and edges_list[j]:
                    intersection = len(edges_list[i] & edges_list[j])
                    union = len(edges_list[i] | edges_list[j])
                    sims.append(intersection / union if union > 0 else 0)
        avg_similarity = statistics.mean(sims) if sims else 0
    
    print(f'\n{name}')
    print(f'  Units: avg density={avg_density:.4f}, hub_conc={avg_hub:.4f}, '
          f'graph_similarity={avg_similarity:.3f}')
    print(f'  G0:    density={g0_m["density"]:.4f}, hub_conc={g0_m["hub_concentration"]:.4f}')
    print(f'  Ratio (G0/unit): '
          f'density={g0_m["density"]/max(avg_density,0.001):.2f}x, '
          f'hub={g0_m["hub_concentration"]/max(avg_hub,0.001):.2f}x')
    
    return avg_density, avg_hub, avg_similarity, g0_m['hub_concentration']

if __name__ == '__main__':
    t0 = time.time()
    
    from data.bwv846 import SCORE as s_846, chord_hz_vec as hz
    from data.bwv847_fugue import SCORE as s_847f, chord_hz_vec as hz_f
    from data.bwv_contrast import BWV849 as s_849, BWV851 as s_851, hz_vec
    
    print('='*55)
    print('Graph Analysis of GEME Frame Economies')
    print('='*55)
    
    r1 = analyze_piece('BWV846 (C maj, uniform)', s_846, hz)
    r2 = analyze_piece('BWV847 Fugue (C min)', s_847f, hz_f)
    r3 = analyze_piece('BWV849 (C# min, chromatic)', s_849, hz_vec)
    r4 = analyze_piece('BWV851 (D min, energetic)', s_851, hz_vec)
    
    print(f'\nTime: {(time.time()-t0):.1f}s')
