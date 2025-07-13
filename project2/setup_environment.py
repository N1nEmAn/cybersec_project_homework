#!/usr/bin/env python3
"""
环境设置脚本
自动安装依赖和配置开发环境
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """运行命令并显示进度"""
    print(f"\\n[INFO] {description}")
    print(f"[CMD] {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"[SUCCESS] {description}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} 失败")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print("✅ Python版本满足要求")
    return True

def setup_virtual_environment():
    """设置虚拟环境"""
    print("\\n=== 设置虚拟环境 ===")
    
    # 检查是否已在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 已在虚拟环境中")
        return True
    
    # 创建虚拟环境
    if not os.path.exists('venv'):
        if run_command('python -m venv venv', '创建虚拟环境'):
            print("✅ 虚拟环境创建成功")
        else:
            print("❌ 虚拟环境创建失败")
            return False
    else:
        print("✅ 虚拟环境已存在")
    
    # 激活虚拟环境的提示
    system = platform.system()
    if system == "Windows":
        activate_cmd = "venv\\\\Scripts\\\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    print(f"\\n请手动激活虚拟环境:")
    print(f"  {activate_cmd}")
    
    return True

def install_dependencies():
    """安装Python依赖"""
    print("\\n=== 安装Python依赖 ===")
    
    dependencies = [
        "numpy>=1.19.0",
        "opencv-python>=4.0.0",
        "Pillow>=8.0.0",
        "matplotlib>=3.3.0",
        "scipy>=1.6.0",
        "scikit-image>=0.18.0",
        "tk>=0.1.0"
    ]
    
    # 更新pip
    run_command('pip install --upgrade pip', '更新pip')
    
    # 批量安装依赖
    deps_str = ' '.join(dependencies)
    if run_command(f'pip install {deps_str}', '安装Python依赖包'):
        print("✅ 所有依赖安装成功")
        return True
    else:
        print("❌ 依赖安装失败，尝试逐个安装...")
        
        # 逐个安装
        success_count = 0
        for dep in dependencies:
            if run_command(f'pip install {dep}', f'安装 {dep}'):
                success_count += 1
        
        print(f"成功安装 {success_count}/{len(dependencies)} 个依赖包")
        return success_count == len(dependencies)

def install_system_dependencies():
    """安装系统依赖"""
    print("\\n=== 检查系统依赖 ===")
    
    system = platform.system()
    
    if system == "Linux":
        # 检查包管理器
        if subprocess.run(['which', 'apt'], capture_output=True).returncode == 0:
            print("检测到 APT 包管理器")
            commands = [
                'sudo apt update',
                'sudo apt install -y python3-dev python3-tk',
                'sudo apt install -y libopencv-dev python3-opencv'
            ]
        elif subprocess.run(['which', 'yum'], capture_output=True).returncode == 0:
            print("检测到 YUM 包管理器")
            commands = [
                'sudo yum update -y',
                'sudo yum install -y python3-devel tkinter',
                'sudo yum install -y opencv-python3'
            ]
        elif subprocess.run(['which', 'pacman'], capture_output=True).returncode == 0:
            print("检测到 Pacman 包管理器")
            commands = [
                'sudo pacman -Sy',
                'sudo pacman -S --noconfirm python tk opencv'
            ]
        else:
            print("⚠️  未检测到支持的包管理器，请手动安装系统依赖")
            return True
        
        for cmd in commands:
            run_command(cmd, f'执行: {cmd}')
            
    elif system == "Darwin":  # macOS
        print("检测到 macOS 系统")
        if subprocess.run(['which', 'brew'], capture_output=True).returncode == 0:
            commands = [
                'brew update',
                'brew install python-tk opencv'
            ]
            for cmd in commands:
                run_command(cmd, f'执行: {cmd}')
        else:
            print("⚠️  建议安装 Homebrew: https://brew.sh/")
            
    elif system == "Windows":
        print("检测到 Windows 系统")
        print("✅ Windows系统通常不需要额外的系统依赖")
    
    return True

def verify_installation():
    """验证安装"""
    print("\\n=== 验证安装 ===")
    
    test_imports = [
        ('numpy', 'import numpy as np; print(f"NumPy {np.__version__}")'),
        ('opencv', 'import cv2; print(f"OpenCV {cv2.__version__}")'),
        ('PIL', 'from PIL import Image; print(f"Pillow {Image.__version__}")'),
        ('matplotlib', 'import matplotlib; print(f"Matplotlib {matplotlib.__version__}")'),
        ('scipy', 'import scipy; print(f"SciPy {scipy.__version__}")'),
        ('tkinter', 'import tkinter as tk; print("Tkinter 可用")')
    ]
    
    success_count = 0
    for name, import_cmd in test_imports:
        try:
            result = subprocess.run([sys.executable, '-c', import_cmd], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ {name}: {result.stdout.strip()}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"❌ {name}: 导入失败")
            if e.stderr:
                print(f"   错误: {e.stderr.strip()}")
    
    print(f"\\n验证结果: {success_count}/{len(test_imports)} 个模块可用")
    return success_count == len(test_imports)

def create_test_structure():
    """创建测试目录结构"""
    print("\\n=== 创建目录结构 ===")
    
    directories = [
        'data/input',
        'data/output', 
        'data/watermarks',
        'demo',
        'results',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    # 创建日志文件
    log_file = 'logs/watermark_system.log'
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write("# 数字水印系统日志\\n")
        print(f"✅ 创建日志文件: {log_file}")
    
    return True

def run_basic_test():
    """运行基础测试"""
    print("\\n=== 运行基础测试 ===")
    
    if os.path.exists('basic_demo.py'):
        print("发现基础演示脚本，运行测试...")
        if run_command('python basic_demo.py', '运行基础演示'):
            print("✅ 基础功能测试通过")
            return True
        else:
            print("⚠️  基础功能测试失败，但环境配置可能仍然正确")
    else:
        print("⚠️  未找到基础演示脚本，跳过功能测试")
    
    return True

def main():
    """主函数"""
    print("🚀 数字水印系统环境配置脚本")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    steps = [
        ("虚拟环境设置", setup_virtual_environment),
        ("系统依赖安装", install_system_dependencies),
        ("Python依赖安装", install_dependencies),
        ("安装验证", verify_installation),
        ("目录结构创建", create_test_structure),
        ("基础功能测试", run_basic_test)
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\\n{'='*20} {step_name} {'='*20}")
        if step_func():
            success_count += 1
            print(f"✅ {step_name} 完成")
        else:
            print(f"❌ {step_name} 失败")
    
    print(f"\\n{'='*50}")
    print(f"环境配置完成: {success_count}/{len(steps)} 个步骤成功")
    
    if success_count == len(steps):
        print("\\n🎉 环境配置完全成功！")
        print("\\n现在可以运行以下命令测试系统:")
        print("  python basic_demo.py          # 基础演示")
        print("  python watermark_cli.py -h    # 命令行工具")
        print("  python src/gui/watermark_gui.py  # GUI界面")
    else:
        print("\\n⚠️  部分步骤失败，请检查错误信息并手动解决")
        print("\\n常见问题解决方案:")
        print("1. 网络问题: 使用国内镜像源")
        print("   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/")
        print("2. 权限问题: 使用 --user 参数")
        print("   pip install --user <package_name>")
        print("3. 系统依赖: 查看具体错误信息并安装对应依赖")

if __name__ == "__main__":
    main()
