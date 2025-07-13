"""
椭圆曲线群操作模块

实现DDH协议所需的椭圆曲线群运算：
- 点加法和标量乘法
- 群元素的幂运算
- 安全的随机标量生成
"""

import secrets
from typing import Tuple, Optional
from .crypto_utils import secure_random_int


class EllipticCurveGroup:
    """
    椭圆曲线群类，实现SECP256R1曲线上的群运算
    
    椭圆曲线方程：y² = x³ - 3x + b (mod p)
    其中：
    - p = 2^256 - 2^224 + 2^192 + 2^96 - 1
    - b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    - n = 群的阶（基点的阶）
    """
    
    def __init__(self):
        # SECP256R1 (prime256v1) 参数
        self.p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
        self.a = -3
        self.b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
        self.n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
        
        # 基点G的坐标
        self.gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
        self.gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
        self.G = (self.gx, self.gy)
        
        # 无穷远点（群的单位元）
        self.O = None
    
    def is_on_curve(self, point: Optional[Tuple[int, int]]) -> bool:
        """
        检查点是否在椭圆曲线上
        
        Args:
            point: 椭圆曲线点 (x, y) 或 None（无穷远点）
            
        Returns:
            True如果点在曲线上，False否则
        """
        if point is None:  # 无穷远点
            return True
        
        x, y = point
        # 检查椭圆曲线方程：y² ≡ x³ + ax + b (mod p)
        left = (y * y) % self.p
        right = (x * x * x + self.a * x + self.b) % self.p
        return left == right
    
    def point_add(self, P: Optional[Tuple[int, int]], Q: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        椭圆曲线点加法
        
        Args:
            P: 第一个点
            Q: 第二个点
            
        Returns:
            P + Q
        """
        # 处理无穷远点
        if P is None:
            return Q
        if Q is None:
            return P
        
        x1, y1 = P
        x2, y2 = Q
        
        # 如果是同一个点的两倍
        if x1 == x2:
            if y1 == y2:
                return self.point_double(P)
            else:
                return None  # P + (-P) = O
        
        # 一般情况的点加法
        # 斜率 λ = (y2 - y1) / (x2 - x1)
        dx = (x2 - x1) % self.p
        dy = (y2 - y1) % self.p
        lambda_val = (dy * self.mod_inverse(dx, self.p)) % self.p
        
        # 新点的坐标
        x3 = (lambda_val * lambda_val - x1 - x2) % self.p
        y3 = (lambda_val * (x1 - x3) - y1) % self.p
        
        return (x3, y3)
    
    def point_double(self, P: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        椭圆曲线点倍乘（2P）
        
        Args:
            P: 输入点
            
        Returns:
            2P
        """
        if P is None:
            return None
        
        x, y = P
        
        # 斜率 λ = (3x² + a) / (2y)
        numerator = (3 * x * x + self.a) % self.p
        denominator = (2 * y) % self.p
        
        if denominator == 0:
            return None  # 切线垂直，结果是无穷远点
        
        lambda_val = (numerator * self.mod_inverse(denominator, self.p)) % self.p
        
        # 新点的坐标
        x3 = (lambda_val * lambda_val - 2 * x) % self.p
        y3 = (lambda_val * (x - x3) - y) % self.p
        
        return (x3, y3)
    
    def scalar_mult(self, k: int, P: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        椭圆曲线标量乘法：计算 k*P
        
        使用二进制展开方法实现高效的标量乘法
        
        Args:
            k: 标量
            P: 椭圆曲线点
            
        Returns:
            k*P
        """
        if k == 0 or P is None:
            return None
        
        if k == 1:
            return P
        
        # 确保k为正数
        k = k % self.n
        
        # 二进制展开方法
        result = None
        addend = P
        
        while k > 0:
            if k & 1:  # k的最低位为1
                result = self.point_add(result, addend)
            addend = self.point_double(addend)
            k >>= 1
        
        return result
    
    def point_power(self, point: Optional[Tuple[int, int]], exponent: int) -> Optional[Tuple[int, int]]:
        """
        椭圆曲线点的幂运算：计算 point^exponent
        
        这是scalar_mult的别名，用于DDH协议中的表示
        
        Args:
            point: 椭圆曲线点
            exponent: 指数
            
        Returns:
            point^exponent
        """
        return self.scalar_mult(exponent, point)
    
    def generate_private_key(self) -> int:
        """
        生成椭圆曲线私钥
        
        Returns:
            随机私钥，范围在 [1, n-1]
        """
        while True:
            private_key = secure_random_int(256)
            if 1 <= private_key < self.n:
                return private_key
    
    def generate_public_key(self, private_key: int) -> Tuple[int, int]:
        """
        从私钥生成公钥
        
        Args:
            private_key: 私钥
            
        Returns:
            公钥点 = private_key * G
        """
        return self.scalar_mult(private_key, self.G)
    
    def mod_inverse(self, a: int, m: int) -> int:
        """
        计算模逆：找到 x 使得 ax ≡ 1 (mod m)
        
        使用扩展欧几里得算法
        
        Args:
            a: 输入数
            m: 模数
            
        Returns:
            a在模m下的逆元
        """
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
    
    def point_to_string(self, point: Optional[Tuple[int, int]]) -> str:
        """
        将椭圆曲线点转换为字符串表示
        
        Args:
            point: 椭圆曲线点
            
        Returns:
            点的字符串表示
        """
        if point is None:
            return "O"  # 无穷远点
        
        x, y = point
        return f"({x:064x}, {y:064x})"
    
    def string_to_point(self, point_str: str) -> Optional[Tuple[int, int]]:
        """
        从字符串表示恢复椭圆曲线点
        
        Args:
            point_str: 点的字符串表示
            
        Returns:
            椭圆曲线点
        """
        if point_str == "O":
            return None
        
        # 解析格式：(x, y)
        import re
        match = re.match(r'\(([0-9a-f]+), ([0-9a-f]+)\)', point_str)
        if not match:
            raise ValueError("无效的点字符串格式")
        
        x = int(match.group(1), 16)
        y = int(match.group(2), 16)
        return (x, y)
