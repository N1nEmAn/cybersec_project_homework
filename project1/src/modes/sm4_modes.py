#!/usr/bin/env python3
"""
SM4加密模式实现
支持ECB、CBC、CTR等多种加密模式
"""

import os
from typing import List, Optional
from ..basic.sm4_basic import SM4Basic


class SM4Modes:
    """
    SM4加密模式实现类
    
    支持的模式:
    - ECB (Electronic Codebook)
    - CBC (Cipher Block Chaining)
    - CTR (Counter Mode)
    - CFB (Cipher Feedback)
    - OFB (Output Feedback)
    """
    
    def __init__(self, key: bytes):
        """
        初始化SM4模式实现
        
        Args:
            key: 16字节密钥
        """
        self.sm4 = SM4Basic(key)
    
    def _xor_blocks(self, block1: bytes, block2: bytes) -> bytes:
        """
        两个块的异或运算
        
        Args:
            block1: 第一个块
            block2: 第二个块
            
        Returns:
            异或结果
        """
        return bytes(a ^ b for a, b in zip(block1, block2))
    
    def _increment_counter(self, counter: bytes) -> bytes:
        """
        计数器递增（大端序）
        
        Args:
            counter: 当前计数器值
            
        Returns:
            递增后的计数器
        """
        # 转换为整数，递增，再转换回字节
        counter_int = int.from_bytes(counter, 'big')
        counter_int = (counter_int + 1) % (2 ** 128)
        return counter_int.to_bytes(16, 'big')
    
    def encrypt_ecb(self, plaintext: bytes, padding: bool = True) -> bytes:
        """
        ECB模式加密
        
        Args:
            plaintext: 明文
            padding: 是否使用PKCS7填充
            
        Returns:
            密文
        """
        return self.sm4.encrypt_ecb(plaintext, padding)
    
    def decrypt_ecb(self, ciphertext: bytes, padding: bool = True) -> bytes:
        """
        ECB模式解密
        
        Args:
            ciphertext: 密文
            padding: 是否使用PKCS7填充
            
        Returns:
            明文
        """
        return self.sm4.decrypt_ecb(ciphertext, padding)
    
    def encrypt_cbc(self, plaintext: bytes, iv: Optional[bytes] = None, 
                   padding: bool = True) -> tuple[bytes, bytes]:
        """
        CBC模式加密
        
        Args:
            plaintext: 明文
            iv: 初始化向量（16字节），如果为None则随机生成
            padding: 是否使用PKCS7填充
            
        Returns:
            (密文, 初始化向量)
        """
        if iv is None:
            iv = os.urandom(16)
        elif len(iv) != 16:
            raise ValueError("初始化向量必须为16字节")
        
        if padding:
            plaintext = self.sm4._pkcs7_pad(plaintext)
        
        if len(plaintext) % 16 != 0:
            raise ValueError("明文长度必须是16的倍数")
        
        ciphertext = b''
        prev_block = iv
        
        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            # CBC: C[i] = E(P[i] ⊕ C[i-1])
            xor_block = self._xor_blocks(block, prev_block)
            cipher_block = self.sm4.encrypt_block(xor_block)
            ciphertext += cipher_block
            prev_block = cipher_block
        
        return ciphertext, iv
    
    def decrypt_cbc(self, ciphertext: bytes, iv: bytes, 
                   padding: bool = True) -> bytes:
        """
        CBC模式解密
        
        Args:
            ciphertext: 密文
            iv: 初始化向量（16字节）
            padding: 是否使用PKCS7填充
            
        Returns:
            明文
        """
        if len(iv) != 16:
            raise ValueError("初始化向量必须为16字节")
        
        if len(ciphertext) % 16 != 0:
            raise ValueError("密文长度必须是16的倍数")
        
        plaintext = b''
        prev_block = iv
        
        for i in range(0, len(ciphertext), 16):
            cipher_block = ciphertext[i:i+16]
            # CBC: P[i] = D(C[i]) ⊕ C[i-1]
            decrypted_block = self.sm4.decrypt_block(cipher_block)
            plain_block = self._xor_blocks(decrypted_block, prev_block)
            plaintext += plain_block
            prev_block = cipher_block
        
        if padding:
            plaintext = self.sm4._pkcs7_unpad(plaintext)
        
        return plaintext
    
    def encrypt_ctr(self, plaintext: bytes, counter: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """
        CTR模式加密
        
        Args:
            plaintext: 明文
            counter: 计数器初始值（16字节），如果为None则随机生成
            
        Returns:
            (密文, 计数器初始值)
        """
        if counter is None:
            counter = os.urandom(16)
        elif len(counter) != 16:
            raise ValueError("计数器必须为16字节")
        
        ciphertext = b''
        current_counter = counter
        
        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            # CTR: C[i] = P[i] ⊕ E(Counter[i])
            encrypted_counter = self.sm4.encrypt_block(current_counter)
            
            # 如果是最后一个不完整的块
            if len(block) < 16:
                encrypted_counter = encrypted_counter[:len(block)]
            
            cipher_block = self._xor_blocks(block, encrypted_counter)
            ciphertext += cipher_block
            current_counter = self._increment_counter(current_counter)
        
        return ciphertext, counter
    
    def decrypt_ctr(self, ciphertext: bytes, counter: bytes) -> bytes:
        """
        CTR模式解密（与加密操作相同）
        
        Args:
            ciphertext: 密文
            counter: 计数器初始值（16字节）
            
        Returns:
            明文
        """
        # CTR模式的解密与加密操作相同
        plaintext, _ = self.encrypt_ctr(ciphertext, counter)
        return plaintext
    
    def encrypt_cfb(self, plaintext: bytes, iv: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """
        CFB模式加密
        
        Args:
            plaintext: 明文
            iv: 初始化向量（16字节），如果为None则随机生成
            
        Returns:
            (密文, 初始化向量)
        """
        if iv is None:
            iv = os.urandom(16)
        elif len(iv) != 16:
            raise ValueError("初始化向量必须为16字节")
        
        ciphertext = b''
        shift_register = iv
        
        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            # CFB: C[i] = P[i] ⊕ E(shift_register)
            encrypted_register = self.sm4.encrypt_block(shift_register)
            
            # 如果是最后一个不完整的块
            if len(block) < 16:
                encrypted_register = encrypted_register[:len(block)]
            
            cipher_block = self._xor_blocks(block, encrypted_register)
            ciphertext += cipher_block
            
            # 更新移位寄存器
            if len(cipher_block) == 16:
                shift_register = cipher_block
            else:
                # 不完整块的处理
                shift_register = shift_register[len(cipher_block):] + cipher_block
        
        return ciphertext, iv
    
    def decrypt_cfb(self, ciphertext: bytes, iv: bytes) -> bytes:
        """
        CFB模式解密
        
        Args:
            ciphertext: 密文
            iv: 初始化向量（16字节）
            
        Returns:
            明文
        """
        if len(iv) != 16:
            raise ValueError("初始化向量必须为16字节")
        
        plaintext = b''
        shift_register = iv
        
        for i in range(0, len(ciphertext), 16):
            cipher_block = ciphertext[i:i+16]
            # CFB: P[i] = C[i] ⊕ E(shift_register)
            encrypted_register = self.sm4.encrypt_block(shift_register)
            
            # 如果是最后一个不完整的块
            if len(cipher_block) < 16:
                encrypted_register = encrypted_register[:len(cipher_block)]
            
            plain_block = self._xor_blocks(cipher_block, encrypted_register)
            plaintext += plain_block
            
            # 更新移位寄存器
            if len(cipher_block) == 16:
                shift_register = cipher_block
            else:
                shift_register = shift_register[len(cipher_block):] + cipher_block
        
        return plaintext
    
    def encrypt_ofb(self, plaintext: bytes, iv: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """
        OFB模式加密
        
        Args:
            plaintext: 明文
            iv: 初始化向量（16字节），如果为None则随机生成
            
        Returns:
            (密文, 初始化向量)
        """
        if iv is None:
            iv = os.urandom(16)
        elif len(iv) != 16:
            raise ValueError("初始化向量必须为16字节")
        
        ciphertext = b''
        shift_register = iv
        
        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            # OFB: O[i] = E(O[i-1]), C[i] = P[i] ⊕ O[i]
            encrypted_register = self.sm4.encrypt_block(shift_register)
            
            # 如果是最后一个不完整的块
            if len(block) < 16:
                encrypted_register = encrypted_register[:len(block)]
            
            cipher_block = self._xor_blocks(block, encrypted_register)
            ciphertext += cipher_block
            
            # 更新移位寄存器（使用加密输出）
            if len(block) == 16:
                shift_register = encrypted_register
            # OFB模式中，不完整块不会影响下一次的移位寄存器
        
        return ciphertext, iv
    
    def decrypt_ofb(self, ciphertext: bytes, iv: bytes) -> bytes:
        """
        OFB模式解密（与加密操作相同）
        
        Args:
            ciphertext: 密文
            iv: 初始化向量（16字节）
            
        Returns:
            明文
        """
        # OFB模式的解密与加密操作相同
        plaintext, _ = self.encrypt_ofb(ciphertext, iv)
        return plaintext


def main():
    """演示SM4各种加密模式"""
    print("=== SM4加密模式演示 ===")
    
    # 初始化
    key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
    sm4_modes = SM4Modes(key)
    
    plaintext = b"Hello, SM4 encryption modes! This is a test message for demonstrating different modes."
    print(f"明文: {plaintext.decode()}")
    print(f"明文长度: {len(plaintext)} 字节")
    
    print("\n=== ECB模式 ===")
    ecb_cipher = sm4_modes.encrypt_ecb(plaintext)
    ecb_plain = sm4_modes.decrypt_ecb(ecb_cipher)
    print(f"加密成功: {'✓' if ecb_plain == plaintext else '✗'}")
    print(f"密文长度: {len(ecb_cipher)} 字节")
    
    print("\n=== CBC模式 ===")
    cbc_cipher, iv = sm4_modes.encrypt_cbc(plaintext)
    cbc_plain = sm4_modes.decrypt_cbc(cbc_cipher, iv)
    print(f"加密成功: {'✓' if cbc_plain == plaintext else '✗'}")
    print(f"密文长度: {len(cbc_cipher)} 字节")
    print(f"IV: {iv.hex().upper()}")
    
    print("\n=== CTR模式 ===")
    ctr_cipher, counter = sm4_modes.encrypt_ctr(plaintext)
    ctr_plain = sm4_modes.decrypt_ctr(ctr_cipher, counter)
    print(f"加密成功: {'✓' if ctr_plain == plaintext else '✗'}")
    print(f"密文长度: {len(ctr_cipher)} 字节")
    print(f"计数器: {counter.hex().upper()}")
    
    print("\n=== CFB模式 ===")
    cfb_cipher, cfb_iv = sm4_modes.encrypt_cfb(plaintext)
    cfb_plain = sm4_modes.decrypt_cfb(cfb_cipher, cfb_iv)
    print(f"加密成功: {'✓' if cfb_plain == plaintext else '✗'}")
    print(f"密文长度: {len(cfb_cipher)} 字节")
    print(f"IV: {cfb_iv.hex().upper()}")
    
    print("\n=== OFB模式 ===")
    ofb_cipher, ofb_iv = sm4_modes.encrypt_ofb(plaintext)
    ofb_plain = sm4_modes.decrypt_ofb(ofb_cipher, ofb_iv)
    print(f"加密成功: {'✓' if ofb_plain == plaintext else '✗'}")
    print(f"密文长度: {len(ofb_cipher)} 字节")
    print(f"IV: {ofb_iv.hex().upper()}")
    
    print("\n=== 模式特性比较 ===")
    modes_comparison = {
        'ECB': {'并行': '✓', '错误传播': '单块', '需要IV': '✗', '适用场景': '小数据'},
        'CBC': {'并行': '解密可并行', '错误传播': '两块', '需要IV': '✓', '适用场景': '通用'},
        'CTR': {'并行': '✓', '错误传播': '单块', '需要IV': '✓', '适用场景': '流数据'},
        'CFB': {'并行': '解密可并行', '错误传播': '两块', '需要IV': '✓', '适用场景': '字符流'},
        'OFB': {'并行': '✗', '错误传播': '单块', '需要IV': '✓', '适用场景': '噪声信道'}
    }
    
    print(f"{'模式':<6} {'并行性':<12} {'错误传播':<8} {'需要IV':<8} {'适用场景':<10}")
    print("-" * 50)
    for mode, props in modes_comparison.items():
        print(f"{mode:<6} {props['并行']:<12} {props['错误传播']:<8} {props['需要IV']:<8} {props['适用场景']:<10}")


if __name__ == "__main__":
    main()
