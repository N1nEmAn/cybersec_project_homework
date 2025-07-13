"""
信号处理攻击测试模块
实现图像的信号处理攻击，包括滤波、噪声、压缩等
"""

import numpy as np
import cv2
from typing import Tuple, Union, Optional
import logging
from scipy.ndimage import gaussian_filter, median_filter
from scipy.signal import butter, filtfilt
import random

logger = logging.getLogger(__name__)


class SignalProcessingAttacks:
    """信号处理攻击测试类"""
    
    def __init__(self):
        self.logger = logger
    
    def add_gaussian_noise(self, image: np.ndarray, mean: float = 0, 
                          std: float = 25) -> np.ndarray:
        """
        添加高斯噪声
        
        Args:
            image: 输入图像
            mean: 噪声均值
            std: 噪声标准差
            
        Returns:
            添加噪声后的图像
        """
        # 生成高斯噪声
        noise = np.random.normal(mean, std, image.shape)
        
        # 添加噪声
        noisy_image = image.astype(np.float64) + noise
        
        # 限制像素值范围
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        
        self.logger.info(f"添加高斯噪声，均值: {mean}，标准差: {std}")
        return noisy_image
    
    def add_salt_pepper_noise(self, image: np.ndarray, 
                             salt_prob: float = 0.05,
                             pepper_prob: float = 0.05) -> np.ndarray:
        """
        添加椒盐噪声
        
        Args:
            image: 输入图像
            salt_prob: 盐噪声概率
            pepper_prob: 胡椒噪声概率
            
        Returns:
            添加噪声后的图像
        """
        noisy_image = image.copy()
        
        # 生成随机位置
        h, w = image.shape[:2]
        
        # 添加盐噪声（白点）
        salt_coords = np.random.random((h, w)) < salt_prob
        if len(image.shape) == 3:
            noisy_image[salt_coords] = 255
        else:
            noisy_image[salt_coords] = 255
            
        # 添加胡椒噪声（黑点）
        pepper_coords = np.random.random((h, w)) < pepper_prob
        if len(image.shape) == 3:
            noisy_image[pepper_coords] = 0
        else:
            noisy_image[pepper_coords] = 0
        
        self.logger.info(f"添加椒盐噪声，盐噪声概率: {salt_prob}，胡椒噪声概率: {pepper_prob}")
        return noisy_image
    
    def add_uniform_noise(self, image: np.ndarray, 
                         low: float = -20, high: float = 20) -> np.ndarray:
        """
        添加均匀噪声
        
        Args:
            image: 输入图像
            low: 噪声下界
            high: 噪声上界
            
        Returns:
            添加噪声后的图像
        """
        # 生成均匀噪声
        noise = np.random.uniform(low, high, image.shape)
        
        # 添加噪声
        noisy_image = image.astype(np.float64) + noise
        
        # 限制像素值范围
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        
        self.logger.info(f"添加均匀噪声，范围: [{low}, {high}]")
        return noisy_image
    
    def gaussian_blur(self, image: np.ndarray, sigma: float = 1.0) -> np.ndarray:
        """
        高斯模糊滤波
        
        Args:
            image: 输入图像
            sigma: 高斯核标准差
            
        Returns:
            模糊后的图像
        """
        if len(image.shape) == 3:
            # 彩色图像，对每个通道单独处理
            blurred = np.zeros_like(image)
            for i in range(image.shape[2]):
                blurred[:, :, i] = gaussian_filter(image[:, :, i], sigma=sigma)
        else:
            # 灰度图像
            blurred = gaussian_filter(image, sigma=sigma)
        
        self.logger.info(f"应用高斯模糊，标准差: {sigma}")
        return blurred.astype(np.uint8)
    
    def median_blur(self, image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        中值滤波
        
        Args:
            image: 输入图像
            kernel_size: 滤波核大小
            
        Returns:
            滤波后的图像
        """
        blurred = cv2.medianBlur(image, kernel_size)
        
        self.logger.info(f"应用中值滤波，核大小: {kernel_size}")
        return blurred
    
    def motion_blur(self, image: np.ndarray, size: int = 15, 
                   angle: float = 0) -> np.ndarray:
        """
        运动模糊
        
        Args:
            image: 输入图像
            size: 模糊核大小
            angle: 运动角度（度）
            
        Returns:
            运动模糊后的图像
        """
        # 创建运动模糊核
        kernel = np.zeros((size, size))
        
        # 计算线条的起始和结束位置
        center = size // 2
        angle_rad = np.radians(angle)
        
        # 绘制运动轨迹
        for i in range(size):
            offset = i - center
            x = int(center + offset * np.cos(angle_rad))
            y = int(center + offset * np.sin(angle_rad))
            if 0 <= x < size and 0 <= y < size:
                kernel[y, x] = 1
        
        # 归一化核
        kernel = kernel / np.sum(kernel)
        
        # 应用模糊
        blurred = cv2.filter2D(image, -1, kernel)
        
        self.logger.info(f"应用运动模糊，大小: {size}，角度: {angle}度")
        return blurred
    
    def sharpen(self, image: np.ndarray, strength: float = 1.0) -> np.ndarray:
        """
        锐化滤波
        
        Args:
            image: 输入图像
            strength: 锐化强度
            
        Returns:
            锐化后的图像
        """
        # 定义锐化核
        kernel = np.array([[-1, -1, -1],
                          [-1, 8 + strength, -1],
                          [-1, -1, -1]]) / (strength + 1)
        
        # 应用锐化
        sharpened = cv2.filter2D(image, -1, kernel)
        
        # 限制像素值范围
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        self.logger.info(f"应用锐化滤波，强度: {strength}")
        return sharpened
    
    def adjust_brightness(self, image: np.ndarray, 
                         brightness: float = 0) -> np.ndarray:
        """
        调整亮度
        
        Args:
            image: 输入图像
            brightness: 亮度调整值（-100到100）
            
        Returns:
            调整亮度后的图像
        """
        adjusted = image.astype(np.float64) + brightness
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
        
        self.logger.info(f"调整亮度: {brightness}")
        return adjusted
    
    def adjust_contrast(self, image: np.ndarray, 
                       contrast: float = 1.0) -> np.ndarray:
        """
        调整对比度
        
        Args:
            image: 输入图像
            contrast: 对比度系数（0.5-2.0）
            
        Returns:
            调整对比度后的图像
        """
        # 计算图像均值
        mean = np.mean(image)
        
        # 调整对比度
        adjusted = (image - mean) * contrast + mean
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
        
        self.logger.info(f"调整对比度: {contrast}")
        return adjusted
    
    def adjust_gamma(self, image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
        """
        伽马校正
        
        Args:
            image: 输入图像
            gamma: 伽马值
            
        Returns:
            伽马校正后的图像
        """
        # 构建查找表
        table = np.array([((i / 255.0) ** (1.0 / gamma)) * 255 
                         for i in range(256)]).astype(np.uint8)
        
        # 应用伽马校正
        corrected = cv2.LUT(image, table)
        
        self.logger.info(f"应用伽马校正: {gamma}")
        return corrected
    
    def histogram_equalization(self, image: np.ndarray) -> np.ndarray:
        """
        直方图均衡化
        
        Args:
            image: 输入图像
            
        Returns:
            均衡化后的图像
        """
        if len(image.shape) == 3:
            # 彩色图像，转换到LAB空间进行L通道均衡化
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = cv2.equalizeHist(lab[:, :, 0])
            equalized = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            # 灰度图像
            equalized = cv2.equalizeHist(image)
        
        self.logger.info("应用直方图均衡化")
        return equalized
    
    def jpeg_compression(self, image: np.ndarray, 
                        quality: int = 85) -> np.ndarray:
        """
        JPEG压缩攻击
        
        Args:
            image: 输入图像
            quality: JPEG质量（1-100）
            
        Returns:
            压缩后的图像
        """
        # 编码为JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, encoded_img = cv2.imencode('.jpg', image, encode_param)
        
        # 解码
        compressed = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
        if compressed is None:
            compressed = cv2.imdecode(encoded_img, cv2.IMREAD_GRAYSCALE)
        
        self.logger.info(f"JPEG压缩，质量: {quality}")
        return compressed
    
    def low_pass_filter(self, image: np.ndarray, 
                       cutoff_freq: float = 0.3) -> np.ndarray:
        """
        低通滤波
        
        Args:
            image: 输入图像
            cutoff_freq: 截止频率（归一化频率，0-1）
            
        Returns:
            滤波后的图像
        """
        if len(image.shape) == 3:
            # 彩色图像，对每个通道单独处理
            filtered = np.zeros_like(image)
            for i in range(image.shape[2]):
                filtered[:, :, i] = self._apply_butterworth_filter(
                    image[:, :, i], cutoff_freq, 'low')
        else:
            # 灰度图像
            filtered = self._apply_butterworth_filter(image, cutoff_freq, 'low')
        
        self.logger.info(f"应用低通滤波，截止频率: {cutoff_freq}")
        return filtered.astype(np.uint8)
    
    def high_pass_filter(self, image: np.ndarray, 
                        cutoff_freq: float = 0.1) -> np.ndarray:
        """
        高通滤波
        
        Args:
            image: 输入图像
            cutoff_freq: 截止频率（归一化频率，0-1）
            
        Returns:
            滤波后的图像
        """
        if len(image.shape) == 3:
            # 彩色图像，对每个通道单独处理
            filtered = np.zeros_like(image)
            for i in range(image.shape[2]):
                filtered[:, :, i] = self._apply_butterworth_filter(
                    image[:, :, i], cutoff_freq, 'high')
        else:
            # 灰度图像
            filtered = self._apply_butterworth_filter(image, cutoff_freq, 'high')
        
        self.logger.info(f"应用高通滤波，截止频率: {cutoff_freq}")
        return filtered.astype(np.uint8)
    
    def _apply_butterworth_filter(self, image: np.ndarray, 
                                 cutoff: float, filter_type: str) -> np.ndarray:
        """
        应用巴特沃斯滤波器
        """
        # 进行2D FFT
        f_transform = np.fft.fft2(image)
        f_shift = np.fft.fftshift(f_transform)
        
        # 创建频域滤波器
        h, w = image.shape
        center_h, center_w = h // 2, w // 2
        
        # 创建距离矩阵
        y, x = np.ogrid[:h, :w]
        distance = np.sqrt((x - center_w)**2 + (y - center_h)**2)
        
        # 归一化距离
        max_distance = np.sqrt(center_h**2 + center_w**2)
        normalized_distance = distance / max_distance
        
        # 巴特沃斯滤波器
        if filter_type == 'low':
            filter_mask = 1 / (1 + (normalized_distance / cutoff)**4)
        else:  # high pass
            filter_mask = 1 / (1 + (cutoff / (normalized_distance + 1e-8))**4)
        
        # 应用滤波器
        filtered_shift = f_shift * filter_mask
        filtered_transform = np.fft.ifftshift(filtered_shift)
        filtered_image = np.fft.ifft2(filtered_transform)
        
        # 取实部并限制范围
        result = np.real(filtered_image)
        result = np.clip(result, 0, 255)
        
        return result
    
    def apply_multiple_attacks(self, image: np.ndarray, 
                              attack_sequence: list) -> np.ndarray:
        """
        应用多个信号处理攻击的组合
        
        Args:
            image: 输入图像
            attack_sequence: 攻击序列，每个元素为(攻击名称, 参数字典)
            
        Returns:
            攻击后的图像
        """
        result_image = image.copy()
        
        for attack_name, params in attack_sequence:
            if attack_name == 'gaussian_noise':
                result_image = self.add_gaussian_noise(result_image, **params)
            elif attack_name == 'salt_pepper_noise':
                result_image = self.add_salt_pepper_noise(result_image, **params)
            elif attack_name == 'uniform_noise':
                result_image = self.add_uniform_noise(result_image, **params)
            elif attack_name == 'gaussian_blur':
                result_image = self.gaussian_blur(result_image, **params)
            elif attack_name == 'median_blur':
                result_image = self.median_blur(result_image, **params)
            elif attack_name == 'motion_blur':
                result_image = self.motion_blur(result_image, **params)
            elif attack_name == 'sharpen':
                result_image = self.sharpen(result_image, **params)
            elif attack_name == 'brightness':
                result_image = self.adjust_brightness(result_image, **params)
            elif attack_name == 'contrast':
                result_image = self.adjust_contrast(result_image, **params)
            elif attack_name == 'gamma':
                result_image = self.adjust_gamma(result_image, **params)
            elif attack_name == 'histogram_eq':
                result_image = self.histogram_equalization(result_image)
            elif attack_name == 'jpeg_compression':
                result_image = self.jpeg_compression(result_image, **params)
            elif attack_name == 'low_pass':
                result_image = self.low_pass_filter(result_image, **params)
            elif attack_name == 'high_pass':
                result_image = self.high_pass_filter(result_image, **params)
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
            'light_noise': [('gaussian_noise', {'std': 10})],
            'medium_noise': [('gaussian_noise', {'std': 25})],
            'heavy_noise': [('gaussian_noise', {'std': 50})],
            'salt_pepper': [('salt_pepper_noise', {'salt_prob': 0.05, 'pepper_prob': 0.05})],
            'light_blur': [('gaussian_blur', {'sigma': 1.0})],
            'medium_blur': [('gaussian_blur', {'sigma': 2.0})],
            'heavy_blur': [('gaussian_blur', {'sigma': 3.0})],
            'jpeg_high': [('jpeg_compression', {'quality': 85})],
            'jpeg_medium': [('jpeg_compression', {'quality': 50})],
            'jpeg_low': [('jpeg_compression', {'quality': 20})],
            'brightness_up': [('brightness', {'brightness': 30})],
            'brightness_down': [('brightness', {'brightness': -30})],
            'contrast_up': [('contrast', {'contrast': 1.5})],
            'contrast_down': [('contrast', {'contrast': 0.7})],
            'filtering_combo': [
                ('gaussian_blur', {'sigma': 1.5}),
                ('sharpen', {'strength': 0.5})
            ],
            'noise_filter_combo': [
                ('gaussian_noise', {'std': 20}),
                ('median_blur', {'kernel_size': 3})
            ],
            'compression_enhancement': [
                ('jpeg_compression', {'quality': 40}),
                ('sharpen', {'strength': 1.0}),
                ('contrast', {'contrast': 1.2})
            ]
        }


def demo_signal_processing_attacks():
    """信号处理攻击演示函数"""
    from ..utils.image_loader import ImageLoader
    
    # 创建测试图像
    test_image = ImageLoader.create_test_image((256, 256), 'lena')
    
    # 初始化信号处理攻击类
    sp_attacks = SignalProcessingAttacks()
    
    # 测试各种攻击
    print("信号处理攻击演示:")
    
    # 噪声攻击
    noisy = sp_attacks.add_gaussian_noise(test_image, std=25)
    print(f"高斯噪声结果尺寸: {noisy.shape}")
    
    # 模糊攻击
    blurred = sp_attacks.gaussian_blur(test_image, sigma=2.0)
    print(f"高斯模糊结果尺寸: {blurred.shape}")
    
    # 压缩攻击
    compressed = sp_attacks.jpeg_compression(test_image, quality=50)
    print(f"JPEG压缩结果尺寸: {compressed.shape}")
    
    # 对比度调整
    contrast_adjusted = sp_attacks.adjust_contrast(test_image, contrast=1.5)
    print(f"对比度调整结果尺寸: {contrast_adjusted.shape}")
    
    # 组合攻击
    attack_sequence = [
        ('gaussian_noise', {'std': 15}),
        ('gaussian_blur', {'sigma': 1.0}),
        ('jpeg_compression', {'quality': 60})
    ]
    combined_result = sp_attacks.apply_multiple_attacks(test_image, attack_sequence)
    print(f"组合攻击结果尺寸: {combined_result.shape}")
    
    # 显示可用的攻击配置
    configs = sp_attacks.get_common_attack_configs()
    print(f"可用攻击配置: {list(configs.keys())}")


if __name__ == "__main__":
    demo_signal_processing_attacks()
