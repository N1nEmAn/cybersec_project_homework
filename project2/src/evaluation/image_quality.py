"""
图像质量评估模块
实现PSNR、SSIM等图像质量评估指标
"""

import numpy as np
import cv2
from typing import Tuple, Union, Optional
import logging
from scipy.signal import convolve2d
from skimage.metrics import structural_similarity as ssim

logger = logging.getLogger(__name__)


class ImageQualityMetrics:
    """图像质量评估指标类"""
    
    def __init__(self):
        self.logger = logger
    
    def mse(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        计算均方误差 (Mean Squared Error)
        
        Args:
            img1: 原始图像
            img2: 比较图像
            
        Returns:
            MSE值
        """
        if img1.shape != img2.shape:
            raise ValueError("图像尺寸不匹配")
        
        # 转换为浮点型避免溢出
        img1_float = img1.astype(np.float64)
        img2_float = img2.astype(np.float64)
        
        # 计算MSE
        mse_value = np.mean((img1_float - img2_float) ** 2)
        
        self.logger.info(f"MSE计算完成: {mse_value:.4f}")
        return mse_value
    
    def psnr(self, img1: np.ndarray, img2: np.ndarray, 
             max_pixel_value: float = 255.0) -> float:
        """
        计算峰值信噪比 (Peak Signal-to-Noise Ratio)
        
        数学公式：
        PSNR = 10 * log10(MAX²/MSE)
        其中 MAX 是像素的最大可能值，MSE 是均方误差
        
        Args:
            img1: 原始图像
            img2: 比较图像
            max_pixel_value: 像素最大值（通常为255）
            
        Returns:
            PSNR值（dB）
        """
        mse_value = self.mse(img1, img2)
        
        if mse_value == 0:
            # 图像完全相同
            return float('inf')
        
        # 计算PSNR
        psnr_value = 10 * np.log10((max_pixel_value ** 2) / mse_value)
        
        self.logger.info(f"PSNR计算完成: {psnr_value:.4f} dB")
        return psnr_value
    
    def ssim(self, img1: np.ndarray, img2: np.ndarray, 
             window_size: int = 11, k1: float = 0.01, 
             k2: float = 0.03, L: float = 255.0) -> float:
        """
        计算结构相似性指数 (Structural Similarity Index)
        
        数学公式：
        SSIM(x,y) = (2μₓμᵧ + C₁)(2σₓᵧ + C₂) / ((μₓ² + μᵧ² + C₁)(σₓ² + σᵧ² + C₂))
        其中：
        - μₓ, μᵧ 是图像x和y的均值
        - σₓ², σᵧ² 是图像x和y的方差
        - σₓᵧ 是图像x和y的协方差
        - C₁ = (k₁L)², C₂ = (k₂L)² 是稳定常数
        
        Args:
            img1: 原始图像
            img2: 比较图像
            window_size: 滑动窗口大小
            k1, k2: 稳定常数参数
            L: 像素值动态范围
            
        Returns:
            SSIM值（0-1之间，1表示完全相同）
        """
        if img1.shape != img2.shape:
            raise ValueError("图像尺寸不匹配")
        
        # 如果是彩色图像，转换为灰度图像
        if len(img1.shape) == 3:
            img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        else:
            img1_gray = img1
            img2_gray = img2
        
        # 使用skimage的SSIM实现
        ssim_value = ssim(img1_gray, img2_gray, 
                         win_size=window_size,
                         data_range=L)
        
        self.logger.info(f"SSIM计算完成: {ssim_value:.4f}")
        return ssim_value
    
    def ssim_manual(self, img1: np.ndarray, img2: np.ndarray,
                   window_size: int = 11, k1: float = 0.01,
                   k2: float = 0.03, L: float = 255.0) -> float:
        """
        手动实现SSIM计算（用于理解算法原理）
        
        Args:
            img1: 原始图像
            img2: 比较图像
            window_size: 滑动窗口大小
            k1, k2: 稳定常数参数
            L: 像素值动态范围
            
        Returns:
            SSIM值
        """
        if img1.shape != img2.shape:
            raise ValueError("图像尺寸不匹配")
        
        # 转换为浮点型
        img1_float = img1.astype(np.float64)
        img2_float = img2.astype(np.float64)
        
        # 计算稳定常数
        C1 = (k1 * L) ** 2
        C2 = (k2 * L) ** 2
        
        # 创建高斯权重窗口
        window = self._create_gaussian_window(window_size)
        
        # 计算局部均值
        mu1 = convolve2d(img1_float, window, mode='valid')
        mu2 = convolve2d(img2_float, window, mode='valid')
        
        # 计算局部方差和协方差
        mu1_sq = mu1 ** 2
        mu2_sq = mu2 ** 2
        mu1_mu2 = mu1 * mu2
        
        sigma1_sq = convolve2d(img1_float ** 2, window, mode='valid') - mu1_sq
        sigma2_sq = convolve2d(img2_float ** 2, window, mode='valid') - mu2_sq
        sigma12 = convolve2d(img1_float * img2_float, window, mode='valid') - mu1_mu2
        
        # 计算SSIM
        numerator = (2 * mu1_mu2 + C1) * (2 * sigma12 + C2)
        denominator = (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
        
        ssim_map = numerator / denominator
        ssim_value = np.mean(ssim_map)
        
        self.logger.info(f"手动SSIM计算完成: {ssim_value:.4f}")
        return ssim_value
    
    def _create_gaussian_window(self, size: int, sigma: float = 1.5) -> np.ndarray:
        """
        创建高斯窗口函数
        
        Args:
            size: 窗口大小
            sigma: 标准差
            
        Returns:
            归一化的高斯窗口
        """
        coords = np.arange(size) - size // 2
        g = np.exp(-0.5 * (coords / sigma) ** 2)
        g = g / np.sum(g)
        
        # 创建2D高斯窗口
        window = np.outer(g, g)
        return window / np.sum(window)
    
    def ncc(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        计算归一化相关系数 (Normalized Cross-Correlation)
        
        数学公式：
        NCC = Σ(x-x̄)(y-ȳ) / √(Σ(x-x̄)²Σ(y-ȳ)²)
        
        Args:
            img1: 原始图像
            img2: 比较图像
            
        Returns:
            NCC值（-1到1之间，1表示完全正相关）
        """
        if img1.shape != img2.shape:
            raise ValueError("图像尺寸不匹配")
        
        # 转换为浮点型并展平
        img1_flat = img1.astype(np.float64).flatten()
        img2_flat = img2.astype(np.float64).flatten()
        
        # 去除均值
        img1_centered = img1_flat - np.mean(img1_flat)
        img2_centered = img2_flat - np.mean(img2_flat)
        
        # 计算相关系数
        numerator = np.sum(img1_centered * img2_centered)
        denominator = np.sqrt(np.sum(img1_centered ** 2) * np.sum(img2_centered ** 2))
        
        if denominator == 0:
            return 0.0
        
        ncc_value = numerator / denominator
        
        self.logger.info(f"NCC计算完成: {ncc_value:.4f}")
        return ncc_value
    
    def mad(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        计算平均绝对差 (Mean Absolute Difference)
        
        Args:
            img1: 原始图像
            img2: 比较图像
            
        Returns:
            MAD值
        """
        if img1.shape != img2.shape:
            raise ValueError("图像尺寸不匹配")
        
        mad_value = np.mean(np.abs(img1.astype(np.float64) - img2.astype(np.float64)))
        
        self.logger.info(f"MAD计算完成: {mad_value:.4f}")
        return mad_value
    
    def uqi(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        计算通用图像质量指数 (Universal Image Quality Index)
        
        数学公式：
        UQI = (4σₓᵧ·x̄·ȳ) / ((σₓ² + σᵧ²)·(x̄² + ȳ²))
        
        Args:
            img1: 原始图像
            img2: 比较图像
            
        Returns:
            UQI值（-1到1之间，1表示完全相同）
        """
        if img1.shape != img2.shape:
            raise ValueError("图像尺寸不匹配")
        
        # 转换为浮点型并展平
        img1_flat = img1.astype(np.float64).flatten()
        img2_flat = img2.astype(np.float64).flatten()
        
        # 计算统计量
        mean1 = np.mean(img1_flat)
        mean2 = np.mean(img2_flat)
        var1 = np.var(img1_flat)
        var2 = np.var(img2_flat)
        covar = np.mean((img1_flat - mean1) * (img2_flat - mean2))
        
        # 计算UQI
        numerator = 4 * covar * mean1 * mean2
        denominator = (var1 + var2) * (mean1**2 + mean2**2)
        
        if denominator == 0:
            return 0.0
        
        uqi_value = numerator / denominator
        
        self.logger.info(f"UQI计算完成: {uqi_value:.4f}")
        return uqi_value
    
    def compute_all_metrics(self, img1: np.ndarray, img2: np.ndarray) -> dict:
        """
        计算所有质量评估指标
        
        Args:
            img1: 原始图像
            img2: 比较图像
            
        Returns:
            包含所有指标的字典
        """
        metrics = {}
        
        try:
            metrics['mse'] = self.mse(img1, img2)
            metrics['psnr'] = self.psnr(img1, img2)
            metrics['ssim'] = self.ssim(img1, img2)
            metrics['ncc'] = self.ncc(img1, img2)
            metrics['mad'] = self.mad(img1, img2)
            metrics['uqi'] = self.uqi(img1, img2)
        except Exception as e:
            self.logger.error(f"计算质量指标时出错: {e}")
            raise
        
        self.logger.info("所有质量指标计算完成")
        return metrics
    
    def quality_assessment(self, metrics: dict) -> str:
        """
        基于指标值进行质量评估
        
        Args:
            metrics: 质量指标字典
            
        Returns:
            质量评估结果
        """
        psnr = metrics.get('psnr', 0)
        ssim = metrics.get('ssim', 0)
        
        if psnr >= 40 and ssim >= 0.95:
            return "优秀"
        elif psnr >= 30 and ssim >= 0.90:
            return "良好"
        elif psnr >= 25 and ssim >= 0.80:
            return "一般"
        elif psnr >= 20 and ssim >= 0.70:
            return "较差"
        else:
            return "很差"


def demo_image_quality_metrics():
    """图像质量评估演示函数"""
    from ..utils.image_loader import ImageLoader
    from ..attacks import SignalProcessingAttacks
    
    # 创建测试图像
    original = ImageLoader.create_test_image((256, 256), 'lena')
    
    # 创建攻击图像
    sp_attacks = SignalProcessingAttacks()
    attacked = sp_attacks.add_gaussian_noise(original, std=25)
    
    # 初始化质量评估
    quality_metrics = ImageQualityMetrics()
    
    # 计算所有指标
    metrics = quality_metrics.compute_all_metrics(original, attacked)
    
    # 显示结果
    print("图像质量评估结果:")
    for metric_name, value in metrics.items():
        print(f"{metric_name.upper()}: {value:.4f}")
    
    # 质量评估
    assessment = quality_metrics.quality_assessment(metrics)
    print(f"整体质量评估: {assessment}")


if __name__ == "__main__":
    demo_image_quality_metrics()
