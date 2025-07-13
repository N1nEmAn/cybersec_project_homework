# Project6 - 基于DDH的私有交集和协议

## 项目简介

本项目实现了基于DDH（Decisional Diffie-Hellman）假设的私有交集和协议（$\Pi_{DDH}$），用于解决广告转化归因等场景中的隐私计算问题。该协议能够在保护双方私有数据的前提下，安全地计算两个数据集的交集大小及交集中关联值的总和。

协议基于经典的集合交集协议扩展而来，结合了加法同态加密实现聚合功能，具有通信效率高、实现简单等特点，适用于批量计算场景。

## 协议概述

### 问题定义

该协议解决双方私有集合求交并聚合的问题：
- **参与方**：两方（$P_1$和$P_2$）
- **输入数据**：
  - $P_1$ 持有用户标识符集合 $V = \{v_i\}_{i=1}^{m_1}$（例如，看过广告的用户ID）
  - $P_2$ 持有用户标识符与关联值的集合 $W = \{(w_j, t_j)\}_{j=1}^{m_2}$（例如，购买商品的用户ID及消费金额）
- **输出目标**：计算交集大小 $|V \cap W|$ 和交集中关联值总和 $\sum_{j: w_j \in V} t_j$

### 密码学基础

#### DDH假设（Decisional Diffie-Hellman Assumption）

设 $G$ 是素数阶 $q$ 的循环群，$g$ 是群的生成元。DDH假设声明对于随机选择的 $a, b, c \in \mathbb{Z}_q$，计算上无法区分以下两个分布：
- $(g, g^a, g^b, g^{ab})$（DDH元组）
- $(g, g^a, g^b, g^c)$（随机元组）

DDH假设的困难性保证了我们协议中双加密值 $H(x)^{k_1 k_2}$ 的安全性。

#### 加法同态加密

协议使用满足以下性质的加法同态加密方案 $(AGen, AEnc, ADec, ASum, ARefresh)$：

1. **密钥生成**：$(pk, sk) \leftarrow AGen(\lambda)$
2. **加密**：$c \leftarrow AEnc(pk, m)$
3. **解密**：$m \leftarrow ADec(sk, c)$
4. **同态加法**：$ASum(c_1, c_2) = AEnc(pk, m_1 + m_2)$，其中 $c_i = AEnc(pk, m_i)$
5. **重随机化**：$ARefresh(c)$ 产生与 $c$ 加密相同明文但随机性不同的密文

## 协议数学推导

### 协议流程数学分析

#### 第一步：初始化（Setup）
- $P_1$ 选择随机私钥 $k_1 \in \mathbb{Z}_q$
- $P_2$ 选择随机私钥 $k_2 \in \mathbb{Z}_q$
- $P_2$ 生成同态加密密钥对 $(pk, sk) \leftarrow AGen(\lambda)$

**数学基础**：选择的私钥 $k_1, k_2$ 在群 $\mathbb{Z}_q$ 中均匀分布，确保后续计算的随机性。

#### 第二步：第一轮通信（$P_1 \to P_2$）
$P_1$ 对每个 $v_i \in V$ 计算：
$$X_i = H(v_i)^{k_1}$$

其中 $H: \{0,1\}^* \to G$ 是哈希函数，建模为随机预言机。

**数学性质**：
- 哈希函数的随机预言机性质保证 $H(v_i)$ 在群 $G$ 中均匀分布
- 指数运算 $H(v_i)^{k_1}$ 保持群的结构
- 打乱顺序防止位置信息泄露

#### 第三步：第二轮通信（$P_2 \to P_1$）
$P_2$ 执行两个并行操作：

**操作1**：对收到的 $X_i$ 计算双加密值
$$Z_i = X_i^{k_2} = (H(v_i)^{k_1})^{k_2} = H(v_i)^{k_1 k_2}$$

**操作2**：对自己的数据 $(w_j, t_j)$ 计算
$$Y_j = H(w_j)^{k_2}$$
$$C_j = AEnc(pk, t_j)$$

**数学推导**：
双加密的可交换性：$H(x)^{k_1 k_2} = H(x)^{k_2 k_1}$，这是群指数运算的基本性质。

#### 第四步：第三轮通信（$P_1 \to P_2$）
$P_1$ 对收到的 $(Y_j, C_j)$ 计算：
$$Z'_j = Y_j^{k_1} = (H(w_j)^{k_2})^{k_1} = H(w_j)^{k_1 k_2}$$

