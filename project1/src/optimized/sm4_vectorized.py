#!/usr/bin/env python3
"""
SM4向量化优化实现
使用NumPy向量化操作实现SIMD加速
"""

import numpy as np
from typing import List, Union
import time
from ..utils.constants import SBOX, FK, CK
from ..basic.sm4_basic import SM4Basic


class SM4Vectorized(SM4Basic):
    """
    SM4向量化优化实现
    
    特性:
    - NumPy向量化操作
    - SIMD指令利用
    - 批量数据处理
    - 内存访问优化
    """
    
    def __init__(self):
        super().__init__(b'\x00' * 16)  # 使用默认密钥初始化
        self._setup_vectorized_tables()
    
    def _setup_vectorized_tables(self):
        """设置向量化查找表"""
        # 将S盒转换为NumPy数组
        self.sbox_array = np.array(SBOX, dtype=np.uint8)
        
        # 预计算S盒的所有可能输入输出（256个值）
        self.sbox_lookup = np.zeros(256, dtype=np.uint32)
        for i in range(256):
            self.sbox_lookup[i] = self.sbox_array[i]
        
        # 预计算线性变换的常数
        self.fk_array = np.array(FK, dtype=np.uint32)
        self.ck_array = np.array(CK, dtype=np.uint32)
    
    def _s_transform_vectorized(self, data: np.ndarray) -> np.ndarray:
        """
        向量化S变换
        
        Args:
            data: 输入数据数组
            
        Returns:
            S变换后的数据
        """
        # 分解为字节
        bytes_data = np.array([
            (data >> 24) & 0xFF,
            (data >> 16) & 0xFF,
            (data >> 8) & 0xFF,
            data & 0xFF
        ], dtype=np.uint8)
        
        # 向量化S盒查找
        s_bytes = self.sbox_array[bytes_data]
        
        # 重新组合
        result = (s_bytes[0].astype(np.uint32) << 24) | \
                (s_bytes[1].astype(np.uint32) << 16) | \
                (s_bytes[2].astype(np.uint32) << 8) | \
                s_bytes[3].astype(np.uint32)
        
        return result
    
    def _linear_transform_vectorized(self, data: np.ndarray) -> np.ndarray:
        """
        向量化线性变换 L(B) = B ⊕ (B<<<2) ⊕ (B<<<10) ⊕ (B<<<18) ⊕ (B<<<24)
        
        Args:
            data: 输入数据
            
        Returns:
            线性变换结果
        """
        # 使用NumPy的位运算进行向量化计算
        result = data ^ np.roll(data, -2) ^ np.roll(data, -10) ^ \
                np.roll(data, -18) ^ np.roll(data, -24)
        
        # 处理32位整数的循环左移
        shifts = [2, 10, 18, 24]
        for shift in shifts:
            shifted = ((data << shift) | (data >> (32 - shift))) & 0xFFFFFFFF
            result ^= shifted
        
        return result & 0xFFFFFFFF
    
    def _round_function_vectorized(self, x: np.ndarray, rk: int) -> np.ndarray:
        """
        向量化轮函数
        
        Args:
            x: 输入状态数组 [X0, X1, X2, X3]
            rk: 轮密钥
            
        Returns:
            轮函数输出
        """
        # 计算 X1 ⊕ X2 ⊕ X3 ⊕ rk
        temp = x[1] ^ x[2] ^ x[3] ^ rk
        
        # S变换
        s_temp = self._s_transform_vectorized(temp)
        
        # 线性变换
        l_temp = self._linear_transform_vectorized(s_temp)
        
        # 返回 X0 ⊕ L(S(X1 ⊕ X2 ⊕ X3 ⊕ rk))
        return x[0] ^ l_temp
    
    def encrypt_block_vectorized(self, plaintext: bytes) -> bytes:
        """
        向量化块加密
        
        Args:
            plaintext: 16字节明文
            
        Returns:
            16字节密文
        """
        if len(plaintext) != 16:
            raise ValueError("明文块大小必须为16字节")
        
        # 转换为32位整数数组
        x = np.array([
            int.from_bytes(plaintext[0:4], 'big'),
            int.from_bytes(plaintext[4:8], 'big'),
            int.from_bytes(plaintext[8:12], 'big'),
            int.from_bytes(plaintext[12:16], 'big')
        ], dtype=np.uint32)
        
        # 32轮加密
        for i in range(32):
            x_new = self._round_function_vectorized(x, self.round_keys[i])
            # 循环更新状态
            x = np.roll(x, -1)
            x[3] = x_new
        
        # 逆序变换
        result = x[::-1]
        
        # 转换回字节
        ciphertext = b''.join([
            result[i].tobytes()[:4][::-1] for i in range(4)
        ])
        
        return ciphertext
    
    def decrypt_block_vectorized(self, ciphertext: bytes) -> bytes:
        """
        向量化块解密
        
        Args:
            ciphertext: 16字节密文
            
        Returns:
            16字节明文
        """
        if len(ciphertext) != 16:
            raise ValueError("密文块大小必须为16字节")
        
        # 转换为32位整数数组
        x = np.array([
            int.from_bytes(ciphertext[0:4], 'big'),
            int.from_bytes(ciphertext[4:8], 'big'),
            int.from_bytes(ciphertext[8:12], 'big'),
            int.from_bytes(ciphertext[12:16], 'big')
        ], dtype=np.uint32)
        
        # 32轮解密（使用逆序轮密钥）
        for i in range(32):
            x_new = self._round_function_vectorized(x, self.round_keys[31-i])
            # 循环更新状态
            x = np.roll(x, -1)
            x[3] = x_new
        
        # 逆序变换
        result = x[::-1]
        
        # 转换回字节
        plaintext = b''.join([
            result[i].tobytes()[:4][::-1] for i in range(4)
        ])
        
        return plaintext
    
    def encrypt_batch(self, plaintexts: List[bytes]) -> List[bytes]:
        """
        批量加密多个块
        
        Args:
            plaintexts: 明文块列表
            
        Returns:
            密文块列表
        """
        if not all(len(p) == 16 for p in plaintexts):
            raise ValueError("所有明文块大小必须为16字节")
        
        # 转换为NumPy数组进行批量处理
        batch_size = len(plaintexts)
        data_array = np.zeros((batch_size, 4), dtype=np.uint32)
        
        for i, plaintext in enumerate(plaintexts):
            data_array[i] = [
                int.from_bytes(plaintext[0:4], 'big'),
                int.from_bytes(plaintext[4:8], 'big'),
                int.from_bytes(plaintext[8:12], 'big'),
                int.from_bytes(plaintext[12:16], 'big')
            ]
        
        # 批量加密
        ciphertexts = []
        for i in range(batch_size):
            x = data_array[i].copy()
            
            # 32轮加密
            for round_i in range(32):
                x_new = self._round_function_vectorized(x, self.round_keys[round_i])
                x = np.roll(x, -1)
                x[3] = x_new
            
            # 逆序变换并转换回字节
            result = x[::-1]
            ciphertext = b''.join([
                result[j].tobytes()[:4][::-1] for j in range(4)
            ])
            ciphertexts.append(ciphertext)
        
        return ciphertexts
    
    def benchmark_vectorized(self, data_size: int = 1024) -> dict:
        """
        向量化实现性能基准测试
        
        Args:
            data_size: 测试数据大小（字节）
            
        Returns:
            性能测试结果
        """
        # 生成测试数据
        test_data = np.random.bytes(data_size)
        blocks = [test_data[i:i+16] for i in range(0, len(test_data), 16)]
        
        # 测试单块加密
        start_time = time.time()
        for _ in range(1000):
            self.encrypt_block_vectorized(blocks[0])
        single_time = time.time() - start_time
        
        # 测试批量加密
        start_time = time.time()
        self.encrypt_batch(blocks)
        batch_time = time.time() - start_time
        
        # 与基础实现比较
        basic_sm4 = SM4Basic()
        basic_sm4.set_key(self.key)
        
        start_time = time.time()
        for _ in range(1000):
            basic_sm4.encrypt_block(blocks[0])
        basic_time = time.time() - start_time
        
        return {
            'vectorized_single_time': single_time,
            'vectorized_batch_time': batch_time,
            'basic_time': basic_time,
            'speedup_single': basic_time / single_time,
            'speedup_batch': basic_time / batch_time,
            'blocks_processed': len(blocks)
        }


