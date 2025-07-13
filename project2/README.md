# Project 2: 数字图像水印系统

基于频域变换的鲁棒性数字水印嵌入与提取系统

## 项目概述

本项目实现了一个完整的数字水印系统，支持多种水印算法和鲁棒性测试。主要特性包括：

- 🔐 **多种水印算法**: LSB、DCT、DWT、SVD等水印技术
- 🛡️ **鲁棒性测试**: 抗翻转、平移、截取、对比度调整等攻击
- 🎨 **多格式支持**: JPEG、PNG、BMP等图像格式
- 📊 **性能评估**: PSNR、SSIM、NC等客观指标
- 🖥️ **图形界面**: 直观的GUI操作界面
- ⚡ **批量处理**: 支持批量水印嵌入和提取
- 🧮 **算法优化**: 包含完整的数学推导和性能分析

## 快速开始

### 安装依赖
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
