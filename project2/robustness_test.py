"""
综合鲁棒性测试脚本
自动测试多种攻击对水印算法的影响
"""

import sys
import os
from pathlib import Path
import numpy as np
import cv2
import logging
import json
from typing import Dict, List, Tuple
import argparse

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.algorithms import AlgorithmRegistry
from src.attacks import AttackEngine
from src.evaluation import EvaluationEngine
from src.utils.image_loader import ImageLoader
from src.utils.logger import setup_logger


class RobustnessTestSuite:
    """鲁棒性测试套件"""
    
    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化组件
        self.algorithm_registry = AlgorithmRegistry()
        self.attack_engine = AttackEngine()
        self.evaluation_engine = EvaluationEngine()
        
        # 设置日志
        self.logger = setup_logger(
            name='robustness_test',
            level=logging.INFO,
            log_file=str(self.output_dir / 'test.log')
        )
        
        # 测试结果
        self.test_results = {}
    
    def get_test_attack_configs(self) -> Dict:
        """获取测试用的攻击配置"""
        return {
            # 几何攻击
            'rotation_light': [('rotate', {'angle': 5})],
            'rotation_medium': [('rotate', {'angle': 15})],
            'rotation_heavy': [('rotate', {'angle': 30})],
            'scaling_down': [('scale', {'scale_factor': 0.8})],
            'scaling_up': [('scale', {'scale_factor': 1.2})],
            'translation': [('translate', {'tx': 20, 'ty': 15})],
            'cropping_light': [('crop', {'crop_ratio': 0.9})],
            'cropping_medium': [('crop', {'crop_ratio': 0.75})],
            'cropping_heavy': [('crop', {'crop_ratio': 0.5})],
            'flip_horizontal': [('flip_horizontal', {})],
            'flip_vertical': [('flip_vertical', {})],
            
            # 信号处理攻击
            'noise_light': [('gaussian_noise', {'std': 10})],
            'noise_medium': [('gaussian_noise', {'std': 25})],
            'noise_heavy': [('gaussian_noise', {'std': 50})],
            'blur_light': [('gaussian_blur', {'sigma': 1.0})],
            'blur_medium': [('gaussian_blur', {'sigma': 2.0})],
            'blur_heavy': [('gaussian_blur', {'sigma': 3.0})],
            'jpeg_high': [('jpeg_compression', {'quality': 85})],
            'jpeg_medium': [('jpeg_compression', {'quality': 50})],
            'jpeg_low': [('jpeg_compression', {'quality': 20})],
            'brightness_up': [('brightness', {'brightness': 30})],
            'brightness_down': [('brightness', {'brightness': -30})],
            'contrast_up': [('contrast', {'contrast': 1.5})],
            'contrast_down': [('contrast', {'contrast': 0.7})],
            'salt_pepper': [('salt_pepper_noise', {'salt_prob': 0.05, 'pepper_prob': 0.05})],
            
            # 组合攻击
            'combo_light': [
                ('gaussian_noise', {'std': 15}),
                ('gaussian_blur', {'sigma': 1.0})
            ],
            'combo_medium': [
                ('rotate', {'angle': 10}),
                ('scale', {'scale_factor': 0.9}),
                ('jpeg_compression', {'quality': 60})
            ],
            'combo_heavy': [
                ('gaussian_noise', {'std': 20}),
                ('rotate', {'angle': 15}),
                ('crop', {'crop_ratio': 0.8}),
                ('jpeg_compression', {'quality': 40})
            ]
        }
    
    def create_test_images(self) -> Dict[str, np.ndarray]:
        """创建测试图像"""
        test_images = {}
        
        # 标准测试图像
        sizes = [(256, 256), (512, 512)]
        patterns = ['lena', 'baboon', 'peppers', 'checkerboard']
        
        for size in sizes:
            for pattern in patterns:
                try:
                    image = ImageLoader.create_test_image(size, pattern)
                    key = f"{pattern}_{size[0]}x{size[1]}"
                    test_images[key] = image
                    
                    # 保存测试图像
                    output_path = self.output_dir / 'test_images' / f"{key}.png"
                    output_path.parent.mkdir(exist_ok=True)
                    cv2.imwrite(str(output_path), image)
                    
                except Exception as e:
                    self.logger.warning(f"创建测试图像 {pattern} 失败: {e}")
        
        self.logger.info(f"创建了 {len(test_images)} 个测试图像")
        return test_images
    
    def create_test_watermarks(self) -> Dict[str, np.ndarray]:
        """创建测试水印"""
        test_watermarks = {}
        
        sizes = [(32, 32), (64, 64)]
        patterns = ['logo', 'text', 'random_binary']
        
        for size in sizes:
            for pattern in patterns:
                try:
                    watermark = ImageLoader.create_test_watermark(size, pattern)
                    key = f"{pattern}_{size[0]}x{size[1]}"
                    test_watermarks[key] = watermark
                    
                    # 保存测试水印
                    output_path = self.output_dir / 'test_watermarks' / f"{key}.png"
                    output_path.parent.mkdir(exist_ok=True)
                    cv2.imwrite(str(output_path), watermark)
                    
                except Exception as e:
                    self.logger.warning(f"创建测试水印 {pattern} 失败: {e}")
        
        self.logger.info(f"创建了 {len(test_watermarks)} 个测试水印")
        return test_watermarks
    
    def test_algorithm_robustness(self, algorithm_name: str, 
                                 host_image: np.ndarray,
                                 watermark: np.ndarray,
                                 test_name: str) -> Dict:
        """测试单个算法的鲁棒性"""
        self.logger.info(f"测试算法 {algorithm_name} 的鲁棒性 - {test_name}")
        
        results = {
            'algorithm': algorithm_name,
            'test_name': test_name,
            'attacks': {},
            'summary': {}
        }
        
        try:
            # 获取算法实例
            algorithm = self.algorithm_registry.get_algorithm(algorithm_name)
            
            # 嵌入水印
            watermarked_image = algorithm.embed(host_image, watermark, strength=0.1)
            
            # 保存原始水印图像
            original_path = self.output_dir / 'results' / test_name / algorithm_name / 'original_watermarked.png'
            original_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(original_path), watermarked_image)
            
            # 获取攻击配置
            attack_configs = self.get_test_attack_configs()
            
            # 收集所有指标
            all_ber_values = []
            all_nc_values = []
            all_psnr_values = []
            all_ssim_values = []
            
            # 测试每种攻击
            for attack_name, attack_sequence in attack_configs.items():
                try:
                    self.logger.info(f"  测试攻击: {attack_name}")
                    
                    # 执行攻击
                    if attack_name.startswith(('geo_', 'sp_')):
                        attacked_image = self.attack_engine.apply_attack_by_name(
                            watermarked_image, attack_name)
                    else:
                        # 使用自定义攻击序列
                        if 'geo_' in attack_name or any(x[0] in ['rotate', 'scale', 'translate', 'crop', 'flip_horizontal', 'flip_vertical'] for x in attack_sequence):
                            attacked_image = self.attack_engine.geometric.apply_multiple_attacks(
                                watermarked_image, attack_sequence)
                        else:
                            attacked_image = self.attack_engine.signal_processing.apply_multiple_attacks(
                                watermarked_image, attack_sequence)
                    
                    # 保存攻击后的图像
                    attack_path = original_path.parent / f'attacked_{attack_name}.png'
                    cv2.imwrite(str(attack_path), attacked_image)
                    
                    # 提取水印
                    if algorithm_name == 'dct':
                        # DCT算法使用非盲提取
                        extracted_watermark = algorithm.extract_non_blind(
                            attacked_image, host_image, watermark.shape[:2])
                    else:
                        # LSB算法使用盲提取
                        extracted_watermark = algorithm.extract(
                            attacked_image, watermark.shape[:2])
                    
                    # 保存提取的水印
                    extracted_path = original_path.parent / f'extracted_{attack_name}.png'
                    cv2.imwrite(str(extracted_path), extracted_watermark)
                    
                    # 评估图像质量
                    image_metrics = self.evaluation_engine.image_quality.compute_all_metrics(
                        watermarked_image, attacked_image)
                    
                    # 评估水印鲁棒性
                    # 转换为灰度图像进行水印评估
                    if len(watermark.shape) == 3:
                        watermark_gray = cv2.cvtColor(watermark, cv2.COLOR_BGR2GRAY)
                    else:
                        watermark_gray = watermark
                    
                    if len(extracted_watermark.shape) == 3:
                        extracted_gray = cv2.cvtColor(extracted_watermark, cv2.COLOR_BGR2GRAY)
                    else:
                        extracted_gray = extracted_watermark
                    
                    watermark_metrics = self.evaluation_engine.watermark_robustness.compute_watermark_metrics(
                        watermark_gray, extracted_gray)
                    
                    # 记录结果
                    attack_result = {
                        'image_quality': image_metrics,
                        'watermark_robustness': watermark_metrics,
                        'paths': {
                            'attacked_image': str(attack_path),
                            'extracted_watermark': str(extracted_path)
                        }
                    }
                    
                    results['attacks'][attack_name] = attack_result
                    
                    # 收集统计数据
                    all_ber_values.append(watermark_metrics['ber'])
                    all_nc_values.append(watermark_metrics['nc'])
                    all_psnr_values.append(image_metrics['psnr'])
                    all_ssim_values.append(image_metrics['ssim'])
                    
                except Exception as e:
                    self.logger.error(f"    攻击 {attack_name} 测试失败: {e}")
                    results['attacks'][attack_name] = {'error': str(e)}
            
            # 计算统计摘要
            if all_ber_values:
                results['summary'] = {
                    'total_attacks': len(attack_configs),
                    'successful_attacks': len(all_ber_values),
                    'average_ber': np.mean(all_ber_values),
                    'average_nc': np.mean(all_nc_values),
                    'average_psnr': np.mean(all_psnr_values),
                    'average_ssim': np.mean(all_ssim_values),
                    'worst_ber': np.max(all_ber_values),
                    'best_ber': np.min(all_ber_values),
                    'worst_nc': np.min(all_nc_values),
                    'best_nc': np.max(all_nc_values),
                    'robustness_score': self.evaluation_engine.watermark_robustness.robustness_score(
                        all_ber_values, all_nc_values)
                }
            
        except Exception as e:
            self.logger.error(f"算法 {algorithm_name} 测试失败: {e}")
            results['error'] = str(e)
        
        return results
    
    def run_comprehensive_test(self, algorithms: List[str] = None,
                              image_subset: List[str] = None) -> Dict:
        """运行综合测试"""
        if algorithms is None:
            algorithms = ['lsb', 'dct']
        
        self.logger.info("开始综合鲁棒性测试")
        
        # 创建测试数据
        test_images = self.create_test_images()
        test_watermarks = self.create_test_watermarks()
        
        # 选择测试子集
        if image_subset:
            test_images = {k: v for k, v in test_images.items() if k in image_subset}
        
        comprehensive_results = {
            'test_config': {
                'algorithms': algorithms,
                'test_images': list(test_images.keys()),
                'test_watermarks': list(test_watermarks.keys()),
                'attack_count': len(self.get_test_attack_configs())
            },
            'results': {}
        }
        
        # 对每个算法和每个图像组合进行测试
        for algorithm_name in algorithms:
            self.logger.info(f"测试算法: {algorithm_name}")
            algorithm_results = {}
            
            for img_name, host_image in test_images.items():
                for wm_name, watermark in test_watermarks.items():
                    # 确保尺寸兼容性
                    if watermark.shape[0] > host_image.shape[0] // 4 or watermark.shape[1] > host_image.shape[1] // 4:
                        continue  # 跳过过大的水印
                    
                    test_name = f"{img_name}__{wm_name}"
                    
                    try:
                        result = self.test_algorithm_robustness(
                            algorithm_name, host_image, watermark, test_name)
                        algorithm_results[test_name] = result
                        
                    except Exception as e:
                        self.logger.error(f"测试组合 {test_name} 失败: {e}")
                        algorithm_results[test_name] = {'error': str(e)}
            
            comprehensive_results['results'][algorithm_name] = algorithm_results
        
        # 保存结果
        results_file = self.output_dir / 'comprehensive_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"综合测试完成，结果保存到: {results_file}")
        return comprehensive_results
    
    def generate_summary_report(self, results: Dict) -> str:
        """生成摘要报告"""
        report_lines = []
        report_lines.append("=== 数字水印鲁棒性测试报告 ===\n")
        
        # 测试配置
        config = results['test_config']
        report_lines.append(f"测试算法: {', '.join(config['algorithms'])}")
        report_lines.append(f"测试图像: {len(config['test_images'])} 个")
        report_lines.append(f"测试水印: {len(config['test_watermarks'])} 个")
        report_lines.append(f"攻击类型: {config['attack_count']} 种\n")
        
        # 算法性能对比
        report_lines.append("=== 算法性能对比 ===")
        
        for algorithm_name, algorithm_results in results['results'].items():
            report_lines.append(f"\n{algorithm_name.upper()} 算法:")
            
            # 收集所有有效的摘要数据
            summaries = []
            for test_name, test_result in algorithm_results.items():
                if 'summary' in test_result and test_result['summary']:
                    summaries.append(test_result['summary'])
            
            if summaries:
                # 计算平均性能
                avg_ber = np.mean([s['average_ber'] for s in summaries])
                avg_nc = np.mean([s['average_nc'] for s in summaries])
                avg_psnr = np.mean([s['average_psnr'] for s in summaries])
                avg_ssim = np.mean([s['average_ssim'] for s in summaries])
                avg_robustness = np.mean([s['robustness_score'] for s in summaries])
                
                report_lines.append(f"  平均 BER: {avg_ber:.4f}")
                report_lines.append(f"  平均 NC: {avg_nc:.4f}")
                report_lines.append(f"  平均 PSNR: {avg_psnr:.2f} dB")
                report_lines.append(f"  平均 SSIM: {avg_ssim:.4f}")
                report_lines.append(f"  鲁棒性分数: {avg_robustness:.4f}")
            else:
                report_lines.append("  无有效测试结果")
        
        # 保存报告
        report_content = "\n".join(report_lines)
        report_file = self.output_dir / 'summary_report.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"摘要报告保存到: {report_file}")
        return report_content


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数字水印鲁棒性测试套件')
    parser.add_argument('-o', '--output', default='test_results',
                       help='结果输出目录')
    parser.add_argument('-a', '--algorithms', nargs='+', 
                       choices=['lsb', 'dct'], default=['lsb', 'dct'],
                       help='要测试的算法')
    parser.add_argument('-q', '--quick', action='store_true',
                       help='快速测试模式（减少测试用例）')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出')
    
    args = parser.parse_args()
    
    # 创建测试套件
    test_suite = RobustnessTestSuite(args.output)
    
    # 设置日志级别
    if args.verbose:
        test_suite.logger.setLevel(logging.DEBUG)
    
    # 选择测试图像子集（快速模式）
    image_subset = None
    if args.quick:
        image_subset = ['lena_256x256', 'baboon_256x256']
    
    try:
        # 运行综合测试
        print("开始鲁棒性测试...")
        results = test_suite.run_comprehensive_test(
            algorithms=args.algorithms,
            image_subset=image_subset
        )
        
        # 生成摘要报告
        print("生成摘要报告...")
        summary = test_suite.generate_summary_report(results)
        
        print("\n测试完成！")
        print(f"详细结果: {test_suite.output_dir / 'comprehensive_results.json'}")
        print(f"摘要报告: {test_suite.output_dir / 'summary_report.txt'}")
        
        # 显示摘要
        print("\n" + "="*50)
        print(summary)
        
    except Exception as e:
        print(f"测试失败: {e}")
        logging.exception("测试过程中发生错误")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
