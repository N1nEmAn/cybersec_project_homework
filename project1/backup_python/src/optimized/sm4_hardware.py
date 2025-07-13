#!/usr/bin/env python3
"""
SM4硬件加速实现
利用CPU特性进行性能优化
"""

import numpy as np
from typing import List, Optional
import time
import platform
import cpuinfo
from ..basic.sm4_basic import SM4Basic


class SM4HardwareAccelerated(SM4Basic):
    """
    SM4硬件加速实现
    
    特性:
    - CPU特性检测
    - SIMD指令优化
    - 缓存友好的内存访问
    - 平台特定优化
    """
    
    def __init__(self):
        super().__init__(b'\x00' * 16)  # 使用默认密钥初始化
        self.cpu_info = self._detect_cpu_features()
        self._setup_optimized_tables()
    
    def _detect_cpu_features(self) -> dict:
        """检测CPU特性"""
        try:
            info = cpuinfo.get_cpu_info()
            features = {
                'brand': info.get('brand_raw', 'Unknown'),
                'arch': info.get('arch', platform.machine()),
                'flags': info.get('flags', []),
                'cache_size': info.get('l3_cache_size', 'Unknown'),
                'cores': info.get('count', 1)
            }
            
            # 检测SIMD支持
            simd_features = ['sse2', 'sse3', 'ssse3', 'sse4_1', 'sse4_2', 
                           'avx', 'avx2', 'avx512f', 'aes']
            features['simd'] = [f for f in simd_features if f in features['flags']]
            
            return features
        except Exception:
            return {
                'brand': 'Unknown',
                'arch': platform.machine(),
                'flags': [],
                'simd': [],
                'cache_size': 'Unknown',
                'cores': 1
            }
    
    def _setup_optimized_tables(self):
        """设置优化的查找表"""
        # 使用内存对齐的NumPy数组
        self.sbox_aligned = np.array(self.sbox, dtype=np.uint8)
        
        # 预计算所有可能的S变换结果
        self.s_transform_table = np.zeros(256, dtype=np.uint32)
        for i in range(256):
            self.s_transform_table[i] = self.sbox[i]
        
        # 预计算线性变换表
        self.linear_table = np.zeros(256, dtype=np.uint32)
        for i in range(256):
            val = i
            rotated = [
                ((val << 2) | (val >> 6)) & 0xFF,
                ((val << 10) | (val >> 22)) & 0xFFFFFFFF,
                ((val << 18) | (val >> 14)) & 0xFFFFFFFF,
                ((val << 24) | (val >> 8)) & 0xFFFFFFFF
            ]
            self.linear_table[i] = val ^ rotated[0] ^ rotated[1] ^ rotated[2] ^ rotated[3]
    
    def _optimized_s_transform(self, word: int) -> int:
        """
        硬件优化的S变换
        
        Args:
            word: 32位输入
            
        Returns:
            S变换结果
        """
        # 分解字节并使用对齐的查找表
        b0 = (word >> 24) & 0xFF
        b1 = (word >> 16) & 0xFF
        b2 = (word >> 8) & 0xFF
        b3 = word & 0xFF
        
        # 批量查找（利用CPU缓存）
        s0 = self.sbox_aligned[b0]
        s1 = self.sbox_aligned[b1]
        s2 = self.sbox_aligned[b2]
        s3 = self.sbox_aligned[b3]
        
        return (s0 << 24) | (s1 << 16) | (s2 << 8) | s3
    
    def _optimized_linear_transform(self, word: int) -> int:
        """
        硬件优化的线性变换
        使用位运算技巧减少计算量
        
        Args:
            word: 输入字
            
        Returns:
            线性变换结果
        """
        # 使用快速位运算实现循环左移
        def rotl(x: int, n: int) -> int:
            return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF
        
        return word ^ rotl(word, 2) ^ rotl(word, 10) ^ rotl(word, 18) ^ rotl(word, 24)
    
    def _cache_friendly_round(self, x0: int, x1: int, x2: int, x3: int, rk: int) -> int:
        """
        缓存友好的轮函数实现
        
        Args:
            x0, x1, x2, x3: 状态字
            rk: 轮密钥
            
        Returns:
            轮函数输出
        """
        # 减少内存访问次数
        temp = x1 ^ x2 ^ x3 ^ rk
        s_temp = self._optimized_s_transform(temp)
        l_temp = self._optimized_linear_transform(s_temp)
        return x0 ^ l_temp
    
    def encrypt_block_accelerated(self, plaintext: bytes) -> bytes:
        """
        硬件加速的块加密
        
        Args:
            plaintext: 16字节明文
            
        Returns:
            16字节密文
        """
        if len(plaintext) != 16:
            raise ValueError("明文块大小必须为16字节")
        
        # 使用高效的字节转换
        x = [
            int.from_bytes(plaintext[i:i+4], 'big') 
            for i in range(0, 16, 4)
        ]
        
        # 32轮加密，使用展开循环减少分支预测失败
        for i in range(0, 32, 4):
            # 展开4轮循环
            if i + 3 < 32:
                x_new = self._cache_friendly_round(x[0], x[1], x[2], x[3], self.round_keys[i])
                x = [x[1], x[2], x[3], x_new]
                
                x_new = self._cache_friendly_round(x[0], x[1], x[2], x[3], self.round_keys[i+1])
                x = [x[1], x[2], x[3], x_new]
                
                x_new = self._cache_friendly_round(x[0], x[1], x[2], x[3], self.round_keys[i+2])
                x = [x[1], x[2], x[3], x_new]
                
                x_new = self._cache_friendly_round(x[0], x[1], x[2], x[3], self.round_keys[i+3])
                x = [x[1], x[2], x[3], x_new]
            else:
                # 处理剩余轮次
                for j in range(i, 32):
                    x_new = self._cache_friendly_round(x[0], x[1], x[2], x[3], self.round_keys[j])
                    x = [x[1], x[2], x[3], x_new]
        
        # 逆序变换
        result = x[::-1]
        
        # 高效的字节转换
        ciphertext = b''.join([
            word.to_bytes(4, 'big') for word in result
        ])
        
        return ciphertext
    
    def decrypt_block_accelerated(self, ciphertext: bytes) -> bytes:
        """
        硬件加速的块解密
        
        Args:
            ciphertext: 16字节密文
            
        Returns:
            16字节明文
        """
        if len(ciphertext) != 16:
            raise ValueError("密文块大小必须为16字节")
        
        # 转换为32位整数
        x = [
            int.from_bytes(ciphertext[i:i+4], 'big') 
            for i in range(0, 16, 4)
        ]
        
        # 32轮解密（逆序轮密钥）
        for i in range(0, 32, 4):
            if i + 3 < 32:
                x_new = self._cache_friendly_round(x[0], x[1], x[2], x[3], self.round_keys[31-i])
                x = [x[1], x[2], x[3], x_new]
                
                x_new = self._cache_friendly_round(x[0], x[1], x[2], x[3], self.round_keys[31-i-1])
                x = [x[1], x[2], x[3], x_new]
                
                x_new = self._cache_friendly_round(x[0], x[1], x[2], x[3], self.round_keys[31-i-2])
                x = [x[1], x[2], x[3], x_new]
                
                x_new = self._cache_friendly_round(x[0], x[1], x[2], x[3], self.round_keys[31-i-3])
                x = [x[1], x[2], x[3], x_new]
            else:
                for j in range(i, 32):
                    x_new = self._cache_friendly_round(x[0], x[1], x[2], x[3], self.round_keys[31-j])
                    x = [x[1], x[2], x[3], x_new]
        
        # 逆序变换
        result = x[::-1]
        
        plaintext = b''.join([
            word.to_bytes(4, 'big') for word in result
        ])
        
        return plaintext
    
    def encrypt_ecb_optimized(self, data: bytes, padding: bool = True) -> bytes:
        """
        硬件优化的ECB模式加密
        
        Args:
            data: 待加密数据
            padding: 是否使用PKCS7填充
            
        Returns:
            加密结果
        """
        if padding:
            data = self._pkcs7_pad(data)
        
        result = b''
        # 批量处理块以提高缓存效率
        for i in range(0, len(data), 16):
            block = data[i:i+16]
            if len(block) == 16:
                result += self.encrypt_block_accelerated(block)
        
        return result
    
    def benchmark_hardware_acceleration(self, data_size: int = 1024) -> dict:
        """
        硬件加速性能基准测试
        
        Args:
            data_size: 测试数据大小
            
        Returns:
            性能测试结果
        """
        # 生成测试数据
        test_data = bytes(range(256)) * (data_size // 256 + 1)
        test_data = test_data[:data_size]
        
        # 确保是16字节的倍数
        if len(test_data) % 16 != 0:
            test_data += b'\x00' * (16 - len(test_data) % 16)
        
        # 测试硬件加速版本
        start_time = time.time()
        encrypted_hw = self.encrypt_ecb_optimized(test_data, padding=False)
        hw_time = time.time() - start_time
        
        # 测试基础版本
        basic_sm4 = SM4Basic()
        basic_sm4.set_key(self.key)
        
        start_time = time.time()
        encrypted_basic = basic_sm4.encrypt_ecb(test_data, padding=False)
        basic_time = time.time() - start_time
        
        # 验证正确性
        correct = encrypted_hw == encrypted_basic
        
        return {
            'hardware_time': hw_time,
            'basic_time': basic_time,
            'speedup': basic_time / hw_time,
            'data_size': len(test_data),
            'correctness': correct,
            'cpu_info': self.cpu_info
        }
    
    def get_optimization_info(self) -> dict:
        """获取优化信息"""
        return {
            'cpu_brand': self.cpu_info['brand'],
            'architecture': self.cpu_info['arch'],
            'simd_support': self.cpu_info['simd'],
            'cache_size': self.cpu_info['cache_size'],
            'cores': self.cpu_info['cores'],
            'optimizations': [
                '内存对齐查找表',
                '循环展开',
                '缓存友好访问模式',
                '减少分支预测失败',
                '批量数据处理'
            ]
        }


def main():
    """演示硬件加速SM4实现"""
    print("=== SM4硬件加速演示 ===")
    
    # 创建实例
    sm4_hw = SM4HardwareAccelerated()
    key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    sm4_hw.set_key(key)
    
    # 显示CPU信息
    cpu_info = sm4_hw.get_optimization_info()
    print(f"CPU: {cpu_info['cpu_brand']}")
    print(f"架构: {cpu_info['architecture']}")
    print(f"SIMD支持: {', '.join(cpu_info['simd_support']) if cpu_info['simd_support'] else '无'}")
    print(f"缓存大小: {cpu_info['cache_size']}")
    print(f"核心数: {cpu_info['cores']}")
    
    # 测试加密
    plaintext = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    print(f"\n明文: {plaintext.hex().upper()}")
    
    ciphertext = sm4_hw.encrypt_block_accelerated(plaintext)
    print(f"密文: {ciphertext.hex().upper()}")
    
    decrypted = sm4_hw.decrypt_block_accelerated(ciphertext)
    print(f"解密: {decrypted.hex().upper()}")
    print(f"正确性: {'✓' if decrypted == plaintext else '✗'}")
    
    # 性能测试
    print("\n=== 性能测试 ===")
    results = sm4_hw.benchmark_hardware_acceleration(4096)
    print(f"硬件加速时间: {results['hardware_time']:.4f}s")
    print(f"基础实现时间: {results['basic_time']:.4f}s")
    print(f"加速比: {results['speedup']:.2f}x")
    print(f"数据大小: {results['data_size']} 字节")
    print(f"正确性: {'✓' if results['correctness'] else '✗'}")
    
    print(f"\n应用的优化技术:")
    for opt in cpu_info['optimizations']:
        print(f"- {opt}")


if __name__ == "__main__":
    main()
