"""
密码学工具模块

提供协议所需的基础密码学操作：
- 安全随机数生成
- 哈希到椭圆曲线映射
- 群元素序列化/反序列化
"""

import hashlib
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec


def secure_random(byte_length: int) -> bytes:
    """
    生成密码学安全的随机字节串
    
    Args:
        byte_length: 需要的字节长度
        
    Returns:
        密码学安全的随机字节串
    """
    return secrets.token_bytes(byte_length)


def secure_random_int(bit_length: int) -> int:
    """
    生成指定位长度的安全随机整数
    
    Args:
        bit_length: 位长度
        
    Returns:
        随机整数
    """
    byte_length = (bit_length + 7) // 8
    random_bytes = secure_random(byte_length)
    return int.from_bytes(random_bytes, 'big') % (1 << bit_length)


def hash_to_curve(data: str, curve_name: str = "prime256v1") -> ec.EllipticCurvePoint:
    """
    将字符串数据哈希映射到椭圆曲线上的点
    
    这个函数实现了安全的哈希到曲线映射，基于SHA-256哈希函数
    和try-and-increment方法。
    
    Args:
        data: 要映射的字符串数据
        curve_name: 椭圆曲线名称（默认prime256v1）
        
    Returns:
        椭圆曲线上的点
    """
    if curve_name == "prime256v1":
        curve = ec.SECP256R1()
    else:
        raise ValueError(f"Unsupported curve: {curve_name}")
    
    # 使用SHA-256哈希数据
    hasher = hashlib.sha256()
    hasher.update(data.encode('utf-8'))
    
    # Try-and-increment方法寻找有效的曲线点
    counter = 0
    while counter < 256:  # 安全上界
        # 将计数器添加到哈希中
        attempt_hasher = hashlib.sha256()
        attempt_hasher.update(hasher.digest())
        attempt_hasher.update(counter.to_bytes(4, 'big'))
        hash_result = attempt_hasher.digest()
        
        try:
            # 尝试从哈希结果构造x坐标
            x = int.from_bytes(hash_result[:32], 'big')
            
            # 计算对应的y坐标（椭圆曲线方程：y² = x³ + ax + b）
            # 对于SECP256R1：y² = x³ - 3x + b
            p = curve.key_size // 8  # 字段大小
            field_prime = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
            
            x = x % field_prime
            
            # 计算右侧：x³ - 3x + b
            b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
            rhs = (pow(x, 3, field_prime) - 3 * x + b) % field_prime
            
            # 检查是否为二次剩余
            y_squared = rhs
            y = pow(y_squared, (field_prime + 1) // 4, field_prime)
            
            if pow(y, 2, field_prime) == y_squared:
                # 找到有效点，构造椭圆曲线点
                # 由于cryptography库的限制，我们返回坐标元组
                return (x, y)
                
        except Exception:
            pass
            
        counter += 1
    
    raise ValueError("无法将数据映射到椭圆曲线点")


def point_to_bytes(point: tuple) -> bytes:
    """
    将椭圆曲线点转换为字节串
    
    Args:
        point: 椭圆曲线点的坐标 (x, y)
        
    Returns:
        点的字节表示
    """
    x, y = point
    # 使用非压缩格式：0x04 || x || y
    return b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')


def bytes_to_point(data: bytes) -> tuple:
    """
    将字节串转换为椭圆曲线点
    
    Args:
        data: 点的字节表示
        
    Returns:
        椭圆曲线点的坐标 (x, y)
    """
    if len(data) != 65 or data[0] != 0x04:
        raise ValueError("无效的椭圆曲线点格式")
    
    x = int.from_bytes(data[1:33], 'big')
    y = int.from_bytes(data[33:65], 'big')
    return (x, y)


def sha256_hash(data: bytes) -> bytes:
    """
    计算SHA-256哈希值
    
    Args:
        data: 输入数据
        
    Returns:
        SHA-256哈希值
    """
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.digest()
