"""
评估模块初始化
"""

from .image_quality import ImageQualityMetrics
from .watermark_robustness import WatermarkRobustnessMetrics

__all__ = [
    'ImageQualityMetrics',
    'WatermarkRobustnessMetrics'
]


class EvaluationEngine:
    """评估引擎，统一管理所有评估指标"""
    
    def __init__(self):
        self.image_quality = ImageQualityMetrics()
        self.watermark_robustness = WatermarkRobustnessMetrics()
    
    def comprehensive_evaluation(self, original_image, watermarked_image,
                               original_watermark, extracted_watermark):
        """
        综合评估：包括图像质量和水印鲁棒性
        
        Args:
            original_image: 原始图像
            watermarked_image: 水印图像
            original_watermark: 原始水印
            extracted_watermark: 提取的水印
            
        Returns:
            综合评估结果字典
        """
        results = {
            'image_quality': {},
            'watermark_robustness': {},
            'overall_assessment': {}
        }
        
        # 图像质量评估
        try:
            results['image_quality'] = self.image_quality.compute_all_metrics(
                original_image, watermarked_image)
            results['overall_assessment']['image_quality'] = \
                self.image_quality.quality_assessment(results['image_quality'])
        except Exception as e:
            print(f"图像质量评估失败: {e}")
        
        # 水印鲁棒性评估
        try:
            results['watermark_robustness'] = \
                self.watermark_robustness.compute_watermark_metrics(
                    original_watermark, extracted_watermark)
            results['overall_assessment']['watermark_quality'] = \
                self.watermark_robustness.watermark_quality_assessment(
                    results['watermark_robustness'])
        except Exception as e:
            print(f"水印鲁棒性评估失败: {e}")
        
        return results
    
    def batch_evaluation(self, test_cases):
        """
        批量评估多个测试案例
        
        Args:
            test_cases: 测试案例列表，每个案例包含所需的图像和水印数据
            
        Returns:
            批量评估结果
        """
        batch_results = []
        
        for i, case in enumerate(test_cases):
            try:
                result = self.comprehensive_evaluation(**case)
                result['case_id'] = i
                batch_results.append(result)
            except Exception as e:
                print(f"测试案例 {i} 评估失败: {e}")
        
        return batch_results
