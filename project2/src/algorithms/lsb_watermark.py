"""
LSB (Least Significant Bit) 水印算法实现
基于最低有效位替换的空域水印技术
"""

import numpy as np
import cv2
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class LSBWatermark:
    """LSB水印算法实现类"""
    
    def __init__(self, bit_plane: int = 1):
        """
        初始化LSB水印算法
        
        Args:
            bit_plane: 要修改的位平面数量（1-8）
        """
        self.bit_plane = max(1, min(8, bit_plane))
        self.logger = logger
        
    def embed(self, cover_image: np.ndarray, watermark: np.ndarray, 
              strength: float = 1.0) -> np.ndarray:
        """
        嵌入水印到载体图像中
        
        Args:
            cover_image: 载体图像 (H, W, 3) 或 (H, W)
            watermark: 水印图像，二值化后使用
            strength: 水印强度 (0.0-1.0)
            
        Returns:
            带水印的图像
        """
        # 图像预处理
        cover = self._preprocess_image(cover_image)
        watermark_binary = self._preprocess_watermark(watermark)
        
        # 检查尺寸兼容性
        if not self._check_capacity(cover, watermark_binary):
            raise ValueError("载体图像容量不足以嵌入水印")
        
        # 执行LSB嵌入
        watermarked = self._embed_lsb(cover, watermark_binary, strength)
        
        self.logger.info(f"LSB水印嵌入完成，使用{self.bit_plane}位平面，强度{strength}")
        return watermarked
    
    def extract(self, watermarked_image: np.ndarray, 
                watermark_size: Tuple[int, int]) -> np.ndarray:
        """
        从水印图像中提取水印
        
        Args:
            watermarked_image: 含水印的图像
            watermark_size: 水印尺寸 (height, width)
            
        Returns:
            提取的水印图像
        """
        # 图像预处理
        watermarked = self._preprocess_image(watermarked_image)
        
        # 执行LSB提取
        extracted_watermark = self._extract_lsb(watermarked, watermark_size)
        
        self.logger.info(f"LSB水印提取完成，水印尺寸{watermark_size}")
        return extracted_watermark
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """预处理载体图像"""
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        # 确保是灰度图像
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        return image
    
    def _preprocess_watermark(self, watermark: np.ndarray) -> np.ndarray:
        """预处理水印图像，转换为二值图像"""
        if len(watermark.shape) == 3:
            watermark = cv2.cvtColor(watermark, cv2.COLOR_BGR2GRAY)
        
        # 二值化处理
        _, binary_watermark = cv2.threshold(watermark, 127, 1, cv2.THRESH_BINARY)
        return binary_watermark.astype(np.uint8)
    
    def _check_capacity(self, cover: np.ndarray, watermark: np.ndarray) -> bool:
        """检查载体图像是否有足够容量嵌入水印"""
        cover_capacity = cover.size * self.bit_plane
        watermark_size = watermark.size
        return cover_capacity >= watermark_size
    
    def _embed_lsb(self, cover: np.ndarray, watermark: np.ndarray, 
                   strength: float) -> np.ndarray:
        """
        执行LSB水印嵌入
        
        数学原理:
        对于每个像素点 p，修改其最低 k 位：
        p' = (p & mask) | (w << (8-k))
        其中 mask = ~((2^k - 1)) 用于清除最低k位
        """
        watermarked = cover.copy()
        watermark_flat = watermark.flatten()
        
        # 计算位掩码
        mask = ~((1 << self.bit_plane) - 1)
        
        # 获取载体图像的像素点
        cover_flat = watermarked.flatten()
        
        # 调整水印强度
        effective_strength = max(0.0, min(1.0, strength))
        
        # 嵌入水印位
        for i, watermark_bit in enumerate(watermark_flat):
            if i >= len(cover_flat):
                break
            
            # 清除最低位平面
            pixel = cover_flat[i] & mask
            
            # 嵌入水印位（考虑强度因子）
            if effective_strength == 1.0:
                # 完全替换
                pixel |= watermark_bit
            else:
                # 部分替换，保留原始信息
                original_bit = cover_flat[i] & ((1 << self.bit_plane) - 1)
                watermark_contribution = int(watermark_bit * effective_strength)
                original_contribution = int(original_bit * (1.0 - effective_strength))
                pixel |= watermark_contribution + original_contribution
            
            cover_flat[i] = pixel
        
        return cover_flat.reshape(cover.shape)
    
    def _extract_lsb(self, watermarked: np.ndarray, 
                     watermark_size: Tuple[int, int]) -> np.ndarray:
        """
        执行LSB水印提取
        
        数学原理:
        对于每个像素点 p，提取最低 k 位：
        w = p & ((2^k - 1))
        """
        h, w = watermark_size
        watermark_length = h * w
        
        # 获取掩码，用于提取最低位平面
        mask = (1 << self.bit_plane) - 1
        
        # 提取水印位
        watermarked_flat = watermarked.flatten()
        extracted_bits = []
        
        for i in range(min(watermark_length, len(watermarked_flat))):
            # 提取最低位平面
            watermark_bit = watermarked_flat[i] & mask
            extracted_bits.append(watermark_bit)
        
        # 重构水印图像
        extracted_watermark = np.array(extracted_bits[:watermark_length])
        extracted_watermark = extracted_watermark.reshape((h, w))
        
        # 二值化处理
        extracted_watermark = (extracted_watermark * 255).astype(np.uint8)
        
        return extracted_watermark
    
    def get_algorithm_info(self) -> dict:
        """获取算法信息"""
        return {
            "name": "LSB",
            "type": "spatial_domain",
            "bit_plane": self.bit_plane,
            "capacity": f"{self.bit_plane} bits per pixel",
            "complexity": "O(n)",
            "robustness": "low",
            "invisibility": "high"
        }


def demo_lsb_watermark():
    """LSB水印演示函数"""
    # 创建测试图像
    cover_image = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
    watermark = np.random.randint(0, 2, (64, 64), dtype=np.uint8) * 255
    
    # 初始化LSB算法
    lsb = LSBWatermark(bit_plane=1)
    
    # 嵌入水印
    watermarked_image = lsb.embed(cover_image, watermark)
    
    # 提取水印
    extracted_watermark = lsb.extract(watermarked_image, (64, 64))
    
    print("LSB水印演示完成")
    print(f"算法信息: {lsb.get_algorithm_info()}")
    print(f"原始图像形状: {cover_image.shape}")
    print(f"水印形状: {watermark.shape}")
    print(f"含水印图像形状: {watermarked_image.shape}")
    print(f"提取水印形状: {extracted_watermark.shape}")


if __name__ == "__main__":
    demo_lsb_watermark()
