#!/usr/bin/env python3
"""
快速测试小工具
用来快速验证SM4实现是否正确，不用每次都跑完整测试
写这个主要是因为测试太慢了，每次改完代码都要等半天...
"""

import sys
from pathlib import Path

# 老套路，添加路径
sys.path.insert(0, str(Path(__file__).parent))

from src.basic.sm4_basic import SM4Basic
from src.optimized.sm4_lookup_table import SM4LookupTable


def quick_test():
    """超快速测试，就测试一下基本功能能不能跑"""
    print("🚀 快速测试开始...")
    
    # 用标准测试向量
    key = bytes.fromhex('0123456789abcdeffedcba9876543210')
    plaintext = bytes.fromhex('0123456789abcdeffedcba9876543210')
    expected = bytes.fromhex('681edf34d206965e86b3e94f536e4246')
    
    try:
        # 测试基础实现
        print("测试基础实现...", end=" ")
        sm4_basic = SM4Basic(key)
        result = sm4_basic.encrypt_block(plaintext)
        if result == expected:
            print("✓")
        else:
            print("✗ 坏了!")
            return False
            
        # 测试查找表实现
        print("测试查找表实现...", end=" ")
        sm4_lookup = SM4LookupTable(key)
        result2 = sm4_lookup.encrypt_block(plaintext)
        if result2 == expected:
            print("✓")
        else:
            print("✗ 坏了!")
            return False
            
        # 测试加解密对称性
        print("测试加解密对称性...", end=" ")
        test_data = b"Hello SM4!"
        encrypted = sm4_basic.encrypt_ecb(test_data)
        decrypted = sm4_basic.decrypt_ecb(encrypted)
        if decrypted == test_data:
            print("✓")
        else:
            print("✗ 坏了!")
            return False
            
        print("🎉 所有测试通过! 代码应该没问题")
        return True
        
    except Exception as e:
        print(f"💥 测试炸了: {e}")
        return False


def performance_peek():
    """偷看一下性能，不做完整测试"""
    import time
    import os
    
    print("\n⚡ 偷看一下性能...")
    
    key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    test_data = os.urandom(1024)  # 1KB够了，不用太大
    
    # 基础实现
    sm4_basic = SM4Basic(key)
    start = time.time()
    for _ in range(50):  # 50次就够了，不用1000次
        sm4_basic.encrypt_ecb(test_data)
    basic_time = time.time() - start
    
    # 查找表实现
    sm4_lookup = SM4LookupTable(key)
    start = time.time()
    for _ in range(50):
        sm4_lookup.encrypt_ecb(test_data)
    lookup_time = time.time() - start
    
    speedup = basic_time / lookup_time
    print(f"基础实现: {basic_time:.3f}s")
    print(f"查找表: {lookup_time:.3f}s")
    print(f"加速比: {speedup:.2f}x {'🔥' if speedup > 1.5 else '😐' if speedup > 1.0 else '😭'}")


if __name__ == "__main__":
    if quick_test():
        performance_peek()
    else:
        print("❌ 基础测试都过不了，先修bug吧...")
        sys.exit(1)
