"""
攻击模块初始化
"""

from .geometric_attacks import GeometricAttacks
from .signal_processing_attacks import SignalProcessingAttacks

__all__ = [
    'GeometricAttacks',
    'SignalProcessingAttacks'
]


class AttackEngine:
    """攻击引擎，统一管理各种攻击"""
    
    def __init__(self):
        self.geometric = GeometricAttacks()
        self.signal_processing = SignalProcessingAttacks()
    
    def get_all_attack_configs(self):
        """获取所有攻击配置"""
        configs = {}
        configs.update({f"geo_{k}": v for k, v in self.geometric.get_common_attack_configs().items()})
        configs.update({f"sp_{k}": v for k, v in self.signal_processing.get_common_attack_configs().items()})
        return configs
    
    def apply_attack_by_name(self, image, attack_name, **params):
        """根据名称应用攻击"""
        if attack_name.startswith('geo_'):
            config_name = attack_name[4:]  # 移除 'geo_' 前缀
            configs = self.geometric.get_common_attack_configs()
            if config_name in configs:
                return self.geometric.apply_multiple_attacks(image, configs[config_name])
        elif attack_name.startswith('sp_'):
            config_name = attack_name[3:]  # 移除 'sp_' 前缀
            configs = self.signal_processing.get_common_attack_configs()
            if config_name in configs:
                return self.signal_processing.apply_multiple_attacks(image, configs[config_name])
        
        # 如果不是预定义配置，尝试直接调用方法
        if hasattr(self.geometric, attack_name):
            return getattr(self.geometric, attack_name)(image, **params)
        elif hasattr(self.signal_processing, attack_name):
            return getattr(self.signal_processing, attack_name)(image, **params)
        
        raise ValueError(f"未知的攻击类型: {attack_name}")
