"""
SM4优化实现测试
测试各种优化版本的正确性和性能
"""

import pytest
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from basic.sm4_basic import SM4Basic
from optimized.sm4_lookup_table import SM4LookupTable
from optimized.sm4_bitwise import SM4Bitwise
from optimized.sm4_parallel import SM4Parallel
from utils.constants import TEST_VECTORS
from utils.helpers import format_hex

class TestOptimizedImplementations:
    """优化实现测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.key = TEST_VECTORS['key']
        self.plaintext = TEST_VECTORS['plaintext']
        self.expected_ciphertext = TEST_VECTORS['ciphertext']
        
        # 创建所有实现的实例
        self.sm4_basic = SM4Basic(self.key)
        self.sm4_lookup = SM4LookupTable(self.key)
        self.sm4_bitwise = SM4Bitwise(self.key)
        self.sm4_parallel = SM4Parallel(self.key, num_threads=2)  # 使用2线程避免测试过慢
    
    def test_lookup_table_correctness(self):
        """测试查找表优化版本的正确性"""
        # 加密测试
        ciphertext = self.sm4_lookup.encrypt(self.plaintext)
        assert ciphertext == self.expected_ciphertext, \
            f"查找表版本加密失败: 期望 {format_hex(self.expected_ciphertext)}, 实际 {format_hex(ciphertext)}"
        
        # 解密测试
        decrypted = self.sm4_lookup.decrypt(ciphertext)
        assert decrypted == self.plaintext, \
            f"查找表版本解密失败: 期望 {format_hex(self.plaintext)}, 实际 {format_hex(decrypted)}"
    
    def test_bitwise_correctness(self):
        """测试位运算优化版本的正确性"""
        # 加密测试
        ciphertext = self.sm4_bitwise.encrypt(self.plaintext)
        assert ciphertext == self.expected_ciphertext, \
            f"位运算版本加密失败: 期望 {format_hex(self.expected_ciphertext)}, 实际 {format_hex(ciphertext)}"
        
        # 解密测试
        decrypted = self.sm4_bitwise.decrypt(ciphertext)
        assert decrypted == self.plaintext, \
            f"位运算版本解密失败: 期望 {format_hex(self.plaintext)}, 实际 {format_hex(decrypted)}"
    
    def test_parallel_correctness(self):
        """测试并行优化版本的正确性"""
        # 加密测试
        ciphertext = self.sm4_parallel.encrypt(self.plaintext)
        assert ciphertext == self.expected_ciphertext, \
            f"并行版本加密失败: 期望 {format_hex(self.expected_ciphertext)}, 实际 {format_hex(ciphertext)}"
        
        # 解密测试
        decrypted = self.sm4_parallel.decrypt(ciphertext)
        assert decrypted == self.plaintext, \
            f"并行版本解密失败: 期望 {format_hex(self.plaintext)}, 实际 {format_hex(decrypted)}"
    
    def test_all_implementations_consistency(self):
        """测试所有实现的一致性"""
        # 测试多个不同的输入
        test_data = [
            TEST_VECTORS['plaintext'],
            b'\x00' * 16,  # 全零
            b'\xff' * 16,  # 全一
            b'\x01\x23\x45\x67\x89\xab\xcd\xef' * 2,  # 重复模式
        ]
        
        for data in test_data:
            # 所有版本加密结果应该相同
            basic_encrypted = self.sm4_basic.encrypt(data)
            lookup_encrypted = self.sm4_lookup.encrypt(data)
            bitwise_encrypted = self.sm4_bitwise.encrypt(data)
            parallel_encrypted = self.sm4_parallel.encrypt(data)
            
            assert basic_encrypted == lookup_encrypted, "基础版本和查找表版本加密结果不一致"
            assert basic_encrypted == bitwise_encrypted, "基础版本和位运算版本加密结果不一致"
            assert basic_encrypted == parallel_encrypted, "基础版本和并行版本加密结果不一致"
            
            # 所有版本解密结果应该相同
            basic_decrypted = self.sm4_basic.decrypt(basic_encrypted)
            lookup_decrypted = self.sm4_lookup.decrypt(lookup_encrypted)
            bitwise_decrypted = self.sm4_bitwise.decrypt(bitwise_encrypted)
            parallel_decrypted = self.sm4_parallel.decrypt(parallel_encrypted)
            
            assert basic_decrypted == lookup_decrypted, "基础版本和查找表版本解密结果不一致"
            assert basic_decrypted == bitwise_decrypted, "基础版本和位运算版本解密结果不一致"
            assert basic_decrypted == parallel_decrypted, "基础版本和并行版本解密结果不一致"
            assert basic_decrypted == data, "解密结果与原数据不符"
    
    def test_key_expansion_consistency(self):
        """测试密钥扩展的一致性"""
        basic_keys = self.sm4_basic.round_keys
        lookup_keys = self.sm4_lookup.round_keys
        bitwise_keys = self.sm4_bitwise.round_keys
        parallel_keys = self.sm4_parallel.round_keys
        
        assert basic_keys == lookup_keys, "基础版本和查找表版本轮密钥不一致"
        assert basic_keys == bitwise_keys, "基础版本和位运算版本轮密钥不一致"
        assert basic_keys == parallel_keys, "基础版本和并行版本轮密钥不一致"
    
    def test_optimization_info(self):
        """测试优化信息输出"""
        lookup_info = self.sm4_lookup.get_optimization_info()
        bitwise_info = self.sm4_bitwise.get_optimization_info()
        parallel_info = self.sm4_parallel.get_optimization_info()
        
        # 检查信息格式
        assert 'optimization_type' in lookup_info
        assert 'optimization_type' in bitwise_info
        assert 'optimization_type' in parallel_info
        
        print(f"\n查找表优化信息: {lookup_info}")
        print(f"位运算优化信息: {bitwise_info}")
        print(f"并行优化信息: {parallel_info}")

class TestLargeDataProcessing:
    """大数据处理测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.key = TEST_VECTORS['key']
        self.sm4_basic = SM4Basic(self.key)
        self.sm4_lookup = SM4LookupTable(self.key)
        self.sm4_bitwise = SM4Bitwise(self.key)
    
    def test_large_data_consistency(self):
        """测试大量数据的一致性"""
        # 创建1KB的测试数据
        large_data = (TEST_VECTORS['plaintext'] * 64)  # 1024字节
        
        # 所有版本处理结果应该一致
        basic_result = self.sm4_basic.encrypt(large_data)
        lookup_result = self.sm4_lookup.encrypt(large_data)
        bitwise_result = self.sm4_bitwise.encrypt(large_data)
        parallel_result = self.sm4_parallel.encrypt(large_data)
        
        assert basic_result == lookup_result, "大数据处理：基础版本和查找表版本结果不一致"
        assert basic_result == bitwise_result, "大数据处理：基础版本和位运算版本结果不一致"
        assert basic_result == parallel_result, "大数据处理：基础版本和并行版本结果不一致"
        
        # 解密测试
        basic_decrypted = self.sm4_basic.decrypt(basic_result)
        lookup_decrypted = self.sm4_lookup.decrypt(lookup_result)
        bitwise_decrypted = self.sm4_bitwise.decrypt(bitwise_result)
        parallel_decrypted = self.sm4_parallel.decrypt(parallel_result)
        
        assert basic_decrypted == large_data, "基础版本大数据解密失败"
        assert lookup_decrypted == large_data, "查找表版本大数据解密失败"
        assert bitwise_decrypted == large_data, "位运算版本大数据解密失败"
        assert parallel_decrypted == large_data, "并行版本大数据解密失败"

