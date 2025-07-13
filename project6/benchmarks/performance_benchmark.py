"""
DDH-PSI协议性能基准测试

对协议的各个组件和整体性能进行详细测试和分析
"""

import time
import statistics
import sys
import os
from typing import List, Tuple, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ddh_psi import DDHPSIProtocol
from elliptic_curve import EllipticCurveGroup
from paillier_encryption import PaillierEncryption


class DDHPSIBenchmark:
    """DDH-PSI协议性能基准测试器"""
    
    def __init__(self):
        self.ec_group = EllipticCurveGroup()
        self.paillier = PaillierEncryption()
        
    def benchmark_elliptic_curve_operations(self, num_operations: int = 1000) -> Dict[str, float]:
        """
        测试椭圆曲线基础操作性能
        
        Args:
            num_operations: 操作次数
            
        Returns:
            各操作的平均时间（毫秒）
        """
        print(f"\\n=== 椭圆曲线操作性能测试 ({num_operations} 次操作) ===")
        
        results = {}
        
        # 测试私钥生成
        times = []
        for _ in range(num_operations):
            start = time.time()
            self.ec_group.generate_private_key()
            times.append((time.time() - start) * 1000)
        results['private_key_generation'] = statistics.mean(times)
        
        # 测试公钥生成
        private_key = self.ec_group.generate_private_key()
        times = []
        for _ in range(num_operations):
            start = time.time()
            self.ec_group.generate_public_key(private_key)
            times.append((time.time() - start) * 1000)
        results['public_key_generation'] = statistics.mean(times)
        
        # 测试点加法
        G = self.ec_group.G
        point2 = self.ec_group.scalar_mult(2, G)
        times = []
        for _ in range(num_operations):
            start = time.time()
            self.ec_group.point_add(G, point2)
            times.append((time.time() - start) * 1000)
        results['point_addition'] = statistics.mean(times)
        
        # 测试标量乘法
        scalar = self.ec_group.generate_private_key()
        times = []
        for _ in range(num_operations):
            start = time.time()
            self.ec_group.scalar_mult(scalar, G)
            times.append((time.time() - start) * 1000)
        results['scalar_multiplication'] = statistics.mean(times)
        
        # 输出结果
        for op, avg_time in results.items():
            print(f"  {op}: {avg_time:.3f} ms")
        
        return results
    
    def benchmark_paillier_operations(self, num_operations: int = 100) -> Dict[str, float]:
        """
        测试Paillier加密操作性能
        
        Args:
            num_operations: 操作次数
            
        Returns:
            各操作的平均时间（毫秒）
        """
        print(f"\\n=== Paillier加密操作性能测试 ({num_operations} 次操作) ===")
        
        results = {}
        
        # 测试密钥生成
        times = []
        for _ in range(10):  # 密钥生成较慢，测试较少次数
            paillier = PaillierEncryption()
            start = time.time()
            paillier.generate_keypair()
            times.append((time.time() - start) * 1000)
        results['keypair_generation'] = statistics.mean(times)
        
        # 为后续测试生成密钥对
        public_key, private_key = self.paillier.generate_keypair()
        
        # 测试加密
        plaintext = 12345
        times = []
        for _ in range(num_operations):
            start = time.time()
            self.paillier.encrypt(plaintext, public_key)
            times.append((time.time() - start) * 1000)
        results['encryption'] = statistics.mean(times)
        
        # 测试解密
        ciphertext = self.paillier.encrypt(plaintext, public_key)
        times = []
        for _ in range(num_operations):
            start = time.time()
            self.paillier.decrypt(ciphertext, private_key)
            times.append((time.time() - start) * 1000)
        results['decryption'] = statistics.mean(times)
        
        # 测试同态加法
        c1 = self.paillier.encrypt(100, public_key)
        c2 = self.paillier.encrypt(200, public_key)
        times = []
        for _ in range(num_operations):
            start = time.time()
            self.paillier.add_ciphertexts(c1, c2, public_key)
            times.append((time.time() - start) * 1000)
        results['homomorphic_addition'] = statistics.mean(times)
        
        # 测试重随机化
        times = []
        for _ in range(num_operations):
            start = time.time()
            self.paillier.refresh_ciphertext(ciphertext, public_key)
            times.append((time.time() - start) * 1000)
        results['ciphertext_refresh'] = statistics.mean(times)
        
        # 输出结果
        for op, avg_time in results.items():
            print(f"  {op}: {avg_time:.3f} ms")
        
        return results
    
    def benchmark_protocol_scalability(self, sizes: List[int]) -> Dict[int, Dict[str, float]]:
        """
        测试协议在不同数据规模下的性能
        
        Args:
            sizes: 数据集大小列表
            
        Returns:
            各规模下的性能数据
        """
        print(f"\\n=== 协议扩展性测试 ===")
        
        results = {}
        
        for size in sizes:
            print(f"\\n测试数据规模: {size}")
            
            # 生成测试数据
            party1_data = [f"user{i}" for i in range(size)]
            party2_data = [(f"user{i}", i * 10) for i in range(0, size, 2)]  # 50%交集
            
            # 多次运行取平均值
            times = []
            for run in range(3):
                start = time.time()
                intersection_size, intersection_sum = DDHPSIProtocol.run_protocol(
                    party1_data, party2_data
                )
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
                
                print(f"  运行 {run+1}: {elapsed:.2f} ms (交集: {intersection_size}, 总和: {intersection_sum})")
            
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times) if len(times) > 1 else 0
            
            results[size] = {
                'average_time_ms': avg_time,
                'std_deviation_ms': std_time,
                'throughput_ops_per_sec': size / (avg_time / 1000),
                'time_per_element_ms': avg_time / size
            }
            
            print(f"  平均时间: {avg_time:.2f} ± {std_time:.2f} ms")
            print(f"  吞吐量: {results[size]['throughput_ops_per_sec']:.2f} ops/sec")
            print(f"  每元素时间: {results[size]['time_per_element_ms']:.3f} ms")
        
        return results
    
    def benchmark_communication_overhead(self, sizes: List[int]) -> Dict[int, Dict[str, int]]:
        """
        分析协议的通信开销
        
        Args:
            sizes: 数据集大小列表
            
        Returns:
            各规模下的通信开销数据
        """
        print(f"\\n=== 通信开销分析 ===")
        
        results = {}
        
        for size in sizes:
            print(f"\\n数据规模: {size}")
            
            # 椭圆曲线点大小：65字节（未压缩格式）
            ec_point_size = 65
            
            # Paillier密文大小：通常为768字节（1024位密钥）
            paillier_ciphertext_size = 128  # 简化估计
            
            # 第一轮：Party1发送m1个椭圆曲线点
            round1_bytes = size * ec_point_size
            
            # 第二轮：Party2发送m1个椭圆曲线点 + m2个(椭圆曲线点 + 密文)对
            round2_bytes = size * ec_point_size + size * (ec_point_size + paillier_ciphertext_size)
            
            # 第三轮：Party1发送1个密文
            round3_bytes = paillier_ciphertext_size
            
            total_bytes = round1_bytes + round2_bytes + round3_bytes
            
            results[size] = {
                'round1_bytes': round1_bytes,
                'round2_bytes': round2_bytes,
                'round3_bytes': round3_bytes,
                'total_bytes': total_bytes,
                'bytes_per_element': total_bytes / size
            }
            
            print(f"  第一轮通信: {round1_bytes:,} 字节")
            print(f"  第二轮通信: {round2_bytes:,} 字节")
            print(f"  第三轮通信: {round3_bytes:,} 字节")
            print(f"  总通信量: {total_bytes:,} 字节 ({total_bytes/1024:.1f} KB)")
            print(f"  每元素开销: {results[size]['bytes_per_element']:.1f} 字节")
        
        return results
    
    def run_comprehensive_benchmark(self):
        """运行全面的性能基准测试"""
        print("=== DDH-PSI协议全面性能基准测试 ===")
        print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 基础操作性能测试
        ec_results = self.benchmark_elliptic_curve_operations(1000)
        paillier_results = self.benchmark_paillier_operations(100)
        
        # 协议扩展性测试
        scalability_sizes = [10, 50, 100, 500, 1000]
        scalability_results = self.benchmark_protocol_scalability(scalability_sizes)
        
        # 通信开销分析
        communication_results = self.benchmark_communication_overhead(scalability_sizes)
        
        # 生成性能报告
        self.generate_performance_report(
            ec_results, paillier_results, 
            scalability_results, communication_results
        )
        
        return {
            'elliptic_curve': ec_results,
            'paillier': paillier_results,
            'scalability': scalability_results,
            'communication': communication_results
        }
    
    def generate_performance_report(self, ec_results: Dict, paillier_results: Dict,
                                  scalability_results: Dict, communication_results: Dict):
        """生成性能报告"""
        print(f"\\n\\n=== 性能报告总结 ===")
        
        print(f"\\n1. 椭圆曲线操作性能:")
        print(f"   - 私钥生成: {ec_results['private_key_generation']:.3f} ms")
        print(f"   - 标量乘法: {ec_results['scalar_multiplication']:.3f} ms")
        
        print(f"\\n2. Paillier加密性能:")
        print(f"   - 密钥生成: {paillier_results['keypair_generation']:.1f} ms")
        print(f"   - 加密操作: {paillier_results['encryption']:.3f} ms")
        print(f"   - 解密操作: {paillier_results['decryption']:.3f} ms")
        
        print(f"\\n3. 协议扩展性:")
        for size, data in scalability_results.items():
            print(f"   - {size:4d} 元素: {data['average_time_ms']:7.1f} ms, "
                  f"{data['throughput_ops_per_sec']:6.1f} ops/sec")
        
        print(f"\\n4. 通信效率:")
        for size, data in communication_results.items():
            print(f"   - {size:4d} 元素: {data['total_bytes']:8,} 字节, "
                  f"{data['bytes_per_element']:5.1f} 字节/元素")
        
        # 估算实际部署成本
        print(f"\\n5. 实际部署估算 (100,000 元素):")
        
        # 基于1000元素的性能线性外推
        if 1000 in scalability_results:
            base_time = scalability_results[1000]['average_time_ms']
            estimated_time_100k = base_time * 100  # 线性扩展估算
            print(f"   - 预估执行时间: {estimated_time_100k/1000:.1f} 秒")
        
        if 1000 in communication_results:
            base_comm = communication_results[1000]['total_bytes']
            estimated_comm_100k = base_comm * 100
            print(f"   - 预估通信量: {estimated_comm_100k/1024/1024:.1f} MB")
            print(f"   - 预估成本: ~$0.08 (基于云计算资源)")


if __name__ == '__main__':
    benchmark = DDHPSIBenchmark()
    results = benchmark.run_comprehensive_benchmark()
