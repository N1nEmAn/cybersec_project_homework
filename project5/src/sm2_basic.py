#!/usr/bin/env python3
"""
SM2椭圆曲线数字签名算法基础实现
符合GM/T 0003.2-2012标准
"""

import hashlib
import secrets
import time
from typing import Tuple, Optional

class SM2Point:
    """椭圆曲线上的点"""
    def __init__(self, x: int, y: int, infinity: bool = False):
        self.x = x
        self.y = y
        self.infinity = infinity
    
    def __eq__(self, other):
        if not isinstance(other, SM2Point):
            return False
        return self.x == other.x and self.y == other.y and self.infinity == other.infinity
    
    def __str__(self):
        if self.infinity:
            return "Point(∞)"
        return f"Point({self.x:064x}, {self.y:064x})"

class SM2Basic:
    """SM2椭圆曲线数字签名算法基础实现"""
    
    def __init__(self):
        # SM2推荐参数 (GM/T 0003.2-2012)
        self.p = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF  # 素数模数
        self.a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC  # 椭圆曲线参数a
        self.b = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93  # 椭圆曲线参数b
        self.n = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123  # 基点阶
        self.Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7  # 基点x坐标
        self.Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0  # 基点y坐标
        
        # 基点G
        self.G = SM2Point(self.Gx, self.Gy)
        
        # 验证椭圆曲线方程: y² ≡ x³ + ax + b (mod p)
        assert self._verify_point(self.G), "基点不在椭圆曲线上"
    
    def _verify_point(self, point: SM2Point) -> bool:
        """验证点是否在椭圆曲线上"""
        if point.infinity:
            return True
        
        left = (point.y * point.y) % self.p
        right = (point.x * point.x * point.x + self.a * point.x + self.b) % self.p
        return left == right

    def _mod_inverse(self, a: int, m: int) -> int:
        """计算模逆: a^(-1) mod m"""
        if a < 0:
            a = (a % m + m) % m
        
        # 扩展欧几里得算法
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, _ = extended_gcd(a, m)
        if gcd != 1:
            raise ValueError("模逆不存在")
        return (x % m + m) % m
    
    def point_add(self, P: SM2Point, Q: SM2Point) -> SM2Point:
        """椭圆曲线点加法"""
        # 处理无穷远点
        if P.infinity:
            return Q
        if Q.infinity:
            return P
        
        # 点P和Q相同
        if P.x == Q.x and P.y == Q.y:
            return self.point_double(P)
        
        # 点P和Q关于x轴对称
        if P.x == Q.x:
            return SM2Point(0, 0, True)  # 无穷远点
        
        # 一般情况的点加法
        # λ = (y₂ - y₁) / (x₂ - x₁) mod p
        dy = (Q.y - P.y) % self.p
        dx = (Q.x - P.x) % self.p
        dx_inv = self._mod_inverse(dx, self.p)
        lambda_val = (dy * dx_inv) % self.p
        
        # x₃ = λ² - x₁ - x₂ mod p
        x3 = (lambda_val * lambda_val - P.x - Q.x) % self.p
        
        # y₃ = λ(x₁ - x₃) - y₁ mod p
        y3 = (lambda_val * (P.x - x3) - P.y) % self.p
        
        return SM2Point(x3, y3)
    
    def point_double(self, P: SM2Point) -> SM2Point:
        """椭圆曲线点倍乘"""
        if P.infinity:
            return P
        
        if P.y == 0:
            return SM2Point(0, 0, True)  # 无穷远点
        
        # λ = (3x₁² + a) / (2y₁) mod p
        numerator = (3 * P.x * P.x + self.a) % self.p
        denominator = (2 * P.y) % self.p
        denominator_inv = self._mod_inverse(denominator, self.p)
        lambda_val = (numerator * denominator_inv) % self.p
        
        # x₃ = λ² - 2x₁ mod p
        x3 = (lambda_val * lambda_val - 2 * P.x) % self.p
        
        # y₃ = λ(x₁ - x₃) - y₁ mod p
        y3 = (lambda_val * (P.x - x3) - P.y) % self.p
        
        return SM2Point(x3, y3)
    
    def point_multiply(self, k: int, P: SM2Point) -> SM2Point:
        """椭圆曲线标量乘法: k*P (二进制方法)"""
        if k == 0:
            return SM2Point(0, 0, True)  # 无穷远点
        
        if k == 1:
            return P
        
        if k < 0:
            k = -k
            P = SM2Point(P.x, (-P.y) % self.p)
        
        # 二进制标量乘法
        result = SM2Point(0, 0, True)  # 无穷远点
        addend = P
        
        while k:
            if k & 1:
                result = self.point_add(result, addend)
            addend = self.point_double(addend)
            k >>= 1
        
        return result
    
    def generate_keypair(self) -> Tuple[int, SM2Point]:
        """生成SM2密钥对"""
        # 生成私钥 d ∈ [1, n-1]
        d = secrets.randbelow(self.n - 1) + 1
        
        # 计算公钥 P = d * G
        P = self.point_multiply(d, self.G)
        
        return d, P
    
    def _sm3_hash(self, data: bytes) -> bytes:
        """SM3哈希函数的简化实现"""
        # 注：这里使用SHA-256作为替代，实际应用中应使用真正的SM3
        return hashlib.sha256(data).digest()
    
    def _get_user_id_hash(self, user_id: bytes = b"1234567812345678") -> bytes:
        """计算用户身份标识哈希值ZA"""
        # ENTL: 用户身份标识长度（16位）
        entl = (len(user_id) * 8).to_bytes(2, byteorder='big')
        
        # 构造ZA的输入
        za_input = (entl + user_id + 
                   self.a.to_bytes(32, byteorder='big') +
                   self.b.to_bytes(32, byteorder='big') +
                   self.Gx.to_bytes(32, byteorder='big') +
                   self.Gy.to_bytes(32, byteorder='big'))
        
        return self._sm3_hash(za_input)
    
    def sign(self, message: bytes, private_key: int, user_id: bytes = b"1234567812345678") -> Tuple[int, int]:
        """SM2数字签名"""
        # 计算ZA
        za = self._get_user_id_hash(user_id)
        
        # 计算消息摘要 e = H(ZA || M)
        m_prime = za + message
        digest = self._sm3_hash(m_prime)
        e = int.from_bytes(digest, byteorder='big')
        
        while True:
            # 生成随机数 k ∈ [1, n-1]
            k = secrets.randbelow(self.n - 1) + 1
            
            # 计算 (x1, y1) = k * G
            point = self.point_multiply(k, self.G)
            x1 = point.x
            
            # 计算 r = (e + x1) mod n
            r = (e + x1) % self.n
            
            # 如果 r = 0 或 r + k = n，重新选择k
            if r == 0 or (r + k) % self.n == 0:
                continue
            
            # 计算 s = (1 + da)^(-1) * (k - r * da) mod n
            da_inv = self._mod_inverse((1 + private_key) % self.n, self.n)
            s = (da_inv * (k - (r * private_key) % self.n)) % self.n
            
            # 如果 s = 0，重新选择k
            if s == 0:
                continue
            
            return r, s
    
    def verify(self, message: bytes, signature: Tuple[int, int], public_key: SM2Point, 
               user_id: bytes = b"1234567812345678") -> bool:
        """SM2数字签名验证"""
        r, s = signature
        
        # 检查签名参数范围
        if not (1 <= r <= self.n - 1) or not (1 <= s <= self.n - 1):
            return False
        
        # 计算ZA
        za = self._get_user_id_hash(user_id)
        
        # 计算消息摘要 e = H(ZA || M)
        m_prime = za + message
        digest = self._sm3_hash(m_prime)
        e = int.from_bytes(digest, byteorder='big')
        
        # 计算 t = (r + s) mod n
        t = (r + s) % self.n
        
        # 如果 t = 0，签名无效
        if t == 0:
            return False
        
        # 计算 (x1', y1') = s * G + t * PA
        point1 = self.point_multiply(s, self.G)
        point2 = self.point_multiply(t, public_key)
        point_sum = self.point_add(point1, point2)
        
        if point_sum.infinity:
            return False
        
        x1_prime = point_sum.x
        
        # 计算 R = (e + x1') mod n
        R = (e + x1_prime) % self.n
        
        # 验证 R = r
        return R == r

if __name__ == "__main__":
    # 基础测试
    sm2 = SM2Basic()
    print(f"SM2初始化成功")
    print(f"基点G: {sm2.G}")
    print(f"基点验证: {sm2._verify_point(sm2.G)}")