class TestEdgeCases:
    """边缘情况测试"""
    
    def test_all_zero_key(self):
        """测试全零密钥"""
        zero_key = b'\x00' * 16
        plaintext = TEST_VECTORS['plaintext']
        
        sm4_basic = SM4Basic(zero_key)
        sm4_lookup = SM4LookupTable(zero_key)
        sm4_bitwise = SM4Bitwise(zero_key)
        sm4_parallel = SM4Parallel(zero_key, num_threads=2)
        
        # 所有版本结果应该一致
        basic_result = sm4_basic.encrypt(plaintext)
        lookup_result = sm4_lookup.encrypt(plaintext)
        bitwise_result = sm4_bitwise.encrypt(plaintext)
        parallel_result = sm4_parallel.encrypt(plaintext)
        
        assert basic_result == lookup_result
        assert basic_result == bitwise_result
        assert basic_result == parallel_result
    
    def test_all_one_key(self):
        """测试全一密钥"""
        one_key = b'\xff' * 16
        plaintext = TEST_VECTORS['plaintext']
        
        sm4_basic = SM4Basic(one_key)
        sm4_lookup = SM4LookupTable(one_key)
        sm4_bitwise = SM4Bitwise(one_key)
        sm4_parallel = SM4Parallel(one_key, num_threads=2)
        
        # 所有版本结果应该一致
        basic_result = sm4_basic.encrypt(plaintext)
        lookup_result = sm4_lookup.encrypt(plaintext)
        bitwise_result = sm4_bitwise.encrypt(plaintext)
        parallel_result = sm4_parallel.encrypt(plaintext)
        
        assert basic_result == lookup_result
        assert basic_result == bitwise_result
        assert basic_result == parallel_result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
