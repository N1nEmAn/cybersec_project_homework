#!/usr/bin/env python3
"""
SM2椭圆曲线数字签名算法并行优化实现
使用多线程和向量化技术
"""

import time
import secrets
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, List, Optional
import numpy as np
from .sm2_optimized import SM2Optimized, SM2Point

class SM2Parallel(SM2Optimized):
    """SM2椭圆曲线数字签名算法并行优化实现"""
    
    def __init__(self, num_threads: int = 4):
        super().__init__()
        self.num_threads = num_threads
        self.thread_pool = ThreadPoolExecutor(max_workers=num_threads)
    
    def batch_generate_keypairs(self, count: int) -> List[Tuple[int, SM2Point]]:
        """批量生成密钥对"""
        def generate_single():
            return self.generate_keypair_optimized()
        
        # 并行生成
        futures = [self.thread_pool.submit(generate_single) for _ in range(count)]
        
        keypairs = []
        for future in as_completed(futures):
            keypairs.append(future.result())
        
        return keypairs
    
    def batch_sign(self, messages: List[bytes], private_keys: List[int], 
                   user_ids: Optional[List[bytes]] = None) -> List[Tuple[int, int]]:
        """批量数字签名"""
        if user_ids is None:
            user_ids = [b"1234567812345678"] * len(messages)
        
        def sign_single(msg, priv_key, uid):
            return self.sign_optimized(msg, priv_key, uid)
        
        # 并行签名
        futures = []
        for msg, priv_key, uid in zip(messages, private_keys, user_ids):
            future = self.thread_pool.submit(sign_single, msg, priv_key, uid)
            futures.append(future)
        
        signatures = []
        for future in as_completed(futures):
            signatures.append(future.result())
        
        return signatures
    
    def batch_verify(self, messages: List[bytes], signatures: List[Tuple[int, int]], 
                     public_keys: List[SM2Point], user_ids: Optional[List[bytes]] = None) -> List[bool]:
        """批量签名验证"""
        if user_ids is None:
            user_ids = [b"1234567812345678"] * len(messages)
        
        def verify_single(msg, sig, pub_key, uid):
            return self.verify_optimized(msg, sig, pub_key, uid)
        
        # 并行验证
        futures = []
        for msg, sig, pub_key, uid in zip(messages, signatures, public_keys, user_ids):
            future = self.thread_pool.submit(verify_single, msg, sig, pub_key, uid)
            futures.append(future)
        
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        
        return results
    
    def parallel_point_multiply(self, k: int, P: SM2Point, chunk_size: int = 64) -> SM2Point:
        """并行标量乘法（分块计算）"""
        if k == 0:
            return SM2Point(0, 0, True)
        
        if k == 1:
            return P
        
        # 将k分解为多个块
        bit_length = k.bit_length()
        if bit_length <= chunk_size:
            return self.point_multiply_optimized(k, P)
        
        # 分块处理
        chunks = []
        temp_k = k
        shift = 0
        
        while temp_k > 0:
            chunk_val = temp_k & ((1 << chunk_size) - 1)
            if chunk_val > 0:
                chunks.append((chunk_val, shift))
            temp_k >>= chunk_size
            shift += chunk_size
        
        # 并行计算每个块
        def compute_chunk(chunk_val, shift):
            # 计算 chunk_val * (2^shift) * P
            shifted_P = P
            for _ in range(shift):
                shifted_P = self.point_double(shifted_P)
            return self.point_multiply_optimized(chunk_val, shifted_P)
        
        futures = []
        for chunk_val, shift in chunks:
            future = self.thread_pool.submit(compute_chunk, chunk_val, shift)
            futures.append(future)
        
        # 合并结果
        result = SM2Point(0, 0, True)
        for future in as_completed(futures):
            chunk_result = future.result()
            result = self.point_add(result, chunk_result)
        
        return result
    
    def vectorized_point_operations(self, operations: List[Tuple[str, SM2Point, SM2Point]]) -> List[SM2Point]:
        """向量化椭圆曲线点运算"""
        def process_operation(op_type, P, Q):
            if op_type == "add":
                return self.point_add(P, Q)
            elif op_type == "double":
                return self.point_double(P)
            else:
                raise ValueError(f"不支持的操作类型: {op_type}")
        
        # 并行处理操作
        futures = []
        for op_type, P, Q in operations:
            future = self.thread_pool.submit(process_operation, op_type, P, Q)
            futures.append(future)
        
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        
        return results
    
    def simultaneous_multiple_point_multiplication(self, scalars_points: List[Tuple[int, SM2Point]]) -> SM2Point:
        """同时多点标量乘法：计算 Σ(ki * Pi)"""
        def compute_single(k, P):
            return self.point_multiply_optimized(k, P)
        
        # 并行计算每个 ki * Pi
        futures = []
        for k, P in scalars_points:
            future = self.thread_pool.submit(compute_single, k, P)
            futures.append(future)
        
        # 累加所有结果
        result = SM2Point(0, 0, True)
        for future in as_completed(futures):
            partial_result = future.result()
            result = self.point_add(result, partial_result)
        
        return result
    
    def optimized_verify_with_precomputation(self, message: bytes, signature: Tuple[int, int], 
                                           public_key: SM2Point, user_id: bytes = b"1234567812345678") -> bool:
        """使用预计算和并行的优化验证"""
        r, s = signature
        
        # 检查签名参数范围
        if not (1 <= r <= self.n - 1) or not (1 <= s <= self.n - 1):
            return False
        
        # 计算ZA
        za = self._get_user_id_hash(user_id)
        
        # 计算消息摘要 e = H(ZA || M)
        m_prime = za + message
        digest = self._sm3_hash(m_prime)
        e = int.from_bytes(digest, byteorder='big')
        
        # 计算 t = (r + s) mod n
        t = (r + s) % self.n
        
        # 如果 t = 0，签名无效
        if t == 0:
            return False
        
        # 并行计算 s*G 和 t*PA，然后相加
        scalars_points = [(s, self.G), (t, public_key)]
        point_sum = self.simultaneous_multiple_point_multiplication(scalars_points)
        
        if point_sum.infinity:
            return False
        
        x1_prime = point_sum.x
        
        # 计算 R = (e + x1') mod n
        R = (e + x1_prime) % self.n
        
        # 验证 R = r
        return R == r
    
    def __del__(self):
        """清理线程池"""
        if hasattr(self, 'thread_pool'):
            self.thread_pool.shutdown(wait=True)

