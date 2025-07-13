"""
快速性能基准测试
用于快速验证和演示
"""

import time
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from basic.sm4_basic import SM4Basic
from optimized.sm4_lookup_table import SM4LookupTable
from optimized.sm4_bitwise import SM4Bitwise
from utils.constants import TEST_VECTORS
from utils.helpers import format_hex

def quick_benchmark():
    """快速性能测试"""
    print("=== SM4快速性能基准测试 ===")
    
    key = TEST_VECTORS['key']
    plaintext = TEST_VECTORS['plaintext']
    
    # 创建实现实例
    print("初始化实现...")
    sm4_basic = SM4Basic(key)
    sm4_lookup = SM4LookupTable(key)
    sm4_bitwise = SM4Bitwise(key)
    
    implementations = {
        'Basic': sm4_basic,
        'LookupTable': sm4_lookup,
        'Bitwise': sm4_bitwise
    }
    
    # 快速单分组测试
    print("\n单分组加密性能测试 (1000次):")
    iterations = 1000
    
    results = {}
    for name, impl in implementations.items():
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            impl.encrypt(plaintext)
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        throughput = iterations / elapsed
        
        results[name] = {
            'time': elapsed,
            'throughput': throughput
        }
        
        print(f"  {name:12}: {elapsed:.4f}秒, {throughput:.2f} ops/sec")
    
    # 计算加速比
    print("\n性能提升:")
    basic_throughput = results['Basic']['throughput']
    
    for name in ['LookupTable', 'Bitwise']:
        speedup = results[name]['throughput'] / basic_throughput
        print(f"  {name} vs Basic: {speedup:.2f}x")
    
    # 大数据测试
    print("\n大数据加密测试 (64KB):")
    large_data = plaintext * 4096  # 64KB
    
    for name, impl in implementations.items():
        start_time = time.perf_counter()
        ciphertext = impl.encrypt(large_data)
        end_time = time.perf_counter()
        
        elapsed = end_time - start_time
        throughput_mb = (64 / 1024) / elapsed  # MB/s
        
        print(f"  {name:12}: {elapsed:.4f}秒, {throughput_mb:.2f} MB/s")
    
    print("\n✓ 快速基准测试完成")

if __name__ == "__main__":
    quick_benchmark()
