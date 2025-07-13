#!/usr/bin/env python3
"""
测试向量验证工具
验证实现是否符合GB/T 32907-2016标准
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.basic.sm4_basic import SM4Basic
from src.optimized.sm4_lookup_table import SM4LookupTable
from src.optimized.sm4_parallel import SM4Parallel
from src.utils.constants import TEST_VECTORS


def validate_implementation(impl_class, name):
    """验证单个实现是否正确"""
    print(f"\n验证 {name}...")
    
    try:
        key = TEST_VECTORS['key']
        plaintext = TEST_VECTORS['plaintext']
        expected_ciphertext = TEST_VECTORS['ciphertext']
        
        sm4 = impl_class(key)
        
        # 加密测试
        ciphertext = sm4.encrypt(plaintext)
        if ciphertext == expected_ciphertext:
            print(f"  ✓ 加密测试通过")
        else:
            print(f"  ✗ 加密测试失败")
            print(f"    期望: {expected_ciphertext.hex()}")
            print(f"    实际: {ciphertext.hex()}")
            return False
        
        # 解密测试
        decrypted = sm4.decrypt(ciphertext)
        if decrypted == plaintext:
            print(f"  ✓ 解密测试通过")
        else:
            print(f"  ✗ 解密测试失败")
            print(f"    期望: {plaintext.hex()}")
            print(f"    实际: {decrypted.hex()}")
            return False
        
        # ECB模式测试（如果支持）
        if hasattr(sm4, 'encrypt_ecb'):
            test_data = b"Hello World!1234"  # 16字节
            encrypted = sm4.encrypt_ecb(test_data)
            decrypted_ecb = sm4.decrypt_ecb(encrypted)
            if decrypted_ecb == test_data:
                print(f"  ✓ ECB模式测试通过")
            else:
                print(f"  ✗ ECB模式测试失败")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ 验证出错: {e}")
        return False


def main():
    """主验证函数"""
    print("SM4实现标准符合性验证")
    print("=" * 40)
    
    implementations = [
        (SM4Basic, "基础实现"),
        (SM4LookupTable, "查找表优化"),
        (SM4Parallel, "并行实现")
    ]
    
    all_passed = True
    
    for impl_class, name in implementations:
        result = validate_implementation(impl_class, name)
        if not result:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ 所有实现均通过标准验证")
    else:
        print("✗ 部分实现未通过验证，请检查")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
