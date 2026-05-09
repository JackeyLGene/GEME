"""Build GEME Paper Draft v2 — integrating code review adjustments and author annotations."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'final-v1.5'))
from geme import DELTA, GAMMA, TAU

# Use the shared docx-js approach — but let's use python-docx for simpler edits
# Copy original and apply modifications
import shutil
src = r"C:\Users\Administrator.DESKTOP-EM03IHL\Desktop\GEME_Paper_Draft.docx"
dst = r"C:\Users\Administrator.DESKTOP-EM03IHL\Desktop\GEME_Paper_Draft_v2.docx"
shutil.copy2(src, dst)

# Use python to apply tracked changes via unpack/edit/pack
unpack_dir = "g:/GEME/docs/docx_v2_unpacked"
os.makedirs(unpack_dir, exist_ok=True)
os.system(f'python C:\\Users\\Administrator.DESKTOP-EM03IHL\\.codebuddy\\plugins\\marketplaces\\codebuddy-plugins-official\\plugins\\docx\\scripts\\office\\unpack.py "{dst}" {unpack_dir}')

# Read document.xml
with open(f"{unpack_dir}/word/document.xml", encoding='utf-8') as f:
    xml = f.read()

# 1. Replace "【增加一段一些更新的工作思路，与我们的不同】" with actual content
old1 = "【\n增加一段一些更新的工作思路，与我们的不同\n】"
new1 = """Recent work has explored the intersection of self-reference and computation from multiple angles. Aaronson (2013) examined the relationship between quantum mechanics and computational complexity, while Friston (2010) proposed the free-energy principle as a unified account of brain function. Tononi's integrated information theory (Oizumi et al., 2014) directly addresses consciousness as an information-theoretic quantity. GEME differs from these approaches in a fundamental respect: it does not define what cognition should look like, but provides a minimal substrate in which cognitive-like structures emerge from economic pressure alone — no free energy, no integrated information, and no quantum mechanics are assumed."""

xml = xml.replace(old1, new1)

# 2. Replace the metaframework annotation
old2 = "【\n增加我们其实做了的元层的框架，指向意识的解释以及演化，增加有了输出后作为元（geruon）组件网络的可能性\n】"
new2 = """GEME's layered architecture separates world-processing (L1-L3) from self-referential verification (L4-L6). The upper three layers form what might be called a metaframework: L4 predicts the next state, L5 observes the prediction outcome, and L6 issues a judgment. This tripartite structure suggests that consciousness — if it emerges in computational systems — may require not self-reference alone, but self-reference organized into a prediction-observation-judgment pipeline. A single self-referential frame (the 'geruon') acting as the output node of this pipeline could serve as a component in a larger network of such agents, opening the possibility of inter-system communication at the L6 level."""

xml = xml.replace(old2, new2)

# 3. Rewrite the "27-dimensional vectors" sentence
old3 = """The input space is synthetic and limited to 27-dimensional vectors"""
new3 = """The input space is synthetic (fixed-dimensional vectors, currently of moderate size)"""

# More specific: replace the sentence
old3_full = """The input space is synthetic and limited to 27-dimensional vectors. Real-world cognitive tasks require richer sensory grounding."""
new3_full = """The input space is synthetic (fixed-dimensional vectors, currently of moderate size). Real-world cognitive tasks require richer sensory grounding, and we are actively extending GEME to handle variable-dimensional and natural language inputs."""

xml = xml.replace(old3_full, new3_full)

# Write back
with open(f"{unpack_dir}/word/document.xml", 'w', encoding='utf-8') as f:
    f.write(xml)

# Repack
os.system(f'python C:\\Users\\Administrator.DESKTOP-EM03IHL\\.codebuddy\\plugins\\marketplaces\\codebuddy-plugins-official\\plugins\\docx\\scripts\\office\\pack.py {unpack_dir} "{dst}" --original "{src}"')

# Cleanup
import shutil
shutil.rmtree(unpack_dir, ignore_errors=True)

print(f"v2 saved to {dst}")
