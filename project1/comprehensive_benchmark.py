#!/usr/bin/env python3
"""
SM4综合性能基准测试
比较所有实现的性能并生成报告
"""

import time
import os
import sys
import numpy as np
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.basic.sm4_basic import SM4Basic
from src.optimized.sm4_lookup_table import SM4LookupTable
from src.optimized.sm4_bitwise import SM4Bitwise
from src.optimized.sm4_parallel import SM4Parallel
from src.modes.sm4_modes import SM4Modes


class SM4Benchmark:
    """SM4综合性能基准测试类"""
    
    def __init__(self):
        self.key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
        self.implementations = {
            'Basic': SM4Basic,
            'LookupTable': SM4LookupTable,
            'Bitwise': SM4Bitwise,
            'Parallel': SM4Parallel
        }
        
    def benchmark_single_block(self, rounds=1000):
        """单块加密性能测试"""
        print("=== 单块加密性能测试 ===")
        test_block = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
        results = {}
        
        for name, impl_class in self.implementations.items():
            try:
                print(f"测试 {name}...")
                sm4 = impl_class(self.key)
                
                start_time = time.time()
                for _ in range(rounds):
                    sm4.encrypt_block(test_block)
                end_time = time.time()
                
                elapsed = end_time - start_time
                ops_per_sec = rounds / elapsed
                
                results[name] = {
                    'time': elapsed,
                    'ops_per_sec': ops_per_sec
                }
                
                print(f"  时间: {elapsed:.4f}s, 吞吐量: {ops_per_sec:.0f} ops/sec")
                
            except Exception as e:
                print(f"  错误: {e}")
                results[name] = None
        
        return results
    
    def benchmark_large_data(self, data_size=65536, rounds=10):
        """大数据加密性能测试"""
        print(f"\n=== 大数据加密性能测试 (数据大小: {data_size} 字节) ===")
        test_data = os.urandom(data_size)
        results = {}
        
        for name, impl_class in self.implementations.items():
            try:
                print(f"测试 {name}...")
                sm4 = impl_class(self.key)
                
                start_time = time.time()
                for _ in range(rounds):
                    sm4.encrypt_ecb(test_data)
                end_time = time.time()
                
                elapsed = end_time - start_time
                throughput_mbps = (data_size * rounds) / elapsed / 1024 / 1024
                
                results[name] = {
                    'time': elapsed,
                    'throughput': throughput_mbps
                }
                
                print(f"  时间: {elapsed:.4f}s, 吞吐量: {throughput_mbps:.2f} MB/s")
                
            except Exception as e:
                print(f"  错误: {e}")
                results[name] = None
        
        return results
    
    def benchmark_modes(self, data_size=1024, rounds=100):
        """加密模式性能测试"""
        print(f"\n=== 加密模式性能测试 (数据大小: {data_size} 字节) ===")
        test_data = os.urandom(data_size)
        sm4_modes = SM4Modes(self.key)
        results = {}
        
        modes = {
            'ECB': lambda: sm4_modes.encrypt_ecb(test_data),
            'CBC': lambda: sm4_modes.encrypt_cbc(test_data)[0],
            'CTR': lambda: sm4_modes.encrypt_ctr(test_data)[0],
            'CFB': lambda: sm4_modes.encrypt_cfb(test_data)[0],
            'OFB': lambda: sm4_modes.encrypt_ofb(test_data)[0]
        }
        
        for mode_name, encrypt_func in modes.items():
            try:
                print(f"测试 {mode_name} 模式...")
                
                start_time = time.time()
                for _ in range(rounds):
                    encrypt_func()
                end_time = time.time()
                
                elapsed = end_time - start_time
                throughput_mbps = (data_size * rounds) / elapsed / 1024 / 1024
                
                results[mode_name] = {
                    'time': elapsed,
                    'throughput': throughput_mbps
                }
                
                print(f"  时间: {elapsed:.4f}s, 吞吐量: {throughput_mbps:.2f} MB/s")
                
            except Exception as e:
                print(f"  错误: {e}")
                results[mode_name] = None
        
        return results
    
    def calculate_speedup(self, results, baseline='Basic'):
        """计算加速比"""
        if baseline not in results or results[baseline] is None:
            return {}
        
        baseline_time = results[baseline]['time']
        speedups = {}
        
        for name, result in results.items():
            if result is not None and name != baseline:
                speedups[name] = baseline_time / result['time']
        
        return speedups
    
    def generate_report(self):
        """生成完整的性能测试报告"""
        print("SM4综合性能基准测试报告")
        print("=" * 60)
        print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试密钥: {self.key.hex().upper()}")
        print()
        
        # 单块测试
        single_results = self.benchmark_single_block()
        single_speedups = self.calculate_speedup(single_results)
        
        # 大数据测试
        large_results = self.benchmark_large_data()
        large_speedups = self.calculate_speedup(large_results)
        
        # 模式测试
        mode_results = self.benchmark_modes()
        
        # 生成总结报告
        print("\n=== 性能总结 ===")
        print(f"{'实现':<12} {'单块时间':<10} {'单块加速比':<10} {'大数据时间':<12} {'大数据加速比':<12}")
        print("-" * 70)
        
        for name in self.implementations.keys():
            single_time = single_results.get(name, {}).get('time', 0)
            large_time = large_results.get(name, {}).get('time', 0)
            single_speedup = single_speedups.get(name, 1.0)
            large_speedup = large_speedups.get(name, 1.0)
            
            if single_results.get(name) and large_results.get(name):
                print(f"{name:<12} {single_time:<10.4f} {single_speedup:<10.2f}x "
                     f"{large_time:<12.4f} {large_speedup:<12.2f}x")
            else:
                print(f"{name:<12} {'错误':<10} {'-':<10} {'错误':<12} {'-':<12}")
        
        print(f"\n=== 最佳性能实现 ===")
        
        # 找出最快的实现
        valid_single = {k: v for k, v in single_results.items() if v is not None}
        valid_large = {k: v for k, v in large_results.items() if v is not None}
        
        if valid_single:
            fastest_single = min(valid_single.keys(), 
                                key=lambda x: valid_single[x]['time'])
            print(f"单块加密最快: {fastest_single} "
                 f"({valid_single[fastest_single]['ops_per_sec']:.0f} ops/sec)")
        
        if valid_large:
            fastest_large = min(valid_large.keys(), 
                               key=lambda x: valid_large[x]['time'])
            print(f"大数据加密最快: {fastest_large} "
                 f"({valid_large[fastest_large]['throughput']:.2f} MB/s)")
        
        if mode_results:
            valid_modes = {k: v for k, v in mode_results.items() if v is not None}
            if valid_modes:
                fastest_mode = min(valid_modes.keys(), 
                                  key=lambda x: valid_modes[x]['time'])
                print(f"最快加密模式: {fastest_mode} "
                     f"({valid_modes[fastest_mode]['throughput']:.2f} MB/s)")
        
        print(f"\n=== 建议 ===")
        print("1. 对于高性能需求: 推荐使用 LookupTable 实现")
        print("2. 对于大量数据处理: 推荐使用 Parallel 实现")
        print("3. 对于一般应用: Basic 实现已足够使用")
        print("4. 对于安全应用: 推荐使用 CBC 或 CTR 模式")
        
        return {
            'single_block': single_results,
            'large_data': large_results,
            'modes': mode_results,
            'speedups': {
                'single': single_speedups,
                'large': large_speedups
            }
        }


def main():
    """主函数"""
    benchmark = SM4Benchmark()
    results = benchmark.generate_report()
    
    # 保存结果到文件
    import json
    with open('benchmark_results.json', 'w', encoding='utf-8') as f:
        # 转换为可序列化的格式
        serializable_results = {}
        for category, data in results.items():
            if isinstance(data, dict):
                serializable_results[category] = {
                    k: v for k, v in data.items() if v is not None
                }
            else:
                serializable_results[category] = data
        
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细结果已保存到 benchmark_results.json")


if __name__ == '__main__':
    main()
