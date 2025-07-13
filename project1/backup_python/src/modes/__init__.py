"""
SM4加密模式模块

支持多种SM4加密模式:
- ECB (Electronic Codebook)
- CBC (Cipher Block Chaining) 
- CTR (Counter Mode)
- CFB (Cipher Feedback)
- OFB (Output Feedback)
"""

from .sm4_modes import SM4Modes

__all__ = ['SM4Modes']
