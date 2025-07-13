#!/usr/bin/env python3
"""
Makefile Python实现
提供项目管理的便捷命令
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class ProjectManager:
    """项目管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        os.chdir(self.project_root)
    
    def clean(self):
        """清理项目"""
        print("🧹 清理项目...")
        
        # 清理目录
        clean_dirs = [
            '__pycache__',
            '.pytest_cache', 
            'build',
            'dist',
            '*.egg-info',
            '.coverage',
            'htmlcov'
        ]
        
        for pattern in clean_dirs:
            for path in Path('.').rglob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"  删除目录: {path}")
                elif path.is_file():
                    path.unlink()
                    print(f"  删除文件: {path}")
        
        # 清理文件
        clean_files = ['*.pyc', '*.pyo', '*.log']
        for pattern in clean_files:
            for file in Path('.').rglob(pattern):
                file.unlink()
                print(f"  删除文件: {file}")
        
        print("✅ 清理完成")
    
    def install(self):
        """安装依赖"""
        print("📦 安装依赖...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         check=True)
            print("✅ 依赖安装完成")
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
        return True
    
    def test(self):
        """运行测试"""
        print("🧪 运行测试...")
        
        test_files = [
            'tests/test_algorithms.py',
            'basic_demo.py'
        ]
        
        success = True
        for test_file in test_files:
            if Path(test_file).exists():
                print(f"运行: {test_file}")
                try:
                    result = subprocess.run([sys.executable, test_file], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✅ {test_file} 通过")
                    else:
                        print(f"❌ {test_file} 失败")
                        print(result.stderr)
                        success = False
                except Exception as e:
                    print(f"❌ {test_file} 运行失败: {e}")
                    success = False
        
        return success
    
    def demo(self):
        """运行演示"""
        print("🚀 运行演示...")
        try:
            subprocess.run([sys.executable, 'basic_demo.py'], check=True)
            print("✅ 演示完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 演示失败: {e}")
            return False
    
    def gui(self):
        """启动GUI"""
        print("🖼️  启动GUI...")
        try:
            subprocess.run([sys.executable, 'src/gui/watermark_gui.py'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ GUI启动失败: {e}")
            return False
    
    def benchmark(self):
        """运行性能测试"""
        print("⏱️  运行性能测试...")
        try:
            subprocess.run([sys.executable, 'benchmark.py'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 性能测试失败: {e}")
            return False
    
    def deploy(self):
        """部署项目"""
        print("🚀 部署项目...")
        try:
            subprocess.run([sys.executable, 'deploy.py'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 部署失败: {e}")
            return False
    
    def setup(self):
        """设置环境"""
        print("⚙️  设置环境...")
        try:
            subprocess.run([sys.executable, 'setup_environment.py'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 环境设置失败: {e}")
            return False
    
    def lint(self):
        """代码检查"""
        print("🔍 代码检查...")
        
        # 检查Python语法
        python_files = list(Path('.').rglob('*.py'))
        syntax_errors = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), py_file, 'exec')
            except SyntaxError as e:
                print(f"❌ 语法错误 {py_file}:{e.lineno}: {e.msg}")
                syntax_errors += 1
            except Exception as e:
                print(f"⚠️  检查 {py_file} 时出错: {e}")
        
        if syntax_errors == 0:
            print("✅ 代码语法检查通过")
            return True
        else:
            print(f"❌ 发现 {syntax_errors} 个语法错误")
            return False
    
    def docs(self):
        """生成文档"""
        print("📚 生成文档...")
        
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)
        
        # 收集所有Python文件的文档字符串
        doc_content = "# 数字水印系统API文档\\n\\n"
        
        for py_file in Path('src').rglob('*.py'):
            if py_file.name != '__init__.py':
                doc_content += f"## {py_file}\\n\\n"
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 提取文档字符串
                        if '"""' in content:
                            doc_start = content.find('"""')
                            doc_end = content.find('"""', doc_start + 3)
                            if doc_end > doc_start:
                                docstring = content[doc_start+3:doc_end].strip()
                                doc_content += f"{docstring}\\n\\n"
                except Exception as e:
                    doc_content += f"文档提取失败: {e}\\n\\n"
        
        with open(docs_dir / 'API.md', 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print("✅ 文档生成完成")
        return True
    
    def all(self):
        """运行所有检查"""
        print("🔄 运行完整检查流程...")
        
        steps = [
            ("清理", self.clean),
            ("安装依赖", self.install),
            ("代码检查", self.lint),
            ("运行测试", self.test),
            ("运行演示", self.demo),
            ("生成文档", self.docs)
        ]
        
        failed_steps = []
        for step_name, step_func in steps:
            print(f"\\n{'='*20} {step_name} {'='*20}")
            if not step_func():
                failed_steps.append(step_name)
        
        print(f"\\n{'='*50}")
        if failed_steps:
            print(f"❌ 失败的步骤: {', '.join(failed_steps)}")
            return False
        else:
            print("✅ 所有步骤完成")
            return True
    
    def help(self):
        """显示帮助信息"""
        print("""
🛠️  数字水印系统项目管理工具

可用命令:
  clean      - 清理项目（删除缓存文件等）
  install    - 安装依赖包
  test       - 运行测试
  demo       - 运行基础演示
  gui        - 启动图形界面
  benchmark  - 运行性能测试
  deploy     - 部署项目
  setup      - 设置环境
  lint       - 代码检查
  docs       - 生成文档
  all        - 运行完整检查流程
  help       - 显示此帮助信息

使用方法:
  python Makefile.py <command>
  
示例:
  python Makefile.py clean
  python Makefile.py test
  python Makefile.py all
        """)

def main():
    """主函数"""
    manager = ProjectManager()
    
    if len(sys.argv) < 2:
        manager.help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        'clean': manager.clean,
        'install': manager.install,
        'test': manager.test,
        'demo': manager.demo,
        'gui': manager.gui,
        'benchmark': manager.benchmark,
        'deploy': manager.deploy,
        'setup': manager.setup,
        'lint': manager.lint,
        'docs': manager.docs,
        'all': manager.all,
        'help': manager.help
    }
    
    if command in commands:
        try:
            success = commands[command]()
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\\n❌ 用户取消操作")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            sys.exit(1)
    else:
        print(f"❌ 未知命令: {command}")
        manager.help()
        sys.exit(1)

if __name__ == "__main__":
    main()
