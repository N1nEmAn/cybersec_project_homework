"""
SM4算法基础功能测试
测试基础实现的正确性
"""

import pytest
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from basic.sm4_basic import SM4Basic
from utils.constants import TEST_VECTORS
from utils.helpers import format_hex, pad_pkcs7, unpad_pkcs7

class TestSM4Basic:
    """SM4基础实现测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.key = TEST_VECTORS['key']
        self.plaintext = TEST_VECTORS['plaintext']
        self.expected_ciphertext = TEST_VECTORS['ciphertext']
        self.sm4 = SM4Basic(self.key)
    
    def test_standard_vector(self):
        """测试标准测试向量"""
        # 加密测试
        ciphertext = self.sm4.encrypt(self.plaintext)
        assert ciphertext == self.expected_ciphertext, \
            f"加密失败: 期望 {format_hex(self.expected_ciphertext)}, 实际 {format_hex(ciphertext)}"
        
        # 解密测试
        decrypted = self.sm4.decrypt(ciphertext)
        assert decrypted == self.plaintext, \
            f"解密失败: 期望 {format_hex(self.plaintext)}, 实际 {format_hex(decrypted)}"
    
    def test_multiple_blocks(self):
        """测试多分组加解密"""
        # 创建多个分组的数据
        long_plaintext = self.plaintext * 3  # 48字节，3个分组
        
        ciphertext = self.sm4.encrypt(long_plaintext)
        assert len(ciphertext) == 48, f"密文长度错误: {len(ciphertext)}"
        
        decrypted = self.sm4.decrypt(ciphertext)
        assert decrypted == long_plaintext, "多分组解密失败"
    
    def test_key_expansion(self):
        """测试密钥扩展"""
        round_keys = self.sm4.round_keys
        
        # 检查轮密钥数量
        assert len(round_keys) == 32, f"轮密钥数量错误: {len(round_keys)}"
        
        # 检查轮密钥范围
        for i, rk in enumerate(round_keys):
            assert 0 <= rk <= 0xffffffff, f"轮密钥{i}超出范围: {rk:08x}"
    
    def test_empty_data(self):
        """测试空数据"""
        empty_data = b''
        
        ciphertext = self.sm4.encrypt(empty_data)
        assert ciphertext == b'', "空数据加密应返回空"
        
        decrypted = self.sm4.decrypt(empty_data)
        assert decrypted == b'', "空数据解密应返回空"
    
    def test_invalid_key_length(self):
        """测试无效密钥长度"""
        with pytest.raises(ValueError):
            SM4Basic(b'shortkey')  # 8字节
        
        with pytest.raises(ValueError):
            SM4Basic(b'this_key_is_too_long_for_sm4_algorithm')  # 34字节
    
    def test_invalid_data_length(self):
        """测试无效数据长度"""
        invalid_data = b'not_16_byte_mul'  # 15字节
        
        with pytest.raises(ValueError):
            self.sm4.encrypt(invalid_data)
        
        with pytest.raises(ValueError):
            self.sm4.decrypt(invalid_data)
    
    def test_with_padding(self):
        """测试PKCS#7填充"""
        # 原始数据不是16字节倍数
        original_data = b'Hello, SM4!'  # 11字节
        
        # 添加填充
        padded_data = pad_pkcs7(original_data)
        assert len(padded_data) % 16 == 0, "填充后长度应该是16的倍数"
        
        # 加密
        ciphertext = self.sm4.encrypt(padded_data)
        
        # 解密
        decrypted_padded = self.sm4.decrypt(ciphertext)
        
        # 移除填充
        decrypted = unpad_pkcs7(decrypted_padded)
        
        assert decrypted == original_data, "填充测试失败"
    
    def test_consistency(self):
        """测试多次加解密的一致性"""
        for i in range(10):
            ciphertext = self.sm4.encrypt(self.plaintext)
            assert ciphertext == self.expected_ciphertext, f"第{i+1}次加密不一致"
            
            decrypted = self.sm4.decrypt(ciphertext)
            assert decrypted == self.plaintext, f"第{i+1}次解密不一致"

class TestSM4Components:
    """SM4组件测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.sm4 = SM4Basic(TEST_VECTORS['key'])
    
    def test_sbox_transform(self):
        """测试S盒变换"""
        # 测试一些已知的S盒值
        assert self.sm4._sbox_transform(0x00) == 0xd6
        assert self.sm4._sbox_transform(0xff) == 0x48
        assert self.sm4._sbox_transform(0x12) == 0x9a
    
    def test_linear_transform(self):
        """测试线性变换"""
        # 测试L变换的性质：L(0) = 0
        assert self.sm4._linear_transform_l(0) == 0
        
        # 测试L'变换的性质：L'(0) = 0  
        assert self.sm4._linear_transform_l_prime(0) == 0
    
    def test_rotl(self):
        """测试左循环移位"""
        from utils.helpers import rotl
        
        # 测试已知值
        assert rotl(0x12345678, 4) == 0x23456781
        assert rotl(0x80000000, 1) == 0x00000001
        assert rotl(0x00000001, 31) == 0x80000000

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
