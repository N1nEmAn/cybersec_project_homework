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

## 项目结构

```
project5/
├── README.md           # 项目文档
├── requirements.txt    # 依赖包列表
└── src/
    └── sm2_basic.py   # SM2算法实现
```

## 算法说明

### SM2椭圆曲线参数

本实现使用GM/T 0003.2-2012标准推荐的椭圆曲线参数：

- **椭圆曲线方程**: y² = x³ + ax + b (mod p)
- **素数p**: FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
- **参数a**: FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC  
- **参数b**: 28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
- **基点G**: (32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7, BC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0)
- **阶n**: FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B61C6823781B4B10E0B3BCF0
- **余因子h**: 1

### 核心算法

#### 1. 椭圆曲线点运算
- **点加法**: P + Q = R (椭圆曲线上两点相加)
- **点倍乘**: 2P (椭圆曲线上点的倍乘)
- **标量乘法**: kP (使用二进制展开法高效计算)

#### 2. 密钥生成
1. 随机生成私钥 d ∈ [1, n-1]
2. 计算公钥 P = dG

#### 3. 数字签名
输入: 消息 M, 私钥 d
1. 计算消息摘要 e = Hash(M)
2. 随机选择 k ∈ [1, n-1]
3. 计算 (x₁, y₁) = kG
4. 计算 r = (e + x₁) mod n
5. 计算 s = (1 + d)⁻¹(k - rd) mod n
6. 输出签名 (r, s)

#### 4. 签名验证
输入: 消息 M, 签名 (r, s), 公钥 P
1. 计算消息摘要 e = Hash(M)
2. 计算 t = (r + s) mod n
3. 计算 (x₁, y₁) = sG + tP
4. 计算 R = (e + x₁) mod n
5. 验证 R = r

## 数学原理

### 椭圆曲线离散对数问题(ECDLP)

SM2算法的安全性基于椭圆曲线离散对数问题的困难性：
给定椭圆曲线上的点P和Q，找到整数k使得Q = kP在计算上是困难的。

### 有限域运算

所有运算都在有限域 GF(p) 上进行，其中 p 是大素数。
- 模加法: (a + b) mod p
- 模乘法: (a × b) mod p  
- 模逆: a⁻¹ mod p (使用扩展欧几里得算法)

## 性能特点

- **高效点运算**: 使用雅可比坐标系减少模逆运算
- **快速标量乘法**: 二进制展开法，时间复杂度 O(log k)
- **安全随机数**: 使用系统安全随机数生成器

## 安全考虑

1. **侧信道攻击防护**: 使用固定时间算法
2. **随机数质量**: 关键操作使用加密安全的随机数
3. **参数验证**: 严格验证输入参数的有效性

## 兼容性

- Python 3.7+
- 符合 GM/T 0003.2-2012 国家标准
- 支持标准测试向量验证

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题，请提交 Issue 或 Pull Request。
