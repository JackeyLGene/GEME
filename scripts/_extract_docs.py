import zipfile, xml.etree.ElementTree as ET, os

def extract_docx_text(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml')
    root = ET.fromstring(xml)
    texts = []
    ns_url = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    for t in root.iter('{' + ns_url + '}t'):
        if t.text:
            texts.append(t.text)
    return '\n'.join(texts)

base = r'g:\GIRA-CB\哲学三篇核心文档'
files = [
    '1.（本体论）哥德尔定理的生成性转化：从形式边界到认知演进的本体论范式-精修.docx',
    '2.（认知论）认知的生成性复杂化及其逻辑边界：一个构造性论证-精修.docx',
    '3.（价值论）逻辑即价值：休谟问题的生成性闭合与修齐治平的逻辑谱系-精修.docx'
]
for i, fname in enumerate(files):
    path = os.path.join(base, fname)
    if not os.path.exists(path):
        print(f"NOT FOUND: {path}")
        continue
    text = extract_docx_text(path)
    out = os.path.join(base, f'_thesis_{i+1}.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'Extracted thesis {i+1}: {len(text)} chars, {len(text.splitlines())} lines')
print("Done.")
