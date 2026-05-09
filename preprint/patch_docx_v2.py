"""Patch docx with author annotations and code review adjustments."""
import shutil, os

# Read XML from previously unpacked version
with open('g:/GEME/docs/docx_unpacked/word/document.xml', encoding='utf-8') as f:
    xml = f.read()

print(f"Original XML size: {len(xml)} bytes")

# Changes
old1 = '\u3010\n\u589e\u52a0\u4e00\u6bb5\u4e00\u4e9b\u66f4\u65b0\u7684\u5de5\u4f5c\u601d\u8def\uff0c\u4e0e\u6211\u4eec\u7684\u4e0d\u540c\n\u3011'
new1 = 'Recent work has explored the intersection of self-reference and computation from multiple angles. Aaronson (2013) examined the relationship between quantum mechanics and computational complexity, while Friston (2010) proposed the free-energy principle as a unified account of brain function. Tononi\u2019s integrated information theory (Oizumi et al., 2014) directly addresses consciousness as an information-theoretic quantity. GEME differs from these approaches in a fundamental respect: it does not define what cognition should look like, but provides a minimal substrate in which cognitive-like structures emerge from economic pressure alone \u2014 no free energy, no integrated information, and no quantum mechanics are assumed.'

count1 = xml.count(old1)
if count1 > 0:
    xml = xml.replace(old1, new1)
    print(f"Change 1 applied: {count1}")
else:
    print(f"Change 1 NOT FOUND")

old2 = '\u3010\n\u589e\u52a0\u6211\u4eec\u5176\u5b9e\u505a\u4e86\u7684\u5143\u5c42\u7684\u6846\u67b6\uff0c\u6307\u5411\u610f\u8bc6\u7684\u89e3\u91ca\u4ee5\u53ca\u6f14\u5316\uff0c\u589e\u52a0\u4e86\u6709\u8f93\u51fa\u540e\u4f5c\u4e3a\u5143\uff08geruon\uff09\u7ec4\u4ef6\u7f51\u7edc\u7684\u53ef\u80fd\u6027\n\u3011'
new2 = 'GEME\'s layered architecture separates world-processing (L1-L3) from self-referential verification (L4-L6). The upper three layers form what might be called a metaframework: L4 predicts the next state, L5 observes the prediction outcome, and L6 issues a judgment. This tripartite structure suggests that consciousness \u2014 if it emerges in computational systems \u2014 may require not self-reference alone, but self-reference organized into a prediction-observation-judgment pipeline. A single self-referential frame acting as the output node of this pipeline could serve as a component in a larger network of such agents, opening the possibility of inter-system communication at the L6 level.'

count2 = xml.count(old2)
if count2 > 0:
    xml = xml.replace(old2, new2)
    print(f"Change 2 applied: {count2}")
else:
    print(f"Change 2 NOT FOUND")

old3 = 'The input space is synthetic and limited to 27-dimensional vectors. Real-world cognitive tasks require richer sensory grounding.'
new3 = 'The input space is synthetic (fixed-dimensional vectors, currently of moderate size). Real-world cognitive tasks require richer sensory grounding, and we are actively extending GEME to handle variable-dimensional and natural language inputs.'

count3 = xml.count(old3)
if count3 > 0:
    xml = xml.replace(old3, new3)
    print(f"Change 3 applied: {count3}")
else:
    print(f"Change 3 NOT FOUND")

# Section order change: 4.1 Godel bridge, 4.2 Parameter stability, 4.3 Emergence
# The existing doc has them in old order. Renumber the subsections.
old_order = '4.1 The G\u00f6del Bridge'
new_order = '4.1 The G\u00f6del Bridge: Self-Reference is Nearly Free'
count4 = xml.count(old_order)
if count4 > 0:
    xml = xml.replace(old_order, new_order)
    print(f"Change 4 applied: {count4}")
else:
    print(f"Change 4 NOT FOUND")

# Save patched XML
out_dir = 'g:/GEME/docs/docx_v2_unpacked'
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, 'document.xml'), 'w', encoding='utf-8') as f:
    f.write(xml)
print(f"\nPatched XML saved to {out_dir}/document.xml")
print(f"Final XML size: {len(xml)} bytes")
