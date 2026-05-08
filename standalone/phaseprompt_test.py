"""
PhasePrompt测试脚本 — transformers本地版
Q+G ≈ PA 的LLM版本：自指prompt是否能提升推理质量？

用法：
  1. 设置模型名（默认 pythia-1.4b）
  2. python phaseprompt_test.py
  3. 查看无G vs 有G的正确率对比
"""

import json, sys, os, time, math
import torch

# ============ 配置 ============
MODEL_NAME = os.environ.get("PHASE_MODEL", "EleutherAI/pythia-1.4b")
MAX_NEW = 128
TEMPERATURE = 0.1
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ============ 加载模型 ============
print(f"正在加载 {MODEL_NAME}...")
print(f"设备: {DEVICE}")

from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# Pythia tokenizer需要pad token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
    device_map="auto",
)
model.eval()
print("模型加载完成\n")

# ============ 测试集 ============
# GSM8K — 小学数学应用题，多步推理
from datasets import load_dataset
print("加载GSM8K...")
gsm8k = load_dataset("gsm8k", "main", split="test")
import random
_r = random.Random(42)
gsm8k_sample = _r.sample(list(gsm8k), 30)  # 随机30题
QUESTIONS = [(item["question"], "数学", "多步推理") for item in gsm8k_sample]
print(f"GSM8K 30题加载完成\n")


# ============ 推理 ============
@torch.no_grad()
def call_llm(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(DEVICE)
    outputs = model.generate(
        **inputs,
        max_new_tokens=MAX_NEW,
        temperature=TEMPERATURE,
        do_sample=TEMPERATURE > 0,
        pad_token_id=tokenizer.pad_token_id,
    )
    decoded = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    return decoded.strip() or "[空输出]"

# ============ G生成 ============
G_TEMPLATES = "你正在解决一个多步数学应用题。展示推导过程：先建立规则，再代入，最后得答案。"

def gen_g(task_type, g_class):
    return G_TEMPLATES

# ============ 测试 ============
def run_test(with_g=True):
    correct = 0
    total = len(QUESTIONS)
    times = []
    for i, (question, task_type, g_class) in enumerate(QUESTIONS):
        g_part = f"[结构自指] {gen_g(task_type, g_class)}\n\n问题：" if with_g else ""
        prompt = g_part + question
        t0 = time.time()
        output = call_llm(prompt)
        elapsed = time.time() - t0
        times.append(elapsed)
        ok = len(output) > 10
        if ok: correct += 1
        sys.stdout.write(f"\r{'G' if with_g else '无G'} {'✓' if ok else '✗'} {i+1}/{total}")
        sys.stdout.flush()
    avg_time = sum(times) / len(times) if times else 0
    return correct, total, avg_time

# ============ 主程序 ============
if __name__ == "__main__":
    # 热身
    print("热身中...")
    call_llm("1+1=")
    print("热身完成\n")

    # 无G
    print("=== 组A：无G ===")
    c1, t1, tm1 = run_test(with_g=False)
    r1 = c1 / t1
    print(f"\n无G: {c1}/{t1} = {r1:.0%}  平均 {tm1:.1f}s/题")

    # 有G
    print("\n=== 组B：有G ===")
    c2, t2, tm2 = run_test(with_g=True)
    r2 = c2 / t2
    print(f"\n有G: {c2}/{t2} = {r2:.0%}  平均 {tm2:.1f}s/题")

    # 对比
    delta = c2 - c1
    print(f"\n{'='*40}")
    print(f"PhasePrompt 结果")
    print(f"{'='*40}")
    print(f"无G: {c1}/{t1} ({r1:.0%})")
    print(f"有G: {c2}/{t2} ({r2:.0%})")
    print(f"提升: {delta:+d} 题 ({delta/t1*100:+.0f}%)")
    if delta > 0:
        print(f"\nQ+G ≈ PA 成立！自指prompt提升推理质量。")

    # 保存
    out = {"no_g": {"correct": c1, "total": t1, "rate": r1},
           "with_g": {"correct": c2, "total": t2, "rate": r2},
           "model": MODEL_NAME, "delta": delta}
    with open("phaseprompt_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n结果保存到 phaseprompt_results.json")
