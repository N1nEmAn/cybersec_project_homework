#!/usr/bin/env python3
"""
图像质量评估工具
提供各种图像质量指标的计算和分析
"""

import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import argparse

class ImageQualityAnalyzer:
    """图像质量分析器"""
    
    def __init__(self):
        self.metrics = {}
    
    def calculate_psnr(self, original, compressed, max_val=255):
        """计算PSNR"""
        try:
            return psnr(original, compressed, data_range=max_val)
        except:
            mse = np.mean((original - compressed) ** 2)
            if mse == 0:
                return float('inf')
            return 20 * np.log10(max_val / np.sqrt(mse))
    
    def calculate_ssim(self, original, compressed):
        """计算SSIM"""
        if len(original.shape) == 3:
            # 对彩色图像计算多通道SSIM
            ssim_values = []
            for i in range(original.shape[2]):
                ssim_val = ssim(original[:,:,i], compressed[:,:,i], data_range=255)
                ssim_values.append(ssim_val)
            return np.mean(ssim_values)
        else:
            return ssim(original, compressed, data_range=255)
    
    def calculate_mse(self, original, compressed):
        """计算均方误差"""
        return np.mean((original.astype(float) - compressed.astype(float)) ** 2)
    
    def calculate_ncc(self, original, compressed):
        """计算归一化交叉相关"""
        orig_flat = original.flatten().astype(float)
        comp_flat = compressed.flatten().astype(float)
        
        # 减去均值
        orig_centered = orig_flat - np.mean(orig_flat)
        comp_centered = comp_flat - np.mean(comp_flat)
        
        # 计算NCC
        numerator = np.sum(orig_centered * comp_centered)
        denominator = np.sqrt(np.sum(orig_centered**2) * np.sum(comp_centered**2))
        
        if denominator == 0:
            return 0
        return numerator / denominator
    
    def calculate_mad(self, original, compressed):
        """计算平均绝对差"""
        return np.mean(np.abs(original.astype(float) - compressed.astype(float)))
    
    def evaluate_quality(self, original_path, compressed_path):
        """评估两张图像的质量差异"""
        # 加载图像
        original = cv2.imread(original_path)
        compressed = cv2.imread(compressed_path)
        
        if original is None or compressed is None:
            raise ValueError("无法加载图像文件")
        
        # 确保尺寸一致
        if original.shape != compressed.shape:
            compressed = cv2.resize(compressed, (original.shape[1], original.shape[0]))
        
        # 计算各种指标
        self.metrics = {
            'psnr': self.calculate_psnr(original, compressed),
            'ssim': self.calculate_ssim(original, compressed),
            'mse': self.calculate_mse(original, compressed),
            'ncc': self.calculate_ncc(original, compressed),
            'mad': self.calculate_mad(original, compressed)
        }
        
        return self.metrics
    
    def get_quality_grade(self):
        """根据PSNR和SSIM给出质量等级"""
        psnr_val = self.metrics.get('psnr', 0)
        ssim_val = self.metrics.get('ssim', 0)
        
        if psnr_val >= 40 and ssim_val >= 0.98:
            return "优秀"
        elif psnr_val >= 30 and ssim_val >= 0.90:
            return "良好"
        elif psnr_val >= 25 and ssim_val >= 0.80:
            return "可接受"
        else:
            return "较差"
    
    def print_results(self):
        """打印评估结果"""
        print("\n=== 图像质量评估结果 ===")
        for metric, value in self.metrics.items():
            if metric == 'psnr':
                print(f"PSNR: {value:.2f} dB")
            else:
                print(f"{metric.upper()}: {value:.4f}")
        
        print(f"质量等级: {self.get_quality_grade()}")

def main():
    parser = argparse.ArgumentParser(description='图像质量评估工具')
    parser.add_argument('original', help='原始图像路径')
    parser.add_argument('compressed', help='压缩/处理后图像路径')
    parser.add_argument('--output', help='结果输出文件')
    
    args = parser.parse_args()
    
    analyzer = ImageQualityAnalyzer()
    
    try:
        metrics = analyzer.evaluate_quality(args.original, args.compressed)
        analyzer.print_results()
        
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(metrics, f, indent=2)
            print(f"\n结果已保存到: {args.output}")
    
    except Exception as e:
        print(f"评估失败: {e}")

if __name__ == '__main__':
    main()
