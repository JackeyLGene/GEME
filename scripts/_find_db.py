import os
r=r'C:\Users\Administrator.DESKTOP-EM03IHL\AppData\Roaming\CodeBuddy CN'
for dp,dn,fn in os.walk(r):
    for f in fn:
        fp=os.path.join(dp,f)
        sz=os.path.getsize(fp)
        if 'level' in f.lower() or f.endswith('.ldb') or f=='CURRENT' or f.startswith('MANIFEST'):
            print(f"  LEVELDB: {fp} ({sz} bytes)")
        if f.endswith('.sqlite') or f.endswith('.db'):
            print(f"  DB: {fp} ({sz} bytes)")
