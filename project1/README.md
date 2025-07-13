# Project 1: SM4 加密算法软件实现与优化

## 项目概述

本项目实现了国密SM4分组加密算法的软件实现，并进行了多种优化策略的探索和实现。SM4是中华人民共和国政府发布的无线局域网标准的分组数据加密算法，属于对称加密算法。

## 项目结构

```
project1/
├── README.md                    # 项目说明文档
├── docs/                        # 详细文档
│   ├── algorithm_analysis.md    # 算法分析
│   ├── optimization_process.md  # 优化过程推导
│   └── performance_report.md    # 性能测试报告
├── src/                         # 源代码
│   ├── basic/                   # 基础实现
│   │   └── sm4_basic.py        # SM4基础实现
│   ├── optimized/               # 优化实现
│   │   ├── sm4_lookup_table.py # 查找表优化版本
│   │   ├── sm4_bitwise.py      # 位运算优化版本
│   │   └── sm4_parallel.py     # 并行优化版本
│   └── utils/                   # 工具函数
│       ├── constants.py         # 常量定义
│       └── helpers.py           # 辅助函数
├── tests/                       # 测试用例
│   ├── test_basic.py           # 基础功能测试
│   ├── test_optimized.py       # 优化版本测试
│   └── test_vectors.py         # 标准测试向量
├── benchmarks/                  # 性能基准测试
│   ├── benchmark.py            # 性能测试脚本
│   ├── quick_benchmark.py      # 快速性能测试
│   └── results/                # 测试结果
├── requirements.txt            # 依赖包
├── requirements_arch.txt       # Arch Linux专用依赖
└── setup_arch.sh              # Arch Linux自动安装脚本
```

## SM4算法简介

SM4算法是一种分组密码算法，具有以下特点：
- **分组长度**: 128位
- **密钥长度**: 128位
- **轮数**: 32轮
- **结构**: Feistel网络结构

## 快速开始

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 运行基础测试:
```bash
python -m pytest tests/
```

3. 运行性能基准测试:
```bash
python benchmarks/benchmark.py
```

## 快速上手

### 最简单的使用方式

```python
from src.basic.sm4_basic import SM4Basic

# 创建密钥和SM4实例
key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
sm4 = SM4Basic(key)

# 加密文本
plaintext = b"你好，SM4！"
ciphertext = sm4.encrypt_ecb(plaintext)
print(f"密文: {ciphertext.hex().upper()}")

# 解密
decrypted = sm4.decrypt_ecb(ciphertext)
print(f"解密: {decrypted.decode()}")
```

### 推荐的高性能版本

```python
from src.optimized.sm4_lookup_table import SM4LookupTable

# 使用查找表优化版本，速度提升近2倍
sm4_fast = SM4LookupTable(key)
fast_result = sm4_fast.encrypt_ecb(plaintext)
```

## 实现版本

### 1. 基础实现 (basic/sm4_basic.py)
- 严格按照国标GB/T 32907-2016实现
- 注重代码可读性和正确性
- 适合学习和理解算法原理

### 2. 查找表优化 (optimized/sm4_lookup_table.py)
- 预计算S盒查找表
- 减少运行时计算开销
- 提升加解密速度

### 3. 位运算优化 (optimized/sm4_bitwise.py)
- 优化位运算操作
- 减少内存访问
- 提高计算效率

### 4. 并行优化 (optimized/sm4_parallel.py)
- 支持多线程并行处理
- 适用于大量数据加密
- 充分利用多核CPU

## 测试结果

详细的性能测试结果和优化效果分析请参考 `docs/performance_report.md`。

## 开发进度

- [x] SM4基础算法实现
- [x] 标准测试向量验证
- [x] 查找表优化实现
- [x] 位运算优化实现
- [x] 并行优化实现
- [x] 向量化优化实现
- [x] 硬件加速实现
- [x] 完整的测试套件
- [x] 性能基准测试
- [x] 详细技术文档
- [x] Arch Linux环境适配
- [x] 多种加密模式支持 (ECB, CBC, CTR, CFB, OFB)
- [x] GUI演示程序
- [x] 命令行工具
- [ ] 最终性能优化和文档完善

## 贡献指南

本项目采用Git进行版本控制，每个重要的开发阶段都会有相应的commit记录。主要的开发分支：

- `main`: 主分支，包含稳定版本
- `optimization`: 优化实验分支
- `documentation`: 文档完善分支

## 参考资料

1. GB/T 32907-2016 信息安全技术 SM4分组密码算法
2. SM4 Encryption Algorithm - IETF RFC 8018
3. 《现代密码学》- 杨波等著

## 许可证

本项目仅用于学术研究和课程作业，不得用于商业用途。

## 使用方法

### 命令行工具

项目提供了功能完整的命令行工具 `sm4cli.py`：

```bash
# 基础加密解密
python sm4cli.py encrypt -k 0123456789ABCDEFFEDCBA9876543210
python sm4cli.py decrypt -k 0123456789ABCDEFFEDCBA9876543210

# 使用不同加密模式
python sm4cli.py encrypt -k [密钥] -m cbc --output-iv
python sm4cli.py encrypt -k [密钥] -m ctr --hex-output

# 性能测试
python sm4cli.py benchmark
python sm4cli.py test

# 查看帮助
python sm4cli.py --help
```

### GUI界面

启动图形用户界面：

```bash
python -m src.gui.sm4_gui
```

GUI提供以下功能：
- 基础加密解密测试
- 多种优化实现比较
- 全部加密模式演示
- 性能基准测试

### Python API

```python
from src.basic.sm4_basic import SM4Basic
from src.optimized.sm4_lookup_table import SM4LookupTable
from src.modes.sm4_modes import SM4Modes

# 基础使用
key = bytes.fromhex('0123456789ABCDEFFEDCBA9876543210')
sm4 = SM4Basic(key)
ciphertext = sm4.encrypt_ecb(b"Hello, SM4!")

# 优化实现
sm4_opt = SM4LookupTable(key)
ciphertext = sm4_opt.encrypt_ecb(b"Hello, SM4!")

# 加密模式
sm4_modes = SM4Modes(key)
ciphertext, iv = sm4_modes.encrypt_cbc(b"Hello, SM4!")
```

## 🚀 新增功能

### 性能对比演示
```bash
# 运行性能对比演示（需要matplotlib）
python performance_demo.py

# 如果缺少依赖，请先安装：
pip install matplotlib numpy
```

### 实现验证工具
```bash
# 验证所有实现的正确性
python validate_implementations.py
```

### 数学推导文档
查看 `docs/algorithm_analysis.md` 了解：
- 算法复杂度分析
- 优化策略的数学推导
- 理论 vs 实际性能对比

### 错误报告功能
```bash
# 生成错误报告
python sm4cli.py report -d "描述问题"
```
