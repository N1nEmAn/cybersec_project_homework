"""
几何攻击测试模块
实现图像的几何变换攻击，测试水印的鲁棒性
"""

import numpy as np
import cv2
from typing import Tuple, Union, Optional
import logging

logger = logging.getLogger(__name__)


class GeometricAttacks:
    """几何攻击测试类"""
    
    def __init__(self):
        self.logger = logger
    
    def flip_horizontal(self, image: np.ndarray) -> np.ndarray:
        """
        水平翻转攻击
        
        Args:
            image: 输入图像
            
        Returns:
            翻转后的图像
        """
        flipped = cv2.flip(image, 1)  # 1表示水平翻转
        self.logger.info("执行水平翻转攻击")
        return flipped
    
    def flip_vertical(self, image: np.ndarray) -> np.ndarray:
        """
        垂直翻转攻击
        
        Args:
            image: 输入图像
            
        Returns:
            翻转后的图像
        """
        flipped = cv2.flip(image, 0)  # 0表示垂直翻转
        self.logger.info("执行垂直翻转攻击")
        return flipped
    
    def rotate(self, image: np.ndarray, angle: float, 
               keep_size: bool = True) -> np.ndarray:
        """
        旋转攻击
        
        Args:
            image: 输入图像
            angle: 旋转角度（度）
            keep_size: 是否保持原始尺寸
            
        Returns:
            旋转后的图像
        """
        if len(image.shape) == 3:
            h, w, c = image.shape
        else:
            h, w = image.shape
            c = 1
        
        # 计算旋转中心
        center = (w // 2, h // 2)
        
        # 获取旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        if keep_size:
            # 保持原始尺寸
            rotated = cv2.warpAffine(image, rotation_matrix, (w, h))
        else:
            # 调整尺寸以包含完整图像
            cos_val = abs(rotation_matrix[0, 0])
            sin_val = abs(rotation_matrix[0, 1])
            new_w = int(h * sin_val + w * cos_val)
            new_h = int(h * cos_val + w * sin_val)
            
            # 调整平移量
            rotation_matrix[0, 2] += (new_w - w) / 2
            rotation_matrix[1, 2] += (new_h - h) / 2
            
            rotated = cv2.warpAffine(image, rotation_matrix, (new_w, new_h))
        
        self.logger.info(f"执行旋转攻击，角度: {angle}度")
        return rotated
    
    def scale(self, image: np.ndarray, scale_factor: float) -> np.ndarray:
        """
        缩放攻击
        
        Args:
            image: 输入图像
            scale_factor: 缩放因子
            
        Returns:
            缩放后的图像
        """
        if len(image.shape) == 3:
            h, w, c = image.shape
        else:
            h, w = image.shape
        
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        
        scaled = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        self.logger.info(f"执行缩放攻击，缩放因子: {scale_factor}")
        return scaled
    
    def translate(self, image: np.ndarray, tx: int, ty: int) -> np.ndarray:
        """
        平移攻击
        
        Args:
            image: 输入图像
            tx: x方向平移像素数
            ty: y方向平移像素数
            
        Returns:
            平移后的图像
        """
        if len(image.shape) == 3:
            h, w, c = image.shape
        else:
            h, w = image.shape
        
        # 构建平移矩阵
        translation_matrix = np.float32([[1, 0, tx], [0, 1, ty]])
        
        # 执行平移
        translated = cv2.warpAffine(image, translation_matrix, (w, h))
        
        self.logger.info(f"执行平移攻击，偏移: ({tx}, {ty})")
        return translated
    
    def crop(self, image: np.ndarray, crop_ratio: float = 0.8, 
             position: str = 'center') -> np.ndarray:
        """
        裁剪攻击
        
        Args:
            image: 输入图像
            crop_ratio: 保留区域比例 (0.0-1.0)
            position: 裁剪位置 ('center', 'top_left', 'top_right', 'bottom_left', 'bottom_right')
            
        Returns:
            裁剪后的图像
        """
        if len(image.shape) == 3:
            h, w, c = image.shape
        else:
            h, w = image.shape
        
        # 计算裁剪尺寸
        new_h = int(h * crop_ratio)
        new_w = int(w * crop_ratio)
        
        # 根据位置计算起始坐标
        if position == 'center':
            start_y = (h - new_h) // 2
            start_x = (w - new_w) // 2
        elif position == 'top_left':
            start_y = 0
            start_x = 0
        elif position == 'top_right':
            start_y = 0
            start_x = w - new_w
        elif position == 'bottom_left':
            start_y = h - new_h
            start_x = 0
        elif position == 'bottom_right':
            start_y = h - new_h
            start_x = w - new_w
        else:
            raise ValueError(f"未知的裁剪位置: {position}")
        
        # 执行裁剪
        cropped = image[start_y:start_y+new_h, start_x:start_x+new_w]
        
        self.logger.info(f"执行裁剪攻击，保留比例: {crop_ratio}，位置: {position}")
        return cropped
    
    def shear(self, image: np.ndarray, shear_x: float = 0.0, 
              shear_y: float = 0.0) -> np.ndarray:
        """
        剪切攻击
        
        Args:
            image: 输入图像
            shear_x: x方向剪切因子
            shear_y: y方向剪切因子
            
        Returns:
            剪切后的图像
        """
        if len(image.shape) == 3:
            h, w, c = image.shape
        else:
            h, w = image.shape
        
        # 构建剪切矩阵
        shear_matrix = np.float32([[1, shear_x, 0], [shear_y, 1, 0]])
        
        # 执行剪切
        sheared = cv2.warpAffine(image, shear_matrix, (w, h))
        
        self.logger.info(f"执行剪切攻击，剪切因子: ({shear_x}, {shear_y})")
        return sheared
    
    def perspective_transform(self, image: np.ndarray, 
                            corners: Optional[np.ndarray] = None) -> np.ndarray:
        """
        透视变换攻击
        
        Args:
            image: 输入图像
            corners: 目标四角坐标，形状为(4, 2)
            
        Returns:
            透视变换后的图像
        """
        if len(image.shape) == 3:
            h, w, c = image.shape
        else:
            h, w = image.shape
        
        # 原始四角坐标
        src_corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        
        # 默认目标四角坐标（轻微透视效果）
        if corners is None:
            offset = min(w, h) * 0.1
            corners = np.float32([
                [offset, offset],
                [w - offset, offset],
                [w - offset*2, h - offset],
                [offset*2, h - offset]
            ])
        
        # 计算透视变换矩阵
        perspective_matrix = cv2.getPerspectiveTransform(src_corners, corners)
        
        # 执行透视变换
        transformed = cv2.warpPerspective(image, perspective_matrix, (w, h))
        
        self.logger.info("执行透视变换攻击")
        return transformed
    
    def apply_multiple_attacks(self, image: np.ndarray, 
                              attack_sequence: list) -> np.ndarray:
        """
        应用多个几何攻击的组合
        
        Args:
            image: 输入图像
            attack_sequence: 攻击序列，每个元素为(攻击名称, 参数字典)
            
        Returns:
            攻击后的图像
        """
        result_image = image.copy()
        
        for attack_name, params in attack_sequence:
            if attack_name == 'flip_horizontal':
                result_image = self.flip_horizontal(result_image)
            elif attack_name == 'flip_vertical':
                result_image = self.flip_vertical(result_image)
            elif attack_name == 'rotate':
                result_image = self.rotate(result_image, **params)
            elif attack_name == 'scale':
                result_image = self.scale(result_image, **params)
            elif attack_name == 'translate':
                result_image = self.translate(result_image, **params)
            elif attack_name == 'crop':
                result_image = self.crop(result_image, **params)
            elif attack_name == 'shear':
                result_image = self.shear(result_image, **params)
            elif attack_name == 'perspective':
                result_image = self.perspective_transform(result_image, **params)
            else:
                self.logger.warning(f"未知的攻击类型: {attack_name}")
        
        self.logger.info(f"应用组合攻击，攻击序列长度: {len(attack_sequence)}")
        return result_image
    
    def get_common_attack_configs(self) -> dict:
        """
        获取常见的攻击配置
        
        Returns:
            攻击配置字典
        """
        return {
            'light_rotation': [('rotate', {'angle': 5})],
            'heavy_rotation': [('rotate', {'angle': 30})],
            'small_crop': [('crop', {'crop_ratio': 0.9})],
            'medium_crop': [('crop', {'crop_ratio': 0.75})],
            'large_crop': [('crop', {'crop_ratio': 0.5})],
            'scale_down': [('scale', {'scale_factor': 0.8})],
            'scale_up': [('scale', {'scale_factor': 1.2})],
            'translation': [('translate', {'tx': 20, 'ty': 15})],
            'flip_combo': [('flip_horizontal', {}), ('flip_vertical', {})],
            'rotate_crop': [('rotate', {'angle': 15}), ('crop', {'crop_ratio': 0.8})],
            'complex_attack': [
                ('rotate', {'angle': 10}),
                ('scale', {'scale_factor': 0.9}),
                ('translate', {'tx': 10, 'ty': 5}),
                ('crop', {'crop_ratio': 0.85})
            ]
        }


def demo_geometric_attacks():
    """几何攻击演示函数"""
    from ..utils.image_loader import ImageLoader
    
    # 创建测试图像
    test_image = ImageLoader.create_test_image((256, 256), 'lena')
    
    # 初始化几何攻击类
    geo_attacks = GeometricAttacks()
    
    # 测试各种攻击
    print("几何攻击演示:")
    
    # 翻转攻击
    flipped_h = geo_attacks.flip_horizontal(test_image)
    print(f"水平翻转结果尺寸: {flipped_h.shape}")
    
    # 旋转攻击
    rotated = geo_attacks.rotate(test_image, 30)
    print(f"旋转30度结果尺寸: {rotated.shape}")
    
    # 缩放攻击
    scaled = geo_attacks.scale(test_image, 0.8)
    print(f"缩放0.8倍结果尺寸: {scaled.shape}")
    
    # 裁剪攻击
    cropped = geo_attacks.crop(test_image, 0.7)
    print(f"裁剪70%结果尺寸: {cropped.shape}")
    
    # 组合攻击
    attack_sequence = [
        ('rotate', {'angle': 15}),
        ('scale', {'scale_factor': 0.9}),
        ('crop', {'crop_ratio': 0.8})
    ]
    combined_result = geo_attacks.apply_multiple_attacks(test_image, attack_sequence)
    print(f"组合攻击结果尺寸: {combined_result.shape}")
    
    # 显示可用的攻击配置
    configs = geo_attacks.get_common_attack_configs()
    print(f"可用攻击配置: {list(configs.keys())}")


if __name__ == "__main__":
    demo_geometric_attacks()