**交集识别**：
$$J = \{j : Z'_j \in \{Z_i\}_{i=1}^{m_1}\}$$

这里 $j \in J$ 当且仅当 $w_j \in V$，因为：
$$Z'_j = H(w_j)^{k_1 k_2} = Z_i \Leftrightarrow H(w_j) = H(v_i) \Leftrightarrow w_j = v_i$$

**聚合计算**：
$$C_{sum} = ASum(\{C_j\}_{j \in J}) = AEnc(pk, \sum_{j \in J} t_j)$$

#### 第五步：结果输出
$P_2$ 解密得到：
$$S_J = ADec(sk, ARefresh(C_{sum})) = \sum_{j \in J} t_j$$

### 正确性证明

**定理1（协议正确性）**：如果双方诚实执行协议，则输出结果正确。

**证明**：
1. **交集识别正确性**：由于哈希函数 $H$ 是单射的（随机预言机模型），且群指数运算保持相等关系，我们有：
   $$w_j = v_i \Leftrightarrow H(w_j) = H(v_i) \Leftrightarrow H(w_j)^{k_1 k_2} = H(v_i)^{k_1 k_2}$$

2. **聚合计算正确性**：由同态加密的加法同态性质：
   $$ADec(sk, ASum(\{AEnc(pk, t_j)\}_{j \in J})) = \sum_{j \in J} t_j$$

### 安全性分析

#### 半诚实模型下的安全性

**定理2（$P_1$ 的隐私保护）**：在DDH假设和同态加密CPA安全性下，$P_1$ 的视图可被模拟，仅泄露：
- 自身输入 $V$
- $P_2$ 输入大小 $m_2$  
- 交集大小 $|J|$

**证明思路**：
- $P_1$ 收到的 $H(w_j)^{k_2}$ 在DDH假设下与随机群元素不可区分
- 同态加密的CPA安全性保证密文 $AEnc(t_j)$ 不泄露明文信息
- 重随机化确保最终密文不包含额外信息

**定理3（$P_2$ 的隐私保护）**：在DDH假设下，$P_2$ 的视图可被模拟，仅泄露：
- 自身输入 $W$
- $P_1$ 输入大小 $m_1$
- 交集和 $S_J$

**证明思路**：
- $P_2$ 收到的 $H(v_i)^{k_1}$ 在DDH假设下与随机群元素不可区分
- 打乱顺序防止位置关联

### 复杂度分析

#### 计算复杂度
- **$P_1$**：$O(m_1 + m_2)$ 次群指数运算
- **$P_2$**：$O(m_1 + m_2)$ 次群指数运算 + $m_2$ 次同态加密

#### 通信复杂度
- **第一轮**：$m_1$ 个群元素（$m_1 \times 32$ 字节）
- **第二轮**：$m_1$ 个群元素 + $m_2$ 个群元素 + $m_2$ 个密文
- **第三轮**：1个同态密文

总通信量：$O((m_1 + m_2) \times \text{群元素大小} + m_2 \times \text{密文大小})$

## 实现特性

- ✅ 基于椭圆曲线的DDH群（prime256v1）
- ✅ Paillier同态加密实现
- ✅ 安全的哈希到群映射
- ✅ 完整的协议流程实现
- ✅ 详细的性能基准测试
- ✅ 专业的数据分析图表

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 基础使用示例
```python
from src.ddh_psi import DDHPSIProtocol

# 准备数据
party1_data = ["apple", "banana", "cherry"]
party2_data = [("apple", 10), ("banana", 20), ("date", 30)]

# 运行协议
protocol = DDHPSIProtocol()
intersection_size, intersection_sum = protocol.run_protocol(party1_data, party2_data)

print(f"交集大小: {intersection_size}")  # 输出: 2  
print(f"交集总和: {intersection_sum}")    # 输出: 30 (10+20)
```

### 完整演示

运行完整功能演示：

```bash
python demo_complete.py
```

该演示脚本将展示：
- 基本使用方法
- 分步执行过程  
- 性能分析
- 错误处理
- 真实应用场景
- 配置选项
- 性能报告生成

## 项目结构

```
project6/
├── README.md                          # 项目文档
├── requirements.txt                   # 依赖包列表
├── setup.py                          # 项目安装配置
├── src/                              # 源代码目录
│   ├── __init__.py
│   ├── ddh_psi.py                    # 主协议实现
│   ├── crypto_utils.py               # 密码学工具
│   ├── elliptic_curve.py             # 椭圆曲线群操作
│   └── paillier_encryption.py       # Paillier同态加密
├── tests/                            # 测试套件
│   ├── __init__.py
│   ├── test_crypto_utils.py
│   ├── test_elliptic_curve.py
│   ├── test_paillier.py
│   └── test_ddh_psi.py
├── benchmarks/                       # 性能测试
│   ├── __init__.py
│   ├── performance_benchmark.py
│   └── scalability_test.py
├── examples/                         # 使用示例
│   ├── basic_example.py
│   ├── advertising_attribution.py
│   └── batch_processing.py
├── docs/                            # 技术文档
│   ├── protocol_specification.md
│   ├── security_analysis.md
│   └── implementation_notes.md
└── charts/                          # 性能分析图表
    ├── performance_comparison.png
    ├── scalability_analysis.png
    ├── communication_overhead.png
    └── security_overhead.png
```

## 技术亮点

- 🔐 基于DDH假设的强安全性保证
- 📊 高效的通信复杂度优化
- 🚀 支持大规模数据集处理
- 🧮 完整的数学理论推导
- ⚡ 优化的椭圆曲线群运算
- 📈 专业的性能分析
- 🔧 模块化的工程实现

---

**应用场景**：
- 广告转化归因分析
- 用户行为关联分析  
- 隐私保护的数据统计
- 跨平台用户画像
