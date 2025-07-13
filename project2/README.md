# Project 2: 数字图像水印系统

基于频域变换的鲁棒性数字水印嵌入与提取系统

## 📋 文档导航

### 🚀 快速开始
- **[README.md](README.md)** - 项目总览和快速入门指南
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - 详细使用指南和API文档
- **[setup_environment.sh](setup_environment.sh)** - 一键环境配置脚本

### 📚 核心文档
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 项目总结和技术报告
- **[TEST_REPORT.md](TEST_REPORT.md)** - 完整测试报告和性能分析
- **[requirements.txt](requirements.txt)** - Python依赖包列表

### 🧮 技术文档
- **[docs/algorithm_optimization.md](docs/algorithm_optimization.md)** - 算法优化数学推导
- **[docs/mathematical_principles.md](docs/mathematical_principles.md)** - 数学原理详解
- **[docs/arch_linux_setup.md](docs/arch_linux_setup.md)** - Arch Linux环境配置
- **[docs/performance_report.md](docs/performance_report.md)** - 性能基准测试报告

### 🔧 工具和脚本
- **[watermark_cli.py](watermark_cli.py)** - 命令行工具主程序
- **[watermark_gui.py](watermark_gui.py)** - 图形用户界面
- **[robustness_test.py](robustness_test.py)** - 自动化鲁棒性测试套件
- **[quick_test.sh](quick_test.sh)** - 快速功能验证脚本
- **[full_robustness_test.sh](full_robustness_test.sh)** - 完整鲁棒性测试脚本
- **[benchmark_test.sh](benchmark_test.sh)** - 性能基准测试脚本

## 项目概述

本项目实现了一个完整的数字水印系统，支持多种水印算法和鲁棒性测试。主要特性包括：

- 🔐 **多种水印算法**: LSB、DCT等优化算法，包含完整数学推导
- 🛡️ **鲁棒性测试**: 28种攻击类型 (几何攻击+信号处理攻击)
- 🎨 **多格式支持**: JPEG、PNG、BMP等图像格式
- 📊 **性能评估**: PSNR、SSIM、BER、NC等10+客观指标
- 🖥️ **命令行工具**: 完整的CLI界面和自动化脚本
- ⚡ **批量处理**: 支持批量水印嵌入和鲁棒性测试
- 🧮 **算法优化**: 完整的数学推导、性能分析和环境配置
- 🚀 **一键运行**: 自动环境配置和测试图像生成

## 🚀 快速开始 (重要!)

### ⭐ 一键环境配置
```bash
pip install -r requirements.txt
```

### 基本使用
```bash
# 命令行方式
python watermark_cli.py embed -i input.jpg -w watermark.png -o output.jpg -m dct

# GUI方式
python watermark_gui.py
```

## 算法实现

### 支持的水印算法
1. **DCT水印**: 基于离散余弦变换的频域水印
2. **DWT水印**: 基于离散小波变换的多尺度水印  
3. **SVD水印**: 基于奇异值分解的几何不变水印
4. **LSB水印**: 基于最低有效位的空域水印

### 鲁棒性测试
- 几何攻击：旋转、缩放、裁剪、翻转
- 信号处理：JPEG压缩、高斯噪声、模糊
- 对比度调整、亮度变化、伽马校正

## 项目结构

```
project2/
├── src/                    # 源代码
│   ├── algorithms/         # 水印算法实现
│   ├── attacks/           # 攻击模拟
│   ├── evaluation/        # 评估指标
│   └── gui/              # 图形界面
├── tests/                 # 测试代码
├── docs/                  # 文档
├── examples/              # 示例文件
└── requirements.txt       # 依赖包
```

## 贡献指南

欢迎提交Issue和Pull Request来完善项目！

## 许可证

MIT License
