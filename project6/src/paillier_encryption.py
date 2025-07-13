"""
Paillier同态加密实现

实现DDH-PSI协议所需的加法同态加密方案：
- 密钥生成、加密、解密
- 同态加法运算
- 密文重随机化
- 批量加密优化
"""

import random
import secrets
from typing import Tuple, List
from .crypto_utils import secure_random_int


class PaillierEncryption:
    """
    Paillier同态加密系统
    
    该系统支持加法同态性：
    - E(m1) * E(m2) = E(m1 + m2)
    - E(m)^k = E(k * m)
    
    密钥大小：1024位（安全级别对应256位椭圆曲线）
    """
    
    def __init__(self, key_size: int = 1024):
        """
        初始化Paillier加密系统
        
        Args:
            key_size: RSA模数的位长度
        """
        self.key_size = key_size
        self.public_key = None
        self.private_key = None
    
    def generate_keypair(self) -> Tuple[dict, dict]:
        """
        生成Paillier密钥对
        
        Returns:
            (public_key, private_key) 元组
        """
        # 生成两个大素数 p 和 q
        p = self._generate_prime(self.key_size // 2)
        q = self._generate_prime(self.key_size // 2)
        
        # 确保 p != q
        while p == q:
            q = self._generate_prime(self.key_size // 2)
        
        # 计算 n = p * q
        n = p * q
        
        # 计算 λ = lcm(p-1, q-1)
        lambda_n = self._lcm(p - 1, q - 1)
        
        # 选择 g，通常选择 g = n + 1
        g = n + 1
        
        # 计算 μ = (L(g^λ mod n²))^(-1) mod n
        # 其中 L(x) = (x - 1) / n
        n_squared = n * n
        g_lambda = pow(g, lambda_n, n_squared)
        l_result = (g_lambda - 1) // n
        mu = self._mod_inverse(l_result, n)
        
        # 构造密钥
        public_key = {
            'n': n,
            'g': g,
            'n_squared': n_squared
        }
        
        private_key = {
            'lambda': lambda_n,
            'mu': mu,
            'n': n,
            'n_squared': n_squared
        }
        
        self.public_key = public_key
        self.private_key = private_key
        
        return public_key, private_key
    
    def encrypt(self, plaintext: int, public_key: dict = None) -> int:
        """
        加密明文
        
        Args:
            plaintext: 要加密的明文整数
            public_key: 公钥（如果为None则使用实例的公钥）
            
        Returns:
            密文
        """
        if public_key is None:
            public_key = self.public_key
        
        if public_key is None:
            raise ValueError("需要提供公钥")
        
        n = public_key['n']
        g = public_key['g']
        n_squared = public_key['n_squared']
        
        # 确保明文在有效范围内
        if plaintext < 0 or plaintext >= n:
            plaintext = plaintext % n
        
        # 生成随机数 r，满足 gcd(r, n) = 1
        while True:
            r = secure_random_int(self.key_size)
            if r < n and self._gcd(r, n) == 1:
                break
        
        # 计算密文：c = g^m * r^n mod n²
        ciphertext = (pow(g, plaintext, n_squared) * pow(r, n, n_squared)) % n_squared
        
        return ciphertext
    
    def decrypt(self, ciphertext: int, private_key: dict = None) -> int:
        """
        解密密文
        
        Args:
            ciphertext: 要解密的密文
            private_key: 私钥（如果为None则使用实例的私钥）
            
        Returns:
            明文
        """
        if private_key is None:
            private_key = self.private_key
        
        if private_key is None:
            raise ValueError("需要提供私钥")
        
        lambda_n = private_key['lambda']
        mu = private_key['mu']
        n = private_key['n']
        n_squared = private_key['n_squared']
        
        # 计算 c^λ mod n²
        c_lambda = pow(ciphertext, lambda_n, n_squared)
        
        # 计算 L(c^λ mod n²)
        l_result = (c_lambda - 1) // n
        
        # 计算明文：m = L(c^λ mod n²) * μ mod n
        plaintext = (l_result * mu) % n
        
        return plaintext
    
    def add_ciphertexts(self, c1: int, c2: int, public_key: dict = None) -> int:
        """
        同态加法：计算两个密文的乘积，对应明文的加法
        
        Args:
            c1: 第一个密文
            c2: 第二个密文
            public_key: 公钥
            
        Returns:
            E(m1 + m2) = E(m1) * E(m2) mod n²
        """
        if public_key is None:
            public_key = self.public_key
        
        if public_key is None:
            raise ValueError("需要提供公钥")
        
        n_squared = public_key['n_squared']
        return (c1 * c2) % n_squared
    
    def multiply_ciphertext(self, ciphertext: int, scalar: int, public_key: dict = None) -> int:
        """
        同态标量乘法：计算密文的幂，对应明文的标量乘法
        
        Args:
            ciphertext: 密文
            scalar: 标量
            public_key: 公钥
            
        Returns:
            E(scalar * m) = E(m)^scalar mod n²
        """
        if public_key is None:
            public_key = self.public_key
        
        if public_key is None:
            raise ValueError("需要提供公钥")
        
        n_squared = public_key['n_squared']
        return pow(ciphertext, scalar, n_squared)
    
    def refresh_ciphertext(self, ciphertext: int, public_key: dict = None) -> int:
        """
        重随机化密文：生成加密相同明文但具有新随机性的密文
        
        Args:
            ciphertext: 原密文
            public_key: 公钥
            
        Returns:
            重随机化后的密文
        """
        if public_key is None:
            public_key = self.public_key
        
        if public_key is None:
            raise ValueError("需要提供公钥")
        
        n = public_key['n']
        n_squared = public_key['n_squared']
        
        # 生成新的随机数
        while True:
            r = secure_random_int(self.key_size)
            if r < n and self._gcd(r, n) == 1:
                break
        
        # 计算重随机化密文：c' = c * r^n mod n²
        refreshed = (ciphertext * pow(r, n, n_squared)) % n_squared
        return refreshed
    
    def batch_encrypt(self, plaintexts: List[int], public_key: dict = None) -> List[int]:
        """
        批量加密
        
        Args:
            plaintexts: 明文列表
            public_key: 公钥
            
        Returns:
            密文列表
        """
        return [self.encrypt(pt, public_key) for pt in plaintexts]
    
    def sum_ciphertexts(self, ciphertexts: List[int], public_key: dict = None) -> int:
        """
        计算多个密文的同态和
        
        Args:
            ciphertexts: 密文列表
            public_key: 公钥
            
        Returns:
            所有密文对应明文的和的加密
        """
        if not ciphertexts:
            return self.encrypt(0, public_key)
        
        result = ciphertexts[0]
        for i in range(1, len(ciphertexts)):
            result = self.add_ciphertexts(result, ciphertexts[i], public_key)
        
        return result
    
    def _generate_prime(self, bit_length: int) -> int:
        """
        生成指定位长度的素数
        
        Args:
            bit_length: 素数的位长度
            
        Returns:
            随机素数
        """
        while True:
            # 生成随机数
            candidate = secure_random_int(bit_length)
            
            # 确保是奇数且在正确范围内
            candidate |= (1 << (bit_length - 1))  # 设置最高位
            candidate |= 1  # 设置最低位（确保奇数）
            
            if self._is_prime(candidate):
                return candidate
    
    def _is_prime(self, n: int, k: int = 20) -> bool:
        """
        Miller-Rabin素性测试
        
        Args:
            n: 待测试数
            k: 测试轮数
            
        Returns:
            True如果n可能是素数，False如果n是合数
        """
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False
        
        # 将 n-1 写成 2^r * d 的形式
        r = 0
        d = n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        # 进行k轮测试
        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n)
            
            if x == 1 or x == n - 1:
                continue
            
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        
        return True
    
    def _gcd(self, a: int, b: int) -> int:
        """
        计算最大公约数
        
        Args:
            a, b: 两个整数
            
        Returns:
            gcd(a, b)
        """
        while b:
            a, b = b, a % b
        return a
    
    def _lcm(self, a: int, b: int) -> int:
        """
        计算最小公倍数
        
        Args:
            a, b: 两个整数
            
        Returns:
            lcm(a, b)
        """
        return abs(a * b) // self._gcd(a, b)
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """
        计算模逆
        
        Args:
            a: 被逆元素
            m: 模数
            
        Returns:
            a在模m下的逆元
        """
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, _ = extended_gcd(a % m, m)
        if gcd != 1:
            raise ValueError("模逆不存在")
        return (x % m + m) % m