def benchmark_parallel():
    """并行实现性能测试"""
    sm2 = SM2Parallel(num_threads=4)
    
    print("=== SM2并行实现性能测试 ===")
    
    # 批量密钥生成测试
    start_time = time.time()
    keypairs = sm2.batch_generate_keypairs(100)
    batch_keygen_time = time.time() - start_time
    print(f"批量密钥生成(100个): {batch_keygen_time*1000:.2f} ms total, {batch_keygen_time*10:.2f} ms/operation")
    
    # 批量签名测试
    messages = [b"Test message " + str(i).encode() for i in range(100)]
    private_keys = [kp[0] for kp in keypairs]
    public_keys = [kp[1] for kp in keypairs]
    
    start_time = time.time()
    signatures = sm2.batch_sign(messages, private_keys)
    batch_sign_time = time.time() - start_time
    print(f"批量签名(100个): {batch_sign_time*1000:.2f} ms total, {batch_sign_time*10:.2f} ms/operation")
    
    # 批量验证测试
    start_time = time.time()
    results = sm2.batch_verify(messages, signatures, public_keys)
    batch_verify_time = time.time() - start_time
    print(f"批量验证(100个): {batch_verify_time*1000:.2f} ms total, {batch_verify_time*10:.2f} ms/operation")
    
    # 验证所有签名都有效
    assert all(results), "部分签名验证失败"
    print("✓ 所有签名验证通过")
    
    return batch_keygen_time/100, batch_sign_time/100, batch_verify_time/100

