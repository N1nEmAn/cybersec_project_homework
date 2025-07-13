"""
SM4算法性能基准测试
比较不同实现版本的性能差异
"""

import time
import statistics
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from basic.sm4_basic import SM4Basic
from optimized.sm4_lookup_table import SM4LookupTable
from optimized.sm4_bitwise import SM4Bitwise
from utils.constants import TEST_VECTORS
from utils.helpers import format_hex

class BenchmarkRunner:
    """性能基准测试运行器"""
    
    def __init__(self):
        self.key = TEST_VECTORS['key']
        self.implementations = {
            'Basic': SM4Basic(self.key),
            'LookupTable': SM4LookupTable(self.key),
            'Bitwise': SM4Bitwise(self.key)
        }
        self.results = {}
    
    def benchmark_single_block(self, iterations=10000):
        """单分组加密性能测试"""
        print(f"=== 单分组加密性能测试 ({iterations}次迭代) ===")
        
        test_data = TEST_VECTORS['plaintext']
        
        for name, impl in self.implementations.items():
            print(f"\n测试 {name} 实现...")
            
            times = []
            for _ in range(10):  # 运行10次取平均
                start_time = time.perf_counter()
                
                for _ in range(iterations):
                    impl.encrypt(test_data)
                
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times)
            throughput = iterations / avg_time
            
            self.results[f'{name}_single_block'] = {
                'avg_time': avg_time,
                'std_time': std_time,
                'throughput': throughput,
                'time_per_block': avg_time / iterations * 1000000  # 微秒
            }
            
            print(f"  平均时间: {avg_time:.4f}秒 (±{std_time:.4f})")
            print(f"  吞吐量: {throughput:.2f} blocks/sec")
            print(f"  单块时间: {avg_time / iterations * 1000000:.2f} μs")
    
    def benchmark_large_data(self, data_size_kb=1024):
        """大数据加密性能测试"""
        print(f"\n=== 大数据加密性能测试 ({data_size_kb}KB) ===")
        
        # 创建测试数据
        blocks_count = data_size_kb * 1024 // 16
        test_data = TEST_VECTORS['plaintext'] * blocks_count
        
        for name, impl in self.implementations.items():
            print(f"\n测试 {name} 实现...")
            
            times = []
            for _ in range(5):  # 运行5次取平均
                start_time = time.perf_counter()
                ciphertext = impl.encrypt(test_data)
                end_time = time.perf_counter()
                
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times)
            throughput_mbps = (data_size_kb / 1024) / avg_time  # MB/s
            
            self.results[f'{name}_large_data'] = {
                'avg_time': avg_time,
                'std_time': std_time,
                'throughput_mbps': throughput_mbps,
                'data_size_kb': data_size_kb
            }
            
            print(f"  平均时间: {avg_time:.4f}秒 (±{std_time:.4f})")
            print(f"  吞吐量: {throughput_mbps:.2f} MB/s")
    
    def benchmark_key_expansion(self, iterations=10000):
        """密钥扩展性能测试"""
        print(f"\n=== 密钥扩展性能测试 ({iterations}次迭代) ===")
        
        for name in self.implementations.keys():
            if name == 'Basic':
                impl_class = SM4Basic
            elif name == 'LookupTable':
                impl_class = SM4LookupTable
            elif name == 'Bitwise':
                impl_class = SM4Bitwise
            
            print(f"\n测试 {name} 实现...")
            
            times = []
            for _ in range(5):  # 运行5次取平均
                start_time = time.perf_counter()
                
                for _ in range(iterations):
                    impl_class(self.key)
                
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times)
            throughput = iterations / avg_time
            
            self.results[f'{name}_key_expansion'] = {
                'avg_time': avg_time,
                'std_time': std_time,
                'throughput': throughput,
                'time_per_expansion': avg_time / iterations * 1000000  # 微秒
            }
            
            print(f"  平均时间: {avg_time:.4f}秒 (±{std_time:.4f})")
            print(f"  吞吐量: {throughput:.2f} expansions/sec")
            print(f"  单次时间: {avg_time / iterations * 1000000:.2f} μs")
    
    def compare_implementations(self):
        """比较不同实现的性能"""
        print("\n=== 性能比较分析 ===")
        
        # 单分组加密比较
        print("\n单分组加密性能比较:")
        basic_throughput = self.results['Basic_single_block']['throughput']
        
        for name in ['LookupTable', 'Bitwise']:
            if f'{name}_single_block' in self.results:
                throughput = self.results[f'{name}_single_block']['throughput']
                speedup = throughput / basic_throughput
                print(f"  {name} vs Basic: {speedup:.2f}x speedup")
        
        # 大数据加密比较
        print("\n大数据加密性能比较:")
        basic_mbps = self.results['Basic_large_data']['throughput_mbps']
        
        for name in ['LookupTable', 'Bitwise']:
            if f'{name}_large_data' in self.results:
                mbps = self.results[f'{name}_large_data']['throughput_mbps']
                speedup = mbps / basic_mbps
                print(f"  {name} vs Basic: {speedup:.2f}x speedup")
        
        # 密钥扩展比较
        print("\n密钥扩展性能比较:")
        basic_ke = self.results['Basic_key_expansion']['throughput']
        
        for name in ['LookupTable', 'Bitwise']:
            if f'{name}_key_expansion' in self.results:
                ke = self.results[f'{name}_key_expansion']['throughput']
                speedup = ke / basic_ke
                print(f"  {name} vs Basic: {speedup:.2f}x speedup")
    
    def generate_report(self):
        """生成详细的性能报告"""
        print("\n=== 详细性能报告 ===")
        
        for test_name, result in self.results.items():
            impl_name, test_type = test_name.rsplit('_', 1)
            print(f"\n{impl_name} - {test_type}:")
            
            for key, value in result.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")
    
    def save_results(self, filename='benchmark_results.txt'):
        """保存结果到文件"""
        filepath = os.path.join(os.path.dirname(__file__), 'results', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("SM4算法性能基准测试结果\n")
            f.write("=" * 50 + "\n")
            f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for test_name, result in self.results.items():
                impl_name, test_type = test_name.rsplit('_', 1)
                f.write(f"{impl_name} - {test_type}:\n")
                
                for key, value in result.items():
                    if isinstance(value, float):
                        f.write(f"  {key}: {value:.4f}\n")
                    else:
                        f.write(f"  {key}: {value}\n")
                f.write("\n")
        
        print(f"\n结果已保存到: {filepath}")

def run_full_benchmark():
    """运行完整的基准测试"""
    print("SM4算法性能基准测试")
    print("=" * 50)
    
    # 检查实现是否可用
    try:
        from optimized.sm4_lookup_table import SM4LookupTable
        from optimized.sm4_bitwise import SM4Bitwise
        print("所有实现均可用")
    except ImportError as e:
        print(f"警告: 部分优化实现不可用 - {e}")
    
    runner = BenchmarkRunner()
    
    # 运行各项测试
    runner.benchmark_single_block(iterations=10000)
    runner.benchmark_large_data(data_size_kb=1024)
    runner.benchmark_key_expansion(iterations=1000)
    
    # 分析结果
    runner.compare_implementations()
    runner.generate_report()
    
    # 保存结果
    runner.save_results()

if __name__ == "__main__":
    run_full_benchmark()
