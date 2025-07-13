# SM2 Project Makefile

.PHONY: install test demo benchmark charts clean help

# Default target
all: install test demo

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

# Run tests
test:
	@echo "Running SM2 test suite..."
	python -m pytest tests/ -v

# Run quick demo
demo:
	@echo "Running quick demo..."
	python quick_demo.py

# Run complete demo
demo-complete:
	@echo "Running complete demonstration..."
	python demo_complete.py

# Run performance benchmark
benchmark:
	@echo "Running performance benchmark..."
	python benchmarks/performance_benchmark.py

# Generate performance charts
charts:
	@echo "Generating performance charts..."
	python generate_charts.py

# Run basic implementation demo
demo-basic:
	@echo "Running basic implementation demo..."
	python src/sm2_basic.py

# Run optimized implementation demo
demo-optimized:
	@echo "Running optimized implementation demo..."
	python src/sm2_optimized.py

# Run SIMD implementation demo
demo-simd:
	@echo "Running SIMD implementation demo..."
	python src/sm2_simd.py

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf __pycache__/ src/__pycache__/ tests/__pycache__/ benchmarks/__pycache__/
	rm -rf .pytest_cache/
	rm -f *.csv *.json
	rm -f charts/*.png

# Show help
help:
	@echo "SM2 Project Commands:"
	@echo "  install        - Install Python dependencies"
	@echo "  test          - Run test suite"
	@echo "  demo          - Run quick demo"
	@echo "  demo-complete - Run complete demonstration"
	@echo "  benchmark     - Run performance benchmark"
	@echo "  charts        - Generate performance charts"
	@echo "  demo-basic    - Demo basic implementation"
	@echo "  demo-optimized- Demo optimized implementation"
	@echo "  demo-simd     - Demo SIMD implementation"
	@echo "  clean         - Clean generated files"
	@echo "  help          - Show this help message"
