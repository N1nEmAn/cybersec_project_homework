"""
图像加载和保存工具
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Union, Tuple
import logging

logger = logging.getLogger(__name__)


class ImageLoader:
    """图像加载和保存工具类"""
    
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    @staticmethod
    def load_image(image_path: Union[str, Path]) -> np.ndarray:
        """
        加载图像文件
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            图像数组 (H, W, C) 或 (H, W)
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        if image_path.suffix.lower() not in ImageLoader.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的图像格式: {image_path.suffix}")
        
        # 使用OpenCV加载图像
        image = cv2.imread(str(image_path))
        
        if image is None:
            raise ValueError(f"无法加载图像: {image_path}")
        
        # OpenCV默认加载为BGR格式，转换为RGB
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        logger.info(f"成功加载图像: {image_path}, 尺寸: {image.shape}")
        return image
    
    @staticmethod
    def load_watermark(watermark_path: Union[str, Path], 
                      size: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        加载水印图像
        
        Args:
            watermark_path: 水印文件路径
            size: 目标尺寸 (width, height)，可选
            
        Returns:
            水印图像数组
        """
        watermark = ImageLoader.load_image(watermark_path)
        
        # 调整尺寸
        if size is not None:
            watermark = cv2.resize(watermark, size)
        
        # 转换为灰度图像（水印通常使用灰度）
        if len(watermark.shape) == 3:
            watermark = cv2.cvtColor(watermark, cv2.COLOR_RGB2GRAY)
        
        logger.info(f"成功加载水印: {watermark_path}, 尺寸: {watermark.shape}")
        return watermark
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: Union[str, Path], 
                   quality: int = 95) -> None:
        """
        保存图像到文件
        
        Args:
            image: 图像数组
            output_path: 输出文件路径
            quality: JPEG质量 (1-100)
        """
        output_path = Path(output_path)
        
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 处理图像格式
        if len(image.shape) == 3:
            # RGB转BGR（OpenCV保存格式）
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image
        
        # 确保数据类型正确
        if image_bgr.dtype != np.uint8:
            image_bgr = np.clip(image_bgr, 0, 255).astype(np.uint8)
        
        # 设置保存参数
        save_params = []
        if output_path.suffix.lower() in ['.jpg', '.jpeg']:
            save_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        elif output_path.suffix.lower() == '.png':
            save_params = [cv2.IMWRITE_PNG_COMPRESSION, 9]
        
        # 保存图像
        success = cv2.imwrite(str(output_path), image_bgr, save_params)
        
        if not success:
            raise ValueError(f"无法保存图像到: {output_path}")
        
        logger.info(f"成功保存图像: {output_path}")
    
    @staticmethod
    def create_test_image(size: Tuple[int, int] = (512, 512), 
                         pattern: str = 'lena') -> np.ndarray:
        """
        创建测试图像
        
        Args:
            size: 图像尺寸 (width, height)
            pattern: 图像模式 ('lena', 'checkerboard', 'gradient', 'noise')
            
        Returns:
            测试图像数组
        """
        width, height = size
        
        if pattern == 'lena':
            # 生成类似Lena的测试图像
            x, y = np.meshgrid(np.linspace(0, 1, width), np.linspace(0, 1, height))
            image = np.sin(10 * np.pi * x) * np.cos(10 * np.pi * y)
            image = ((image + 1) * 127.5).astype(np.uint8)
            
        elif pattern == 'checkerboard':
            # 棋盘图案
            block_size = min(width, height) // 16
            image = np.zeros((height, width), dtype=np.uint8)
            for i in range(0, height, block_size):
                for j in range(0, width, block_size):
                    if ((i // block_size) + (j // block_size)) % 2 == 0:
                        image[i:i+block_size, j:j+block_size] = 255
                        
        elif pattern == 'gradient':
            # 渐变图像
            x, y = np.meshgrid(np.linspace(0, 255, width), np.linspace(0, 255, height))
            image = ((x + y) / 2).astype(np.uint8)
            
        elif pattern == 'noise':
            # 随机噪声
            image = np.random.randint(0, 256, (height, width), dtype=np.uint8)
            
        else:
            raise ValueError(f"未知的图像模式: {pattern}")
        
        logger.info(f"创建测试图像: {pattern}, 尺寸: {image.shape}")
        return image
    
    @staticmethod
    def create_test_watermark(size: Tuple[int, int] = (64, 64), 
                             pattern: str = 'text') -> np.ndarray:
        """
        创建测试水印
        
        Args:
            size: 水印尺寸 (width, height)
            pattern: 水印模式 ('text', 'logo', 'binary', 'random_binary')
            
        Returns:
            测试水印数组
        """
        width, height = size
        
        if pattern == 'text':
            # 文字水印
            watermark = np.zeros((height, width), dtype=np.uint8)
            # 简单的十字形状作为文字替代
            center_x, center_y = width // 2, height // 2
            watermark[center_y-2:center_y+3, :] = 255  # 水平线
            watermark[:, center_x-2:center_x+3] = 255  # 垂直线
            
        elif pattern == 'logo':
            # Logo水印（圆形）
            watermark = np.zeros((height, width), dtype=np.uint8)
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 4
            
            for i in range(height):
                for j in range(width):
                    if (i - center_y) ** 2 + (j - center_x) ** 2 <= radius ** 2:
                        watermark[i, j] = 255
                        
        elif pattern == 'binary':
            # 二值随机模式
            watermark = np.random.randint(0, 2, (height, width), dtype=np.uint8) * 255
            
        elif pattern == 'random_binary':
            # 高度随机的二值模式
            np.random.seed(42)  # 固定种子确保可重现
            watermark = np.random.randint(0, 2, (height, width), dtype=np.uint8) * 255
            
        else:
            raise ValueError(f"未知的水印模式: {pattern}")
        
        logger.info(f"创建测试水印: {pattern}, 尺寸: {watermark.shape}")
        return watermark
    
    @staticmethod
    def get_image_info(image: np.ndarray) -> dict:
        """
        获取图像信息
        
        Args:
            image: 图像数组
            
        Returns:
            图像信息字典
        """
        info = {
            'shape': image.shape,
            'dtype': str(image.dtype),
            'size': image.size,
            'min_value': float(np.min(image)),
            'max_value': float(np.max(image)),
            'mean_value': float(np.mean(image)),
            'std_value': float(np.std(image))
        }
        
        if len(image.shape) == 3:
            info['channels'] = image.shape[2]
            info['is_color'] = True
        else:
            info['channels'] = 1
            info['is_color'] = False
        
        return info


def demo_image_loader():
    """图像加载器演示函数"""
    # 创建测试图像
    test_image = ImageLoader.create_test_image((256, 256), 'lena')
    test_watermark = ImageLoader.create_test_watermark((64, 64), 'text')
    
    # 保存测试图像
    ImageLoader.save_image(test_image, '/tmp/test_image.png')
    ImageLoader.save_image(test_watermark, '/tmp/test_watermark.png')
    
    print("图像加载器演示完成")
    print(f"测试图像信息: {ImageLoader.get_image_info(test_image)}")
    print(f"测试水印信息: {ImageLoader.get_image_info(test_watermark)}")


if __name__ == "__main__":
    demo_image_loader()
