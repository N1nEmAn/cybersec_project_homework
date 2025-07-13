"""
水印算法包
包含多种数字水印算法的实现
"""

from .lsb_watermark import LSBWatermark
from .dct_watermark import DCTWatermark

__all__ = [
    'LSBWatermark',
    'DCTWatermark',
    'AlgorithmRegistry'
]

# 算法注册表
ALGORITHMS = {
    'lsb': LSBWatermark,
    'dct': DCTWatermark,
}


class AlgorithmRegistry:
    """算法注册表类，用于管理和获取算法实例"""
    
    def __init__(self):
        self.algorithms = ALGORITHMS.copy()
    
    def get_algorithm(self, name: str, **kwargs):
        """
        根据名称获取水印算法实例
        
        Args:
            name: 算法名称 ('lsb', 'dct', 'dwt', 'svd')
            **kwargs: 算法参数
            
        Returns:
            算法实例
        """
        if name.lower() not in self.algorithms:
            raise ValueError(f"未知算法: {name}. 支持的算法: {list(self.algorithms.keys())}")
        
        algorithm_class = self.algorithms[name.lower()]
        return algorithm_class(**kwargs)
    
    def list_algorithms(self):
        """列出所有可用的算法"""
        return list(self.algorithms.keys())
    
    def register_algorithm(self, name: str, algorithm_class):
        """注册新算法"""
        self.algorithms[name.lower()] = algorithm_class


def get_algorithm(name: str, **kwargs):
    """
    根据名称获取水印算法实例
    
    Args:
        name: 算法名称 ('lsb', 'dct', 'dwt', 'svd')
        **kwargs: 算法参数
        
    Returns:
        算法实例
    """
    if name.lower() not in ALGORITHMS:
        raise ValueError(f"未知算法: {name}. 支持的算法: {list(ALGORITHMS.keys())}")
    
    algorithm_class = ALGORITHMS[name.lower()]
    return algorithm_class(**kwargs)

def list_algorithms():
    """列出所有可用的算法"""
    return list(ALGORITHMS.keys())
