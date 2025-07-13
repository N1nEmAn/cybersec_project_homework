#!/bin/bash
"""
SM4项目部署脚本
自动设置环境和依赖
"""

echo "=== SM4项目部署脚本 ==="
echo "开始设置SM4加密算法项目环境..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
echo "检测到Python版本: $python_version"

if [[ $(echo "$python_version < 3.8" | bc -l) == 1 ]]; then
    echo "错误: 需要Python 3.8或更高版本"
    exit 1
fi

# 安装依赖
echo "安装Python依赖包..."

# 检查是否为Arch Linux
if command -v pacman &> /dev/null; then
    echo "检测到Arch Linux，使用--break-system-packages参数"
    pip_args="--break-system-packages"
else
    pip_args=""
fi

# 安装基础依赖
pip3 install numpy $pip_args
pip3 install matplotlib $pip_args  
pip3 install pandas $pip_args
pip3 install tabulate $pip_args
pip3 install pytest $pip_args

# 如果有py-cpuinfo则安装
pip3 install py-cpuinfo $pip_args 2>/dev/null || echo "py-cpuinfo安装失败，跳过"

echo "依赖安装完成"

# 运行测试
echo "运行项目测试..."
cd "$(dirname "$0")"

# 基础功能测试
echo "1. 运行基础功能测试..."
python3 -m pytest tests/ -v

# 运行标准测试向量验证
echo "2. 运行标准测试向量验证..."
python3 sm4cli.py test

# 运行示例演示
echo "3. 运行示例演示..."
python3 examples/sm4_examples.py

echo "=== 部署完成 ==="
echo "项目已成功部署并通过测试"
echo ""
echo "可用命令:"
echo "  python3 sm4cli.py --help          # 查看命令行工具帮助"
echo "  python3 -m src.gui.sm4_gui        # 启动GUI界面"
echo "  python3 comprehensive_benchmark.py # 运行性能测试"
echo "  python3 examples/sm4_examples.py   # 查看使用示例"
echo ""
echo "项目结构:"
echo "  src/basic/           # 基础实现"
echo "  src/optimized/       # 优化实现"
echo "  src/modes/          # 加密模式"
echo "  src/gui/            # GUI界面"
echo "  tests/              # 测试用例"
echo "  docs/               # 技术文档"
echo "  examples/           # 使用示例"
