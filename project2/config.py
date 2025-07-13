"""
项目配置文件
用于设置水印系统的默认参数和配置选项
"""

# 水印算法配置
ALGORITHMS = {
    'lsb': {
        'name': 'LSB水印算法',
        'strength_range': (0.01, 0.5),
        'default_strength': 0.1,
        'supports_blind_extraction': True
    },
    'dct': {
        'name': 'DCT水印算法', 
        'strength_range': (0.05, 1.0),
        'default_strength': 0.2,
        'supports_blind_extraction': False
    }
}

# 攻击测试配置
ATTACK_CONFIGS = {
    'noise_levels': [5, 10, 15, 20, 25],
    'rotation_angles': [1, 2, 5, 10, 15],
    'scaling_factors': [0.8, 0.9, 1.1, 1.2],
    'jpeg_qualities': [50, 60, 70, 80, 90]
}

# 评估指标阈值
QUALITY_THRESHOLDS = {
    'psnr': {
        'excellent': 40,
        'good': 30,
        'acceptable': 25
    },
    'ssim': {
        'excellent': 0.98,
        'good': 0.90,
        'acceptable': 0.80
    }
}

# 默认参数
DEFAULT_WATERMARK_SIZE = (64, 64)
DEFAULT_BLOCK_SIZE = 8
DEFAULT_OUTPUT_FORMAT = 'png'
LOG_LEVEL = 'INFO'
