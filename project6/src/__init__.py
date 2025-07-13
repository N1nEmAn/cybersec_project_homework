"""
基于DDH的私有交集和协议实现

该模块提供了完整的DDH-PSI协议实现，包括：
- 椭圆曲线群操作
- Paillier同态加密
- 协议核心逻辑
- 安全性保证
"""

__version__ = "1.0.0"
__author__ = "DDH-PSI Protocol Implementation"

from .ddh_psi import DDHPSIParty1, DDHPSIParty2
from .crypto_utils import hash_to_curve, secure_random
from .elliptic_curve import EllipticCurveGroup
from .paillier_encryption import PaillierEncryption

__all__ = [
    "DDHPSIParty1",
    "DDHPSIParty2", 
    "EllipticCurveGroup",
    "PaillierEncryption",
    "hash_to_curve",
    "secure_random",
]
