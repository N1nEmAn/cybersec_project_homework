# Arch Linux 环境配置指南

## 概述

本文档提供在Arch Linux系统上配置数字水印系统开发环境的详细步骤。

## 系统要求

- Arch Linux (最新版本)
- Python 3.8+
- 至少2GB可用磁盘空间
- 网络连接

## 基础环境配置

### 1. 更新系统

```bash
# 更新系统包
sudo pacman -Syu

# 安装基础开发工具
sudo pacman -S base-devel git wget curl
```

### 2. 安装Python环境

```bash
# 安装Python和pip
sudo pacman -S python python-pip python-virtualenv

# 验证安装
python --version
pip --version
```

### 3. 安装系统依赖

#### OpenCV依赖
```bash
# 安装OpenCV相关包
sudo pacman -S opencv python-opencv

# 安装图像处理库
sudo pacman -S python-pillow python-matplotlib

# 安装科学计算库
sudo pacman -S python-numpy python-scipy
```

#### 图形界面依赖
```bash
# 安装Tkinter (GUI支持)
sudo pacman -S tk python-tkinter

# 安装Qt (可选，用于更高级GUI)
sudo pacman -S python-pyqt5
```

#### 多媒体支持
```bash
# 安装图像格式支持
sudo pacman -S libpng libjpeg-turbo libtiff

# 安装视频处理支持(可选)
sudo pacman -S ffmpeg
```

## 项目环境设置

### 1. 克隆项目

```bash
# 创建工作目录
mkdir -p ~/projects
cd ~/projects

# 克隆项目
git clone https://github.com/N1nEmAn/cybersec_project_homework.git
cd cybersec_project_homework/project2
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

### 3. 安装Python依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 验证安装
python -c "import cv2, numpy, PIL; print('All dependencies loaded successfully')"
```

## 开发工具配置

### 1. 代码编辑器

#### VS Code配置
```bash
# 安装VS Code (从AUR)
yay -S visual-studio-code-bin

# 安装Python扩展
code --install-extension ms-python.python
code --install-extension ms-python.pylint
```

#### Vim配置 (可选)
```bash
# 安装Vim插件管理器
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

# 编辑.vimrc
cat >> ~/.vimrc << 'EOF'
call plug#begin('~/.vim/plugged')
Plug 'davidhalter/jedi-vim'
Plug 'vim-syntastic/syntastic'
call plug#end()

" Python配置
autocmd FileType python setlocal expandtab shiftwidth=4 softtabstop=4
EOF

# 安装插件
vim +PlugInstall +qall
```

### 2. 调试工具

```bash
# 安装调试工具
pip install ipdb pdb++

# 安装性能分析工具
pip install memory-profiler line-profiler
```

### 3. 测试工具

```bash
# 安装测试框架
pip install pytest pytest-cov

# 安装代码质量工具
pip install flake8 black isort
```

## 性能优化配置

### 1. NumPy优化

```bash
# 安装优化版BLAS库
sudo pacman -S openblas lapack

# 配置环境变量
echo 'export OPENBLAS_NUM_THREADS=4' >> ~/.bashrc
source ~/.bashrc
```

### 2. OpenCV优化

```bash
# 安装Intel TBB (Threading Building Blocks)
sudo pacman -S intel-tbb

# 检查OpenCV编译选项
python -c "import cv2; print(cv2.getBuildInformation())"
```

### 3. 并行处理配置

```bash
# 安装并行处理工具
pip install joblib multiprocessing-logging

# 设置CPU核心数
echo 'export OMP_NUM_THREADS=4' >> ~/.bashrc
```

## 项目测试验证

### 1. 基础功能测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行基础演示
python basic_demo.py

# 检查输出结果
ls demo/
```

### 2. 依赖检查

```bash
# 创建依赖检查脚本
cat > check_deps.py << 'EOF'
#!/usr/bin/env python3

import sys
import importlib

dependencies = [
    'cv2',
    'numpy',
    'PIL',
    'matplotlib',
    'tkinter'
]

print("检查依赖包...")
all_ok = True

for dep in dependencies:
    try:
        importlib.import_module(dep)
        print(f"✅ {dep}")
    except ImportError as e:
        print(f"❌ {dep}: {e}")
        all_ok = False

if all_ok:
    print("\n🎉 所有依赖包正常!")
    sys.exit(0)
else:
    print("\n❌ 部分依赖包缺失")
    sys.exit(1)
EOF

# 运行检查
python check_deps.py
```

### 3. 性能测试

```bash
# 运行性能基准测试
python benchmark.py

