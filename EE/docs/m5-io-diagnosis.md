# M5 IO 瓶颈诊断报告

**日期：** 2026-05-20
**状态：** 已修复

---

## 问题

M5 积累实验（`archive_run.py`）在 16 We × 3 代运行中出现卡死。症状：进程状态停滞，无崩溃但无输出。

---

## 根因

三个问题叠加：

### P0：JSON 文件 IO

每个 worker 写一篇 JSON 到临时目录，主进程完成后逐一读取。16 worker × 3 代 = 96 次文件读写。`ProcessPoolExecutor.submit().result()` 已经可以通过返回值和管道传回主进程内存——JSON 是多余的。

### P0：MIDI 编码在 worker 内重复执行

每次 `we_worker` 被调用时都 `importlib` 加载 `wtc_scores.py` 并 `midi_encode`。16 worker × 3 代 = 48 次。MIDI 编码是 CPU 密集操作，且同一文件被 16 个进程并发加载——Windows 文件锁使各进程陷入等待。

### P1：临时目录竞争

`tempfile.mkdtemp` 下所有 worker 同时进行文件写入——IO 时间片竞争累积延迟至超时级别。

---

## 修复

| 变更 | 说明 |
|------|------|
| MIDI 预编码 | 主进程预编码所有段，传 `(vec, label)` 列表给 worker——零 IO |
| 移除 JSON | worker 通过 `return {'entries': [...], ...}` 直接返回结果——`pool.map()` 收集 |
| 移除 tempdir | 不再需要临时目录 |
| `pool.map()` 替代 | 使用 `map` 简化未来并行，自动等待收集 |

---

## 预期效果

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| 每代 IO 操作 | 16+X（MIDI编码）+16（JSON写）+16（JSON读） | 0 |
| 卡死概率 | 高（Windows文件锁） | 无文件锁 |
| 缩放至 N=128 | 不可行 | 可行（IO不再随N增长） |
