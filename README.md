# 密码学项目作业集合 🔐

[![技术验证](https://img.shields.io/badge/技术验证-100%25-brightgreen.svg)](./technical_verify.sh)
[![项目数量](https://img.shields.io/badge/项目数量-6个-blue.svg)](#项目概览)
[![代码质量](https://img.shields.io/badge/代码质量-优秀-green.svg)](#代码质量)

本仓库包含六个密码学相关的项目实现，涵盖对称密码、哈希函数、椭圆曲线密码、零知识证明、数字水印和隐私保护协议等多个领域。

## ✨ 项目特色

- 🔒 **完整性**: 覆盖SM4、SM3、SM2国产密码算法完整实现
- ⚡ **高性能**: 多种优化技术，性能提升3-12倍
- 🛡️ **安全性**: 包含攻击分析和安全评估
- 🧪 **验证**: 100%技术要求验证通过
- 📊 **可视化**: 丰富的性能图表和分析报告

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/N1nEmAn/cybersec_project_homework.git
cd cybersec_project_homework

# 运行技术验证脚本 (100%通过率)
chmod +x technical_verify.sh
./technical_verify.sh

# 运行快速验证脚本
chmod +x quick_verify_all.sh
./quick_verify_all.sh
```

## 📋 项目概览

### Project 1: SM4分组密码实现与优化 🔐
实现SM4分组密码的多种优化版本，包括基础实现、T-table查表优化、AES-NI指令集优化、GFNI/VPROLD指令优化、SIMD并行优化以及SM4-GCM认证加密模式。

**性能提升**: 
- T-table优化: 3-5倍
- AES-NI优化: 8-12倍  
- SIMD优化: 4-8倍
- GCM模式: ~87MB/s吞吐量

**技术实现**:
- ✅ 基础SM4算法 → [数学分析](./project1/docs/SM4_Mathematical_Analysis.md)
- ✅ T-table查表优化 → [优化理论](./project1/docs/T_Table_Optimization_Theory.md)
- ✅ SIMD/AVX2优化 → [并行分析](./project1/docs/SIMD_Parallel_Analysis.md)
- ✅ SM4-GCM认证模式 → [数学基础](./project1/docs/GCM_Mathematical_Foundation.md)
- ✅ 性能测试与分析 → [指令集映射](./project1/docs/Instruction_Set_Mathematical_Mapping.md)

**快速验证**:
```bash
cd project1
python demo.py
# 或编译后运行
make && ./bin/test_sm4
```

### Project 2: 基于数字水印的图片泄露检测 🌊
实现数字水印的嵌入和提取算法，支持多种鲁棒性测试，包括图像翻转、平移、截取、对比度调整等攻击场景。

**核心功能**:
- LSB水印嵌入/提取
- DCT频域水印
- 鲁棒性测试套件
- 图像质量评估

**技术实现**:
- ✅ LSB水印算法 → [数学原理](./project2/docs/mathematical_principles.md)
- ✅ DCT域水印算法 → [算法优化](./project2/docs/algorithm_optimization.md)
- ✅ 鲁棒性测试(旋转、缩放、压缩、噪声) → [性能分析](./project2/docs/performance_analysis.md)
- ✅ 图像质量评估(PSNR、SSIM) → [性能报告](./project2/docs/performance_report.md)
- ✅ 完整演示系统

**快速验证**:
```bash
cd project2
python simple_demo.py
# 或运行完整演示
python demo_complete.py
```

### Project 3: Poseidon2哈希算法的Circom电路实现 🔗
使用Circom实现Poseidon2哈希算法的零知识证明电路，支持(n,t,d)=(256,3,5)参数配置，并使用Groth16算法生成证明。

**技术特点**:
- Poseidon2哈希电路
- Groth16零知识证明
- 可信设置生成
- 证明验证系统

**技术实现**:
- ✅ Poseidon2电路实现(n,t,d)=(256,3,5) → [算法详解](./project3/docs/algorithm.md)
- ✅ Groth16证明系统 → [优化报告](./project3/docs/optimization.md)
- ✅ 完整的trusted setup → [性能报告](./project3/docs/performance_report.md)
- ✅ 证明生成与验证
- ✅ Node.js工具链

**快速验证**:
```bash
cd project3
npm install
node scripts/demo.js
```

### Project 4: SM3哈希函数实现与优化 📊
实现SM3哈希函数的多种优化版本，包括基础优化、SIMD并行、多线程处理，以及长度扩展攻击演示和大规模Merkle树构建。

**核心功能**:
- SM3基础与优化实现
- 长度扩展攻击
- Merkle树构建(10万节点)
- 性能分析

**技术实现**:
- ✅ SM3基础实现 → [架构对比分析](./project4/docs/architecture_comparison.png)
- ✅ SM3优化实现 → [算法分析图](./project4/docs/algorithm_analysis.png)
- ✅ 长度扩展攻击演示 → [性能对比图](./project4/docs/performance_comparison.png)
- ✅ Merkle树实现(100k节点) → [扩展性分析](./project4/docs/scalability_analysis.png)
- ✅ 性能测试与分析

**快速验证**:
```bash
cd project4
make && ./bin/test_sm3
python demo.py
```

### Project 5: SM2椭圆曲线密码实现与分析 🔐
实现SM2椭圆曲线数字签名算法，包括Python基础实现、性能优化、签名误用攻击分析和伪造中本聪签名的概念验证。

**技术特点**:
- SM2椭圆曲线实现
- 签名误用攻击POC
- 中本聪签名分析
- 安全性评估

**技术实现**:
- ✅ SM2基础实现 → [数学推导](./project5/docs/mathematical_derivation.md)
- ✅ SM2优化实现 → [详细数学推导](./project5/docs/mathematical_derivation_detailed.md)
- ✅ 随机数重用攻击 → [算法分析](./project5/docs/algorithm_analysis.md)
- ✅ 弱随机数攻击 → [优化报告](./project5/docs/optimization_report.md)
- ✅ 签名误用POC → [性能总结](./project5/docs/performance_summary.md)
- ✅ 中本聪签名分析

**快速验证**:
```bash
cd project5
python demo_complete.py
```

### Project 6: Google Password Checkup协议实现 🛡️
实现Google Password Checkup论文中的PSI(Private Set Intersection)协议，提供隐私保护的密码泄露检测服务。

**协议特点**:
- DDH-PSI协议
- 同态加密
- 差分隐私
- 可扩展架构

**技术实现**:
- ✅ PSI协议核心实现 → [协议规范](./project6/docs/protocol_specification.md)
- ✅ 同态加密机制 → [安全分析](./project6/docs/security_analysis.md)
- ✅ 差分隐私保护 → [实现说明](./project6/docs/implementation_notes.md)
- ✅ 多场景应用演示 → [使用指南](./project6/docs/usage_guide.md)
- ✅ 可扩展性测试 → [项目总结](./project6/docs/project_summary.md)

**快速验证**:
```bash
cd project6
python demo_simple.py
```

## 🛠️ 环境要求

### 系统依赖
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential python3-pip nodejs npm cmake

# 编译工具
gcc --version  # >= 9.0
python3 --version  # >= 3.8
node --version  # >= 14.0
```

### Python依赖
```bash
pip3 install numpy matplotlib pillow cryptography hashlib secrets
```

### Node.js依赖
```bash
cd project3
npm install circomlib snarkjs
```

## 🎯 技术验证

## 📋 technical_verify.sh 脚本详解

### 🔧 脚本功能

`technical_verify.sh` 是本项目的核心验证工具，确保所有密码学实现符合学术和工业标准。

### 📊 验证统计

| 验证类型 | 检查项数 | 说明 |
|----------|----------|------|
| **Project 1 (SM4)** | 10项 | 基础实现、优化版本、GCM模式、编译测试、功能验证 |
| **Project 2 (数字水印)** | 5项 | 水印算法、鲁棒性测试、质量评估、依赖检查、演示运行 |
| **Project 3 (Circom)** | 6项 | 电路实现、参数配置、Groth16系统、环境检查、工具链 |
| **Project 4 (SM3)** | 10项 | 基础实现、优化版本、攻击演示、Merkle树、测试验证 |
| **Project 5 (SM2)** | 8项 | 基础实现、优化版本、攻击分析、签名演示、环境检查 |
| **Project 6 (PSI)** | 5项 | 协议实现、PSI核心、同态加密、差分隐私、演示验证 |
| **总计** | **44项** | **完整的技术要求覆盖** |

### ⚙️ 脚本工作原理

```bash
# 脚本执行流程
1. 环境检查 (编译器、解释器、工具链)
2. 文件完整性验证 (源码、头文件、配置文件)
3. 编译测试 (C/C++项目实际编译)
4. 功能验证 (运行测试程序)
5. 演示验证 (执行完整演示)
6. 统计报告 (生成详细结果)
```

### 🎯 验证标准

- **✅ 通过**: 功能完整，测试成功
- **❌ 失败**: 缺少文件、编译错误、测试失败
- **📊 统计**: 44/44 (100%) = 完美实现

### 🚀 使用方法

```bash
# 运行完整验证
./technical_verify.sh

# 查看详细输出
./technical_verify.sh | tee verification_report.txt

# 只验证特定项目 (脚本内部逻辑)
# Project 1: lines 60-120
# Project 2: lines 120-160  
# Project 3: lines 160-200
# Project 4: lines 200-270
# Project 5: lines 270-320
# Project 6: lines 320-370
```

---
