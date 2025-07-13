"""
SM4分组密码算法基础实现
严格按照国标GB/T 32907-2016实现
注重代码可读性和正确性，适合学习和理解算法原理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import SBOX, FK, CK, BLOCK_SIZE, KEY_SIZE, ROUNDS
from utils.helpers import (
    bytes_to_int_list, int_list_to_bytes, rotl, get_byte,
    validate_key, validate_data, format_hex
)

class SM4Basic:
    """SM4基础实现类"""
    
    def __init__(self, key):
        """
        初始化SM4加密器
        
        Args:
            key (bytes): 128位密钥
        """
        validate_key(key)
        self.key = key
        self.round_keys = self._key_expansion(key)
    
    def _sbox_transform(self, byte_val):
        """
        S盒变换 - 非线性变换的核心
        
        Args:
            byte_val (int): 输入字节值 (0-255)
            
        Returns:
            int: 变换后的字节值
        """
        return SBOX[byte_val]
    
    def _linear_transform_l(self, b):
        """
        线性变换L - 用于轮函数
        L(B) = B ⊕ (B <<< 2) ⊕ (B <<< 10) ⊕ (B <<< 18) ⊕ (B <<< 24)
        
        Args:
            b (int): 32位输入
            
        Returns:
            int: 变换后的32位值
        """
        return b ^ rotl(b, 2) ^ rotl(b, 10) ^ rotl(b, 18) ^ rotl(b, 24)
    
    def _linear_transform_l_prime(self, b):
        """
        线性变换L' - 用于密钥扩展
        L'(B) = B ⊕ (B <<< 13) ⊕ (B <<< 23)
        
        Args:
            b (int): 32位输入
            
        Returns:
            int: 变换后的32位值
        """
        return b ^ rotl(b, 13) ^ rotl(b, 23)
    
    def _tau_transform(self, a):
        """
        置换函数τ - 对每个字节进行S盒变换
        
        Args:
            a (int): 32位输入
            
        Returns:
            int: 变换后的32位值
        """
        # 将32位分成4个字节，分别进行S盒变换
        b0 = self._sbox_transform(get_byte(a, 0))
        b1 = self._sbox_transform(get_byte(a, 1))
        b2 = self._sbox_transform(get_byte(a, 2))
        b3 = self._sbox_transform(get_byte(a, 3))
        
        # 重新组合成32位
        return (b0 << 24) | (b1 << 16) | (b2 << 8) | b3
    
    def _round_function_t(self, x0, x1, x2, x3, rk):
        """
        轮函数T - SM4的核心变换函数
        T(X0, X1, X2, X3, rk) = X0 ⊕ L(τ(X1 ⊕ X2 ⊕ X3 ⊕ rk))
        
        Args:
            x0, x1, x2, x3 (int): 四个32位输入
            rk (int): 轮密钥
            
        Returns:
            int: 变换结果
        """
        temp = x1 ^ x2 ^ x3 ^ rk
        temp = self._tau_transform(temp)
        temp = self._linear_transform_l(temp)
        return x0 ^ temp
    
    def _key_expansion(self, key):
        """
        密钥扩展算法 - 从主密钥生成32个轮密钥
        
        Args:
            key (bytes): 128位主密钥
            
        Returns:
            list: 32个32位轮密钥
        """
        # 将密钥转换为4个32位字
        mk = bytes_to_int_list(key)
        
        # 初始化：K0 = MK0 ⊕ FK0, K1 = MK1 ⊕ FK1, ...
        k = [mk[i] ^ FK[i] for i in range(4)]
        
        # 生成32个轮密钥
        round_keys = []
        for i in range(ROUNDS):
            # rki = Ki+4 = Ki ⊕ T'(Ki+1 ⊕ Ki+2 ⊕ Ki+3 ⊕ CKi)
            temp = k[1] ^ k[2] ^ k[3] ^ CK[i]
            temp = self._tau_transform(temp)
            temp = self._linear_transform_l_prime(temp)
            
            rk = k[0] ^ temp
            round_keys.append(rk)
            
            # 更新K值：左移一位
            k = k[1:] + [rk]
        
        return round_keys
    
    def _encrypt_block(self, plaintext_block):
        """
        加密单个分组
        
        Args:
            plaintext_block (bytes): 16字节明文分组
            
        Returns:
            bytes: 16字节密文分组
        """
        # 将明文转换为4个32位字
        x = bytes_to_int_list(plaintext_block)
        
        # 进行32轮变换
        for i in range(ROUNDS):
            # Xi+4 = F(Xi, Xi+1, Xi+2, Xi+3, rki) = Xi ⊕ T(Xi+1, Xi+2, Xi+3, rki)
            temp = self._round_function_t(x[0], x[1], x[2], x[3], self.round_keys[i])
            x = x[1:] + [temp]
        
        # 反序变换：(Y0, Y1, Y2, Y3) = (X35, X34, X33, X32)
        y = [x[3], x[2], x[1], x[0]]
        
        return int_list_to_bytes(y)
    
    def _decrypt_block(self, ciphertext_block):
        """
        解密单个分组
        
        Args:
            ciphertext_block (bytes): 16字节密文分组
            
        Returns:
            bytes: 16字节明文分组
        """
        # 将密文转换为4个32位字
        x = bytes_to_int_list(ciphertext_block)
        
        # 使用逆序的轮密钥进行32轮变换
        for i in range(ROUNDS):
            temp = self._round_function_t(x[0], x[1], x[2], x[3], self.round_keys[31-i])
            x = x[1:] + [temp]
        
        # 反序变换
        y = [x[3], x[2], x[1], x[0]]
        
        return int_list_to_bytes(y)
    
    def encrypt(self, plaintext):
        """
        加密数据（ECB模式）
        
        Args:
            plaintext (bytes): 明文数据，长度必须是16的倍数
            
        Returns:
            bytes: 密文数据
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
        
        Args:
            ciphertext (bytes): 密文数据，长度必须是16的倍数
            
        Returns:
            bytes: 明文数据
        """
        validate_data(ciphertext)
        
        plaintext = bytearray()
        for i in range(0, len(ciphertext), BLOCK_SIZE):
            block = ciphertext[i:i+BLOCK_SIZE]
            decrypted_block = self._decrypt_block(block)
            plaintext.extend(decrypted_block)
        
        return bytes(plaintext)
    
    def _pkcs7_pad(self, data: bytes) -> bytes:
        """
        PKCS7填充
        
        Args:
            data: 待填充的数据
            
        Returns:
            填充后的数据
        """
        pad_len = 16 - (len(data) % 16)
        return data + bytes([pad_len] * pad_len)
    
    def _pkcs7_unpad(self, data: bytes) -> bytes:
        """
        PKCS7去填充
        
        Args:
            data: 填充后的数据
            
        Returns:
            去填充后的数据
        """
        if not data:
            raise ValueError("数据为空")
        
        pad_len = data[-1]
        if pad_len < 1 or pad_len > 16:
            raise ValueError("无效的填充")
        
        if len(data) < pad_len:
            raise ValueError("数据长度不足")
        
        # 验证填充的正确性
        for i in range(pad_len):
            if data[-(i+1)] != pad_len:
                raise ValueError("填充格式错误")
        
        return data[:-pad_len]
    
    def encrypt_ecb(self, plaintext: bytes, padding: bool = True) -> bytes:
        """
        ECB模式加密
        
        Args:
            plaintext: 明文
            padding: 是否使用PKCS7填充
            
        Returns:
            密文
        """
        if padding:
            plaintext = self._pkcs7_pad(plaintext)
        
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
            plaintext = self._pkcs7_unpad(plaintext)
        
        return plaintext

    def get_round_keys_info(self):
        """
        获取轮密钥信息，用于调试和分析
        
        Returns:
            list: 格式化的轮密钥信息
        """
        return [f"RK{i:2d}: {format_hex(rk)}" for i, rk in enumerate(self.round_keys)]
    
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

# 测试函数
def test_basic_sm4():
    """基础功能测试"""
    from utils.constants import TEST_VECTORS
    
    print("=== SM4基础实现测试 ===")
    
    key = TEST_VECTORS['key']
    plaintext = TEST_VECTORS['plaintext']
    expected_ciphertext = TEST_VECTORS['ciphertext']
    
    print(f"密钥:     {format_hex(key)}")
    print(f"明文:     {format_hex(plaintext)}")
    print(f"期望密文: {format_hex(expected_ciphertext)}")
    
    # 创建SM4实例
    sm4 = SM4Basic(key)
    
    # 加密测试
    ciphertext = sm4.encrypt(plaintext)
    print(f"实际密文: {format_hex(ciphertext)}")
    
    # 验证加密结果
    if ciphertext == expected_ciphertext:
        print("✓ 加密测试通过")
    else:
        print("✗ 加密测试失败")
        return False
    
    # 解密测试
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
    test_basic_sm4()
