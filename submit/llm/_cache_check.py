import os
base = r"C:\Users\Administrator.DESKTOP-EM03IHL\.cache\huggingface\hub\datasets--Hello-SimpleAI--HC3"
for root, dirs, files in os.walk(base):
    for f in files:
        fp = os.path.join(root, f)
        size = os.path.getsize(fp)
        if size > 1000 and f.endswith('.arrow'):
            print(fp, f"{size/1024:.0f} KB")
