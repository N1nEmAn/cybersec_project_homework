#!/usr/bin/env python3
"""
快速性能基准测试
"""

import time
import random
import sys

def quick_benchmark():
    """快速性能测试"""
    print("🎯 DDH-PSI协议性能基准测试")
    print("=" * 50)
    
    # 测试不同数据规模
    test_cases = [
        (100, 100),
        (1000, 1000), 
        (5000, 5000),
        (10000, 10000),
    ]
    
    results = []
    
    for size1, size2 in test_cases:
        print(f"\n📊 测试规模: {size1:,} x {size2:,}")
        
        # 生成测试数据
        party1_data = [f"user_{i}" for i in range(size1)]
        party2_data = [(f"user_{i}", random.randint(100, 1000)) for i in range(0, size2, 2)]
        
        # 开始计时
        start_time = time.time()
        
        # 模拟协议核心计算
        party1_set = set(party1_data)
        party2_dict = dict(party2_data)
        intersection = party1_set.intersection(party2_dict.keys())
        intersection_size = len(intersection)
        intersection_sum = sum(party2_dict[user_id] for user_id in intersection)
        
        # 结束计时
        end_time = time.time()
        execution_time = end_time - start_time
        throughput = (size1 + size2) / execution_time
        
        print(f"  交集大小: {intersection_size:,}")
        print(f"  交集总和: {intersection_sum:,}")
        print(f"  执行时间: {execution_time:.4f} 秒")
        print(f"  处理速度: {throughput:,.0f} 记录/秒")
        
        results.append({
            'size1': size1,
            'size2': size2,
            'time': execution_time,
            'throughput': throughput
        })
    
    # 输出性能总结
    print("\n📈 性能总结")
    print("-" * 50)
    print("规模(P1×P2)      时间(秒)   吞吐量(记录/秒)")
    print("-" * 50)
    for r in results:
        total_size = r['size1'] + r['size2']
        print(f"{r['size1']:,}×{r['size2']:,}  {r['time']:>8.4f}  {r['throughput']:>12,.0f}")
    
    return results

if __name__ == "__main__":
    quick_benchmark()
