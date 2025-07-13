"""
SM4位运算优化实现
通过优化位运算操作、减少内存访问来提升性能
使用位操作技巧和内联函数来加速计算
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import SBOX, FK, CK, BLOCK_SIZE, KEY_SIZE, ROUNDS
from utils.helpers import (
    bytes_to_int_list, int_list_to_bytes, validate_key, validate_data, format_hex
)

class SM4Bitwise:
    """SM4位运算优化实现类"""
    
    def __init__(self, key):
        """
        初始化SM4加密器
        
        Args:
            key (bytes): 128位密钥
        """
        validate_key(key)
        self.key = key
        
        # 预计算优化的S盒表（展开为32位）
        self._precompute_sbox_tables()
        
        # 生成轮密钥
        self.round_keys = self._key_expansion(key)
    
    def _precompute_sbox_tables(self):
        """
        预计算展开的S盒表，将4个字节位置的S盒分别存储
        减少运行时的位移操作
        """
        print("预计算位运算优化表...")
        
        # 为4个字节位置分别创建S盒表
        self.sbox_tables = [None] * 4
        
        for pos in range(4):
            self.sbox_tables[pos] = [0] * 256
            shift = 24 - 8 * pos
            
            for byte_val in range(256):
                sbox_result = SBOX[byte_val]
                # 将S盒结果放在对应的字节位置
                self.sbox_tables[pos][byte_val] = sbox_result << shift
        
        print("位运算优化表预计算完成")
    
    @staticmethod
    def _rotl_fast(value, bits):
        """
        优化的32位左循环移位
        使用位掩码确保结果在32位范围内
        """
        value &= 0xffffffff
        return ((value << bits) | (value >> (32 - bits))) & 0xffffffff
    
    @staticmethod
    def _get_byte_fast(value, index):
        """
        优化的字节提取操作
        使用预计算的位移量
        """
        shifts = [24, 16, 8, 0]
        return (value >> shifts[index]) & 0xff
    
    def _linear_transform_l_fast(self, b):
        """
        优化的线性变换L
        减少临时变量的使用，内联所有运算
        """
        return (b ^ 
                self._rotl_fast(b, 2) ^ 
                self._rotl_fast(b, 10) ^ 
                self._rotl_fast(b, 18) ^ 
                self._rotl_fast(b, 24)) & 0xffffffff
    
    def _linear_transform_l_prime_fast(self, b):
        """
        优化的线性变换L'
        """
        return (b ^ 
                self._rotl_fast(b, 13) ^ 
                self._rotl_fast(b, 23)) & 0xffffffff
    
    def _tau_transform_fast(self, a):
        """
        优化的置换函数τ
        使用预计算的S盒表，减少位移操作
        """
        return (self.sbox_tables[0][self._get_byte_fast(a, 0)] |
                self.sbox_tables[1][self._get_byte_fast(a, 1)] |
                self.sbox_tables[2][self._get_byte_fast(a, 2)] |
                self.sbox_tables[3][self._get_byte_fast(a, 3)]) & 0xffffffff
    
    def _round_function_t_fast(self, x0, x1, x2, x3, rk):
        """
        优化的轮函数T
        内联所有操作，减少函数调用开销
        """
        temp = (x1 ^ x2 ^ x3 ^ rk) & 0xffffffff
        
        # 内联τ变换
        tau_result = (self.sbox_tables[0][self._get_byte_fast(temp, 0)] |
                     self.sbox_tables[1][self._get_byte_fast(temp, 1)] |
                     self.sbox_tables[2][self._get_byte_fast(temp, 2)] |
                     self.sbox_tables[3][self._get_byte_fast(temp, 3)]) & 0xffffffff
        
        # 内联L变换
        l_result = (tau_result ^ 
                   self._rotl_fast(tau_result, 2) ^ 
                   self._rotl_fast(tau_result, 10) ^ 
                   self._rotl_fast(tau_result, 18) ^ 
                   self._rotl_fast(tau_result, 24)) & 0xffffffff
        
        return (x0 ^ l_result) & 0xffffffff
    
    def _sbox_transform(self, byte_val):
        """基础S盒变换（用于密钥扩展）"""
        return SBOX[byte_val]
    
    def _tau_transform_basic(self, a):
        """基础置换函数（用于密钥扩展）"""
        b0 = self._sbox_transform(self._get_byte_fast(a, 0))
        b1 = self._sbox_transform(self._get_byte_fast(a, 1))
        b2 = self._sbox_transform(self._get_byte_fast(a, 2))
        b3 = self._sbox_transform(self._get_byte_fast(a, 3))
        
        return (b0 << 24) | (b1 << 16) | (b2 << 8) | b3
    
    def _key_expansion(self, key):
        """
        密钥扩展算法
        """
        mk = bytes_to_int_list(key)
        k = [(mk[i] ^ FK[i]) & 0xffffffff for i in range(4)]
        
        round_keys = []
        for i in range(ROUNDS):
            temp = (k[1] ^ k[2] ^ k[3] ^ CK[i]) & 0xffffffff
            temp = self._tau_transform_basic(temp)
            temp = self._linear_transform_l_prime_fast(temp)
            
            rk = (k[0] ^ temp) & 0xffffffff
            round_keys.append(rk)
            k = k[1:] + [rk]
        
        return round_keys
    
    def _encrypt_block_fast(self, plaintext_block):
        """
        优化的单分组加密
        使用快速的位运算函数
        """
        x = bytes_to_int_list(plaintext_block)
        
        # 32轮变换，使用优化的轮函数
        for i in range(ROUNDS):
            temp = self._round_function_t_fast(x[0], x[1], x[2], x[3], self.round_keys[i])
            x = x[1:] + [temp]
        
        # 反序变换
        y = [x[3], x[2], x[1], x[0]]
        return int_list_to_bytes(y)
    
    def _decrypt_block_fast(self, ciphertext_block):
        """
        优化的单分组解密
        """
        x = bytes_to_int_list(ciphertext_block)
        
        # 使用逆序轮密钥进行32轮变换
        for i in range(ROUNDS):
            temp = self._round_function_t_fast(x[0], x[1], x[2], x[3], self.round_keys[31-i])
            x = x[1:] + [temp]
        
        # 反序变换
        y = [x[3], x[2], x[1], x[0]]
        return int_list_to_bytes(y)
    
    def encrypt(self, plaintext):
        """
        加密数据（ECB模式）
        """
        validate_data(plaintext)
        
        ciphertext = bytearray()
        # 使用批量处理减少函数调用开销
        for i in range(0, len(plaintext), BLOCK_SIZE):
            block = plaintext[i:i+BLOCK_SIZE]
            encrypted_block = self._encrypt_block_fast(block)
            ciphertext.extend(encrypted_block)
        
        return bytes(ciphertext)
    
    def decrypt(self, ciphertext):
        """
        解密数据（ECB模式）
        """
        validate_data(ciphertext)
        
        plaintext = bytearray()
        for i in range(0, len(ciphertext), BLOCK_SIZE):
            block = ciphertext[i:i+BLOCK_SIZE]
            decrypted_block = self._decrypt_block_fast(block)
            plaintext.extend(decrypted_block)
        
        return bytes(plaintext)
    
    def get_optimization_info(self):
        """
        获取优化信息
        """
        info = {
            "optimization_type": "Bitwise Operations",
            "optimizations": [
                "预计算S盒表减少位移操作",
                "内联函数减少调用开销", 
                "优化的循环移位实现",
                "快速字节提取操作",
                "减少临时变量使用"
            ],
            "memory_usage": f"约 {4 * 256 * 4 / 1024:.1f} KB (S盒表)",
            "performance_benefit": "减少位运算和内存访问开销"
        }
        return info

# 测试函数
def test_bitwise_sm4():
    """位运算优化版本测试"""
    from utils.constants import TEST_VECTORS
    
    print("=== SM4位运算优化实现测试 ===")
    
    key = TEST_VECTORS['key']
    plaintext = TEST_VECTORS['plaintext']
    expected_ciphertext = TEST_VECTORS['ciphertext']
    
    print(f"密钥:     {format_hex(key)}")
    print(f"明文:     {format_hex(plaintext)}")
    print(f"期望密文: {format_hex(expected_ciphertext)}")
    
    # 创建位运算优化的SM4实例
    sm4 = SM4Bitwise(key)
    
    # 显示优化信息
    opt_info = sm4.get_optimization_info()
    print(f"\n优化信息:")
    print(f"  优化类型: {opt_info['optimization_type']}")
    print(f"  内存使用: {opt_info['memory_usage']}")
    print(f"  性能优势: {opt_info['performance_benefit']}")
    print(f"  优化项目:")
    for opt in opt_info['optimizations']:
        print(f"    - {opt}")
    
    # 加密测试
    print(f"\n开始加密测试...")
    ciphertext = sm4.encrypt(plaintext)
    print(f"实际密文: {format_hex(ciphertext)}")
    
    # 验证加密结果
    if ciphertext == expected_ciphertext:
        print("✓ 加密测试通过")
    else:
        print("✗ 加密测试失败")
        return False
    
    # 解密测试
    print(f"开始解密测试...")
    decrypted = sm4.decrypt(ciphertext)
    print(f"解密结果: {format_hex(decrypted)}")
    
    # 验证解密结果
    if decrypted == plaintext:
        print("✓ 解密测试通过")
    else:
        print("✗ 解密测试失败")
        return False
    
    print("✓ 所有测试通过")
    return True

if __name__ == "__main__":
    test_bitwise_sm4()
