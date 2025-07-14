#!/usr/bin/env python3
"""
SM2椭圆曲线数字签名算法性能基准测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import secrets
import statistics
from typing import List, Tuple, Dict
from src.sm2_basic import SM2Basic
from src.sm2_optimized import SM2Optimized
from src.sm2_parallel import SM2Parallel

class SM2Benchmark:
    """SM2性能基准测试类"""
    
    def __init__(self):
        self.sm2_basic = SM2Basic()
        self.sm2_optimized = SM2Optimized()
        self.sm2_parallel = SM2Parallel(num_threads=4)
        self.results = {}
    
    def benchmark_scalar_multiplication(self, iterations: int = 100) -> Dict[str, float]:
        """基准测试标量乘法算法"""
        print(f"\n=== 标量乘法性能测试 ({iterations} 次迭代) ===")
        
        # 生成随机标量
        scalars = [secrets.randbelow(self.sm2_basic.n - 1) + 1 for _ in range(iterations)]
        P = self.sm2_basic.G
        
        methods = {
            "基础二进制": lambda k: self.sm2_basic.point_multiply(k, P),
            "NAF": lambda k: self.sm2_optimized.point_multiply_naf(k, P),
            "滑动窗口": lambda k: self.sm2_optimized.point_multiply_window(k, P),
            "Montgomery阶梯": lambda k: self.sm2_optimized.montgomery_ladder(k, P),
            "预计算优化": lambda k: self.sm2_optimized.point_multiply_optimized(k, P),
        }
        
        results = {}
        
        for method_name, method_func in methods.items():
            print(f"测试 {method_name}...")
            
            times = []
            for k in scalars:
                start_time = time.perf_counter()
                result = method_func(k)
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)  # 转换为毫秒
            
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times) if len(times) > 1 else 0
            results[method_name] = {
                'avg': avg_time,
                'std': std_time,
                'min': min(times),
                'max': max(times)
            }
            
            print(f"  平均时间: {avg_time:.3f} ± {std_time:.3f} ms")
        
        self.results['scalar_multiplication'] = results
        return results
    
    def benchmark_keypair_generation(self, iterations: int = 100) -> Dict[str, float]:
        """基准测试密钥对生成"""
        print(f"\n=== 密钥对生成性能测试 ({iterations} 次迭代) ===")
        
        methods = {
            "基础实现": lambda: self.sm2_basic.generate_keypair(),
            "优化实现": lambda: self.sm2_optimized.generate_keypair_optimized(),
        }
        
        results = {}
        
        for method_name, method_func in methods.items():
            print(f"测试 {method_name}...")
            
            times = []
            for _ in range(iterations):
                start_time = time.perf_counter()
                private_key, public_key = method_func()
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)
            
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times) if len(times) > 1 else 0
            results[method_name] = {
                'avg': avg_time,
                'std': std_time,
                'min': min(times),
                'max': max(times)
            }
            
            print(f"  平均时间: {avg_time:.3f} ± {std_time:.3f} ms")
        
        # 批量密钥生成测试
        print("测试 批量生成...")
        start_time = time.perf_counter()
        keypairs = self.sm2_parallel.batch_generate_keypairs(iterations)
        end_time = time.perf_counter()
        
        batch_time = (end_time - start_time) * 1000 / iterations
        results["批量生成"] = {
            'avg': batch_time,
            'std': 0,
            'min': batch_time,
            'max': batch_time
        }
        print(f"  平均时间: {batch_time:.3f} ms/operation")
        
        self.results['keypair_generation'] = results
        return results
    
    def benchmark_signing(self, iterations: int = 100) -> Dict[str, float]:
        """基准测试数字签名"""
        print(f"\n=== 数字签名性能测试 ({iterations} 次迭代) ===")
        
        # 准备测试数据
        message = b"Benchmark test message for SM2 digital signature"
        private_key, public_key = self.sm2_optimized.generate_keypair_optimized()
        
        methods = {
            "基础实现": lambda: self.sm2_basic.sign(message, private_key),
            "优化实现": lambda: self.sm2_optimized.sign_optimized(message, private_key),
        }
        
        results = {}
        
        for method_name, method_func in methods.items():
            print(f"测试 {method_name}...")
            
            times = []
            for _ in range(iterations):
                start_time = time.perf_counter()
                signature = method_func()
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)
            
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times) if len(times) > 1 else 0
            results[method_name] = {
                'avg': avg_time,
                'std': std_time,
                'min': min(times),
                'max': max(times)
            }
            
            print(f"  平均时间: {avg_time:.3f} ± {std_time:.3f} ms")
        
        # 批量签名测试
        print("测试 批量签名...")
        messages = [message] * iterations
        private_keys = [private_key] * iterations
        
        start_time = time.perf_counter()
        signatures = self.sm2_parallel.batch_sign(messages, private_keys)
        end_time = time.perf_counter()
        
        batch_time = (end_time - start_time) * 1000 / iterations
        results["批量签名"] = {
            'avg': batch_time,
            'std': 0,
            'min': batch_time,
            'max': batch_time
        }
        print(f"  平均时间: {batch_time:.3f} ms/operation")
        
        self.results['signing'] = results
        return results
    
    def benchmark_verification(self, iterations: int = 100) -> Dict[str, float]:
        """基准测试签名验证"""
        print(f"\n=== 签名验证性能测试 ({iterations} 次迭代) ===")
        
        # 准备测试数据
        message = b"Benchmark test message for SM2 signature verification"
        private_key, public_key = self.sm2_optimized.generate_keypair_optimized()
        signature = self.sm2_optimized.sign_optimized(message, private_key)
        
        methods = {
            "基础实现": lambda: self.sm2_basic.verify(message, signature, public_key),
            "优化实现": lambda: self.sm2_optimized.verify_optimized(message, signature, public_key),
            "预计算优化": lambda: self.sm2_parallel.optimized_verify_with_precomputation(message, signature, public_key),
        }
        
        results = {}
        
        for method_name, method_func in methods.items():
            print(f"测试 {method_name}...")
            
            times = []
            for _ in range(iterations):
                start_time = time.perf_counter()
                is_valid = method_func()
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)
                assert is_valid, f"{method_name} 验证失败"
            
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times) if len(times) > 1 else 0
            results[method_name] = {
                'avg': avg_time,
                'std': std_time,
                'min': min(times),
                'max': max(times)
            }
            
            print(f"  平均时间: {avg_time:.3f} ± {std_time:.3f} ms")
        
        # 批量验证测试
        print("测试 批量验证...")
        messages = [message] * iterations
        signatures = [signature] * iterations
        public_keys = [public_key] * iterations
        
        start_time = time.perf_counter()
        results_batch = self.sm2_parallel.batch_verify(messages, signatures, public_keys)
        end_time = time.perf_counter()
        
        batch_time = (end_time - start_time) * 1000 / iterations
        results["批量验证"] = {
            'avg': batch_time,
            'std': 0,
            'min': batch_time,
            'max': batch_time
        }
        print(f"  平均时间: {batch_time:.3f} ms/operation")
        assert all(results_batch), "批量验证失败"
        
        self.results['verification'] = results
        return results
    
    def benchmark_end_to_end(self, iterations: int = 100) -> Dict[str, float]:
        """端到端性能测试"""
        print(f"\n=== 端到端性能测试 ({iterations} 次迭代) ===")
        
        message = b"End-to-end benchmark test message"
        
        implementations = {
            "基础实现": (
                self.sm2_basic.generate_keypair,
                self.sm2_basic.sign,
                self.sm2_basic.verify
            ),
            "优化实现": (
                self.sm2_optimized.generate_keypair_optimized,
                self.sm2_optimized.sign_optimized,
                self.sm2_optimized.verify_optimized
            ),
        }
        
        results = {}
        
        for impl_name, (keygen_func, sign_func, verify_func) in implementations.items():
            print(f"测试 {impl_name}...")
            
            times = []
            for _ in range(iterations):
                start_time = time.perf_counter()
                
                # 密钥生成
                private_key, public_key = keygen_func()
                
                # 数字签名
                signature = sign_func(message, private_key)
                
                # 签名验证
                is_valid = verify_func(message, signature, public_key)
                
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)
                assert is_valid, f"{impl_name} 端到端验证失败"
            
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times) if len(times) > 1 else 0
            results[impl_name] = {
                'avg': avg_time,
                'std': std_time,
                'min': min(times),
                'max': max(times)
            }
            
            print(f"  平均时间: {avg_time:.3f} ± {std_time:.3f} ms")
        
        # 并行批量测试
        print("测试 并行批量...")
        start_time = time.perf_counter()
        
        keypairs = self.sm2_parallel.batch_generate_keypairs(iterations)
        messages = [message] * iterations
        private_keys = [kp[0] for kp in keypairs]
        public_keys = [kp[1] for kp in keypairs]
        
        signatures = self.sm2_parallel.batch_sign(messages, private_keys)
        results_batch = self.sm2_parallel.batch_verify(messages, signatures, public_keys)
        
        end_time = time.perf_counter()
        
        batch_time = (end_time - start_time) * 1000 / iterations
        results["并行批量"] = {
            'avg': batch_time,
            'std': 0,
            'min': batch_time,
            'max': batch_time
        }
        print(f"  平均时间: {batch_time:.3f} ms/operation")
        assert all(results_batch), "并行批量验证失败"
        
        self.results['end_to_end'] = results
        return results
    
    def print_summary(self):
        """打印性能测试摘要"""
        print("\n" + "=" * 80)
        print("SM2 性能测试摘要")
        print("=" * 80)
        
        for category, category_results in self.results.items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            print("-" * 50)
            
            # 找到最快的实现作为基准
            baseline_time = min(result['avg'] for result in category_results.values())
            
            for method, result in category_results.items():
                speedup = baseline_time / result['avg']
                print(f"{method:15s}: {result['avg']:8.3f} ms "
                      f"(加速比: {speedup:5.2f}x)")
        
        print("\n" + "=" * 80)
    
    def get_performance_data_for_charts(self) -> Dict:
        """获取用于图表生成的性能数据"""
        chart_data = {}
        
        for category, category_results in self.results.items():
            chart_data[category] = {
                'methods': list(category_results.keys()),
                'times': [result['avg'] for result in category_results.values()],
                'errors': [result['std'] for result in category_results.values()]
            }
        
        return chart_data

def run_comprehensive_benchmark():
    """运行完整的性能基准测试"""
    print("SM2 椭圆曲线数字签名算法 - 性能基准测试")
    print("=" * 80)
    
    benchmark = SM2Benchmark()
    
    # 运行各项基准测试
    benchmark.benchmark_scalar_multiplication(50)
    benchmark.benchmark_keypair_generation(100)
    benchmark.benchmark_signing(100)
    benchmark.benchmark_verification(100)
    benchmark.benchmark_end_to_end(50)
    
    # 打印摘要
    benchmark.print_summary()
    
    return benchmark

def quick_benchmark():
    """快速性能测试"""
    print("SM2 快速性能测试")
    print("=" * 40)
    
    sm2_basic = SM2Basic()
    sm2_optimized = SM2Optimized()
    sm2_parallel = SM2Parallel()
    
    message = b"Quick benchmark test"
    iterations = 20
    
    # 基础实现
    start_time = time.perf_counter()
    for _ in range(iterations):
        private_key, public_key = sm2_basic.generate_keypair()
        signature = sm2_basic.sign(message, private_key)
        is_valid = sm2_basic.verify(message, signature, public_key)
        assert is_valid
    basic_time = time.perf_counter() - start_time
    
    # 优化实现
    start_time = time.perf_counter()
    for _ in range(iterations):
        private_key, public_key = sm2_optimized.generate_keypair_optimized()
        signature = sm2_optimized.sign_optimized(message, private_key)
        is_valid = sm2_optimized.verify_optimized(message, signature, public_key)
        assert is_valid
    optimized_time = time.perf_counter() - start_time
    
    # 并行实现
    start_time = time.perf_counter()
    keypairs = sm2_parallel.batch_generate_keypairs(iterations)
    messages = [message] * iterations
    private_keys = [kp[0] for kp in keypairs]
    public_keys = [kp[1] for kp in keypairs]
    signatures = sm2_parallel.batch_sign(messages, private_keys)
    results = sm2_parallel.batch_verify(messages, signatures, public_keys)
    assert all(results)
    parallel_time = time.perf_counter() - start_time
    
    print(f"基础实现:   {basic_time*1000/iterations:6.2f} ms/operation")
    print(f"优化实现:   {optimized_time*1000/iterations:6.2f} ms/operation (加速比: {basic_time/optimized_time:.2f}x)")
    print(f"并行实现:   {parallel_time*1000/iterations:6.2f} ms/operation (加速比: {basic_time/parallel_time:.2f}x)")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SM2性能基准测试")
    parser.add_argument("--quick", action="store_true", help="运行快速测试")
    parser.add_argument("--full", action="store_true", help="运行完整测试")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_benchmark()
    elif args.full:
        benchmark = run_comprehensive_benchmark()
    else:
        # 默认运行快速测试
        quick_benchmark()
