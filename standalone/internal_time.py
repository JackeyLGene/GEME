# 内部时间：GEME自生成的时间尺度
# 不再是"外部输入驱动步进"——而是帧经济自监视
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM

_r = random.Random(42)

class GEME_InternalTime:
    """给GEME加一个内时模块"""
    def __init__(self, base_interval=5):
        self.g = GEME(memory_cap=32, cooccur_window=60, cooccur_thresh=0.08, max_chains=10)
        self.g.memory.preserve_sig = True; self.g.memory._chain_cooccur_thresh = 2
        self.g.memory._merge_dists = [0.3]*50; self.g._induction_threshold = 2.0
        
        self.base_interval = base_interval  # 基础心跳间隔（外部步数）
        self.tick_count = 0
        self.snapshots = []  # 自观察历史
        self.last_frame_sig = set()
        self.tick_speed = 1.0  # 当前内部时间流速
        
        # 内时专用的"心跳"向量
        self.tick_vec = [0.0]*_VEC_DIM; self.tick_vec[0] = 1.0
    
    def step(self, ext_vec=None, ext_sig=None):
        """一个外部步进（带或不带外部输入）"""
        if ext_vec is not None:
            self.g.process_vec(ext_vec, ext_sig)
        
        # 检查帧经济的变化率
        current_frames = set()
        for f in self.g.memory.frames:
            current_frames.add(f.sig_full or f.sig)
        
        if self.last_frame_sig:
            # 帧变化率 = 新增+消失的帧数 / 总帧数
            added = len(current_frames - self.last_frame_sig)
            removed = len(self.last_frame_sig - current_frames)
            change_rate = (added + removed) / max(len(current_frames), 1)
        else:
            change_rate = 0
        
        self.last_frame_sig = current_frames
        
        # 内部时间流速 = 基础间隔 / (1 + 变化率)
        # 变化大时（帧经济活跃）→ 间隔变小（时间变快）？NO——变化大时应该时间变慢？
        # 让我们试两者：
        # 变化率大 → 很多事情发生 → 内时需要更密集采样 → tick间隔变小
        # 但物理对应：更多帧→时间分辨率更细→"时间变慢"
        # 内部时间：系统对自身变化率的感知——变化快时感觉"很多事发生"
        # 所以：变化率大 → tick间隔大？还是小？
        
        # 暂时用：变化率大→tick间隔变小（为了尽快捕捉变化）
        self.tick_speed = self.base_interval / (1 + change_rate * 5)
        
        # 判断是否要自检一次
        self.tick_count += 1
        if self.tick_count >= max(1, int(self.tick_speed)):
            self._self_observe()
            self.tick_count = 0
    
    def _self_observe(self):
        """GEME观察自己的帧经济状态，生成一个'意识帧'"""
        frames = self.g.memory.frames
        state_vec = [0.0]*_VEC_DIM
        
        # 编码：当前帧权重的分布
        total_w = sum(f.weight for f in frames) or 1
        for i, f in enumerate(frames[:_VEC_DIM]):
            state_vec[i % _VEC_DIM] = f.weight / total_w
        
        sig = f"self_tick_{len(self.snapshots)}"
        self.g.process_vec(state_vec, sig)
        self.snapshots.append({
            "tick": len(self.snapshots),
            "speed": self.tick_speed,
            "frames": len(frames),
            "change_rate": None,  # 来不及算
        })

def run_test():
    """测试：先无输入跑内部时间，再有输入跑"""
    g = GEME_InternalTime(base_interval=10)
    
    print("="*55)
    print("内部时间测试：无输入状态")
    print("="*55)
    print()
    
    # Phase 1: 无外部输入——纯内部心跳
    for _ in range(200):
        g.step()
    print(f"无输入阶段：{len(g.snapshots)}次自检, {len(g.g.memory.frames)}帧")
    print(f"  自检频率变化: ", end="")
    speeds_before = [s["speed"] for s in g.snapshots[:5]]
    print(f"前5次[{speeds_before[0]:.1f}→{speeds_before[-1]:.1f}], ", end="")
    speeds_after = [s["speed"] for s in g.snapshots[-5:]]
    print(f"后5次[{speeds_after[0]:.1f}→{speeds_after[-1]:.1f}]")
    
    # Phase 2: 高密度外部输入
    print(f"\n高密度输入阶段：")
    for i in range(500):
        v = [0.0]*_VEC_DIM; v[0] = math.cos(i*0.01)*0.8+0.1; v[1] = math.sin(i*0.01)*0.8+0.1
        g.step(v, f"ext_{i%20}")
    
    speeds_input = [s["speed"] for s in g.snapshots[-10:]]
    avg_speed = statistics.mean(speeds_input)
    print(f"  输入后10次自检平均速度: {avg_speed:.2f}")
    print(f"  自检总数: {len(g.snapshots)}")
    
    # Phase 3: 停止输入——看内时是否收敛回基线
    print(f"\n恢复无输入阶段：")
    for _ in range(300):
        g.step()
    
    speeds_rest = [s["speed"] for s in g.snapshots[-5:]]
    avg_rest = statistics.mean(speeds_rest)
    print(f"  恢复后5次自检平均速度: {avg_rest:.2f}")
    
    if avg_speed < avg_rest:
        print("\n结果：输入活跃→自检间隔变小→系统'感知到事发生了'")
    else:
        print(f"\n结果：输入活跃→自检间隔{avg_speed:.1f} 恢复→{avg_rest:.1f}")
        print("  差异不大——可能需要调整self_tick_speed公式")

run_test()
