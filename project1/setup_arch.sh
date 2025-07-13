#!/bin/bash

# SM4项目安装脚本 - 适用于Arch Linux
# 使用方法: chmod +x setup_arch.sh && ./setup_arch.sh

echo "=== SM4项目环境配置脚本 (Arch Linux) ==="

# 检查是否为Arch Linux系统
if ! command -v pacman &> /dev/null; then
    echo "错误: 此脚本仅适用于Arch Linux系统"
    exit 1
fi

echo "1. 更新系统包..."
sudo pacman -Syu --noconfirm

echo "2. 安装Python和基础包..."
sudo pacman -S --needed --noconfirm python python-pip python-numpy python-pytest python-matplotlib python-pandas

echo "3. 安装额外的Python包..."
# 对于不在Arch仓库中的包，使用pip安装
pip install tabulate --break-system-packages

echo "4. 验证安装..."
echo "Python版本:"
python --version

echo "检查已安装的包:"
python -c "
import numpy as np
import pytest
import matplotlib
import pandas as pd
import tabulate
print('✓ 所有依赖包安装成功')
print(f'NumPy版本: {np.__version__}')
print(f'Matplotlib版本: {matplotlib.__version__}')
print(f'Pandas版本: {pd.__version__}')
"

echo "5. 运行测试验证..."
if [ -f "tests/test_basic.py" ]; then
    echo "运行基础测试..."
    python -m pytest tests/ -v
else
    echo "测试文件不存在，跳过测试"
fi

echo "=== 安装完成! ==="
echo "现在您可以运行以下命令："
echo "  python -m pytest tests/          # 运行测试"
echo "  python benchmarks/benchmark.py   # 运行性能测试"
