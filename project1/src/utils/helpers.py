"""
SM4算法辅助函数
包含位运算、字节操作等通用函数
"""

def bytes_to_int_list(data):
    """将字节数组转换为32位整数列表"""
    if len(data) % 4 != 0:
        raise ValueError("数据长度必须是4的倍数")
    
    result = []
    for i in range(0, len(data), 4):
        # 大端序转换
        value = (data[i] << 24) | (data[i+1] << 16) | (data[i+2] << 8) | data[i+3]
        result.append(value)
    return result

def int_list_to_bytes(int_list):
    """将32位整数列表转换为字节数组"""
    result = bytearray()
    for value in int_list:
        # 大端序转换
        result.extend([
            (value >> 24) & 0xff,
            (value >> 16) & 0xff,
            (value >> 8) & 0xff,
            value & 0xff
        ])
    return bytes(result)

def rotl(value, bits):
    """32位左循环移位"""
    value &= 0xffffffff
    return ((value << bits) | (value >> (32 - bits))) & 0xffffffff

def get_byte(value, index):
    """获取32位整数的指定字节 (0=最高字节, 3=最低字节)"""
    return (value >> (24 - 8 * index)) & 0xff

def set_byte(value, index, byte_val):
    """设置32位整数的指定字节"""
    mask = 0xff << (24 - 8 * index)
    value &= ~mask
    value |= (byte_val & 0xff) << (24 - 8 * index)
    return value & 0xffffffff

def xor_bytes(a, b):
    """字节数组异或运算"""
    if len(a) != len(b):
        raise ValueError("两个字节数组长度必须相同")
    return bytes(x ^ y for x, y in zip(a, b))

def format_hex(data, group_size=16):
    """格式化输出十六进制数据，便于调试"""
    if isinstance(data, int):
        return f"0x{data:08x}"
    elif isinstance(data, (bytes, bytearray)):
        hex_str = data.hex()
        if group_size > 0:
            groups = [hex_str[i:i+group_size*2] for i in range(0, len(hex_str), group_size*2)]
            return ' '.join(groups)
        return hex_str
    elif isinstance(data, list):
        return [format_hex(item, 0) for item in data]
    else:
        return str(data)

def validate_key(key):
    """验证密钥格式和长度"""
    if not isinstance(key, (bytes, bytearray)):
        raise TypeError("密钥必须是bytes或bytearray类型")
    if len(key) != 16:
        raise ValueError(f"密钥长度必须是16字节，当前长度: {len(key)}")

def validate_data(data):
    """验证数据格式和长度"""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("数据必须是bytes或bytearray类型")
    if len(data) % 16 != 0:
        raise ValueError(f"数据长度必须是16字节的倍数，当前长度: {len(data)}")

def pad_pkcs7(data, block_size=16):
    """PKCS#7填充"""
    padding_len = block_size - (len(data) % block_size)
    padding = bytes([padding_len] * padding_len)
    return data + padding

def unpad_pkcs7(data, block_size=16):
    """移除PKCS#7填充"""
    if len(data) == 0 or len(data) % block_size != 0:
        raise ValueError("数据长度无效")
    
    padding_len = data[-1]
    if padding_len == 0 or padding_len > block_size:
        raise ValueError("填充无效")
    
    # 验证填充的正确性
    for i in range(padding_len):
        if data[-(i+1)] != padding_len:
            raise ValueError("填充格式错误")
    
    return data[:-padding_len]