def main():
    """演示向量化SM4实现"""
    print("=== SM4向量化优化演示 ===")
    
    # 创建实例并设置密钥
    sm4_vec = SM4Vectorized()
    key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    sm4_vec.set_key(key)
    
    # 测试单块加密
    plaintext = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    print(f"明文: {plaintext.hex().upper()}")
    
    ciphertext = sm4_vec.encrypt_block_vectorized(plaintext)
    print(f"密文: {ciphertext.hex().upper()}")
    
    decrypted = sm4_vec.decrypt_block_vectorized(ciphertext)
    print(f"解密: {decrypted.hex().upper()}")
    print(f"正确性: {'✓' if decrypted == plaintext else '✗'}")
    
    # 批量加密测试
    plaintexts = [bytes(range(16)) for _ in range(10)]
    ciphertexts = sm4_vec.encrypt_batch(plaintexts)
    print(f"\n批量加密测试: 处理{len(plaintexts)}个块")
    
    # 性能测试
    print("\n=== 性能测试 ===")
    results = sm4_vec.benchmark_vectorized()
    print(f"向量化单块时间: {results['vectorized_single_time']:.4f}s")
    print(f"向量化批量时间: {results['vectorized_batch_time']:.4f}s")
    print(f"基础实现时间: {results['basic_time']:.4f}s")
    print(f"单块加速比: {results['speedup_single']:.2f}x")
    print(f"批量加速比: {results['speedup_batch']:.2f}x")


if __name__ == "__main__":
    main()