def compare_parallel_vs_sequential():
    """比较并行与串行性能"""
    print("\n=== 并行 vs 串行性能比较 ===")
    
    # 串行实现
    sm2_seq = SM2Optimized()
    
    # 并行实现
    sm2_par = SM2Parallel(num_threads=4)
    
    num_operations = 50
    
    # 串行密钥生成
    start_time = time.time()
    for _ in range(num_operations):
        sm2_seq.generate_keypair_optimized()
    seq_keygen_time = time.time() - start_time
    
    # 并行密钥生成
    start_time = time.time()
    sm2_par.batch_generate_keypairs(num_operations)
    par_keygen_time = time.time() - start_time
    
    print(f"密钥生成 - 串行: {seq_keygen_time*1000:.2f} ms, 并行: {par_keygen_time*1000:.2f} ms")
    print(f"密钥生成加速比: {seq_keygen_time/par_keygen_time:.2f}x")
    
    # 准备数据
    keypairs = sm2_par.batch_generate_keypairs(num_operations)
    messages = [b"Test message " + str(i).encode() for i in range(num_operations)]
    private_keys = [kp[0] for kp in keypairs]
    public_keys = [kp[1] for kp in keypairs]
    
    # 串行签名
    start_time = time.time()
    seq_signatures = []
    for msg, priv_key in zip(messages, private_keys):
        seq_signatures.append(sm2_seq.sign_optimized(msg, priv_key))
    seq_sign_time = time.time() - start_time
    
    # 并行签名
    start_time = time.time()
    par_signatures = sm2_par.batch_sign(messages, private_keys)
    par_sign_time = time.time() - start_time
    
    print(f"签名 - 串行: {seq_sign_time*1000:.2f} ms, 并行: {par_sign_time*1000:.2f} ms")
    print(f"签名加速比: {seq_sign_time/par_sign_time:.2f}x")
    
    # 串行验证
    start_time = time.time()
    seq_results = []
    for msg, sig, pub_key in zip(messages, seq_signatures, public_keys):
        seq_results.append(sm2_seq.verify_optimized(msg, sig, pub_key))
    seq_verify_time = time.time() - start_time
    
    # 并行验证
    start_time = time.time()
    par_results = sm2_par.batch_verify(messages, par_signatures, public_keys)
    par_verify_time = time.time() - start_time
    
    print(f"验证 - 串行: {seq_verify_time*1000:.2f} ms, 并行: {par_verify_time*1000:.2f} ms")
    print(f"验证加速比: {seq_verify_time/par_verify_time:.2f}x")
    
    # 验证结果一致性
    assert all(seq_results) and all(par_results), "签名验证失败"
    print("✓ 串行和并行结果一致")

def test_parallel_scalar_multiplication():
    """测试并行标量乘法"""
    print("\n=== 并行标量乘法测试 ===")
    
    sm2 = SM2Parallel(num_threads=4)
    k = secrets.randbelow(sm2.n - 1) + 1
    P = sm2.G
    
    # 串行标量乘法
    start_time = time.time()
    result1 = sm2.point_multiply_optimized(k, P)
    seq_time = time.time() - start_time
    
    # 并行标量乘法
    start_time = time.time()
    result2 = sm2.parallel_point_multiply(k, P)
    par_time = time.time() - start_time
    
    print(f"标量乘法 - 串行: {seq_time*1000:.2f} ms, 并行: {par_time*1000:.2f} ms")
    print(f"标量乘法加速比: {seq_time/par_time:.2f}x")
    
    # 验证结果一致性
    assert result1 == result2, "并行标量乘法结果不一致"
    print("✓ 并行标量乘法结果正确")

if __name__ == "__main__":
    # 并行版本功能测试
    sm2 = SM2Parallel(num_threads=4)
    
    print("SM2椭圆曲线数字签名算法 - 并行优化实现")
    print("=" * 50)
    
    # 批量密钥生成测试
    print("批量生成5个密钥对...")
    keypairs = sm2.batch_generate_keypairs(5)
    for i, (priv_key, pub_key) in enumerate(keypairs):
        print(f"密钥对{i+1}: {priv_key:064x}")
    
    # 批量签名和验证测试
    messages = [b"Message " + str(i).encode() for i in range(5)]
    private_keys = [kp[0] for kp in keypairs]
    public_keys = [kp[1] for kp in keypairs]
    
    print(f"\n批量签名{len(messages)}个消息...")
    signatures = sm2.batch_sign(messages, private_keys)
    
    print(f"批量验证{len(signatures)}个签名...")
    results = sm2.batch_verify(messages, signatures, public_keys)
    
    print(f"验证结果: {sum(results)}/{len(results)} 通过")
    
    # 性能测试
    print("\n" + "=" * 50)
    benchmark_parallel()
    
    # 性能比较
    compare_parallel_vs_sequential()
    
    # 并行标量乘法测试
    test_parallel_scalar_multiplication()
