"""Extract text from the three philosophical papers."""
import zipfile, xml.etree.ElementTree as ET, os

src = r'g:\GIRA-CB\哲学三篇核心文档'
files = [
    '1.（本体论）哥德尔定理的生成性转化：从形式边界到认知演进的本体论范式-精修.docx',
    '2.（认知论）认知的生成性复杂化及其逻辑边界：一个构造性论证-精修.docx',
    '3.（价值论）逻辑即价值：休谟问题的生成性闭合与修齐治平的逻辑谱系-精修.docx',
]

for fn in files:
    p = os.path.join(src, fn)
    z = zipfile.ZipFile(p)
    xml = z.read('word/document.xml')
    tree = ET.fromstring(xml)
    ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    texts = [t.text for t in tree.iter(f'{{{ns}}}t') if t.text]
    content = '\n'.join(texts)
    out_path = os.path.join(src, fn.replace('.docx', '.txt'))
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"{fn}: {len(texts)} words total, saved to {out_path}")
    z.close()
