#!/usr/bin/env python3
"""
SM4加密模式测试
"""

import pytest
import os
from src.modes.sm4_modes import SM4Modes


class TestSM4Modes:
    """SM4加密模式测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
        self.sm4_modes = SM4Modes(self.key)
        self.test_data = b"Hello, World! This is a test message for SM4 modes."
        self.short_data = b"Hello"
        self.block_data = b"0123456789ABCDEF"  # 正好16字节
    
    def test_ecb_mode(self):
        """测试ECB模式"""
        # 测试加密解密
        ciphertext = self.sm4_modes.encrypt_ecb(self.test_data)
        plaintext = self.sm4_modes.decrypt_ecb(ciphertext)
        assert plaintext == self.test_data
        
        # 测试无填充模式（使用正确长度的数据）
        block_aligned_data = self.test_data[:48]  # 取48字节（3个完整块）
        if len(block_aligned_data) % 16 != 0:
            # 填充到16字节的倍数
            pad_len = 16 - (len(block_aligned_data) % 16)
            block_aligned_data += b'\x00' * pad_len
        
        ciphertext_no_pad = self.sm4_modes.encrypt_ecb(block_aligned_data, padding=False)
        plaintext_no_pad = self.sm4_modes.decrypt_ecb(ciphertext_no_pad, padding=False)
        assert plaintext_no_pad == block_aligned_data
    
    def test_cbc_mode(self):
        """测试CBC模式"""
        # 使用随机IV
        ciphertext, iv = self.sm4_modes.encrypt_cbc(self.test_data)
        plaintext = self.sm4_modes.decrypt_cbc(ciphertext, iv)
        assert plaintext == self.test_data
        assert len(iv) == 16
        
        # 使用指定IV
        custom_iv = b'\x00' * 16
        ciphertext2, iv2 = self.sm4_modes.encrypt_cbc(self.test_data, custom_iv)
        plaintext2 = self.sm4_modes.decrypt_cbc(ciphertext2, iv2)
        assert plaintext2 == self.test_data
        assert iv2 == custom_iv
        
        # 测试不同IV产生不同密文
        ciphertext3, iv3 = self.sm4_modes.encrypt_cbc(self.test_data)
        assert ciphertext != ciphertext3  # 不同IV应产生不同密文
    
    def test_ctr_mode(self):
        """测试CTR模式"""
        # 测试基本功能
        ciphertext, counter = self.sm4_modes.encrypt_ctr(self.test_data)
        plaintext = self.sm4_modes.decrypt_ctr(ciphertext, counter)
        assert plaintext == self.test_data
        assert len(counter) == 16
        
        # 测试指定计数器
        custom_counter = b'\x01' * 16
        ciphertext2, counter2 = self.sm4_modes.encrypt_ctr(self.test_data, custom_counter)
        plaintext2 = self.sm4_modes.decrypt_ctr(ciphertext2, counter2)
        assert plaintext2 == self.test_data
        assert counter2 == custom_counter
        
        # 测试短数据
        short_cipher, short_counter = self.sm4_modes.encrypt_ctr(self.short_data)
        short_plain = self.sm4_modes.decrypt_ctr(short_cipher, short_counter)
        assert short_plain == self.short_data
        assert len(short_cipher) == len(self.short_data)  # CTR不增加长度
    
    def test_cfb_mode(self):
        """测试CFB模式"""
        # 测试基本功能
        ciphertext, iv = self.sm4_modes.encrypt_cfb(self.test_data)
        plaintext = self.sm4_modes.decrypt_cfb(ciphertext, iv)
        assert plaintext == self.test_data
        assert len(iv) == 16
        
        # 测试指定IV
        custom_iv = b'\x02' * 16
        ciphertext2, iv2 = self.sm4_modes.encrypt_cfb(self.test_data, custom_iv)
        plaintext2 = self.sm4_modes.decrypt_cfb(ciphertext2, iv2)
        assert plaintext2 == self.test_data
        assert iv2 == custom_iv
        
        # 测试短数据
        short_cipher, short_iv = self.sm4_modes.encrypt_cfb(self.short_data)
        short_plain = self.sm4_modes.decrypt_cfb(short_cipher, short_iv)
        assert short_plain == self.short_data
        assert len(short_cipher) == len(self.short_data)
    
    def test_ofb_mode(self):
        """测试OFB模式"""
        # 测试基本功能
        ciphertext, iv = self.sm4_modes.encrypt_ofb(self.test_data)
        plaintext = self.sm4_modes.decrypt_ofb(ciphertext, iv)
        assert plaintext == self.test_data
        assert len(iv) == 16
        
        # 测试指定IV
        custom_iv = b'\x03' * 16
        ciphertext2, iv2 = self.sm4_modes.encrypt_ofb(self.test_data, custom_iv)
        plaintext2 = self.sm4_modes.decrypt_ofb(ciphertext2, iv2)
        assert plaintext2 == self.test_data
        assert iv2 == custom_iv
        
        # 测试短数据
        short_cipher, short_iv = self.sm4_modes.encrypt_ofb(self.short_data)
        short_plain = self.sm4_modes.decrypt_ofb(short_cipher, short_iv)
        assert short_plain == self.short_data
        assert len(short_cipher) == len(self.short_data)
    
    def test_mode_compatibility(self):
        """测试模式间的兼容性和独立性"""
        # 相同明文，不同模式应产生不同密文
        ecb_cipher = self.sm4_modes.encrypt_ecb(self.block_data, padding=False)
        cbc_cipher, _ = self.sm4_modes.encrypt_cbc(self.block_data, b'\x01' * 16, padding=False)  # 使用非零IV
        ctr_cipher, _ = self.sm4_modes.encrypt_ctr(self.block_data, b'\x00' * 16)
        cfb_cipher, _ = self.sm4_modes.encrypt_cfb(self.block_data, b'\x01' * 16)  # 使用不同IV
        ofb_cipher, _ = self.sm4_modes.encrypt_ofb(self.block_data, b'\x02' * 16)  # 使用不同IV
        
        # ECB和CBC使用非零IV时应该不同
        assert ecb_cipher != cbc_cipher, "ECB和CBC(非零IV)产生了相同的密文"
        
        # 流模式使用不同IV时应该不同
        assert ctr_cipher != cfb_cipher, "CTR和CFB产生了相同的密文"
        assert ctr_cipher != ofb_cipher, "CTR和OFB产生了相同的密文"
        assert cfb_cipher != ofb_cipher, "CFB和OFB产生了相同的密文"
        
        # 验证CBC使用零IV时与ECB相同（这是正确的行为）
        cbc_zero_iv, _ = self.sm4_modes.encrypt_cbc(self.block_data, b'\x00' * 16, padding=False)
        assert ecb_cipher == cbc_zero_iv, "CBC使用零IV时应该与ECB产生相同结果"
        
        # 验证CTR和CFB使用相同IV/计数器时会产生相同结果（对于单块）
        cfb_same_iv, _ = self.sm4_modes.encrypt_cfb(self.block_data, b'\x00' * 16)
        assert ctr_cipher == cfb_same_iv, "CTR和CFB使用相同初始值时应该产生相同结果"
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效IV长度
        with pytest.raises(ValueError, match="初始化向量必须为16字节"):
            self.sm4_modes.encrypt_cbc(self.test_data, b'\x00' * 15)
        
        with pytest.raises(ValueError, match="计数器必须为16字节"):
            self.sm4_modes.encrypt_ctr(self.test_data, b'\x00' * 15)
        
        # 测试解密时无效IV长度
        with pytest.raises(ValueError, match="初始化向量必须为16字节"):
            self.sm4_modes.decrypt_cbc(b'\x00' * 16, b'\x00' * 15)
        
        # 测试无效密文长度（仅对需要完整块的模式）
        with pytest.raises(ValueError, match="密文长度必须是16的倍数"):
            self.sm4_modes.decrypt_cbc(b'\x00' * 15, b'\x00' * 16)
    
    def test_large_data(self):
        """测试大数据处理"""
        large_data = b'A' * 10000  # 10KB数据
        
        # 测试ECB
        ecb_cipher = self.sm4_modes.encrypt_ecb(large_data)
        ecb_plain = self.sm4_modes.decrypt_ecb(ecb_cipher)
        assert ecb_plain == large_data
        
        # 测试CBC
        cbc_cipher, iv = self.sm4_modes.encrypt_cbc(large_data)
        cbc_plain = self.sm4_modes.decrypt_cbc(cbc_cipher, iv)
        assert cbc_plain == large_data
        
        # 测试CTR
        ctr_cipher, counter = self.sm4_modes.encrypt_ctr(large_data)
        ctr_plain = self.sm4_modes.decrypt_ctr(ctr_cipher, counter)
        assert ctr_plain == large_data
        assert len(ctr_cipher) == len(large_data)  # CTR不改变长度
    
    def test_empty_data(self):
        """测试空数据"""
        empty_data = b''
        
        # ECB模式会添加一个完整的填充块
        ecb_cipher = self.sm4_modes.encrypt_ecb(empty_data)
        ecb_plain = self.sm4_modes.decrypt_ecb(ecb_cipher)
        assert ecb_plain == empty_data
        assert len(ecb_cipher) == 16  # 一个填充块
        
        # 流模式应该返回空数据
        ctr_cipher, _ = self.sm4_modes.encrypt_ctr(empty_data)
        assert len(ctr_cipher) == 0
        
        cfb_cipher, _ = self.sm4_modes.encrypt_cfb(empty_data)
        assert len(cfb_cipher) == 0
        
        ofb_cipher, _ = self.sm4_modes.encrypt_ofb(empty_data)
        assert len(ofb_cipher) == 0
    
    def test_counter_increment(self):
        """测试CTR模式的计数器递增"""
        # 使用已知计数器进行测试
        counter = b'\x00' * 15 + b'\x01'  # 计数器值为1
        
        # 加密多个块的数据
        multi_block_data = b'A' * 48  # 3个块
        ciphertext, used_counter = self.sm4_modes.encrypt_ctr(multi_block_data, counter)
        plaintext = self.sm4_modes.decrypt_ctr(ciphertext, used_counter)
        
        assert plaintext == multi_block_data
        assert used_counter == counter  # 返回的应该是初始计数器
    
    def test_iv_randomness(self):
        """测试IV的随机性"""
        # 多次生成IV，应该都不相同
        ivs = []
        for _ in range(10):
            _, iv = self.sm4_modes.encrypt_cbc(self.test_data)
            ivs.append(iv)
        
        # 检查所有IV都不相同
        for i, iv1 in enumerate(ivs):
            for j, iv2 in enumerate(ivs):
                if i != j:
                    assert iv1 != iv2, "生成了重复的IV"


def run_mode_tests():
    """运行所有模式测试"""
    print("=== SM4加密模式测试 ===")
    
    # 创建测试实例
    test_instance = TestSM4Modes()
    test_instance.setup_method()
    
    # 运行所有测试
    tests = [
        ('ECB模式', test_instance.test_ecb_mode),
        ('CBC模式', test_instance.test_cbc_mode),
        ('CTR模式', test_instance.test_ctr_mode),
        ('CFB模式', test_instance.test_cfb_mode),
        ('OFB模式', test_instance.test_ofb_mode),
        ('模式兼容性', test_instance.test_mode_compatibility),
        ('错误处理', test_instance.test_error_handling),
        ('大数据处理', test_instance.test_large_data),
        ('空数据处理', test_instance.test_empty_data),
        ('计数器递增', test_instance.test_counter_increment),
        ('IV随机性', test_instance.test_iv_randomness),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_name}: {e}")
            failed += 1
    
    print(f"\n测试结果: {passed} 通过, {failed} 失败")
    return failed == 0


if __name__ == "__main__":
    run_mode_tests()
