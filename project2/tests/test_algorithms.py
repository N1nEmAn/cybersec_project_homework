#!/usr/bin/env python3
"""
单元测试 - 算法模块
测试LSB和DCT水印算法的正确性
"""

import unittest
import numpy as np
import cv2
import os
import sys

# 添加项目路径
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

try:
    from src.algorithms.lsb_watermark import LSBWatermark
    from src.algorithms.dct_watermark import DCTWatermark
except ImportError:
    print("警告: 无法导入算法模块，将跳过相关测试")
    LSBWatermark = None
    DCTWatermark = None

class TestLSBWatermark(unittest.TestCase):
    """LSB水印算法测试类"""
    
    def setUp(self):
        """测试初始化"""
        if LSBWatermark is None:
            self.skipTest("LSB模块未可用")
        
        self.lsb = LSBWatermark(bit_plane=1)
        
        # 创建测试图像
        self.host_image = np.random.randint(0, 256, (64, 64), dtype=np.uint8)
        self.watermark = np.random.randint(0, 2, (16, 16), dtype=np.uint8) * 255
    
    def test_initialization(self):
        """测试初始化"""
        lsb = LSBWatermark(bit_plane=2)
        self.assertEqual(lsb.bit_plane, 2)
        
        # 测试边界值
        lsb_min = LSBWatermark(bit_plane=0)
        self.assertEqual(lsb_min.bit_plane, 1)
        
        lsb_max = LSBWatermark(bit_plane=10)
        self.assertEqual(lsb_max.bit_plane, 8)
    
    def test_embed_extract_basic(self):
        """测试基本嵌入和提取"""
        # 嵌入水印
        watermarked = self.lsb.embed(self.host_image, self.watermark)
        
        # 检查输出形状
        self.assertEqual(watermarked.shape, self.host_image.shape)
        self.assertEqual(watermarked.dtype, np.uint8)
        
        # 提取水印
        extracted = self.lsb.extract(watermarked, self.watermark.shape)
        
        # 检查提取结果
        self.assertEqual(extracted.shape, self.watermark.shape)
        self.assertEqual(extracted.dtype, np.uint8)
    
    def test_embed_strength(self):
        """测试不同强度的嵌入"""
        strengths = [0.1, 0.5, 0.8, 1.0]
        
        for strength in strengths:
            with self.subTest(strength=strength):
                watermarked = self.lsb.embed(self.host_image, self.watermark, strength)
                self.assertEqual(watermarked.shape, self.host_image.shape)
                
                # 计算PSNR
                mse = np.mean((self.host_image.astype(float) - watermarked.astype(float)) ** 2)
                if mse > 0:
                    psnr = 10 * np.log10(255**2 / mse)
                    self.assertGreater(psnr, 20)  # PSNR应该大于20dB
    
    def test_capacity_check(self):
        """测试容量检查"""
        # 创建过大的水印
        large_watermark = np.random.randint(0, 2, (100, 100), dtype=np.uint8) * 255
        
        with self.assertRaises(ValueError):
            self.lsb.embed(self.host_image, large_watermark)
    
    def test_different_bit_planes(self):
        """测试不同位平面"""
        bit_planes = [1, 2, 4, 8]
        
        for bit_plane in bit_planes:
            with self.subTest(bit_plane=bit_plane):
                lsb = LSBWatermark(bit_plane=bit_plane)
                watermarked = lsb.embed(self.host_image, self.watermark)
                extracted = lsb.extract(watermarked, self.watermark.shape)
                
                self.assertEqual(extracted.shape, self.watermark.shape)
    
    def test_algorithm_info(self):
        """测试算法信息"""
        info = self.lsb.get_algorithm_info()
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info['name'], 'LSB')
        self.assertEqual(info['type'], 'spatial_domain')
        self.assertEqual(info['bit_plane'], 1)

