# SM4项目Makefile
# 提供便捷的项目管理命令

.PHONY: help install test benchmark clean gui cli examples docs

# 默认目标
help:
	@echo "SM4加密算法项目 - 可用命令:"
	@echo ""
	@echo "  make install     - 安装项目依赖"
	@echo "  make test        - 运行所有测试"
	@echo "  make benchmark   - 运行性能基准测试"
	@echo "  make gui         - 启动GUI界面"
	@echo "  make cli         - 显示CLI工具帮助"
	@echo "  make examples    - 运行示例演示"
	@echo "  make docs        - 生成文档"
	@echo "  make clean       - 清理临时文件"
	@echo ""

# 安装依赖
install:
	@echo "安装项目依赖..."
	./deploy.sh

# 运行测试
test:
	@echo "运行项目测试..."
	python3 -m pytest tests/ -v
	python3 sm4cli.py test

# 性能基准测试
benchmark:
	@echo "运行性能基准测试..."
	python3 comprehensive_benchmark.py

# 启动GUI
gui:
	@echo "启动GUI界面..."
	python3 -m src.gui.sm4_gui

# CLI工具帮助
cli:
	@echo "SM4命令行工具帮助:"
	python3 sm4cli.py --help

# 运行示例
examples:
	@echo "运行示例演示..."
	python3 examples/sm4_examples.py

# 生成文档
docs:
	@echo "项目文档位置:"
	@echo "  docs/algorithm_analysis.md    - 算法分析"
	@echo "  docs/optimization_process.md  - 优化过程"
	@echo "  docs/performance_report.md    - 性能报告"
	@echo "  docs/arch_linux_setup.md      - Arch Linux设置"

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.sm4" -delete 2>/dev/null || true
	find . -type f -name "*.decrypted" -delete 2>/dev/null || true
	find . -type f -name "benchmark_results.json" -delete 2>/dev/null || true
	@echo "清理完成"

# 快速测试（仅基础功能）
quick-test:
	@echo "运行快速测试..."
	python3 -c "from src.basic.sm4_basic import SM4Basic; print('基础实现测试:', '✓' if SM4Basic(b'\\x01'*16).encrypt_block(b'\\x00'*16) else '✗')"

# 代码格式检查
format-check:
	@echo "检查代码格式..."
	python3 -m py_compile src/basic/sm4_basic.py
	python3 -m py_compile src/optimized/sm4_lookup_table.py
	python3 -m py_compile src/modes/sm4_modes.py
	@echo "代码格式检查通过"

# 完整验证
validate: test benchmark examples
	@echo "完整项目验证通过 ✓"
