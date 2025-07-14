# SM3 Implementation Makefile

CC = gcc
CFLAGS = -Wall -Wextra -O3 -std=c99
INCLUDES = -Isrc
LIBS = -lm

# Detect architecture and set appropriate flags
ARCH := $(shell uname -m)
ifeq ($(ARCH),x86_64)
    CFLAGS += -march=native -mavx2
    ARCH_SPECIFIC = src/sm3_simd.c
else ifeq ($(ARCH),aarch64)
    CFLAGS += -march=native
    ARCH_SPECIFIC = src/sm3_neon.c
else
    ARCH_SPECIFIC = 
endif

# Source files
BASIC_SOURCES = src/sm3_basic.c
ALL_SOURCES = $(BASIC_SOURCES) $(ARCH_SPECIFIC)

# Object files
OBJECTS = $(ALL_SOURCES:.c=.o)

# Targets
TARGETS = bin/test_sm3 bin/benchmark bin/sm3_demo

# Library
LIBRARY = bin/libmerkle.a

# Create directories
$(shell mkdir -p bin obj)

.PHONY: all clean test benchmark charts install

all: $(TARGETS) $(LIBRARY)

# Main targets
bin/test_sm3: tests/test_sm3.c $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ $^ $(LIBS)

bin/benchmark: benchmarks/benchmark.c $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ $^ $(LIBS)

bin/sm3_demo: demo/demo.c $(OBJECTS)
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ $^ $(LIBS)

# Object files
%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c -o $@ $<

# Static library
$(LIBRARY): $(OBJECTS)
	ar rcs $@ $^

# 添加merkle_tree.c到编译规则
MERKLE_SOURCES = src/merkle_tree.c
MERKLE_OBJECTS = obj/merkle_tree.o

$(MERKLE_OBJECTS): $(MERKLE_SOURCES)
	$(CC) $(CFLAGS) -c $< -o $@

LIBRARY: $(MERKLE_OBJECTS)

# Run tests
test: bin/test_sm3
	@echo "Running SM3 correctness tests..."
	./bin/test_sm3

# Run benchmarks
benchmark: bin/benchmark
	@echo "Running SM3 performance benchmarks..."
	./bin/benchmark

# Generate performance charts
charts:
	@echo "Generating performance charts..."
	python3 generate_charts.py

# Debug build
debug: CFLAGS += -g -DDEBUG -O0
debug: clean all

# Profile build
profile: CFLAGS += -pg
profile: clean all

# Install (copy to system directories)
install: all
	@echo "Installing SM3 implementation..."
	sudo cp src/sm3.h /usr/local/include/
	sudo cp bin/sm3_demo /usr/local/bin/sm3

# Clean build artifacts
clean:
	rm -f $(OBJECTS)
	rm -f $(TARGETS)
	rm -f src/*.o tests/*.o benchmarks/*.o demo/*.o
	rm -f gmon.out
	rm -f $(LIBRARY)

# Show build configuration
info:
	@echo "Build Configuration:"
	@echo "==================="
	@echo "Architecture: $(ARCH)"
	@echo "Compiler: $(CC)"
	@echo "Flags: $(CFLAGS)"
	@echo "Sources: $(ALL_SOURCES)"
	@echo "Targets: $(TARGETS)"

# Help
help:
	@echo "SM3 Implementation Build System"
	@echo "==============================="
	@echo ""
	@echo "Targets:"
	@echo "  all       - Build all targets (default)"
	@echo "  test      - Run correctness tests"
	@echo "  benchmark - Run performance benchmarks"
	@echo "  charts    - Generate performance charts"
	@echo "  debug     - Build with debug symbols"
	@echo "  profile   - Build with profiling support"
	@echo "  install   - Install to system directories"
	@echo "  clean     - Remove build artifacts"
	@echo "  info      - Show build configuration"
	@echo "  help      - Show this help message"
