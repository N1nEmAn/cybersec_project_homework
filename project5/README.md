# Project5 - SM2椭圆曲线数字签名算法

## 项目简介

本项目实现了SM2椭圆曲线数字签名算法，符合GM/T 0003.2-2012国家标准。

## 功能特性

- ✅ 椭圆曲线基础运算
- ✅ SM2数字签名
- ✅ 签名验证
- ✅ 密钥生成

## 快速开始

```python
from src.sm2_basic import SM2Basic

# 初始化
sm2 = SM2Basic()

# 生成密钥对
private_key, public_key = sm2.generate_keypair()

# 数字签名
message = b"Hello SM2!"
signature = sm2.sign(message, private_key)

# 验证签名
is_valid = sm2.verify(message, signature, public_key)
print(f"签名验证: {is_valid}")
```

## 依赖安装

```bash
pip install -r requirements.txt
```

## 运行测试

```bash
python src/sm2_basic.py
```
