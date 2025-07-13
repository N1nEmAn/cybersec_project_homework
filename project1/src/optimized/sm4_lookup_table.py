"""
SM4查找表优化实现
通过预计算S盒查找表和合并变换来提升性能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import SBOX, FK, CK, BLOCK_SIZE, KEY_SIZE, ROUNDS
from utils.helpers import (
    bytes_to_int_list, int_list_to_bytes, rotl, get_byte,
    validate_key, validate_data, format_hex
)

class SM4LookupTable:
    """SM4查找表优化实现类"""
    
    def __init__(self, key):
        """
        初始化SM4加密器
        
        Args:
            key (bytes): 128位密钥
        """
        validate_key(key)
        self.key = key
        
        # 预计算查找表
        self._precompute_tables()
        
        # 生成轮密钥
        self.round_keys = self._key_expansion(key)
    
    def _precompute_tables(self):
        """
        预计算查找表以加速S盒变换和线性变换
        合并τ变换和L变换到一个查找表中
        """
        print("预计算查找表...")
        
        # 为每个字节位置预计算 L(τ(x))
        # 这样可以将S盒变换和线性变换合并为一次查表操作
        self.lookup_table = [None] * 4
        
        for pos in range(4):  # 4个字节位置
            self.lookup_table[pos] = [0] * 256
            
            for byte_val in range(256):
                # 构造一个只有对应位置有值的32位数
                temp = byte_val << (24 - 8 * pos)
                
                # 进行τ变换（S盒）
                sbox_result = SBOX[byte_val]
                temp_after_sbox = sbox_result << (24 - 8 * pos)
                
                # 进行L变换
                result = self._linear_transform_l(temp_after_sbox)
                
                self.lookup_table[pos][byte_val] = result
        
        print("查找表预计算完成")
    
    def _linear_transform_l(self, b):
        """
        线性变换L
        L(B) = B ⊕ (B <<< 2) ⊕ (B <<< 10) ⊕ (B <<< 18) ⊕ (B <<< 24)
        """
        return b ^ rotl(b, 2) ^ rotl(b, 10) ^ rotl(b, 18) ^ rotl(b, 24)
    
    def _linear_transform_l_prime(self, b):
        """
        线性变换L' - 用于密钥扩展
        L'(B) = B ⊕ (B <<< 13) ⊕ (B <<< 23)
        """
        return b ^ rotl(b, 13) ^ rotl(b, 23)
    
    def _sbox_transform(self, byte_val):
        """S盒变换"""
        return SBOX[byte_val]
    
    def _tau_transform(self, a):
        """置换函数τ - 对每个字节进行S盒变换"""
        b0 = self._sbox_transform(get_byte(a, 0))
        b1 = self._sbox_transform(get_byte(a, 1))
        b2 = self._sbox_transform(get_byte(a, 2))
        b3 = self._sbox_transform(get_byte(a, 3))
        
        return (b0 << 24) | (b1 << 16) | (b2 << 8) | b3
    
    def _round_function_t_optimized(self, x0, x1, x2, x3, rk):
        """
        优化的轮函数T - 使用查找表加速
        """
        temp = x1 ^ x2 ^ x3 ^ rk
        
        # 使用预计算的查找表进行τ和L变换
        result = (self.lookup_table[0][get_byte(temp, 0)] ^
                 self.lookup_table[1][get_byte(temp, 1)] ^
                 self.lookup_table[2][get_byte(temp, 2)] ^
                 self.lookup_table[3][get_byte(temp, 3)])
        
        return x0 ^ result
    
    def _key_expansion(self, key):
        """
        密钥扩展算法
        在密钥扩展中仍使用基础方法，因为只执行一次
        """
        mk = bytes_to_int_list(key)
        k = [mk[i] ^ FK[i] for i in range(4)]
        
        round_keys = []
        for i in range(ROUNDS):
            temp = k[1] ^ k[2] ^ k[3] ^ CK[i]
            temp = self._tau_transform(temp)
            temp = self._linear_transform_l_prime(temp)
            
            rk = k[0] ^ temp
            round_keys.append(rk)
            k = k[1:] + [rk]
        
        return round_keys
    
    def _encrypt_block(self, plaintext_block):
        """
        加密单个分组 - 使用优化的轮函数
        """
        x = bytes_to_int_list(plaintext_block)
        
        # 使用优化的轮函数进行32轮变换
        for i in range(ROUNDS):
            temp = self._round_function_t_optimized(x[0], x[1], x[2], x[3], self.round_keys[i])
            x = x[1:] + [temp]
        
        # 反序变换
        y = [x[3], x[2], x[1], x[0]]
        return int_list_to_bytes(y)
    
    def _decrypt_block(self, ciphertext_block):
        """
        解密单个分组 - 使用优化的轮函数
        """
        x = bytes_to_int_list(ciphertext_block)
        
        # 使用逆序的轮密钥和优化的轮函数进行32轮变换
        for i in range(ROUNDS):
            temp = self._round_function_t_optimized(x[0], x[1], x[2], x[3], self.round_keys[31-i])
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
        for i in range(0, len(plaintext), BLOCK_SIZE):
            block = plaintext[i:i+BLOCK_SIZE]
            encrypted_block = self._encrypt_block(block)
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
            decrypted_block = self._decrypt_block(block)
            plaintext.extend(decrypted_block)
        
        return bytes(plaintext)
    
    def encrypt_block(self, plaintext: bytes) -> bytes:
        """
        加密单个16字节块（公共接口）
        
        Args:
            plaintext: 16字节明文块
            
        Returns:
            16字节密文块
        """
        if len(plaintext) != 16:
            raise ValueError("明文块必须为16字节")
        
        return self._encrypt_block(plaintext)
    
    def decrypt_block(self, ciphertext: bytes) -> bytes:
        """
        解密单个16字节块（公共接口）
        
        Args:
            ciphertext: 16字节密文块
            
        Returns:
            16字节明文块
        """
        if len(ciphertext) != 16:
            raise ValueError("密文块必须为16字节")
        
        return self._decrypt_block(ciphertext)

    def get_optimization_info(self):
        """
        获取优化信息
        """
        info = {
            "optimization_type": "Lookup Table",
            "table_size": f"{len(self.lookup_table)} tables × 256 entries × 4 bytes = {4 * 256 * 4} bytes",
            "memory_usage": f"约 {4 * 256 * 4 / 1024:.1f} KB",
            "optimization_benefit": "将S盒变换和线性变换合并为单次查表操作"
        }
        return info
    
    def encrypt_ecb(self, plaintext: bytes, padding: bool = True) -> bytes:
        """
        ECB模式加密
        
        Args:
            plaintext: 明文
            padding: 是否使用PKCS7填充
            
        Returns:
            密文
        """
        from ..basic.sm4_basic import SM4Basic
        # 临时创建基础实现来处理ECB模式
        temp_sm4 = SM4Basic(self.key)
        if padding:
            plaintext = temp_sm4._pkcs7_pad(plaintext)
        
        if len(plaintext) % 16 != 0:
            raise ValueError("明文长度必须是16的倍数")
        
        ciphertext = b''
        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            ciphertext += self.encrypt_block(block)
        
        return ciphertext
    
    def decrypt_ecb(self, ciphertext: bytes, padding: bool = True) -> bytes:
        """
        ECB模式解密
        
        Args:
            ciphertext: 密文
            padding: 是否使用PKCS7填充
            
        Returns:
            明文
        """
        if len(ciphertext) % 16 != 0:
            raise ValueError("密文长度必须是16的倍数")
        
        plaintext = b''
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i+16]
            plaintext += self.decrypt_block(block)
        
        if padding:
            from ..basic.sm4_basic import SM4Basic
            temp_sm4 = SM4Basic(self.key)
            plaintext = temp_sm4._pkcs7_unpad(plaintext)
        
        return plaintext

# 测试函数
def test_lookup_table_sm4():
    """查找表优化版本测试"""
    from utils.constants import TEST_VECTORS
    
    print("=== SM4查找表优化实现测试 ===")
    
    key = TEST_VECTORS['key']
    plaintext = TEST_VECTORS['plaintext']
    expected_ciphertext = TEST_VECTORS['ciphertext']
    
    print(f"密钥:     {format_hex(key)}")
    print(f"明文:     {format_hex(plaintext)}")
    print(f"期望密文: {format_hex(expected_ciphertext)}")
    
    # 创建优化的SM4实例
    sm4 = SM4LookupTable(key)
    
    # 显示优化信息
    opt_info = sm4.get_optimization_info()
    print(f"\n优化信息:")
    for key_name, value in opt_info.items():
        print(f"  {key_name}: {value}")
    
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
    test_lookup_table_sm4()
