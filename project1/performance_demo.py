#!/usr/bin/env python3
"""
SM4算法性能对比演示
直观展示不同实现的加速效果
"""

import time
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.basic.sm4_basic import SM4Basic
from src.optimized.sm4_lookup_table import SM4LookupTable
from src.optimized.sm4_parallel import SM4Parallel
from src.optimized.sm4_bitwise import SM4Bitwise


def measure_performance(sm4_impl, test_data, rounds=100):
    """测量单个实现的性能"""
    # 预热
    sm4_impl.encrypt_ecb(test_data[:16])
    
    # 正式测试
    start_time = time.perf_counter()
    for _ in range(rounds):
        sm4_impl.encrypt_ecb(test_data)
    end_time = time.perf_counter()
    
    return end_time - start_time


def performance_comparison():
    """性能对比主函数"""
    print("🚀 SM4算法性能对比演示")
    print("=" * 50)
    
    # 测试参数
    key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    data_sizes = [1024, 4096, 16384, 65536]  # 1KB, 4KB, 16KB, 64KB
    rounds = 50
    
    # 实现列表
    implementations = [
        ("基础实现", SM4Basic, "blue"),
        ("查找表优化", SM4LookupTable, "green"), 
        ("并行优化", SM4Parallel, "red"),
        ("位运算优化", SM4Bitwise, "orange")
    ]
    
    results = {}
    
    print("正在测试各种实现...")
    
    for impl_name, impl_class, color in implementations:
        print(f"\n📊 测试 {impl_name}...")
        sm4 = impl_class(key)
        results[impl_name] = []
        
        for size in data_sizes:
            test_data = os.urandom(size)
            elapsed = measure_performance(sm4, test_data, rounds)
            throughput = (size * rounds) / elapsed / 1024 / 1024  # MB/s
            results[impl_name].append(throughput)
            print(f"  {size//1024}KB: {throughput:.2f} MB/s")
    
    # 计算加速比
    print("\n⚡ 加速比分析 (相对基础实现):")
    base_results = results["基础实现"]
    
    for impl_name in results:
        if impl_name != "基础实现":
            speedups = [results[impl_name][i] / base_results[i] 
                       for i in range(len(data_sizes))]
            avg_speedup = np.mean(speedups)
            print(f"  {impl_name}: {avg_speedup:.2f}x 平均加速")
    
    # 绘制性能图表
    plot_performance(data_sizes, results, implementations)


def plot_performance(data_sizes, results, implementations):
    """绘制性能对比图表"""
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.figure(figsize=(12, 8))
    
    # 主图 - 吞吐量对比
    plt.subplot(2, 2, 1)
    x_labels = [f"{size//1024}KB" for size in data_sizes]
    
    for impl_name, _, color in implementations:
        if impl_name in results:
            plt.plot(x_labels, results[impl_name], 
                    marker='o', label=impl_name, color=color, linewidth=2)
    
    plt.title('SM4算法吞吐量对比', fontsize=14, fontweight='bold')
    plt.xlabel('数据大小')
    plt.ylabel('吞吐量 (MB/s)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 加速比图
    plt.subplot(2, 2, 2)
    base_results = results["基础实现"]
    
    for impl_name, _, color in implementations:
        if impl_name != "基础实现" and impl_name in results:
            speedups = [results[impl_name][i] / base_results[i] 
                       for i in range(len(data_sizes))]
            plt.bar([i + implementations.index((impl_name, _, color)) * 0.2 
                    for i in range(len(x_labels))], 
                   speedups, width=0.2, label=impl_name, color=color, alpha=0.7)
    
    plt.title('加速比对比 (相对基础实现)', fontsize=14, fontweight='bold')
    plt.xlabel('数据大小')
    plt.ylabel('加速比')
    plt.xticks(range(len(x_labels)), x_labels)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 性能随数据大小变化
    plt.subplot(2, 2, 3)
    best_impl = max(results.keys(), 
                   key=lambda x: np.mean(results[x]) if x != "基础实现" else 0)
    
    plt.plot(data_sizes, results["基础实现"], 
            'b-o', label="基础实现", linewidth=2)
    plt.plot(data_sizes, results[best_impl], 
            'g-o', label=f"{best_impl} (最优)", linewidth=2)
    
    plt.title('最优实现 vs 基础实现', fontsize=14, fontweight='bold')
    plt.xlabel('数据大小 (字节)')
    plt.ylabel('吞吐量 (MB/s)')
    plt.xscale('log')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 优化效果总结
    plt.subplot(2, 2, 4)
    impl_names = [name for name, _, _ in implementations if name != "基础实现"]
    avg_speedups = []
    
    for impl_name in impl_names:
        if impl_name in results:
            speedups = [results[impl_name][i] / base_results[i] 
                       for i in range(len(data_sizes))]
            avg_speedups.append(np.mean(speedups))
        else:
            avg_speedups.append(0)
    
    colors = [color for name, _, color in implementations if name != "基础实现"]
    bars = plt.bar(impl_names, avg_speedups, color=colors, alpha=0.7)
    
    # 添加数值标签
    for bar, speedup in zip(bars, avg_speedups):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{speedup:.2f}x', ha='center', va='bottom', fontweight='bold')
    
    plt.title('平均加速比总结', fontsize=14, fontweight='bold')
    plt.ylabel('平均加速比')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图表
    output_file = "performance_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n📈 性能图表已保存到: {output_file}")
    
    # 显示图表
    plt.show()


def algorithm_complexity_analysis():
    """算法复杂度分析"""
    print("\n🔬 算法复杂度理论分析")
    print("=" * 50)
    
    print("基础实现复杂度:")
    print("  - S盒变换: O(1) 查表操作 × 4次 = O(4)")
    print("  - 线性变换: O(1) 位运算 × 3次 = O(3)")  
    print("  - 单轮复杂度: O(7)")
    print("  - 32轮总复杂度: O(224)")
    
    print("\n查找表优化复杂度:")
    print("  - 预计算合并变换: O(1) 查表操作 × 1次 = O(1)")
    print("  - 单轮复杂度: O(1)")
    print("  - 32轮总复杂度: O(32)")
    print("  - 理论加速比: 224/32 = 7.0x")
    print("  - 实际加速比: ~2.0x (受内存访问限制)")
    
    print("\n并行优化复杂度:")
    print("  - 多线程处理: O(224/n) where n = 线程数")
    print("  - 通信开销: O(log n)")
    print("  - 实际加速比: ~1.6x (受Python GIL限制)")


if __name__ == "__main__":
    try:
        performance_comparison()
        algorithm_complexity_analysis()
        
        print("\n✅ 性能对比演示完成!")
        print("查看生成的 performance_comparison.png 了解详细对比结果")
        
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请安装: pip install matplotlib numpy")
    except Exception as e:
        print(f"运行出错: {e}")
