# 积分再现22帧量子化
# 从GEME的合并动力学直接数值积分
import math, random, statistics

r = 0.8          # 圆半径
dt = 0.01        # 时间步长
freq = 1.0       # 频率
dtheta = 2 * math.pi * freq * dt  # 每步弧度变化
steps = 3000

# 模拟GEME的合并过程
merge_dists = [0.3] * 50  # 初始合并距离记录
centroid = None           # 当前帧重心
frame_count = 0
frame_boundaries = []     # 新帧创建的位置

for i in range(steps):
    theta = dtheta * i
    v = (math.cos(theta) * r + 0.1, math.sin(theta) * r + 0.1)
    
    if centroid is None:
        # 创建第一帧
        centroid = v
        frame_count += 1
        frame_boundaries.append(theta)
        continue
    
    # 计算到当前帧重心的距离
    d = math.sqrt((v[0] - centroid[0])**2 + (v[1] - centroid[1])**2)
    
    # 自适应阈值
    if merge_dists:
        med = statistics.median(merge_dists[-50:])
        last_ok = merge_dists[-1] if merge_dists else 0.001
        thresh = max(med * 1.5, last_ok * 0.5)
    else:
        thresh = 0.3
    
    if d <= thresh:
        # 合并：更新重心（加权平均，权重 ≈ 累积合并次数）
        # 模拟: 权重 = 目前已合并的次数
        merge_dists.append(d)
        if len(merge_dists) > 100:
            merge_dists.pop(0)
        # 重心更新（等权累积平均）
        k = i - sum(1 for b in frame_boundaries if b < theta)  # 当前帧内步数
        if k == 0: k = 1
        centroid = ((centroid[0]*(k-1) + v[0])/k, 
                     (centroid[1]*(k-1) + v[1])/k)
    else:
        # 新建帧
        centroid = v
        frame_count += 1
        frame_boundaries.append(theta)

total_circ = frame_count
print(f"积分结果：{total_circ}帧（GEME实验：22帧）")
print(f"帧间距：{2*math.pi/total_circ:.4f}弧度 = {(2*math.pi/total_circ)*180/math.pi:.1f}度")

# 分析：帧间距是否均匀
angles = sorted([b % (2*math.pi) for b in frame_boundaries])
gaps = []
for i in range(len(angles)-1):
    gaps.append(angles[i+1] - angles[i])
if gaps:
    avg_gap = statistics.mean(gaps)
    std_gap = statistics.stdev(gaps) if len(gaps)>1 else 0
    print(f"平均帧间距：{avg_gap:.4f}弧度 ± {std_gap:.4f}")
    print(f"均匀度：{std_gap/avg_gap:.2f} {'均匀' if std_gap/avg_gap < 0.3 else '不均匀'}")
