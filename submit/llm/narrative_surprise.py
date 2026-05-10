"""
Narrative Surprise Detection v3: per-narrative training.

Design:
  Each narrative: train GEME on sentences 0-3 (mundane preamble).
  Test: sentences 4-6 (twist + aftermath).
  Control: narratives with NO twist (all sentences mundane).

  Hypothesis: anomaly_score spikes at the twist sentence and stays
  elevated for the aftermath, while control narratives remain flat.

  This isolates the twist signal from vocabulary/style differences —
  each GEME instance learns the specific style of its own narrative.

Encoding: character bigram frequency -> 27-dim.
"""
import sys, math, json
sys.path.insert(0, '../code')
from geme import GEME, _VEC_DIM
from collections import Counter


def bigram_encode(sentence, bg_map):
    text = sentence.lower()
    vec = [0.0] * _VEC_DIM
    total = 0
    for i in range(len(text) - 1):
        bg = text[i:i+2]
        if bg in bg_map:
            vec[bg_map[bg]] += 1.0
            total += 1
    if total > 0:
        vec = [v / total for v in vec]
    return vec


def build_bigram_map(sentences, top_n=27):
    counts = Counter()
    for s in sentences:
        t = s.lower()
        for i in range(len(t) - 1):
            counts[t[i:i+2]] += 1
    top = [bg for bg, _ in counts.most_common(top_n)]
    return {bg: i for i, bg in enumerate(top)}


# Each narrative: preamble (train) + twist + aftermath
# Control: same structure but no actual twist (continuation)
NARRATIVES = [
    # ---- Twist narratives ----
    {
        "name": "latin_ring",
        "type": "twist",
        "preamble": [
            "she opened the small velvet box her grandmother left",
            "inside was a plain silver ring tarnished with age",
            "she slipped it on her finger disappointed but dutiful",
            "nothing happened for three full days",
        ],
        "twist": [
            "on the fourth morning she woke up speaking flawless latin",
        ],
        "aftermath": [
            "she had never studied a word of it in her life",
            "the ring had been rome and rome remembered",
        ],
    },
    {
        "name": "vanishing_passengers",
        "type": "twist",
        "preamble": [
            "tom boarded the morning train as he had for twelve years",
            "he found his usual seat by the window third car from front",
            "the same conductor nodded the same ticket was punched",
            "at precisely eight fifteen the train stopped between stations",
        ],
        "twist": [
            "the passengers in the car ahead began to vanish silently",
        ],
        "aftermath": [
            "tom looked at his reflection and did not recognize the face",
            "the train had never been scheduled to stop at this point",
        ],
    },
    {
        "name": "skull_garden",
        "type": "twist",
        "preamble": [
            "mara dug in the garden behind her rented cottage",
            "the soil was rich and dark promising a good season",
            "her trowel struck something hard at about two feet down",
            "she assumed it was another rock the property was full of them",
        ],
        "twist": [
            "it was a human skull with a neat hole above the left temple",
        ],
        "aftermath": [
            "beside it lay a police badge from nineteen seventy three",
            "the previous tenant had been specific about not disturbing the roses",
        ],
    },
    {
        "name": "axiom_contradiction",
        "type": "twist",
        "preamble": [
            "wei had studied for the exam for six straight weeks",
            "he memorized every formula every proof every edge case",
            "the morning of the test he walked into the hall prepared",
            "the first page was exactly what he expected straightforward",
        ],
        "twist": [
            "page three contained a question contradicting the axioms of the field",
        ],
        "aftermath": [
            "it was not a trick but a genuine inconsistency in the foundations",
            "the professor later admitted he included it to see who would notice",
        ],
    },
    {
        "name": "wrong_house",
        "type": "twist",
        "preamble": [
            "james unlocked the front door and stepped inside",
            "he hung his coat on the hook by the entrance",
            "he called out to his wife but received no answer",
            "the living room was exactly as he remembered it",
        ],
        "twist": [
            "the family photos on the mantle showed strangers smiling back at him",
        ],
        "aftermath": [
            "he checked the address on his phone with trembling hands",
            "this was his house but the people in it were not his family",
        ],
    },
    # ---- Control narratives (no twist) ----
    {
        "name": "control_shopping",
        "type": "control",
        "preamble": [
            "sarah walked to the grocery store on elm street",
            "the automatic doors slid open as she approached",
            "she picked up a basket and checked her shopping list",
            "the produce section had fresh apples on display",
        ],
        "twist": [
            "she selected three apples and placed them in her basket",
        ],
        "aftermath": [
            "she found the milk in the dairy section as always",
            "she paid at the register and walked home the same way",
        ],
    },
    {
        "name": "control_library",
        "type": "control",
        "preamble": [
            "david returned his books to the public library",
            "the librarian scanned each one with a quiet beep",
            "he browsed the new arrivals shelf near the window",
            "a familiar title caught his eye among the displays",
        ],
        "twist": [
            "he picked up the book and read the first page standing there",
        ],
        "aftermath": [
            "he decided to check it out and added it to his stack",
            "the library was quiet except for the turning of pages",
        ],
    },
    {
        "name": "control_office",
        "type": "control",
        "preamble": [
            "linda arrived at the office at her usual time",
            "she greeted the security guard in the lobby",
            "the elevator took her to the seventh floor as always",
            "her desk was exactly as she had left it on friday",
        ],
        "twist": [
            "she powered on her computer and opened her email",
        ],
        "aftermath": [
            "there were twelve new messages all from the usual people",
            "she started with the one from her manager about the project",
        ],
    },
]


