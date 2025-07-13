#!/usr/bin/env python3
"""
SM4算法示例演示
展示SM4的基本使用方法和各种功能
"""

import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.basic.sm4_basic import SM4Basic
from src.optimized.sm4_lookup_table import SM4LookupTable
from src.modes.sm4_modes import SM4Modes


def example_basic_usage():
    """基础使用示例"""
    print("=== SM4基础使用示例 ===")
    
    # 创建密钥
    key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    print(f"密钥: {key.hex().upper()}")
    
    # 创建SM4实例
    sm4 = SM4Basic(key)
    
    # 加密短文本
    plaintext = b"Hello, SM4!"
    print(f"明文: {plaintext.decode()}")
    
    ciphertext = sm4.encrypt_ecb(plaintext)
    print(f"密文: {ciphertext.hex().upper()}")
    
    # 解密
    decrypted = sm4.decrypt_ecb(ciphertext)
    print(f"解密: {decrypted.decode()}")
    
    print(f"正确性验证: {'✓ 通过' if decrypted == plaintext else '✗ 失败'}")
    print()


def example_optimization_comparison():
    """优化实现比较示例"""
    print("=== 优化实现比较示例 ===")
    
    key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    test_data = b"This is a test message for SM4 optimization comparison."
    
    # 基础实现
    sm4_basic = SM4Basic(key)
    basic_result = sm4_basic.encrypt_ecb(test_data)
    print(f"基础实现密文: {basic_result.hex().upper()[:32]}...")
    
    # 查找表优化
    sm4_lookup = SM4LookupTable(key)
    lookup_result = sm4_lookup.encrypt_ecb(test_data)
    print(f"查找表优化密文: {lookup_result.hex().upper()[:32]}...")
    
    # 验证结果一致性
    print(f"结果一致性: {'✓ 一致' if basic_result == lookup_result else '✗ 不一致'}")
    print()


def example_encryption_modes():
    """加密模式示例"""
    print("=== 加密模式示例 ===")
    
    key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    sm4_modes = SM4Modes(key)
    
    message = b"This message will be encrypted using different modes."
    print(f"原始消息: {message.decode()}")
    print(f"消息长度: {len(message)} 字节\n")
    
    # ECB模式
    print("ECB模式:")
    ecb_cipher = sm4_modes.encrypt_ecb(message)
    ecb_plain = sm4_modes.decrypt_ecb(ecb_cipher)
    print(f"  密文长度: {len(ecb_cipher)} 字节")
    print(f"  正确性: {'✓' if ecb_plain == message else '✗'}")
    
    # CBC模式
    print("CBC模式:")
    cbc_cipher, iv = sm4_modes.encrypt_cbc(message)
    cbc_plain = sm4_modes.decrypt_cbc(cbc_cipher, iv)
    print(f"  IV: {iv.hex().upper()}")
    print(f"  密文长度: {len(cbc_cipher)} 字节")
    print(f"  正确性: {'✓' if cbc_plain == message else '✗'}")
    
    # CTR模式
    print("CTR模式:")
    ctr_cipher, counter = sm4_modes.encrypt_ctr(message)
    ctr_plain = sm4_modes.decrypt_ctr(ctr_cipher, counter)
    print(f"  计数器: {counter.hex().upper()}")
    print(f"  密文长度: {len(ctr_cipher)} 字节 (无填充)")
    print(f"  正确性: {'✓' if ctr_plain == message else '✗'}")
    print()


