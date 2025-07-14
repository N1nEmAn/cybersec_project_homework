# 密码学项目作业集合

本仓库包含六个密码学相关的项目实现，涵盖对称密码、哈希函数、椭圆曲线密码、零知识证明、数字水印和隐私保护协议等多个领域。

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/N1nEmAn/cybersec_project_homework.git
cd cybersec_project_homework

# 运行快速验证脚本
chmod +x quick_verify_all.sh
./quick_verify_all.sh
```

## 📋 项目概览

### Project 1: SM4分组密码实现与优化
实现SM4分组密码的多种优化版本，包括基础实现、T-table查表优化、AES-NI指令集优化、GFNI/VPROLD指令优化、SIMD并行优化以及SM4-GCM认证加密模式。

**性能提升**: 
- T-table优化: 3-5倍
- AES-NI优化: 8-12倍  
- SIMD优化: 4-8倍
- GCM模式: ~87MB/s吞吐量

**快速验证**:
```bash
cd project1
python demo.py
# 或编译后运行
make && ./bin/test_sm4
```

### Project 2: 基于数字水印的图片泄露检测
实现数字水印的嵌入和提取算法，支持多种鲁棒性测试，包括图像翻转、平移、截取、对比度调整等攻击场景。

**核心功能**:
- LSB水印嵌入/提取
- DCT频域水印
- 鲁棒性测试套件
- 图像质量评估

**快速验证**:
```bash
cd project2
python quick_demo.py
# 或运行完整演示
python demo_complete.py
```

### Project 3: Poseidon2哈希算法的Circom电路实现
使用Circom实现Poseidon2哈希算法的零知识证明电路，支持(n,t,d)=(256,3,5)参数配置，并使用Groth16算法生成证明。

**技术特点**:
- Poseidon2哈希电路
- Groth16零知识证明
- 可信设置生成
- 证明验证系统

**快速验证**:
```bash
cd project3
npm install
node scripts/demo.js
```

### Project 4: SM3哈希函数实现与优化
实现SM3哈希函数的多种优化版本，包括基础优化、SIMD并行、多线程处理，以及长度扩展攻击演示和大规模Merkle树构建。

**核心功能**:
- 基础优化(查表、代数简化)
- SIMD并行压缩
- 多线程并行处理
- 长度扩展攻击演示
- RFC6962 Merkle树(支持10万叶子节点)
- 架构特定优化(x86_64/ARM64)

**快速验证**:
```bash
cd project4
make && ./bin/test_sm3
# 或运行攻击演示
./demo/length_extension_demo
```

### Project 5: SM2椭圆曲线密码实现与攻击分析
实现SM2椭圆曲线数字签名算法，包含多种攻击分析和安全研究，涵盖随机数攻击、侧信道攻击、Bitcoin签名分析等。

**安全分析**:
- 随机数重用攻击
- 弱随机数模式攻击
- 侧信道攻击(时间、功耗、缓存)
- Bitcoin签名延展性分析
- 中本聪签名模拟分析

**快速验证**:
```bash
cd project5
python demo_complete.py
# 或运行安全分析套件
python src/comprehensive_security_demo.py
```

### Project 6: Google Password Checkup协议实现
实现Google Password Checkup隐私保护协议，基于私有集合求交(PSI)技术，支持用户密码泄露检测而不泄露密码信息。

**协议特点**:
- 私有集合求交(PSI)
- 不经意伪随机函数(OPRF)
- 隐私保护查询
- 可配置安全参数

**快速验证**:
```bash
cd project6
python demo_simple.py
# 或运行完整协议演示
python demo_complete.py
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

## 📊 性能基准

| 项目 | 算法 | 基础性能 | 优化性能 | 提升倍数 |
|------|------|----------|----------|----------|
| Project 1 | SM4 | ~5 MB/s | ~60 MB/s | 12x |
| Project 4 | SM3 | ~15 MB/s | ~120 MB/s | 8x |
| Project 5 | SM2 | ~500 ops/s | ~2000 ops/s | 4x |

## 🔒 安全特性

- **常数时间算法**: 防止时间侧信道攻击
- **安全随机数生成**: 使用密码学安全的熵源
- **内存安全**: 防止缓冲区溢出和内存泄露
- **侧信道对抗**: 实现功耗和缓存攻击防护

## 📖 详细文档

每个项目目录包含详细的README文档，包括：
- 算法原理说明
- 实现细节分析
- 性能基准测试
- 安全性分析
- 使用示例代码

## 🧪 测试验证

### 自动化测试
```bash
# 运行所有项目的快速验证
./quick_verify_all.sh

# 单独测试各项目
cd project1 && make test
cd project2 && python test_watermark.py
cd project3 && npm test
cd project4 && make test
cd project5 && python tests/test_sm2.py
cd project6 && python test_project.py
```

### 性能测试
```bash
# SM4性能基准
cd project1 && ./bin/benchmark

# SM3性能基准  
cd project4 && ./bin/benchmark

# SM2安全分析
cd project5 && python src/comprehensive_security_demo.py
```

## 🏗️ 项目架构

```
cybersec_project_homework/
├── project1/           # SM4分组密码优化
├── project2/           # 数字水印检测
├── project3/           # Poseidon2零知识证明
├── project4/           # SM3哈希函数优化
├── project5/           # SM2椭圆曲线密码
├── project6/           # Password Checkup协议
├── quick_verify_all.sh # 快速验证脚本
└── README.md          # 本文件
```

## 🎯 技术亮点

1. **多层次优化**: 从算法层面到指令集层面的全方位优化
2. **安全分析**: 理论攻击与实际防护相结合
3. **大规模应用**: 支持实际生产环境的性能需求
4. **标准兼容**: 严格遵循国密标准和国际标准
5. **教育价值**: 完整的密码学教学演示平台

## 📈 学习路径

1. **基础密码学**: Project 1 (SM4) → Project 4 (SM3)
2. **椭圆曲线密码**: Project 5 (SM2安全分析)
3. **应用密码学**: Project 2 (数字水印) → Project 6 (隐私协议)
4. **零知识证明**: Project 3 (Circom电路)
5. **攻击与防护**: 所有项目的安全分析模块

## 🔧 常见问题

**Q: 编译失败怎么办？**
A: 检查gcc版本(>=9.0)，安装完整的build-essential包

**Q: Python导入错误？**
A: 安装必要依赖: `pip3 install numpy matplotlib pillow cryptography`

**Q: 性能达不到预期？**
A: 确保使用`-O3 -march=native`编译优化，在支持指令集的CPU上运行

**Q: 如何贡献代码？**
A: Fork本仓库，创建功能分支，提交Pull Request

## 📄 许可证

本项目仅用于学术研究和教育目的。请遵循相关法律法规，不得用于非法用途。

## 📞 联系方式

- 项目仓库: [https://github.com/N1nEmAn/cybersec_project_homework](https://github.com/N1nEmAn/cybersec_project_homework)
- 问题反馈: 通过GitHub Issues提交

---

⭐ 如果这个项目对您有帮助，请给个Star支持！
