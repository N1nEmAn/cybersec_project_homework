"""
椭圆曲线群运算测试

验证椭圆曲线数学运算的正确性和安全性
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from elliptic_curve import EllipticCurveGroup


class TestEllipticCurveGroup(unittest.TestCase):
    """椭圆曲线群运算测试"""
    
    def setUp(self):
        """测试初始化"""
        self.ec = EllipticCurveGroup()
    
    def test_point_on_curve(self):
        """测试点是否在曲线上"""
        # 测试基点G
        self.assertTrue(self.ec.is_on_curve(self.ec.G))
        
        # 测试无穷远点
        self.assertTrue(self.ec.is_on_curve(None))
        
        # 测试不在曲线上的点
        invalid_point = (0, 0)
        self.assertFalse(self.ec.is_on_curve(invalid_point))
    
    def test_point_addition(self):
        """测试椭圆曲线点加法"""
        G = self.ec.G
        
        # 测试 G + O = G
        result = self.ec.point_add(G, None)
        self.assertEqual(result, G)
        
        # 测试 O + G = G
        result = self.ec.point_add(None, G)
        self.assertEqual(result, G)
        
        # 测试 G + G = 2G
        double_G = self.ec.point_double(G)
        result = self.ec.point_add(G, G)
        self.assertEqual(result, double_G)
    
    def test_point_doubling(self):
        """测试椭圆曲线点倍乘"""
        G = self.ec.G
        
        # 测试2G是否在曲线上
        double_G = self.ec.point_double(G)
        self.assertTrue(self.ec.is_on_curve(double_G))
        
        # 测试无穷远点的倍乘
        result = self.ec.point_double(None)
        self.assertIsNone(result)
    
    def test_scalar_multiplication(self):
        """测试标量乘法"""
        G = self.ec.G
        
        # 测试 0*G = O
        result = self.ec.scalar_mult(0, G)
        self.assertIsNone(result)
        
        # 测试 1*G = G
        result = self.ec.scalar_mult(1, G)
        self.assertEqual(result, G)
        
        # 测试 2*G = G + G
        result_mult = self.ec.scalar_mult(2, G)
        result_add = self.ec.point_add(G, G)
        self.assertEqual(result_mult, result_add)
        
        # 测试大数标量乘法
        k = 12345
        result = self.ec.scalar_mult(k, G)
        self.assertTrue(self.ec.is_on_curve(result))
    
    def test_scalar_multiplication_properties(self):
        """测试标量乘法的数学性质"""
        G = self.ec.G
        a, b = 123, 456
        
        # 测试分配律：(a+b)*G = a*G + b*G
        left = self.ec.scalar_mult(a + b, G)
        right = self.ec.point_add(
            self.ec.scalar_mult(a, G),
            self.ec.scalar_mult(b, G)
        )
        self.assertEqual(left, right)
        
        # 测试结合律：a*(b*G) = (a*b)*G
        left = self.ec.scalar_mult(a, self.ec.scalar_mult(b, G))
        right = self.ec.scalar_mult(a * b, G)
        self.assertEqual(left, right)
    
    def test_private_key_generation(self):
        """测试私钥生成"""
        # 生成多个私钥
        keys = [self.ec.generate_private_key() for _ in range(10)]
        
        # 验证私钥在有效范围内
        for key in keys:
            self.assertGreater(key, 0)
            self.assertLess(key, self.ec.n)
        
        # 验证私钥的唯一性（概率很高）
        self.assertEqual(len(set(keys)), len(keys))
    
    def test_public_key_generation(self):
        """测试公钥生成"""
        private_key = self.ec.generate_private_key()
        public_key = self.ec.generate_public_key(private_key)
        
        # 验证公钥在曲线上
        self.assertTrue(self.ec.is_on_curve(public_key))
        
        # 验证公钥 = private_key * G
        expected = self.ec.scalar_mult(private_key, self.ec.G)
        self.assertEqual(public_key, expected)
    
    def test_mod_inverse(self):
        """测试模逆运算"""
        # 测试已知的模逆
        a = 3
        m = 7
        inv = self.ec.mod_inverse(a, m)
        self.assertEqual((a * inv) % m, 1)
        
        # 测试椭圆曲线群的阶
        a = 12345
        inv = self.ec.mod_inverse(a, self.ec.n)
        self.assertEqual((a * inv) % self.ec.n, 1)
    
    def test_point_string_conversion(self):
        """测试点的字符串转换"""
        G = self.ec.G
        
        # 测试点到字符串
        point_str = self.ec.point_to_string(G)
        self.assertIsInstance(point_str, str)
        
        # 测试字符串到点
        recovered_point = self.ec.string_to_point(point_str)
        self.assertEqual(recovered_point, G)
        
        # 测试无穷远点
        none_str = self.ec.point_to_string(None)
        self.assertEqual(none_str, "O")
        recovered_none = self.ec.string_to_point(none_str)
        self.assertIsNone(recovered_none)
    
    def test_ddh_assumption_support(self):
        """测试DDH假设相关的运算"""
        # 生成随机指数
        a = self.ec.generate_private_key()
        b = self.ec.generate_private_key()
        
        G = self.ec.G
        
        # 计算DDH元组：(G, G^a, G^b, G^(ab))
        g_a = self.ec.scalar_mult(a, G)
        g_b = self.ec.scalar_mult(b, G)
        g_ab1 = self.ec.scalar_mult(b, g_a)  # (G^a)^b
        g_ab2 = self.ec.scalar_mult(a, g_b)  # (G^b)^a
        
        # 验证指数运算的可交换性：(G^a)^b = (G^b)^a = G^(ab)
        self.assertEqual(g_ab1, g_ab2)
        
        # 验证所有点都在曲线上
        self.assertTrue(self.ec.is_on_curve(g_a))
        self.assertTrue(self.ec.is_on_curve(g_b))
        self.assertTrue(self.ec.is_on_curve(g_ab1))


if __name__ == '__main__':
    unittest.main()