# 运行内存测试
python -m memory_profiler basic_demo.py
```

## 常见问题解决

### 1. OpenCV安装问题

```bash
# 如果python-opencv包有问题，使用pip安装
pip uninstall opencv-python
pip install opencv-python==4.5.5.64

# 或者从源码编译 (高级用户)
git clone https://github.com/opencv/opencv.git
cd opencv
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local ..
make -j4
sudo make install
```

### 2. Tkinter问题

```bash
# 如果GUI无法启动
sudo pacman -S tk

# 测试Tkinter
python -c "import tkinter; root=tkinter.Tk(); root.mainloop()"
```

### 3. 权限问题

```bash
# 如果遇到权限问题
sudo chown -R $USER:$USER ~/projects/cybersec_project_homework

# 设置正确的执行权限
chmod +x *.py
```

### 4. 中文字体支持

```bash
# 安装中文字体
sudo pacman -S noto-fonts-cjk

# 配置matplotlib中文显示
pip install matplotlib --upgrade
python -c "import matplotlib; print(matplotlib.matplotlib_fname())"
```

## 开发环境优化

### 1. Shell配置

```bash
# 添加项目别名到.bashrc
cat >> ~/.bashrc << 'EOF'
# 数字水印项目快捷命令
alias dwproj='cd ~/projects/cybersec_project_homework/project2'
alias dwenv='source ~/projects/cybersec_project_homework/project2/venv/bin/activate'
alias dwtest='python basic_demo.py'
alias dwgui='python src/gui/watermark_gui.py'
EOF

source ~/.bashrc
```

### 2. Git配置

```bash
# 配置Git用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 配置中文文件名支持
git config --global core.quotepath false
```

### 3. 环境变量

```bash
# 创建环境配置文件
cat > ~/.watermark_env << 'EOF'
export WATERMARK_PROJECT_ROOT=~/projects/cybersec_project_homework/project2
export PYTHONPATH=$WATERMARK_PROJECT_ROOT/src:$PYTHONPATH
export WATERMARK_DATA_DIR=$WATERMARK_PROJECT_ROOT/data
export WATERMARK_OUTPUT_DIR=$WATERMARK_PROJECT_ROOT/demo
EOF

# 添加到shell配置
echo 'source ~/.watermark_env' >> ~/.bashrc
```

## 高级配置

### 1. GPU加速 (可选)

```bash
# 如果有NVIDIA GPU
sudo pacman -S nvidia nvidia-utils cuda

# 安装GPU版本OpenCV
pip install opencv-contrib-python
```

### 2. Jupyter Notebook

```bash
# 安装Jupyter
pip install jupyter notebook

# 启动notebook
jupyter notebook --ip=0.0.0.0 --port=8888
```

### 3. 远程开发

```bash
# 安装SSH服务
sudo pacman -S openssh
sudo systemctl enable sshd
sudo systemctl start sshd

# 配置SSH密钥
ssh-keygen -t rsa -b 4096
```

## 验证安装

### 完整测试脚本

```bash
#!/bin/bash
# 创建综合测试脚本

cat > test_setup.sh << 'EOF'
#!/bin/bash

echo "🔍 测试Arch Linux环境配置..."

# 测试Python环境
echo "📍 Python环境测试"
python --version
pip --version

# 测试虚拟环境
echo "📍 虚拟环境测试"
source venv/bin/activate
which python

# 测试依赖包
echo "📍 依赖包测试"
python check_deps.py

# 测试项目功能
echo "📍 项目功能测试"
python basic_demo.py

# 测试性能
echo "📍 性能测试"
python -c "
import time
import numpy as np
start = time.time()
a = np.random.rand(1000, 1000)
b = np.random.rand(1000, 1000)
c = np.dot(a, b)
end = time.time()
print(f'NumPy性能测试: {end-start:.2f}s')
"

echo "✅ 所有测试完成!"
EOF

chmod +x test_setup.sh
./test_setup.sh
```

## 总结

通过以上配置步骤，您的Arch Linux系统已经具备了：

1. ✅ 完整的Python开发环境
2. ✅ 数字水印系统所需的所有依赖
3. ✅ 优化的性能配置
4. ✅ 便捷的开发工具
5. ✅ 完善的测试验证

现在可以开始数字水印系统的开发和测试工作了！

## 维护建议

- 定期更新系统: `sudo pacman -Syu`
- 定期更新Python包: `pip list --outdated`
- 备份虚拟环境: `pip freeze > requirements_backup.txt`
- 清理不需要的包: `sudo pacman -Rns $(pacman -Qtdq)`
