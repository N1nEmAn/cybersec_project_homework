#!/usr/bin/env python3
"""
数字水印系统完整演示脚本
演示LSB和DCT算法的嵌入、提取和鲁棒性测试
"""

import os
import sys
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import time

# 添加项目路径
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

from src.algorithms.lsb_watermark import LSBWatermark
from src.algorithms.dct_watermark import DCTWatermark
from src.attacks.geometric_attacks import GeometricAttacks
from src.attacks.signal_processing_attacks import SignalProcessingAttacks
from src.evaluation.image_quality import ImageQuality
from src.evaluation.watermark_robustness import WatermarkRobustness

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class WatermarkDemo:
    """水印系统演示类"""
    
    def __init__(self):
        self.output_dir = os.path.join(project_path, 'demo')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化算法
        self.lsb = LSBWatermark(bit_plane=2)
        self.dct = DCTWatermark(block_size=8, alpha=0.1)
        
        # 初始化攻击和评估模块
        self.geo_attacks = GeometricAttacks()
        self.sp_attacks = SignalProcessingAttacks()
        self.quality_eval = ImageQuality()
        self.robustness_eval = WatermarkRobustness()
        
    def load_test_images(self):
        """加载测试图像"""
        host_path = os.path.join(project_path, 'data/input/host.png')
        watermark_path = os.path.join(project_path, 'data/watermarks/watermark.png')
        
        if not os.path.exists(host_path) or not os.path.exists(watermark_path):
            print("❌ 测试图像不存在，请先运行 create_test_data.py")
            return None, None
            
        host = cv2.imread(host_path, cv2.IMREAD_GRAYSCALE)
        watermark = cv2.imread(watermark_path, cv2.IMREAD_GRAYSCALE)
        
        return host, watermark
    
    def demo_lsb_algorithm(self, host, watermark):
        """演示LSB算法"""
        print("\n=== LSB算法演示 ===")
        
        # 嵌入水印
        start_time = time.time()
        watermarked_lsb = self.lsb.embed(host, watermark, strength=0.8)
        embed_time = time.time() - start_time
        
        # 提取水印
        start_time = time.time()
        extracted_lsb = self.lsb.extract(watermarked_lsb, watermark.shape)
        extract_time = time.time() - start_time
        
        print(f"✅ LSB嵌入时间: {embed_time:.4f}秒")
        print(f"✅ LSB提取时间: {extract_time:.4f}秒")
        
        # 保存结果
        cv2.imwrite(os.path.join(self.output_dir, 'lsb_watermarked.png'), watermarked_lsb)
        cv2.imwrite(os.path.join(self.output_dir, 'lsb_extracted.png'), extracted_lsb)
        
        # 质量评估
        metrics = self.quality_eval.calculate_metrics(host, watermarked_lsb)
        print(f"📊 LSB质量指标: PSNR={metrics['psnr']:.2f}dB, SSIM={metrics['ssim']:.4f}")
        
        return watermarked_lsb, extracted_lsb, metrics
    
    def demo_dct_algorithm(self, host, watermark):
        """演示DCT算法"""
        print("\n=== DCT算法演示 ===")
        
        # 嵌入水印
        start_time = time.time()
        watermarked_dct = self.dct.embed(host, watermark, strength=1.0)
        embed_time = time.time() - start_time
        
        # 提取水印
        start_time = time.time()
        extracted_dct = self.dct.extract(watermarked_dct, host)  # 非盲提取
        extract_time = time.time() - start_time
        
        print(f"✅ DCT嵌入时间: {embed_time:.4f}秒")
        print(f"✅ DCT提取时间: {extract_time:.4f}秒")
        
        # 保存结果
        cv2.imwrite(os.path.join(self.output_dir, 'dct_watermarked.png'), watermarked_dct.astype(np.uint8))
        cv2.imwrite(os.path.join(self.output_dir, 'dct_extracted.png'), extracted_dct)
        
        # 质量评估
        watermarked_uint8 = watermarked_dct.astype(np.uint8)
        metrics = self.quality_eval.calculate_metrics(host, watermarked_uint8)
        print(f"📊 DCT质量指标: PSNR={metrics['psnr']:.2f}dB, SSIM={metrics['ssim']:.4f}")
        
        return watermarked_uint8, extracted_dct, metrics
    
    def demo_attacks(self, watermarked_image, algorithm_name):
        """演示攻击测试"""
        print(f"\n=== {algorithm_name}攻击测试演示 ===")
        
        attack_results = {}
        
        # 几何攻击
        attacks_to_test = [
            ('rotation_15', lambda img: self.geo_attacks.rotation(img, 15)),
            ('scaling_0.8', lambda img: self.geo_attacks.scaling(img, 0.8)),
            ('crop_quarter', lambda img: self.geo_attacks.crop(img, (0.25, 0.25, 0.75, 0.75))),
            ('flip_horizontal', lambda img: self.geo_attacks.flip_horizontal(img)),
        ]
        
        # 信号处理攻击
        attacks_to_test.extend([
            ('gaussian_noise_0.01', lambda img: self.sp_attacks.gaussian_noise(img, 0.01)),
            ('jpeg_compression_50', lambda img: self.sp_attacks.jpeg_compression(img, 50)),
            ('gaussian_blur_1.5', lambda img: self.sp_attacks.gaussian_blur(img, 1.5)),
            ('brightness_1.2', lambda img: self.sp_attacks.brightness_contrast(img, 1.2, 0)),
        ])
        
        for attack_name, attack_func in attacks_to_test:
            try:
                attacked_image = attack_func(watermarked_image)
                
                # 保存攻击后的图像
                save_path = os.path.join(self.output_dir, f'{algorithm_name.lower()}_{attack_name}.png')
                cv2.imwrite(save_path, attacked_image)
                
                # 计算质量指标
                metrics = self.quality_eval.calculate_metrics(watermarked_image, attacked_image)
                attack_results[attack_name] = {
                    'psnr': metrics['psnr'],
                    'ssim': metrics['ssim'],
                    'attacked_image': attacked_image
                }
                
                print(f"🔍 {attack_name}: PSNR={metrics['psnr']:.2f}dB, SSIM={metrics['ssim']:.4f}")
                
            except Exception as e:
                print(f"❌ {attack_name} 攻击失败: {e}")
                
        return attack_results
    
    def create_visualization(self, host, watermark, lsb_results, dct_results):
        """创建可视化图表"""
        print("\n=== 创建可视化图表 ===")
        
        # 创建综合图表
        fig = plt.figure(figsize=(20, 12))
        
        # 原始图像展示
        plt.subplot(3, 6, 1)
        plt.imshow(host, cmap='gray')
        plt.title('原始宿主图像\\n(512×512)', fontsize=10)
        plt.axis('off')
        
        plt.subplot(3, 6, 2)
        plt.imshow(watermark, cmap='gray')
        plt.title('水印图像\\n(64×64)', fontsize=10)
        plt.axis('off')
        
        # LSB结果
        plt.subplot(3, 6, 3)
        plt.imshow(lsb_results['watermarked'], cmap='gray')
        plt.title(f'LSB含水印图像\\nPSNR: {lsb_results["metrics"]["psnr"]:.1f}dB', fontsize=10)
        plt.axis('off')
        
        plt.subplot(3, 6, 4)
        plt.imshow(lsb_results['extracted'], cmap='gray')
        plt.title('LSB提取水印', fontsize=10)
        plt.axis('off')
        
        # DCT结果
        plt.subplot(3, 6, 5)
        plt.imshow(dct_results['watermarked'], cmap='gray')
        plt.title(f'DCT含水印图像\\nPSNR: {dct_results["metrics"]["psnr"]:.1f}dB', fontsize=10)
        plt.axis('off')
        
        plt.subplot(3, 6, 6)
        plt.imshow(dct_results['extracted'], cmap='gray')
        plt.title('DCT提取水印', fontsize=10)
        plt.axis('off')
        
        # 攻击测试结果展示（选择几个代表性攻击）
        attack_names = ['rotation_15', 'gaussian_noise_0.01', 'jpeg_compression_50', 'crop_quarter']
        
        for i, attack_name in enumerate(attack_names):
            if attack_name in lsb_results['attacks']:
                plt.subplot(3, 6, 7 + i)
                plt.imshow(lsb_results['attacks'][attack_name]['attacked_image'], cmap='gray')
                psnr = lsb_results['attacks'][attack_name]['psnr']
                plt.title(f'LSB-{attack_name}\\nPSNR: {psnr:.1f}dB', fontsize=9)
                plt.axis('off')
                
        for i, attack_name in enumerate(attack_names):
            if attack_name in dct_results['attacks']:
                plt.subplot(3, 6, 13 + i)
                plt.imshow(dct_results['attacks'][attack_name]['attacked_image'], cmap='gray')
                psnr = dct_results['attacks'][attack_name]['psnr']
                plt.title(f'DCT-{attack_name}\\nPSNR: {psnr:.1f}dB', fontsize=9)
                plt.axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'watermark_demo_results.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
        # 创建性能对比图表
        self.create_performance_chart(lsb_results, dct_results)
        
    def create_performance_chart(self, lsb_results, dct_results):
        """创建性能对比图表"""
        # 算法性能对比
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # PSNR对比
        algorithms = ['LSB', 'DCT']
        psnr_values = [lsb_results['metrics']['psnr'], dct_results['metrics']['psnr']]
        
        axes[0, 0].bar(algorithms, psnr_values, color=['skyblue', 'lightcoral'])
        axes[0, 0].set_title('算法PSNR对比')
        axes[0, 0].set_ylabel('PSNR (dB)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # SSIM对比
        ssim_values = [lsb_results['metrics']['ssim'], dct_results['metrics']['ssim']]
        axes[0, 1].bar(algorithms, ssim_values, color=['skyblue', 'lightcoral'])
        axes[0, 1].set_title('算法SSIM对比')
        axes[0, 1].set_ylabel('SSIM')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 攻击鲁棒性对比（PSNR）
        attack_names = ['rotation_15', 'gaussian_noise_0.01', 'jpeg_compression_50', 'crop_quarter']
        lsb_attack_psnr = [lsb_results['attacks'].get(name, {}).get('psnr', 0) for name in attack_names]
        dct_attack_psnr = [dct_results['attacks'].get(name, {}).get('psnr', 0) for name in attack_names]
        
        x = np.arange(len(attack_names))
        width = 0.35
        
        axes[1, 0].bar(x - width/2, lsb_attack_psnr, width, label='LSB', color='skyblue')
        axes[1, 0].bar(x + width/2, dct_attack_psnr, width, label='DCT', color='lightcoral')
        axes[1, 0].set_title('攻击后PSNR对比')
        axes[1, 0].set_ylabel('PSNR (dB)')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels([name.replace('_', '\\n') for name in attack_names], fontsize=8)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 攻击鲁棒性对比（SSIM）
        lsb_attack_ssim = [lsb_results['attacks'].get(name, {}).get('ssim', 0) for name in attack_names]
        dct_attack_ssim = [dct_results['attacks'].get(name, {}).get('ssim', 0) for name in attack_names]
        
        axes[1, 1].bar(x - width/2, lsb_attack_ssim, width, label='LSB', color='skyblue')
        axes[1, 1].bar(x + width/2, dct_attack_ssim, width, label='DCT', color='lightcoral')
        axes[1, 1].set_title('攻击后SSIM对比')
        axes[1, 1].set_ylabel('SSIM')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels([name.replace('_', '\\n') for name in attack_names], fontsize=8)
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'performance_comparison.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self, lsb_results, dct_results):
        """生成演示报告"""
        report_path = os.path.join(self.output_dir, 'DEMO_REPORT.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 数字水印系统演示报告\\n\\n")
            f.write("## 测试环境\\n")
            f.write(f"- 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write("- 宿主图像: 512×512灰度图像\\n")
            f.write("- 水印图像: 64×64二值图像\\n\\n")
            
            f.write("## LSB算法测试结果\\n")
            f.write(f"- PSNR: {lsb_results['metrics']['psnr']:.2f} dB\\n")
            f.write(f"- SSIM: {lsb_results['metrics']['ssim']:.4f}\\n")
            f.write("- 攻击测试结果:\\n")
            for attack_name, result in lsb_results['attacks'].items():
                f.write(f"  - {attack_name}: PSNR={result['psnr']:.2f}dB, SSIM={result['ssim']:.4f}\\n")
            
            f.write("\\n## DCT算法测试结果\\n")
            f.write(f"- PSNR: {dct_results['metrics']['psnr']:.2f} dB\\n")
            f.write(f"- SSIM: {dct_results['metrics']['ssim']:.4f}\\n")
            f.write("- 攻击测试结果:\\n")
            for attack_name, result in dct_results['attacks'].items():
                f.write(f"  - {attack_name}: PSNR={result['psnr']:.2f}dB, SSIM={result['ssim']:.4f}\\n")
            
            f.write("\\n## 结论\\n")
            f.write("1. LSB算法具有较高的不可感知性但鲁棒性较弱\\n")
            f.write("2. DCT算法在频域操作，对某些攻击有更好的鲁棒性\\n")
            f.write("3. 两种算法都能成功实现水印的嵌入和提取\\n")
            f.write("\\n## 生成的文件\\n")
            f.write("- watermark_demo_results.png: 综合演示结果\\n")
            f.write("- performance_comparison.png: 性能对比图表\\n")
            f.write("- lsb_watermarked.png, dct_watermarked.png: 含水印图像\\n")
            f.write("- lsb_extracted.png, dct_extracted.png: 提取的水印\\n")
            f.write("- 各种攻击后的图像文件\\n")
        
        print(f"✅ 演示报告已生成: {report_path}")
    
    def run_complete_demo(self):
        """运行完整演示"""
        print("🚀 开始数字水印系统完整演示")
        print("=" * 50)
        
        # 加载测试图像
        host, watermark = self.load_test_images()
        if host is None or watermark is None:
            return
        
        print(f"✅ 测试图像加载成功: 宿主图像{host.shape}, 水印图像{watermark.shape}")
        
        # LSB算法演示
        lsb_watermarked, lsb_extracted, lsb_metrics = self.demo_lsb_algorithm(host, watermark)
        lsb_attacks = self.demo_attacks(lsb_watermarked, 'LSB')
        
        lsb_results = {
            'watermarked': lsb_watermarked,
            'extracted': lsb_extracted,
            'metrics': lsb_metrics,
            'attacks': lsb_attacks
        }
        
        # DCT算法演示
        dct_watermarked, dct_extracted, dct_metrics = self.demo_dct_algorithm(host, watermark)
        dct_attacks = self.demo_attacks(dct_watermarked, 'DCT')
        
        dct_results = {
            'watermarked': dct_watermarked,
            'extracted': dct_extracted,
            'metrics': dct_metrics,
            'attacks': dct_attacks
        }
        
        # 创建可视化
        self.create_visualization(host, watermark, lsb_results, dct_results)
        
        # 生成报告
        self.generate_report(lsb_results, dct_results)
        
        print("\\n🎉 完整演示已完成！")
        print(f"📁 结果文件保存在: {self.output_dir}")
        print("请查看生成的图像和报告文件。")

if __name__ == "__main__":
    demo = WatermarkDemo()
    demo.run_complete_demo()
