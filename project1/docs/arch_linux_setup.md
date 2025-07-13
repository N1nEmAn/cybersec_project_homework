# Arch Linux 环境配置指南

本文档专门为Arch Linux用户提供SM4项目的环境配置指南。

## 系统要求

- Arch Linux (最新版本)
- Python 3.8+
- 至少1GB可用磁盘空间

## 快速配置

### 1. 自动安装 (推荐)

使用提供的自动安装脚本：

```bash
cd /home/S3vn/Public/cybersec_project_homework/project1
chmod +x setup_arch.sh
./setup_arch.sh
```

### 2. 手动安装

#### 2.1 系统包安装

```bash
# 更新系统
sudo pacman -Syu

# 安装Python和核心包
sudo pacman -S python python-pip python-numpy python-pytest python-matplotlib python-pandas
```

#### 2.2 Python包安装

```bash
# 对于不在Arch仓库中的包，使用pip安装
pip install tabulate --break-system-packages
```

## 包管理说明

### Arch Linux特殊性

1. **PEP 668合规性**: Arch Linux遵循PEP 668标准，防止pip直接在系统Python环境中安装包
2. **--break-system-packages**: 当确实需要在系统环境安装包时使用此参数
3. **推荐使用虚拟环境**: 对于开发项目，建议使用虚拟环境

### 虚拟环境配置 (推荐)

```bash
# 创建虚拟环境
python -m venv sm4_env

# 激活虚拟环境
source sm4_env/bin/activate

# 在虚拟环境中安装依赖
pip install -r requirements.txt

# 使用完毕后停用
deactivate
```

### AUR包选择

某些Python包也可以从AUR安装：

```bash
# 使用yay或其他AUR助手
yay -S python-tabulate
```

## 常见问题解决

### 问题1: pip安装被阻止

**错误信息**:
```
error: externally-managed-environment
```

**解决方案**:
1. 使用`--break-system-packages`参数
2. 或者使用虚拟环境
3. 或者安装对应的Arch包

### 问题2: numpy导入错误

**解决方案**:
```bash
sudo pacman -S python-numpy
```

### 问题3: matplotlib显示问题

如果遇到GUI相关错误：
```bash
sudo pacman -S tk
```

## 性能优化建议

### 1. 编译优化

确保numpy使用了优化的BLAS库：
```bash
sudo pacman -S openblas
```

### 2. 并行计算

安装多进程支持：
```bash
sudo pacman -S python-multiprocessing-logging
```

## 测试验证

安装完成后运行测试：

```bash
# 基础功能测试
python -m pytest tests/ -v

# 性能基准测试
python benchmarks/benchmark.py

# 验证SM4实现
python -c "from src.basic.sm4_basic import SM4; print('SM4导入成功')"
```

## 卸载

如果需要清理环境：

```bash
# 卸载通过pacman安装的包
sudo pacman -R python-numpy python-pytest python-matplotlib python-pandas

# 清理pip安装的包
pip uninstall tabulate
```

## 开发环境建议

对于开发用途，推荐额外安装：

```bash
# 代码格式化和检查工具
sudo pacman -S python-black python-flake8

# 或使用pip
pip install black flake8 mypy --break-system-packages
```
