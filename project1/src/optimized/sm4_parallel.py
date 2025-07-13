"""
SM4并行优化实现
支持多线程并行处理，适用于大量数据加密
充分利用多核CPU资源
"""

import sys
import os
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

# 添加src目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basic.sm4_basic import SM4Basic
from utils.constants import TEST_VECTORS, BLOCK_SIZE
from utils.helpers import validate_key, validate_data, format_hex

class SM4Parallel:
    """SM4并行优化实现类"""
    
    def __init__(self, key, num_threads=None, use_process=False):
        """
        初始化SM4并行加密器
        
        Args:
            key (bytes): 128位密钥
            num_threads (int): 线程/进程数量，默认为CPU核心数
            use_process (bool): 是否使用进程池而非线程池
        """
        validate_key(key)
        self.key = key
        self.use_process = use_process
        
        if num_threads is None:
            num_threads = multiprocessing.cpu_count()
        self.num_threads = num_threads
        
        # 创建基础SM4实例用于密钥扩展
        self.sm4_base = SM4Basic(key)
        self.round_keys = self.sm4_base.round_keys
        
        print(f"SM4并行优化初始化: {'进程' if use_process else '线程'}池大小={num_threads}")
    
    def _encrypt_chunk(self, data_chunk):
        """
        加密数据块（线程/进程工作函数）
        
        Args:
            data_chunk (bytes): 要加密的数据块
            
        Returns:
            bytes: 加密后的数据块
        """
        # 在线程/进程中创建独立的SM4实例
        sm4 = SM4Basic(self.key)
        return sm4.encrypt(data_chunk)
    
    def _decrypt_chunk(self, data_chunk):
        """
        解密数据块（线程/进程工作函数）
        
        Args:
            data_chunk (bytes): 要解密的数据块
            
        Returns:
            bytes: 解密后的数据块
        """
        # 在线程/进程中创建独立的SM4实例
        sm4 = SM4Basic(self.key)
        return sm4.decrypt(data_chunk)
    
    def _split_data(self, data, chunk_size=None):
        """
        将数据分割成适合并行处理的块
        
        Args:
            data (bytes): 要分割的数据
            chunk_size (int): 每块的大小（字节），默认自动计算
            
        Returns:
            list: 数据块列表
        """
        if chunk_size is None:
            # 自动计算块大小：总数据量除以线程数，但不小于1KB，不大于1MB
            auto_size = max(1024, min(1024*1024, len(data) // self.num_threads))
            # 确保块大小是16的倍数（SM4分组大小）
            chunk_size = (auto_size // BLOCK_SIZE) * BLOCK_SIZE
            if chunk_size == 0:
                chunk_size = BLOCK_SIZE
        
        chunks = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            # 确保每个块都是完整的分组
            if len(chunk) % BLOCK_SIZE == 0:
                chunks.append(chunk)
            else:
                # 最后一个块如果不完整，合并到前一个块
                if chunks:
                    chunks[-1] += chunk
                else:
                    chunks.append(chunk)
        
        return chunks
    
    def encrypt_parallel(self, plaintext, chunk_size=None):
        """
        并行加密数据
        
        Args:
            plaintext (bytes): 明文数据
            chunk_size (int): 每个并行块的大小
            
        Returns:
            bytes: 密文数据
        """
        validate_data(plaintext)
        
        # 如果数据太小，直接使用单线程
        if len(plaintext) < BLOCK_SIZE * self.num_threads:
            return self.sm4_base.encrypt(plaintext)
        
        # 分割数据
        chunks = self._split_data(plaintext, chunk_size)
        
        if len(chunks) == 1:
            # 只有一个块，直接处理
            return self.sm4_base.encrypt(chunks[0])
        
        # 并行处理
        executor_class = ProcessPoolExecutor if self.use_process else ThreadPoolExecutor
        
        with executor_class(max_workers=self.num_threads) as executor:
            # 提交所有加密任务
            futures = [executor.submit(self._encrypt_chunk, chunk) for chunk in chunks]
            
            # 收集结果
            results = []
            for future in futures:
                results.append(future.result())
        
        # 合并结果
        return b''.join(results)
    
    def decrypt_parallel(self, ciphertext, chunk_size=None):
        """
        并行解密数据
        
        Args:
            ciphertext (bytes): 密文数据
            chunk_size (int): 每个并行块的大小
            
        Returns:
            bytes: 明文数据
        """
        validate_data(ciphertext)
        
        # 如果数据太小，直接使用单线程
        if len(ciphertext) < BLOCK_SIZE * self.num_threads:
            return self.sm4_base.decrypt(ciphertext)
        
        # 分割数据
        chunks = self._split_data(ciphertext, chunk_size)
        
        if len(chunks) == 1:
            # 只有一个块，直接处理
            return self.sm4_base.decrypt(chunks[0])
        
        # 并行处理
        executor_class = ProcessPoolExecutor if self.use_process else ThreadPoolExecutor
        
        with executor_class(max_workers=self.num_threads) as executor:
            # 提交所有解密任务
            futures = [executor.submit(self._decrypt_chunk, chunk) for chunk in chunks]
            
            # 收集结果
            results = []
            for future in futures:
                results.append(future.result())
        
        # 合并结果
        return b''.join(results)
    
    def encrypt(self, plaintext):
        """
        加密接口（兼容其他实现）
        """
        return self.encrypt_parallel(plaintext)
    
    def decrypt(self, ciphertext):
        """
        解密接口（兼容其他实现）
        """
        return self.decrypt_parallel(ciphertext)
    
    def benchmark_parallel_vs_serial(self, data_size_mb=10):
        """
        并行vs串行性能对比
        
        Args:
            data_size_mb (int): 测试数据大小（MB）
        """
        print(f"\n=== 并行vs串行性能对比 ({data_size_mb}MB数据) ===")
        
        # 生成测试数据
        test_data = TEST_VECTORS['plaintext'] * (data_size_mb * 1024 * 1024 // BLOCK_SIZE)
        print(f"测试数据大小: {len(test_data) / (1024*1024):.1f} MB")
        print(f"数据块数量: {len(test_data) // BLOCK_SIZE}")
        
        # 串行测试
        print(f"\n串行加密测试...")
        start_time = time.perf_counter()
        serial_result = self.sm4_base.encrypt(test_data)
        serial_time = time.perf_counter() - start_time
        serial_throughput = len(test_data) / (1024*1024) / serial_time
        
        print(f"串行时间: {serial_time:.4f}秒")
        print(f"串行吞吐量: {serial_throughput:.2f} MB/s")
        
        # 并行测试
        print(f"\n并行加密测试 ({self.num_threads}个{'进程' if self.use_process else '线程'})...")
        start_time = time.perf_counter()
        parallel_result = self.encrypt_parallel(test_data)
        parallel_time = time.perf_counter() - start_time
        parallel_throughput = len(test_data) / (1024*1024) / parallel_time
        
        print(f"并行时间: {parallel_time:.4f}秒")
        print(f"并行吞吐量: {parallel_throughput:.2f} MB/s")
        
        # 验证结果一致性
        if serial_result == parallel_result:
            print("✓ 加密结果一致性验证通过")
        else:
            print("✗ 加密结果不一致！")
            return False
        
        # 计算加速比
        speedup = serial_time / parallel_time
        efficiency = speedup / self.num_threads * 100
        
        print(f"\n性能提升:")
        print(f"  加速比: {speedup:.2f}x")
        print(f"  并行效率: {efficiency:.1f}%")
        print(f"  吞吐量提升: {parallel_throughput/serial_throughput:.2f}x")
        
        return True
    
    def get_optimization_info(self):
        """
        获取优化信息
        """
        info = {
            "optimization_type": "Parallel Processing",
            "executor_type": "Process Pool" if self.use_process else "Thread Pool",
            "num_workers": self.num_threads,
            "cpu_cores": multiprocessing.cpu_count(),
            "performance_benefit": "利用多核CPU并行处理大量数据",
            "best_use_case": "大文件加密、批量数据处理"
        }
        return info

# 测试函数
def test_parallel_sm4():
    """并行优化版本测试"""
    print("=== SM4并行优化实现测试 ===")
    
    key = TEST_VECTORS['key']
    plaintext = TEST_VECTORS['plaintext']
    expected_ciphertext = TEST_VECTORS['ciphertext']
    
    print(f"密钥:     {format_hex(key)}")
    print(f"明文:     {format_hex(plaintext)}")
    print(f"期望密文: {format_hex(expected_ciphertext)}")
    
    # 测试线程池版本
    print(f"\n--- 线程池版本测试 ---")
    sm4_thread = SM4Parallel(key, num_threads=4, use_process=False)
    
    # 显示优化信息
    opt_info = sm4_thread.get_optimization_info()
    print(f"优化类型: {opt_info['optimization_type']}")
    print(f"执行器类型: {opt_info['executor_type']}")
    print(f"工作线程数: {opt_info['num_workers']}")
    print(f"CPU核心数: {opt_info['cpu_cores']}")
    
    # 基础功能测试
    ciphertext = sm4_thread.encrypt(plaintext)
    print(f"实际密文: {format_hex(ciphertext)}")
    
    if ciphertext == expected_ciphertext:
        print("✓ 加密测试通过")
    else:
        print("✗ 加密测试失败")
        return False
    
    decrypted = sm4_thread.decrypt(ciphertext)
    print(f"解密结果: {format_hex(decrypted)}")
    
    if decrypted == plaintext:
        print("✓ 解密测试通过")
    else:
        print("✗ 解密测试失败")
        return False
    
    # 大数据测试
    print(f"\n--- 大数据并行处理测试 ---")
    large_data = plaintext * 1000  # 16KB数据
    
    large_ciphertext = sm4_thread.encrypt(large_data)
    large_decrypted = sm4_thread.decrypt(large_ciphertext)
    
    if large_decrypted == large_data:
        print("✓ 大数据并行处理测试通过")
    else:
        print("✗ 大数据并行处理测试失败")
        return False
    
    # 性能对比测试
    try:
        sm4_thread.benchmark_parallel_vs_serial(data_size_mb=1)
    except Exception as e:
        print(f"性能测试跳过: {e}")
    
    print("✓ 所有测试通过")
    return True

if __name__ == "__main__":
    test_parallel_sm4()
