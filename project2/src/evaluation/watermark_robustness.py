"""
水印鲁棒性评估模块
实现水印检测指标：BER、NC、检测率等
"""

import numpy as np
from typing import Tuple, Union, Optional, Dict, List
import logging
from sklearn.metrics import confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class WatermarkRobustnessMetrics:
    """水印鲁棒性评估指标类"""
    
    def __init__(self):
        self.logger = logger
    
    def bit_error_rate(self, original_watermark: np.ndarray, 
                      extracted_watermark: np.ndarray) -> float:
        """
        计算比特错误率 (Bit Error Rate, BER)
        
        数学公式：
        BER = (错误比特数) / (总比特数)
        
        Args:
            original_watermark: 原始水印
            extracted_watermark: 提取的水印
            
        Returns:
            BER值（0-1之间，0表示完全正确）
        """
        if original_watermark.shape != extracted_watermark.shape:
            raise ValueError("水印尺寸不匹配")
        
        # 二值化处理
        orig_binary = (original_watermark > 0.5).astype(np.uint8)
        extr_binary = (extracted_watermark > 0.5).astype(np.uint8)
        
        # 计算错误比特数
        error_bits = np.sum(orig_binary != extr_binary)
        total_bits = orig_binary.size
        
        ber = error_bits / total_bits
        
        self.logger.info(f"BER计算完成: {ber:.4f} ({error_bits}/{total_bits})")
        return ber
    
    def normalized_correlation(self, original_watermark: np.ndarray,
                             extracted_watermark: np.ndarray) -> float:
        """
        计算归一化相关度 (Normalized Correlation, NC)
        
        数学公式：
        NC = Σ(W(i,j) × W'(i,j)) / Σ(W(i,j)²)
        其中 W 是原始水印，W' 是提取的水印
        
        Args:
            original_watermark: 原始水印
            extracted_watermark: 提取的水印
            
        Returns:
            NC值（通常在0-1之间，1表示完全相关）
        """
        if original_watermark.shape != extracted_watermark.shape:
            raise ValueError("水印尺寸不匹配")
        
        # 转换为浮点型并展平
        orig_flat = original_watermark.astype(np.float64).flatten()
        extr_flat = extracted_watermark.astype(np.float64).flatten()
        
        # 计算归一化相关度
        numerator = np.sum(orig_flat * extr_flat)
        denominator = np.sum(orig_flat ** 2)
        
        if denominator == 0:
            return 0.0
        
        nc = numerator / denominator
        
        self.logger.info(f"NC计算完成: {nc:.4f}")
        return nc
    
    def peak_signal_noise_ratio_watermark(self, original_watermark: np.ndarray,
                                        extracted_watermark: np.ndarray,
                                        max_value: float = 1.0) -> float:
        """
        计算水印的峰值信噪比
        
        Args:
            original_watermark: 原始水印
            extracted_watermark: 提取的水印
            max_value: 水印的最大值
            
        Returns:
            PSNR值（dB）
        """
        if original_watermark.shape != extracted_watermark.shape:
            raise ValueError("水印尺寸不匹配")
        
        # 计算MSE
        mse = np.mean((original_watermark.astype(np.float64) - 
                      extracted_watermark.astype(np.float64)) ** 2)
        
        if mse == 0:
            return float('inf')
        
        psnr = 10 * np.log10((max_value ** 2) / mse)
        
        self.logger.info(f"水印PSNR计算完成: {psnr:.4f} dB")
        return psnr
    
    def detection_rate(self, detection_results: List[bool]) -> float:
        """
        计算检测率
        
        Args:
            detection_results: 检测结果列表（True表示检测到水印）
            
        Returns:
            检测率（0-1之间）
        """
        if not detection_results:
            return 0.0
        
        detection_count = sum(detection_results)
        total_count = len(detection_results)
        
        rate = detection_count / total_count
        
        self.logger.info(f"检测率计算完成: {rate:.4f} ({detection_count}/{total_count})")
        return rate
    
    def false_positive_rate(self, detection_results: List[bool],
                           ground_truth: List[bool]) -> float:
        """
        计算误检率（False Positive Rate）
        
        Args:
            detection_results: 检测结果列表
            ground_truth: 真实标签列表（True表示确实有水印）
            
        Returns:
            误检率
        """
        if len(detection_results) != len(ground_truth):
            raise ValueError("检测结果和真实标签长度不匹配")
        
        # 计算混淆矩阵
        tn, fp, fn, tp = confusion_matrix(ground_truth, detection_results).ravel()
        
        # 计算误检率
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        
        self.logger.info(f"误检率计算完成: {fpr:.4f}")
        return fpr
    
    def false_negative_rate(self, detection_results: List[bool],
                           ground_truth: List[bool]) -> float:
        """
        计算漏检率（False Negative Rate）
        
        Args:
            detection_results: 检测结果列表
            ground_truth: 真实标签列表
            
        Returns:
            漏检率
        """
        if len(detection_results) != len(ground_truth):
            raise ValueError("检测结果和真实标签长度不匹配")
        
        # 计算混淆矩阵
        tn, fp, fn, tp = confusion_matrix(ground_truth, detection_results).ravel()
        
        # 计算漏检率
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
        
        self.logger.info(f"漏检率计算完成: {fnr:.4f}")
        return fnr
    
    def accuracy(self, detection_results: List[bool],
                ground_truth: List[bool]) -> float:
        """
        计算准确率
        
        Args:
            detection_results: 检测结果列表
            ground_truth: 真实标签列表
            
        Returns:
            准确率
        """
        if len(detection_results) != len(ground_truth):
            raise ValueError("检测结果和真实标签长度不匹配")
        
        correct = sum(dr == gt for dr, gt in zip(detection_results, ground_truth))
        total = len(detection_results)
        
        acc = correct / total if total > 0 else 0.0
        
        self.logger.info(f"准确率计算完成: {acc:.4f}")
        return acc
    
    def precision_recall_f1(self, detection_results: List[bool],
                           ground_truth: List[bool]) -> Tuple[float, float, float]:
        """
        计算精确率、召回率和F1分数
        
        Args:
            detection_results: 检测结果列表
            ground_truth: 真实标签列表
            
        Returns:
            (精确率, 召回率, F1分数)
        """
        if len(detection_results) != len(ground_truth):
            raise ValueError("检测结果和真实标签长度不匹配")
        
        # 计算混淆矩阵
        tn, fp, fn, tp = confusion_matrix(ground_truth, detection_results).ravel()
        
        # 计算精确率
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        
        # 计算召回率
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        # 计算F1分数
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        self.logger.info(f"精确率: {precision:.4f}, 召回率: {recall:.4f}, F1分数: {f1:.4f}")
        return precision, recall, f1
    
    def robustness_score(self, ber_values: List[float], 
                        nc_values: List[float],
                        weights: Tuple[float, float] = (0.5, 0.5)) -> float:
        """
        计算综合鲁棒性分数
        
        Args:
            ber_values: BER值列表
            nc_values: NC值列表
            weights: BER和NC的权重
            
        Returns:
            鲁棒性分数（0-1之间，1表示最佳）
        """
        if len(ber_values) != len(nc_values):
            raise ValueError("BER和NC值列表长度不匹配")
        
        if len(ber_values) == 0:
            return 0.0
        
        # 计算平均值
        avg_ber = np.mean(ber_values)
        avg_nc = np.mean(nc_values)
        
        # 转换为0-1分数（BER越小越好，NC越大越好）
        ber_score = 1.0 - avg_ber  # BER转换为分数
        nc_score = avg_nc          # NC本身就是分数
        
        # 加权计算
        robustness = weights[0] * ber_score + weights[1] * nc_score
        
        self.logger.info(f"鲁棒性分数计算完成: {robustness:.4f}")
        return robustness
    
    def attack_resistance_analysis(self, attack_results: Dict[str, Dict]) -> Dict:
        """
        攻击抗性分析
        
        Args:
            attack_results: 攻击结果字典，格式为 {攻击名称: {指标名称: 值}}
            
        Returns:
            分析结果字典
        """
        analysis = {
            'strongest_attacks': [],  # 最强攻击
            'weakest_attacks': [],    # 最弱攻击
            'average_performance': {} # 平均性能
        }
        
        # 收集所有指标
        all_metrics = {}
        for attack_name, metrics in attack_results.items():
            for metric_name, value in metrics.items():
                if metric_name not in all_metrics:
                    all_metrics[metric_name] = []
                all_metrics[metric_name].append((attack_name, value))
        
        # 分析每个指标
        for metric_name, values in all_metrics.items():
            # 计算平均值
            avg_value = np.mean([v[1] for v in values])
            analysis['average_performance'][metric_name] = avg_value
            
            # 排序找出最强和最弱的攻击
            if metric_name in ['ber']:  # 对于BER，值越大表示攻击越强
                sorted_values = sorted(values, key=lambda x: x[1], reverse=True)
            else:  # 对于NC等，值越小表示攻击越强
                sorted_values = sorted(values, key=lambda x: x[1])
            
            # 记录最强的3个攻击
            strongest = [attack for attack, _ in sorted_values[:3]]
            if metric_name not in [item[0] for item in analysis['strongest_attacks']]:
                analysis['strongest_attacks'].append((metric_name, strongest))
            
            # 记录最弱的3个攻击
            weakest = [attack for attack, _ in sorted_values[-3:]]
            if metric_name not in [item[0] for item in analysis['weakest_attacks']]:
                analysis['weakest_attacks'].append((metric_name, weakest))
        
        self.logger.info("攻击抗性分析完成")
        return analysis
    
    def compute_watermark_metrics(self, original_watermark: np.ndarray,
                                extracted_watermark: np.ndarray) -> Dict:
        """
        计算所有水印相关指标
        
        Args:
            original_watermark: 原始水印
            extracted_watermark: 提取的水印
            
        Returns:
            包含所有指标的字典
        """
        metrics = {}
        
        try:
            metrics['ber'] = self.bit_error_rate(original_watermark, extracted_watermark)
            metrics['nc'] = self.normalized_correlation(original_watermark, extracted_watermark)
            metrics['psnr_watermark'] = self.peak_signal_noise_ratio_watermark(
                original_watermark, extracted_watermark)
        except Exception as e:
            self.logger.error(f"计算水印指标时出错: {e}")
            raise
        
        self.logger.info("所有水印指标计算完成")
        return metrics
    
    def watermark_quality_assessment(self, metrics: Dict) -> str:
        """
        基于指标进行水印质量评估
        
        Args:
            metrics: 水印指标字典
            
        Returns:
            质量评估结果
        """
        ber = metrics.get('ber', 1.0)
        nc = metrics.get('nc', 0.0)
        
        if ber <= 0.05 and nc >= 0.95:
            return "优秀"
        elif ber <= 0.1 and nc >= 0.90:
            return "良好"
        elif ber <= 0.2 and nc >= 0.80:
            return "一般"
        elif ber <= 0.3 and nc >= 0.70:
            return "较差"
        else:
            return "很差"


