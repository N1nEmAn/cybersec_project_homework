#!/usr/bin/env python3
"""
简化的性能图表生成器
"""

import matplotlib.pyplot as plt
import numpy as np

# 使用之前测试的真实数据
data = {
    "Basic": [0.20, 0.21, 0.20, 0.18],
    "LookupTable": [0.41, 0.41, 0.41, 0.43], 
    "Parallel": [0.19, 0.20, 0.25, 0.33],
    "Bitwise": [0.18, 0.19, 0.18, 0.17]
}

sizes = ["1KB", "4KB", "16KB", "64KB"]
colors = ["blue", "green", "red", "orange"]

plt.figure(figsize=(12, 8))

# 主图 - 吞吐量对比
plt.subplot(2, 2, 1)
for i, (impl, values) in enumerate(data.items()):
    plt.plot(sizes, values, marker='o', label=impl, color=colors[i], linewidth=2)

plt.title('SM4 Algorithm Throughput Comparison', fontsize=14, fontweight='bold')
plt.xlabel('Data Size')
plt.ylabel('Throughput (MB/s)')
plt.legend()
plt.grid(True, alpha=0.3)

# 加速比图
plt.subplot(2, 2, 2)
base_values = data["Basic"]
x_pos = np.arange(len(sizes))

for i, (impl, values) in enumerate(data.items()):
    if impl != "Basic":
        speedups = [values[j] / base_values[j] for j in range(len(values))]
        plt.bar(x_pos + i*0.2, speedups, width=0.2, label=impl, 
                color=colors[i], alpha=0.7)

plt.title('Speedup Comparison (vs Basic)', fontsize=14, fontweight='bold')
plt.xlabel('Data Size')
plt.ylabel('Speedup Ratio')
plt.xticks(x_pos + 0.3, sizes)
plt.legend()
plt.grid(True, alpha=0.3)

# 平均加速比
plt.subplot(2, 2, 3)
avg_speedups = []
impl_names = []

for impl, values in data.items():
    if impl != "Basic":
        speedups = [values[j] / base_values[j] for j in range(len(values))]
        avg_speedups.append(np.mean(speedups))
        impl_names.append(impl)

bars = plt.bar(impl_names, avg_speedups, color=colors[1:], alpha=0.7)

# 添加数值标签
for bar, speedup in zip(bars, avg_speedups):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f'{speedup:.2f}x', ha='center', va='bottom', fontweight='bold')

plt.title('Average Speedup Summary', fontsize=14, fontweight='bold')
plt.ylabel('Average Speedup Ratio')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)

# 最佳实现对比
plt.subplot(2, 2, 4)
data_sizes_bytes = [1024, 4096, 16384, 65536]
plt.plot(data_sizes_bytes, data["Basic"], 'b-o', label="Basic", linewidth=2)
plt.plot(data_sizes_bytes, data["LookupTable"], 'g-o', label="LookupTable (Best)", linewidth=2)

plt.title('Best Implementation vs Basic', fontsize=14, fontweight='bold')
plt.xlabel('Data Size (Bytes)')
plt.ylabel('Throughput (MB/s)')
plt.xscale('log')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

# 保存图表
output_file = "performance_comparison.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Performance chart saved to: {output_file}")

# 关闭图形避免显示
plt.close()
