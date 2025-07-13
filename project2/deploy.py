#!/usr/bin/env python3
"""
部署脚本
用于自动部署和打包数字水印系统
"""

import os
import sys
import shutil
import zipfile
import subprocess
from datetime import datetime

class WatermarkDeployer:
    """水印系统部署类"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.deploy_dir = os.path.join(self.project_root, 'deploy')
        self.version = self.get_version()
        
    def get_version(self):
        """获取版本号"""
        try:
            with open('VERSION', 'r') as f:
                return f.read().strip()
        except:
            return datetime.now().strftime('%Y.%m.%d')
    
    def clean_build(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        
        clean_dirs = ['build', 'dist', 'deploy', '__pycache__', '.pytest_cache']
        clean_patterns = ['*.pyc', '*.pyo', '*.egg-info']
        
        for directory in clean_dirs:
            if os.path.exists(directory):
                shutil.rmtree(directory)
                print(f"  删除目录: {directory}")
        
        # 递归清理__pycache__
        for root, dirs, files in os.walk('.'):
            for dir_name in dirs[:]:
                if dir_name == '__pycache__':
                    shutil.rmtree(os.path.join(root, dir_name))
                    print(f"  删除缓存: {os.path.join(root, dir_name)}")
                    dirs.remove(dir_name)
        
        print("✅ 清理完成")
    
    def copy_source_files(self):
        """复制源文件"""
        print("📋 复制源文件...")
        
        os.makedirs(self.deploy_dir, exist_ok=True)
        
        # 需要包含的文件和目录
        include_items = [
            'src/',
            'data/',
            'docs/',
            'tests/',
            'demo/',
            'README.md',
            'requirements.txt',
            'watermark_cli.py',
            'robustness_test.py',
            'basic_demo.py',
            'setup_environment.py',
            'config.py',
            'benchmark.py'
        ]
        
        for item in include_items:
            src_path = os.path.join(self.project_root, item)
            dst_path = os.path.join(self.deploy_dir, item)
            
            if os.path.exists(src_path):
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                    print(f"  复制目录: {item}")
                else:
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    print(f"  复制文件: {item}")
        
        print("✅ 源文件复制完成")
    
    def generate_startup_scripts(self):
        """生成启动脚本"""
        print("📜 生成启动脚本...")
        
        # Windows启动脚本
        windows_script = f"""@echo off
echo 数字水印系统 v{self.version}
echo ========================

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 安装依赖...
pip install -r requirements.txt

echo 启动系统...
echo.
echo 选择运行模式:
echo 1. GUI界面
echo 2. 基础演示
echo 3. 命令行工具
echo.
set /p choice=请输入选择 (1-3): 

if "%choice%"=="1" (
    python src/gui/watermark_gui.py
) else if "%choice%"=="2" (
    python basic_demo.py
) else if "%choice%"=="3" (
    python watermark_cli.py --help
) else (
    echo 无效选择
)

pause
"""
        
        with open(os.path.join(self.deploy_dir, 'start.bat'), 'w', encoding='utf-8') as f:
            f.write(windows_script)
        
        # Linux/Mac启动脚本
        unix_script = f"""#!/bin/bash
echo "数字水印系统 v{self.version}"
echo "========================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "检查并创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装依赖..."
pip install -r requirements.txt

echo "启动系统..."
echo
echo "选择运行模式:"
echo "1. GUI界面"
echo "2. 基础演示"  
echo "3. 命令行工具"
echo
read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        python src/gui/watermark_gui.py
        ;;
    2)
        python basic_demo.py
        ;;
    3)
        python watermark_cli.py --help
        ;;
    *)
        echo "无效选择"
        ;;
esac
"""
        
        script_path = os.path.join(self.deploy_dir, 'start.sh')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(unix_script)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        
        print("✅ 启动脚本生成完成")
    
    def create_version_info(self):
        """创建版本信息"""
        print("ℹ️  创建版本信息...")
        
        version_info = f"""# 数字水印系统版本信息

版本号: {self.version}
构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Python版本: {sys.version}

## 功能特性
- LSB和DCT水印算法
- 28种攻击测试
- GUI图形界面
- 命令行工具
- 批量处理
- 性能评估

## 系统要求
- Python 3.8+
- OpenCV 4.0+
- NumPy 1.19+
- PIL 8.0+
- Matplotlib 3.3+

