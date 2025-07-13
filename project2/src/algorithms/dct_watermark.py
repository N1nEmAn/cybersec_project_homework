"""
DCT (Discrete Cosine Transform) 水印算法实现
基于离散余弦变换的频域水印技术
"""

import numpy as np
import cv2
from typing import Tuple, Optional
import logging
from scipy.fft import dct, idct

logger = logging.getLogger(__name__)


class DCTWatermark:
    """DCT水印算法实现类"""
    
    def __init__(self, block_size: int = 8, alpha: float = 0.1):
        """
        初始化DCT水印算法
        
        Args:
            block_size: DCT分块大小，通常为8x8
            alpha: 水印嵌入强度系数
        """
        self.block_size = block_size
        self.alpha = alpha
        self.logger = logger
        
    def embed(self, cover_image: np.ndarray, watermark: np.ndarray, 
              strength: float = 1.0) -> np.ndarray:
        """
        在DCT域嵌入水印
        
        Args:
            cover_image: 载体图像
            watermark: 水印图像（二值化）
            strength: 水印强度调节因子
            
        Returns:
            含水印的图像
        """
        # 图像预处理
        cover = self._preprocess_image(cover_image)
        watermark_binary = self._preprocess_watermark(watermark)
        
        # 调整水印尺寸以匹配分块结构
        watermark_resized = self._resize_watermark_for_blocks(cover, watermark_binary)
        
        # 执行DCT域水印嵌入
        watermarked = self._embed_dct(cover, watermark_resized, strength)
        
        self.logger.info(f"DCT水印嵌入完成，块大小{self.block_size}x{self.block_size}，强度{strength}")
        return watermarked
    
    def extract(self, watermarked_image: np.ndarray, 
                original_image: Optional[np.ndarray] = None) -> np.ndarray:
        """
        从DCT域提取水印
        
        Args:
            watermarked_image: 含水印的图像
            original_image: 原始载体图像（用于非盲提取，可选）
            
        Returns:
            提取的水印图像
        """
        # 图像预处理
        watermarked = self._preprocess_image(watermarked_image)
        
        if original_image is not None:
            # 非盲提取
            original = self._preprocess_image(original_image)
            extracted_watermark = self._extract_dct_non_blind(watermarked, original)
        else:
            # 盲提取
            extracted_watermark = self._extract_dct_blind(watermarked)
        
        self.logger.info("DCT水印提取完成")
        return extracted_watermark
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """预处理图像"""
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        # 转换为灰度图像
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 确保图像尺寸是块大小的倍数
        h, w = image.shape
        new_h = (h // self.block_size) * self.block_size
        new_w = (w // self.block_size) * self.block_size
        
        if new_h != h or new_w != w:
            image = cv2.resize(image, (new_w, new_h))
        
        return image.astype(np.float32)
    
    def _preprocess_watermark(self, watermark: np.ndarray) -> np.ndarray:
        """预处理水印图像"""
        if len(watermark.shape) == 3:
            watermark = cv2.cvtColor(watermark, cv2.COLOR_BGR2GRAY)
        
        # 二值化
        _, binary_watermark = cv2.threshold(watermark, 127, 1, cv2.THRESH_BINARY)
        return binary_watermark.astype(np.float32)
    
    def _resize_watermark_for_blocks(self, cover: np.ndarray, 
                                   watermark: np.ndarray) -> np.ndarray:
        """调整水印尺寸以匹配DCT分块结构"""
        h, w = cover.shape
        num_blocks_h = h // self.block_size
        num_blocks_w = w // self.block_size
        
        # 每个块嵌入一个水印位，所以水印最大尺寸为块数
        max_watermark_size = min(num_blocks_h, num_blocks_w)
        
        # 调整水印尺寸
        watermark_resized = cv2.resize(watermark, (max_watermark_size, max_watermark_size))
        
        return watermark_resized
    
    def _dct2d(self, block: np.ndarray) -> np.ndarray:
        """2D DCT变换"""
        return dct(dct(block.T, norm='ortho').T, norm='ortho')
    
    def _idct2d(self, block: np.ndarray) -> np.ndarray:
        """2D 逆DCT变换"""
        return idct(idct(block.T, norm='ortho').T, norm='ortho')
    
    def _embed_dct(self, cover: np.ndarray, watermark: np.ndarray, 
                   strength: float) -> np.ndarray:
        """
        在DCT域嵌入水印
        
        数学原理:
        1. 将图像分成8x8块
        2. 对每个块进行DCT变换: F(u,v) = DCT(f(x,y))
        3. 修改中频系数: F'(u,v) = F(u,v) + α * w * strength
        4. 逆DCT变换: f'(x,y) = IDCT(F'(u,v))
        """
        watermarked = cover.copy()
        h, w = cover.shape
        wh, ww = watermark.shape
        
        effective_alpha = self.alpha * strength
        
        # 选择中频系数位置（避免低频和高频）
        mid_freq_positions = [(2, 1), (1, 2), (2, 2), (3, 1), (1, 3)]
        
        block_idx = 0
        for i in range(0, h, self.block_size):
            for j in range(0, w, self.block_size):
                # 确保不超出水印范围
                wi = (block_idx // ww) % wh
                wj = block_idx % ww
                
                if wi < wh and wj < ww:
                    # 提取8x8块
                    block = cover[i:i+self.block_size, j:j+self.block_size]
                    
                    # DCT变换
                    dct_block = self._dct2d(block)
                    
                    # 获取水印位
                    watermark_bit = watermark[wi, wj]
                    
                    # 在中频系数中嵌入水印
                    for pos in mid_freq_positions:
                        u, v = pos
                        if u < self.block_size and v < self.block_size:
                            # 根据水印位调整DCT系数
                            if watermark_bit > 0.5:  # 水印位为1
                                dct_block[u, v] += effective_alpha * abs(dct_block[u, v])
                            else:  # 水印位为0
                                dct_block[u, v] -= effective_alpha * abs(dct_block[u, v])
                    
                    # 逆DCT变换
                    modified_block = self._idct2d(dct_block)
                    
                    # 更新图像块
                    watermarked[i:i+self.block_size, j:j+self.block_size] = modified_block
                
                block_idx += 1
        
        # 确保像素值在有效范围内
        watermarked = np.clip(watermarked, 0, 255)
        return watermarked.astype(np.uint8)
    
    def _extract_dct_blind(self, watermarked: np.ndarray) -> np.ndarray:
        """
        盲提取DCT水印
        
        通过分析DCT系数的统计特性来提取水印
        """
        h, w = watermarked.shape
        
        # 估算水印尺寸
        num_blocks_h = h // self.block_size
        num_blocks_w = w // self.block_size
        watermark_size = min(num_blocks_h, num_blocks_w)
        
        extracted_watermark = np.zeros((watermark_size, watermark_size))
        
        # 中频系数位置
        mid_freq_positions = [(2, 1), (1, 2), (2, 2), (3, 1), (1, 3)]
        
        block_idx = 0
        for i in range(0, h, self.block_size):
            for j in range(0, w, self.block_size):
                wi = (block_idx // watermark_size) % watermark_size
                wj = block_idx % watermark_size
                
                if wi < watermark_size and wj < watermark_size:
                    # 提取块
                    block = watermarked[i:i+self.block_size, j:j+self.block_size]
                    
                    # DCT变换
                    dct_block = self._dct2d(block.astype(np.float32))
                    
                    # 分析中频系数
                    coeff_sum = 0
                    for pos in mid_freq_positions:
                        u, v = pos
                        if u < self.block_size and v < self.block_size:
                            coeff_sum += dct_block[u, v]
                    
                    # 根据系数大小判断水印位
                    avg_coeff = coeff_sum / len(mid_freq_positions)
                    extracted_watermark[wi, wj] = 1 if avg_coeff > 0 else 0
                
                block_idx += 1
        
        return (extracted_watermark * 255).astype(np.uint8)
    
    def _extract_dct_non_blind(self, watermarked: np.ndarray, 
                              original: np.ndarray) -> np.ndarray:
        """
        非盲提取DCT水印
        
        通过比较原始图像和含水印图像的DCT系数差异来提取水印
        """
        h, w = watermarked.shape
        
        # 估算水印尺寸
        num_blocks_h = h // self.block_size
        num_blocks_w = w // self.block_size
        watermark_size = min(num_blocks_h, num_blocks_w)
        
        extracted_watermark = np.zeros((watermark_size, watermark_size))
        
        # 中频系数位置
        mid_freq_positions = [(2, 1), (1, 2), (2, 2), (3, 1), (1, 3)]
        
        block_idx = 0
        for i in range(0, h, self.block_size):
            for j in range(0, w, self.block_size):
                wi = (block_idx // watermark_size) % watermark_size
                wj = block_idx % watermark_size
                
                if wi < watermark_size and wj < watermark_size:
                    # 提取对应块
                    watermarked_block = watermarked[i:i+self.block_size, j:j+self.block_size]
                    original_block = original[i:i+self.block_size, j:j+self.block_size]
                    
                    # DCT变换
                    dct_watermarked = self._dct2d(watermarked_block.astype(np.float32))
                    dct_original = self._dct2d(original_block.astype(np.float32))
                    
                    # 计算系数差异
                    diff_sum = 0
                    for pos in mid_freq_positions:
                        u, v = pos
                        if u < self.block_size and v < self.block_size:
                            diff_sum += dct_watermarked[u, v] - dct_original[u, v]
                    
                    # 根据差异判断水印位
                    avg_diff = diff_sum / len(mid_freq_positions)
                    extracted_watermark[wi, wj] = 1 if avg_diff > 0 else 0
                
                block_idx += 1
        
        return (extracted_watermark * 255).astype(np.uint8)
    
    def get_algorithm_info(self) -> dict:
        """获取算法信息"""
        return {
            "name": "DCT",
            "type": "frequency_domain",
            "block_size": f"{self.block_size}x{self.block_size}",
            "alpha": self.alpha,
            "complexity": "O(n log n)",
            "robustness": "medium",
            "invisibility": "high"
        }


def demo_dct_watermark():
    """DCT水印演示函数"""
    # 创建测试图像（确保尺寸是8的倍数）
    cover_image = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
    watermark = np.random.randint(0, 2, (32, 32), dtype=np.uint8) * 255
    
    # 初始化DCT算法
    dct_watermark = DCTWatermark(block_size=8, alpha=0.1)
    
    # 嵌入水印
    watermarked_image = dct_watermark.embed(cover_image, watermark)
    
    # 盲提取水印
    extracted_watermark_blind = dct_watermark.extract(watermarked_image)
    
    # 非盲提取水印
    extracted_watermark_non_blind = dct_watermark.extract(watermarked_image, cover_image)
    
    print("DCT水印演示完成")
    print(f"算法信息: {dct_watermark.get_algorithm_info()}")
    print(f"原始图像形状: {cover_image.shape}")
    print(f"水印形状: {watermark.shape}")
    print(f"含水印图像形状: {watermarked_image.shape}")
    print(f"盲提取水印形状: {extracted_watermark_blind.shape}")
    print(f"非盲提取水印形状: {extracted_watermark_non_blind.shape}")


if __name__ == "__main__":
    demo_dct_watermark()
