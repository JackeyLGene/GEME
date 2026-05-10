import sys
sys.path.insert(0, r'g:\GEME\src')
with open('src/gira/phase3/inference.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines[204:212], start=205):
    print(f'{i}:{line}', end='')