def demo_watermark_robustness():
    """水印鲁棒性评估演示函数"""
    # 创建模拟数据
    original_watermark = np.random.rand(32, 32) > 0.5
    
    # 模拟不同程度的攻击
    extracted_perfect = original_watermark.copy()
    extracted_light = original_watermark.copy()
    extracted_light.flat[np.random.choice(extracted_light.size, 50)] = ~extracted_light.flat[np.random.choice(extracted_light.size, 50)]
    
    extracted_heavy = original_watermark.copy()
    extracted_heavy.flat[np.random.choice(extracted_heavy.size, 200)] = ~extracted_heavy.flat[np.random.choice(extracted_heavy.size, 200)]
    
    # 初始化评估器
    robustness_metrics = WatermarkRobustnessMetrics()
    
    print("水印鲁棒性评估演示:")
    
    # 测试不同攻击程度的结果
    test_cases = [
        ("无攻击", extracted_perfect),
        ("轻度攻击", extracted_light),
        ("重度攻击", extracted_heavy)
    ]
    
    for case_name, extracted in test_cases:
        print(f"\n{case_name}:")
        metrics = robustness_metrics.compute_watermark_metrics(original_watermark, extracted)
        for metric_name, value in metrics.items():
            print(f"  {metric_name.upper()}: {value:.4f}")
        
        assessment = robustness_metrics.watermark_quality_assessment(metrics)
        print(f"  质量评估: {assessment}")


if __name__ == "__main__":
    demo_watermark_robustness()