def run_narrative(narr, bigram_map, seed=0):
    """Per-narrative: train on preamble, test on twist+aftermath."""
    g = GEME(memory_cap=12)
    g.memory.preserve_sig = True
    g.memory.quantum_mode = True
    g.memory.cooccur_thresh = 0.08

    # Phase 1: train on preamble (repeat 10x to stabilize)
    for _ in range(10):
        for s in narr["preamble"]:
            vec = bigram_encode(s, bigram_map)
            g.process_vec(vec, s[:25])
        g.memory.induction_clean()

    m_pre = g.metrics()

    # Phase 2: test
    test_results = []
    for tag, sentences in [("preamble", narr["preamble"]),
                            ("twist", narr["twist"]),
                            ("aftermath", narr["aftermath"])]:
        for s in sentences:
            vec = bigram_encode(s, bigram_map)
            g.process_vec(vec, s[:25])
            m = g.metrics()
            test_results.append({
                'tag': tag,
                'sentence': s,
                'anomaly': g.anomaly_score(),
                'doubt': m.get('doubt_mode', False),
                'L4': m.get('L4_frame_count', 0),
                'preds': m.get('pred_total', 0),
                'accuracy': m.get('pred_accuracy', 0.0),
                'frames': m.get('frame_count', 0),
            })

    return {
        'name': narr['name'],
        'type': narr['type'],
        'pre_frames': m_pre.get('frame_count', 0),
        'results': test_results,
    }


if __name__ == '__main__':
    print("=" * 70)
    print("GEME Narrative Surprise Detection v3")
    print("Per-narrative training: preamble->train, twist+aftermath->test")
    print("=" * 70)

    # Build bigram map from ALL sentences
    all_sents = []
    for n in NARRATIVES:
        all_sents.extend(n["preamble"])
        all_sents.extend(n["twist"])
        all_sents.extend(n["aftermath"])
    bg_map = build_bigram_map(all_sents, top_n=_VEC_DIM)

    all_outcomes = []
    for narr in NARRATIVES:
        outcome = run_narrative(narr, bg_map)
        all_outcomes.append(outcome)

        print(f"\n--- {narr['name']} ({narr['type']}) ---")
        print(f"  Post-training: {outcome['pre_frames']} frames")
        for r in outcome['results']:
            anom_bar = "#" * int(r['anomaly'] * 10)
            dflag = " DOUBT" if r['doubt'] else ""
            l4flag = f" L4={r['L4']}" if r['L4'] > 0 else ""
            print(f"  [{r['tag']:>9}] anom={r['anomaly']:.2f} acc={r['accuracy']:.3f} "
                  f"preds={r['preds']:4d} {anom_bar}{dflag}{l4flag}")

    # Aggregate analysis
    twist_anomalies = []
    preamble_anomalies = []
    aftermath_anomalies = []
    control_all = []

    for outcome in all_outcomes:
        for r in outcome['results']:
            if outcome['type'] == 'twist':
                if r['tag'] == 'preamble':
                    preamble_anomalies.append(r['anomaly'])
                elif r['tag'] == 'twist':
                    twist_anomalies.append(r['anomaly'])
                elif r['tag'] == 'aftermath':
                    aftermath_anomalies.append(r['anomaly'])
            else:
                control_all.append(r['anomaly'])

    print(f"\n{'='*70}")
    print("AGGREGATE ANALYSIS")
    print(f"{'='*70}")
    print(f"  Twist narratives:")
    print(f"    Preamble avg anomaly:  {sum(preamble_anomalies)/len(preamble_anomalies):.3f} (n={len(preamble_anomalies)})")
    print(f"    Twist avg anomaly:     {sum(twist_anomalies)/len(twist_anomalies):.3f} (n={len(twist_anomalies)})")
    print(f"    Aftermath avg anomaly: {sum(aftermath_anomalies)/len(aftermath_anomalies):.3f} (n={len(aftermath_anomalies)})")
    print(f"  Control narratives:")
    print(f"    All avg anomaly:       {sum(control_all)/len(control_all):.3f} (n={len(control_all)})")

    delta = sum(twist_anomalies)/len(twist_anomalies) - sum(preamble_anomalies)/len(preamble_anomalies)
    delta_ctrl = sum(twist_anomalies)/len(twist_anomalies) - sum(control_all)/len(control_all)
    print(f"\n  Twist - Preamble delta: {delta:+.3f}")
    print(f"  Twist - Control delta:  {delta_ctrl:+.3f}")

    if delta > 0.05:
        print(f"\n  [SIGNAL DETECTED] GEME anomaly spikes at narrative twist points.")
        print(f"  The frame economy distinguishes surprising from expected sentences.")
    else:
        print(f"\n  [WEAK] Signal insufficient with current encoding.")
