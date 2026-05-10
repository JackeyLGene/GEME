# 内时闭环：自观察帧进入帧经济 → 自迭代
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

class GEME_Conscious:
    def __init__(self):
        self.g = GEME(memory_cap=64, cooccur_window=80, cooccur_thresh=0.08, max_chains=15)
        self.g.memory.preserve_sig = True; self.g.memory._chain_cooccur_thresh = 2
        self.g.memory._merge_dists = [0.3]*50; self.g._induction_threshold = 3.0
        
        self.tick_interval = 10  # 当前自检间隔（会变化）
        self.base_interval = 10
        self.ticks = 0
        self.self_tick_count = 0
        self.prev_frame_count = 0
        self.last_frame_sigs = set()
        self.entropy_history = []
        
        # "本体感觉"：帧经济的熵
    def _frame_entropy(self):
        """帧经济的变化熵——多少帧新增/消失/变化"""
        cur = set()
        for f in self.g.memory.frames:
            cur.add((f.sig_full or f.sig)[:20])
        
        if not self.last_frame_sigs:
            self.last_frame_sigs = cur
            return 0.0
        
        n_cur = len(cur); n_prev = len(self.last_frame_sigs)
        added = len(cur - self.last_frame_sigs) / max(n_cur, 1)
        removed = len(self.last_frame_sigs - cur) / max(n_prev, 1)
        self.last_frame_sigs = cur
        
        # 权重变化（熵）
        w_total = sum(f.weight for f in self.g.memory.frames)
        if w_total == 0: return 0
        
        # 香农熵：frames的权重分布均匀度
        entropy = 0.0
        for f in self.g.memory.frames:
            p = f.weight / w_total
            if p > 0: entropy -= p * math.log2(p)
        
        # 归一化到 [0, 1]
        n = len(self.g.memory.frames)
        max_entropy = math.log2(n) if n > 0 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # 综合变化率 = 新增率 + 熵变
        change_rate = added + normalized_entropy * 0.3
        self.entropy_history.append(normalized_entropy)
        if len(self.entropy_history) > 100: self.entropy_history.pop(0)
        
        return change_rate
    
    def step(self, ext_vec=None, ext_sig=None):
        # 1. 处理外部输入
        if ext_vec is not None:
            self.g.process_vec(ext_vec, ext_sig)
        
        # 2. 计算帧经济变化率
        change = self._frame_entropy()
        
        # 3. 更新内部时间间隔
        # 变化大 → 自检密集（感觉到"有事"）
        # 变化小 → 自检稀疏（单调/睡眠）
        # 但：极高频自检会浪费资源——所以加饱和
        base = self.base_interval
        self.tick_interval = base / (1 + change * 3)
        # 限制范围 [1, base*2]
        self.tick_interval = max(1, min(base * 2, self.tick_interval))
        
        # 4. 步进计数器
        self.ticks += 1
        
        # 5. 到间隔了 → 自观察一次
        if self.ticks >= int(self.tick_interval):
            self._self_observe()
            self.ticks = 0
    
    def _self_observe(self):
        """自观察：把当前帧经济的特征编码为帧，注入自身"""
        self.self_tick_count += 1
        cur_entropy = self.entropy_history[-1] if self.entropy_history else 0
        
        # 编码自状态为向量
        v = [0.0]*_D27
        frames = self.g.memory.frames
        for i, f in enumerate(frames[:min(len(frames), 10)]):
            v[i] = f.weight / (sum(f.weight for f in frames) or 1)
        # 熵特征
        v[11] = cur_entropy
        # 当前内部时间间隔
        v[12] = self.tick_interval / self.base_interval
        
        sig = f"self_{self.self_tick_count}"
        self.g.process_vec(v, sig)
    
    def report(self):
        f = self.g.memory.frames
        self_frames = [x for x in f if "self_" in (x.sig_full or x.sig)]
        print(f"总帧数: {len(f)}; 自帧: {len(self_frames)}; 当前间隔: {self.tick_interval:.1f}")
        print(f"自观察次数: {self.self_tick_count}")
        if self_frames:
            top = sorted(self_frames, key=lambda x: x.weight, reverse=True)[:3]
            print("高权重自帧:")
            for t in top:
                s = t.sig_full or t.sig; print(f"  w={int(t.weight)} {s[:40]}")

print("="*55)
print("内时闭环：自观察帧进入帧经济")
print("="*55)
print()

g = GEME_Conscious()

# Phase 1: 静默——系统只有自观察
print("Phase 1: 纯自观察（无外部输入）")
for _ in range(500):
    g.step()
g.report()
print()

# Phase 2: 密集输入——帧经济活跃
print("Phase 2: 密集外部输入")
for i in range(2000):
    t = i * 0.01
    v = [0.0]*_D27; v[0] = math.cos(t*2)*0.8+0.1; v[1] = math.sin(t*2)*0.8+0.1
    g.step(v, f"ext")
g.report()
print()

# Phase 3: 恢复静默
print("Phase 3: 恢复静默")
for _ in range(500):
    g.step()
g.report()
