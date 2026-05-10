"""Export conversation from message queue files."""
import json, os, glob

base = r"C:\Users\Administrator.DESKTOP-EM03IHL\AppData\Roaming\CodeBuddy CN\User\globalStorage\tencent-cloud.coding-copilot"
target_id = "c18de51b6eef44cda73c3cf535eb5740"
out = r"g:\GEME\docs\conversation_export.txt"

mq_dir = os.path.join(base, "message-queue")
all_entries = []

for fname in os.listdir(mq_dir):
    if not fname.endswith(".json"): continue
    fpath = os.path.join(mq_dir, fname)
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except: continue
    convs = data.get("conversations", {})
    if target_id in convs:
        items = convs[target_id].get("items", [])
        for item in items:
            ts = item.get("id", "")
            cbs = item.get("contentBlocks", [])
            texts = []
            for cb in cbs:
                if cb.get("type") == "text":
                    texts.append(cb.get("text", ""))
                elif cb.get("type") == "toolCall":
                    tc = cb.get("toolCall", {})
                    if tc.get("name") in ("execute_command",):
                        texts.append(f"[TOOL: {tc.get('name', '')}]")
                    elif tc.get("name") in ("write_to_file", "replace_in_file"):
                        ta = tc.get("toolArguments", {})
                        fpath2 = ta.get("filePath", "")
                        action = "WROTE" if tc.get("name") == "write_to_file" else "EDITED"
                        texts.append(f"[{action}: {os.path.basename(fpath2)}]")
            if texts:
                ts_human = ts[:15] if len(ts) > 15 else ts
                is_user = any("role" in cb.get("_meta",{}).get("codebuddy",{}) and
                            cb["_meta"]["codebuddy"].get("role")=="user"
                            for cb in cbs)
                role = "USER" if is_user else "ASSISTANT"
                for t in texts:
                    all_entries.append((ts, role, t))

all_entries.sort(key=lambda x: x[0])

with open(out, "w", encoding="utf-8") as f:
    f.write("=== GEME / PO-Phase Ouroboros 对话导出 ===\n")
    f.write(f"导出时间: {__import__('datetime').datetime.now()}\n\n")
    for ts, role, text in all_entries:
        f.write(f"[{role}] {text[:500]}")
        f.write("\n\n")

print(f"Exported {len(all_entries)} entries to {out}")
print(f"Total chars: {os.path.getsize(out)}")
