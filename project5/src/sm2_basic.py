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

if __name__ == "__main__":
    # 基础测试
    sm2 = SM2Basic()
    print(f"SM2初始化成功")
    print(f"基点G: {sm2.G}")
    print(f"基点验证: {sm2._verify_point(sm2.G)}")