class TestDCTWatermark(unittest.TestCase):
    """DCT水印算法测试类"""
    
    def setUp(self):
        """测试初始化"""
        if DCTWatermark is None:
            self.skipTest("DCT模块未可用")
        
        self.dct = DCTWatermark(block_size=8, alpha=0.1)
        
        # 创建测试图像（必须是8的倍数）
        self.host_image = np.random.randint(0, 256, (64, 64), dtype=np.uint8)
        self.watermark = np.random.randint(0, 2, (16, 16), dtype=np.uint8) * 255
    
    def test_initialization(self):
        """测试初始化"""
        dct = DCTWatermark(block_size=16, alpha=0.2)
        self.assertEqual(dct.block_size, 16)
        self.assertEqual(dct.alpha, 0.2)
    
    def test_embed_extract_basic(self):
        """测试基本嵌入和提取"""
        # 嵌入水印
        watermarked = self.dct.embed(self.host_image, self.watermark)
        
        # 检查输出
        self.assertEqual(watermarked.shape, self.host_image.shape)
        
        # 非盲提取
        extracted = self.dct.extract(watermarked, self.host_image)
        self.assertEqual(extracted.shape[0] * extracted.shape[1], 
                        (self.host_image.shape[0] // 8) * (self.host_image.shape[1] // 8))
    
    def test_different_block_sizes(self):
        """测试不同块大小"""
        block_sizes = [4, 8, 16]
        
        for block_size in block_sizes:
            with self.subTest(block_size=block_size):
                dct = DCTWatermark(block_size=block_size, alpha=0.1)
                
                # 调整图像大小以适应块大小
                size = block_size * 8  # 确保是块大小的倍数
                test_image = cv2.resize(self.host_image, (size, size))
                
                watermarked = dct.embed(test_image, self.watermark)
                self.assertEqual(watermarked.shape, test_image.shape)

class TestImageProcessing(unittest.TestCase):
    """图像处理测试类"""
    
    def test_image_formats(self):
        """测试不同图像格式"""
        if LSBWatermark is None:
            self.skipTest("LSB模块未可用")
        
        lsb = LSBWatermark(bit_plane=1)
        
        # 测试不同数据类型
        formats = [
            (np.uint8, (0, 255)),
            (np.float32, (0.0, 1.0)),
            (np.float64, (0.0, 1.0))
        ]
        
        for dtype, (min_val, max_val) in formats:
            with self.subTest(dtype=dtype):
                if dtype == np.uint8:
                    host = np.random.randint(min_val, max_val + 1, (32, 32), dtype=dtype)
                    watermark = np.random.randint(0, 2, (8, 8), dtype=dtype) * 255
                else:
                    host = np.random.uniform(min_val, max_val, (32, 32)).astype(dtype)
                    watermark = np.random.randint(0, 2, (8, 8)).astype(dtype)
                
                try:
                    watermarked = lsb.embed(host, watermark)
                    extracted = lsb.extract(watermarked, watermark.shape)
                    
                    self.assertEqual(watermarked.dtype, np.uint8)
                    self.assertEqual(extracted.dtype, np.uint8)
                except Exception as e:
                    self.fail(f"处理{dtype}格式失败: {e}")
    
    def test_color_images(self):
        """测试彩色图像处理"""
        if LSBWatermark is None:
            self.skipTest("LSB模块未可用")
        
        lsb = LSBWatermark(bit_plane=1)
        
        # 创建彩色图像
        color_host = np.random.randint(0, 256, (32, 32, 3), dtype=np.uint8)
        watermark = np.random.randint(0, 2, (8, 8), dtype=np.uint8) * 255
        
        # 应该自动转换为灰度图像
        watermarked = lsb.embed(color_host, watermark)
        self.assertEqual(len(watermarked.shape), 2)  # 应该是灰度图像

class TestPerformance(unittest.TestCase):
    """性能测试类"""
    
    def test_processing_time(self):
        """测试处理时间"""
        if LSBWatermark is None:
            self.skipTest("LSB模块未可用")
        
        import time
        
        lsb = LSBWatermark(bit_plane=1)
        
        # 创建较大的测试图像
        host = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
        watermark = np.random.randint(0, 2, (64, 64), dtype=np.uint8) * 255
        
        # 测试嵌入时间
        start_time = time.time()
        watermarked = lsb.embed(host, watermark)
        embed_time = time.time() - start_time
        
        # 测试提取时间
        start_time = time.time()
        extracted = lsb.extract(watermarked, watermark.shape)
        extract_time = time.time() - start_time
        
        print(f"\\n性能测试结果:")
        print(f"  嵌入时间: {embed_time:.4f}秒")
        print(f"  提取时间: {extract_time:.4f}秒")
        
        # 合理的时间范围（根据硬件调整）
        self.assertLess(embed_time, 1.0)  # 嵌入应在1秒内完成
        self.assertLess(extract_time, 0.5)  # 提取应在0.5秒内完成

def create_test_suite():
    """创建测试套件"""
    suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestLSBWatermark,
        TestDCTWatermark,
        TestImageProcessing,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite

def run_tests():
    """运行所有测试"""
    print("🧪 运行水印算法单元测试")
    print("=" * 50)
    
    # 创建测试套件
    suite = create_test_suite()
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果统计
    print("\\n" + "=" * 50)
    print(f"测试结果统计:")
    print(f"  运行测试数: {result.testsRun}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print(f"  跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    if result.errors:
        print("\\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\\n测试结果: {'✅ 通过' if success else '❌ 失败'}")
    
    return success

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
