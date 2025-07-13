# SM4 Encryption Algorithm Build System
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O3 -march=native -mtune=native
LDFLAGS = -lm

SRCDIR = src
TESTDIR = tests
BENCHDIR = benchmarks
BINDIR = bin
OBJDIR = obj

BASIC_SOURCES = $(SRCDIR)/sm4_basic.c
OPTIMIZED_SOURCES = $(SRCDIR)/sm4_optimized.c
SIMD_SOURCES = $(SRCDIR)/sm4_simd.c
NEON_SOURCES = $(SRCDIR)/sm4_neon.c

BASIC_OBJECTS = $(OBJDIR)/sm4_basic.o
OPTIMIZED_OBJECTS = $(OBJDIR)/sm4_optimized.o
SIMD_OBJECTS = $(OBJDIR)/sm4_simd.o
NEON_OBJECTS = $(OBJDIR)/sm4_neon.o

TEST_SOURCES = $(TESTDIR)/test_sm4.c
BENCHMARK_SOURCES = $(BENCHDIR)/benchmark.c
QUICK_BENCHMARK_SOURCES = $(BENCHDIR)/quick_benchmark.c

TEST_BIN = $(BINDIR)/test_sm4
BENCHMARK_BIN = $(BINDIR)/benchmark
QUICK_BENCHMARK_BIN = $(BINDIR)/quick_benchmark

ARCH := $(shell uname -m)

ifeq ($(ARCH),x86_64)
    ARCH_OBJECTS = $(SIMD_OBJECTS)
    ARCH_FLAGS = -mavx2 -msse4.1
else ifeq ($(ARCH),aarch64)
    ARCH_OBJECTS = $(NEON_OBJECTS)
    ARCH_FLAGS = -march=armv8-a+simd
else
    ARCH_OBJECTS =
    ARCH_FLAGS =
endif

ALL_OBJECTS = $(BASIC_OBJECTS) $(OPTIMIZED_OBJECTS) $(ARCH_OBJECTS)

.PHONY: all directories test quick-test benchmark clean help

all: directories $(TEST_BIN) $(BENCHMARK_BIN) $(QUICK_BENCHMARK_BIN)

directories:
	mkdir -p $(OBJDIR) $(BINDIR)

$(BASIC_OBJECTS): $(BASIC_SOURCES) $(SRCDIR)/sm4.h
	$(CC) $(CFLAGS) -c $(BASIC_SOURCES) -o $@

$(OPTIMIZED_OBJECTS): $(OPTIMIZED_SOURCES) $(SRCDIR)/sm4.h
	$(CC) $(CFLAGS) -c $(OPTIMIZED_SOURCES) -o $@

$(SIMD_OBJECTS): $(SIMD_SOURCES) $(SRCDIR)/sm4.h
ifeq ($(ARCH),x86_64)
	$(CC) $(CFLAGS) $(ARCH_FLAGS) -c $(SIMD_SOURCES) -o $@
else
	touch $@
endif

$(NEON_OBJECTS): $(NEON_SOURCES) $(SRCDIR)/sm4.h
ifeq ($(ARCH),aarch64)
	$(CC) $(CFLAGS) $(ARCH_FLAGS) -c $(NEON_SOURCES) -o $@
else
	touch $@
endif

$(TEST_BIN): $(TEST_SOURCES) $(ALL_OBJECTS)
	$(CC) $(CFLAGS) $(TEST_SOURCES) $(ALL_OBJECTS) -o $@ $(LDFLAGS)

$(BENCHMARK_BIN): $(BENCHMARK_SOURCES) $(ALL_OBJECTS)
	$(CC) $(CFLAGS) $(BENCHMARK_SOURCES) $(ALL_OBJECTS) -o $@ $(LDFLAGS)

$(QUICK_BENCHMARK_BIN): $(QUICK_BENCHMARK_SOURCES) $(ALL_OBJECTS)
	$(CC) $(CFLAGS) $(QUICK_BENCHMARK_SOURCES) $(ALL_OBJECTS) -o $@ $(LDFLAGS)

test: $(TEST_BIN)
	./$(TEST_BIN)

quick-test: $(QUICK_BENCHMARK_BIN)
	./$(QUICK_BENCHMARK_BIN)

benchmark: $(BENCHMARK_BIN)
	./$(BENCHMARK_BIN)

clean:
	rm -rf $(OBJDIR) $(BINDIR)

help:
	@echo "SM4 Build System"
	@echo "Available targets:"
	@echo "  all          - Build all executables"
	@echo "  test         - Run test suite"
	@echo "  quick-test   - Run quick performance test"
	@echo "  benchmark    - Run comprehensive benchmark"
	@echo "  clean        - Clean build artifacts"
	@echo "  help         - Show this help"