def example_file_encryption():
    """文件加密示例"""
    print("=== 文件加密示例 ===")
    
    # 创建测试文件
    test_file = "test_document.txt"
    test_content = """这是一个SM4加密测试文档。

SM4是中国国家标准的分组密码算法，具有以下特点：
1. 分组长度：128位
2. 密钥长度：128位
3. 轮数：32轮
4. 结构：Feistel网络

本文档用于演示SM4的文件加密功能。
"""
    
    # 写入测试文件
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"创建测试文件: {test_file}")
    print(f"文件大小: {os.path.getsize(test_file)} 字节")
    
    # 加密文件
    key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    sm4 = SM4Basic(key)
    
    with open(test_file, 'rb') as f:
        file_data = f.read()
    
    encrypted_data = sm4.encrypt_ecb(file_data)
    
    # 保存加密文件
    encrypted_file = test_file + ".sm4"
    with open(encrypted_file, 'wb') as f:
        f.write(encrypted_data)
    
    print(f"加密文件: {encrypted_file}")
    print(f"加密后大小: {os.path.getsize(encrypted_file)} 字节")
    
    # 解密验证
    with open(encrypted_file, 'rb') as f:
        encrypted_data = f.read()
    
    decrypted_data = sm4.decrypt_ecb(encrypted_data)
    
    # 保存解密文件
    decrypted_file = test_file + ".decrypted"
    with open(decrypted_file, 'wb') as f:
        f.write(decrypted_data)
    
    print(f"解密文件: {decrypted_file}")
    
    # 验证
    with open(decrypted_file, 'r', encoding='utf-8') as f:
        decrypted_content = f.read()
    
    print(f"解密正确性: {'✓ 通过' if decrypted_content == test_content else '✗ 失败'}")
    
    # 清理文件
    os.remove(test_file)
    os.remove(encrypted_file)
    os.remove(decrypted_file)
    print("清理临时文件完成")
    print()


def example_performance_test():
    """性能测试示例"""
    print("=== 性能测试示例 ===")
    
    import time
    
    key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    test_data = os.urandom(1024)  # 1KB测试数据
    
    # 测试基础实现
    sm4_basic = SM4Basic(key)
    start_time = time.time()
    for _ in range(100):
        sm4_basic.encrypt_ecb(test_data)
    basic_time = time.time() - start_time
    
    # 测试优化实现
    sm4_lookup = SM4LookupTable(key)
    start_time = time.time()
    for _ in range(100):
        sm4_lookup.encrypt_ecb(test_data)
    lookup_time = time.time() - start_time
    
    print(f"基础实现时间: {basic_time:.4f}s")
    print(f"查找表优化时间: {lookup_time:.4f}s")
    print(f"加速比: {basic_time/lookup_time:.2f}x")
    print()


def example_standard_test_vectors():
    """标准测试向量验证"""
    print("=== 标准测试向量验证 ===")
    
    # GB/T 32907-2016 标准测试向量
    key = bytes.fromhex('0123456789abcdeffedcba9876543210')
    plaintext = bytes.fromhex('0123456789abcdeffedcba9876543210')
    expected_ciphertext = bytes.fromhex('681edf34d206965e86b3e94f536e4246')
    
    print(f"标准密钥: {key.hex().upper()}")
    print(f"标准明文: {plaintext.hex().upper()}")
    print(f"期望密文: {expected_ciphertext.hex().upper()}")
    
    # 测试基础实现
    sm4 = SM4Basic(key)
    actual_ciphertext = sm4.encrypt_block(plaintext)
    
    print(f"实际密文: {actual_ciphertext.hex().upper()}")
    print(f"标准符合性: {'✓ 通过' if actual_ciphertext == expected_ciphertext else '✗ 失败'}")
    
    # 测试解密
    decrypted = sm4.decrypt_block(actual_ciphertext)
    print(f"解密验证: {'✓ 通过' if decrypted == plaintext else '✗ 失败'}")
    print()


def main():
    """主演示函数"""
    print("SM4算法演示程序")
    print("=" * 50)
    print()
    
    # 运行所有示例
    example_basic_usage()
    example_optimization_comparison()
    example_encryption_modes()
    example_file_encryption()
    example_performance_test()
    example_standard_test_vectors()
    
    print("所有演示完成！")
    print("\n更多功能请查看:")
    print("- 命令行工具: python sm4cli.py --help")
    print("- GUI界面: python -m src.gui.sm4_gui")
    print("- 性能测试: python comprehensive_benchmark.py")


if __name__ == '__main__':
    main()
