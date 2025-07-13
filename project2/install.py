"""
数字水印系统安装脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def install_system_dependencies():
    """安装系统依赖"""
    print("📦 安装系统依赖...")
    
    system_deps = {
        'ubuntu': [
            'sudo apt-get update',
            'sudo apt-get install -y python3-opencv libopencv-dev',
            'sudo apt-get install -y python3-tk'
        ],
        'arch': [
            'sudo pacman -S opencv python-opencv',
            'sudo pacman -S tk'
        ],
        'fedora': [
            'sudo dnf install opencv-python opencv-devel',
            'sudo dnf install tkinter'
        ]
    }
    
    # 检测系统类型
    try:
        with open('/etc/os-release', 'r') as f:
            content = f.read().lower()
            if 'ubuntu' in content or 'debian' in content:
                os_type = 'ubuntu'
            elif 'arch' in content:
                os_type = 'arch'
            elif 'fedora' in content:
                os_type = 'fedora'
            else:
                print("⚠️  未识别的Linux发行版，请手动安装OpenCV和Tkinter")
                return True
        
        for cmd in system_deps[os_type]:
            try:
                subprocess.run(cmd.split(), check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ 命令执行失败: {cmd}")
                print(f"错误: {e}")
                return False
        
        print("✅ 系统依赖安装完成")
        return True
        
    except Exception as e:
        print(f"⚠️  系统依赖安装失败: {e}")
        return False

def create_virtual_environment():
    """创建虚拟环境"""
    venv_path = Path('./venv')
    
    if venv_path.exists():
        print("📁 虚拟环境已存在")
        return True
    
    print("🔧 创建虚拟环境...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ 虚拟环境创建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 虚拟环境创建失败: {e}")
        return False

def install_python_dependencies():
    """安装Python依赖"""
    print("📦 安装Python依赖...")
    
    # 确定pip路径
    venv_pip = Path('./venv/bin/pip')
    if not venv_pip.exists():
        venv_pip = Path('./venv/Scripts/pip.exe')  # Windows
    
    if venv_pip.exists():
        pip_cmd = str(venv_pip)
    else:
        pip_cmd = 'pip'
    
    try:
        # 升级pip
        subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], check=True)
        
        # 安装依赖
        subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
        
        print("✅ Python依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Python依赖安装失败: {e}")
        return False

def create_data_directories():
    """创建数据目录"""
    print("📁 创建数据目录...")
    
    directories = [
        'data/input',
        'data/output',
        'data/watermarks',
        'data/results',
        'logs',
        'temp'
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  创建目录: {dir_path}")
    
    print("✅ 数据目录创建完成")

def create_sample_data():
    """创建示例数据"""
    print("🖼️  创建示例数据...")
    
    try:
        import numpy as np
        from PIL import Image
        
        # 创建示例图像
        sample_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
        Image.fromarray(sample_image).save('data/input/sample_host.png')
        
        # 创建示例水印
        watermark = np.random.randint(0, 256, (64, 64), dtype=np.uint8)
        Image.fromarray(watermark, mode='L').save('data/watermarks/sample_watermark.png')
        
        print("✅ 示例数据创建完成")
        return True
    except Exception as e:
        print(f"⚠️  示例数据创建失败: {e}")
        return False

def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    
    try:
        # 运行基础演示
        result = subprocess.run([sys.executable, 'basic_demo.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 基础测试通过")
        else:
            print("❌ 基础测试失败")
            print(result.stderr)
            return False
        
        return True
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return False

def create_shortcuts():
    """创建快捷方式"""
    print("🔗 创建快捷方式...")
    
    # 创建启动脚本
    scripts = {
        'run_demo.sh': '#!/bin/bash\\ncd "$(dirname "$0")"\\npython basic_demo.py',
        'run_gui.sh': '#!/bin/bash\\ncd "$(dirname "$0")"\\npython src/gui/watermark_gui.py',
        'run_tests.sh': '#!/bin/bash\\ncd "$(dirname "$0")"\\npython -m pytest tests/'
    }
    
    for script_name, content in scripts.items():
        with open(script_name, 'w') as f:
            f.write(content)
        os.chmod(script_name, 0o755)
        print(f"  创建脚本: {script_name}")
    
    print("✅ 快捷方式创建完成")

def main():
    """主安装流程"""
    print("🚀 数字水印系统安装程序")
    print("=" * 50)
    
    steps = [
        ("检查Python版本", check_python_version),
        ("安装系统依赖", install_system_dependencies),
        ("创建虚拟环境", create_virtual_environment),
        ("安装Python依赖", install_python_dependencies),
        ("创建数据目录", create_data_directories),
        ("创建示例数据", create_sample_data),
        ("运行测试", run_tests),
        ("创建快捷方式", create_shortcuts)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\\n{'='*20} {step_name} {'='*20}")
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} 执行失败: {e}")
            failed_steps.append(step_name)
    
    print(f"\\n{'='*50}")
    
    if failed_steps:
        print(f"❌ 安装失败，以下步骤有问题:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\\n请检查错误信息并手动解决问题")
        return False
    else:
        print("✅ 安装完成！")
        print("\\n可用命令:")
        print("  python basic_demo.py          - 运行基础演示")
        print("  python src/gui/watermark_gui.py - 启动图形界面")
        print("  python Makefile.py help       - 查看项目管理命令")
        print("  ./run_demo.sh                 - 运行演示脚本")
        print("  ./run_gui.sh                  - 启动GUI脚本")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