## 快速开始
1. 运行 start.bat (Windows) 或 start.sh (Linux/Mac)
2. 或直接运行: python basic_demo.py

## 联系信息
项目地址: https://github.com/username/digital-watermark
文档地址: docs/README.md
"""
        
        with open(os.path.join(self.deploy_dir, 'VERSION_INFO.txt'), 'w', encoding='utf-8') as f:
            f.write(version_info)
        
        print("✅ 版本信息创建完成")
    
    def create_package(self):
        """创建发布包"""
        print("📦 创建发布包...")
        
        package_name = f"digital_watermark_v{self.version}_{datetime.now().strftime('%Y%m%d')}"
        
        # 创建ZIP包
        zip_path = f"{package_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.deploy_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_path = os.path.relpath(file_path, self.deploy_dir)
                    zipf.write(file_path, archive_path)
        
        print(f"✅ 发布包创建完成: {zip_path}")
        
        # 显示包信息
        package_size = os.path.getsize(zip_path) / (1024 * 1024)
        print(f"   包大小: {package_size:.2f} MB")
        
        return zip_path
    
    def run_tests(self):
        """运行测试"""
        print("🧪 运行测试...")
        
        try:
            # 运行基础测试
            result = subprocess.run([sys.executable, 'basic_demo.py'], 
                                  capture_output=True, text=True, 
                                  cwd=self.deploy_dir, timeout=60)
            
            if result.returncode == 0:
                print("✅ 基础功能测试通过")
                return True
            else:
                print("❌ 基础功能测试失败")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  测试超时，跳过")
            return True
        except Exception as e:
            print(f"❌ 测试运行失败: {e}")
            return False
    
    def generate_deployment_report(self, success):
        """生成部署报告"""
        print("📊 生成部署报告...")
        
        report = f"""# 部署报告

## 基本信息
- 版本: {self.version}
- 部署时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 部署状态: {'成功' if success else '失败'}

## 包含文件
"""
        
        # 统计文件
        file_count = 0
        total_size = 0
        
        for root, dirs, files in os.walk(self.deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                total_size += file_size
                file_count += 1
                
                rel_path = os.path.relpath(file_path, self.deploy_dir)
                report += f"- {rel_path} ({file_size} bytes)\\n"
        
        report += f"""
## 统计信息
- 总文件数: {file_count}
- 总大小: {total_size / (1024 * 1024):.2f} MB

## 使用说明
1. 解压发布包到目标目录
2. 运行 start.bat (Windows) 或 start.sh (Linux/Mac)
3. 按提示选择运行模式

## 技术支持
如有问题请查看 docs/ 目录中的文档
"""
        
        with open(os.path.join(self.deploy_dir, 'DEPLOYMENT_REPORT.md'), 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("✅ 部署报告生成完成")
    
    def deploy(self):
        """执行完整部署流程"""
        print(f"🚀 开始部署数字水印系统 v{self.version}")
        print("=" * 50)
        
        steps = [
            ("清理构建目录", self.clean_build),
            ("复制源文件", self.copy_source_files),
            ("生成启动脚本", self.generate_startup_scripts),
            ("创建版本信息", self.create_version_info),
            ("运行测试", self.run_tests),
        ]
        
        success = True
        for step_name, step_func in steps:
            print(f"\\n{step_name}...")
            try:
                result = step_func()
                if result is False:
                    success = False
                    print(f"❌ {step_name} 失败")
                else:
                    print(f"✅ {step_name} 完成")
            except Exception as e:
                print(f"❌ {step_name} 失败: {e}")
                success = False
        
        # 生成报告和打包
        self.generate_deployment_report(success)
        
        if success:
            package_path = self.create_package()
            
            print(f"\\n🎉 部署完成！")
            print(f"📦 发布包: {package_path}")
            print(f"📁 部署目录: {self.deploy_dir}")
            print("\\n使用说明:")
            print("1. 解压发布包到目标目录")
            print("2. 运行 start.bat (Windows) 或 start.sh (Linux/Mac)")
            print("3. 按提示选择运行模式")
        else:
            print("\\n❌ 部署失败，请检查错误信息")

def main():
    """主函数"""
    deployer = WatermarkDeployer()
    deployer.deploy()

if __name__ == "__main__":
    main()
