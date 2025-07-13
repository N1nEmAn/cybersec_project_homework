# Project 4: SM3 Hash Algorithm Implementation and Optimization

## Overview

This project implements the SM3 cryptographic hash function according to the Chinese national standard GM/T 0004-2012. SM3 is a 256-bit hash function designed as part of China's cryptographic standards suite, offering strong security properties and excellent performance characteristics.

## Mathematical Foundation

### SM3 Algorithm Overview

SM3 processes messages in 512-bit blocks and produces a 256-bit hash digest. The algorithm consists of:

1. **Message Preprocessing**: Padding and block division
2. **Message Expansion**: Each 512-bit block expands to 132 32-bit words
3. **Compression Function**: 64 rounds of cryptographic operations
4. **Final Output**: 256-bit hash digest

### Core Mathematical Functions

The SM3 algorithm employs several key mathematical functions:

#### Boolean Functions (FF and GG)
```
FF_j(X,Y,Z) = X ⊕ Y ⊕ Z                    (0 ≤ j ≤ 15)
FF_j(X,Y,Z) = (X ∧ Y) ∨ (X ∧ Z) ∨ (Y ∧ Z)  (16 ≤ j ≤ 63)

GG_j(X,Y,Z) = X ⊕ Y ⊕ Z                    (0 ≤ j ≤ 15)
GG_j(X,Y,Z) = (X ∧ Y) ∨ (¬X ∧ Z)           (16 ≤ j ≤ 63)
```

#### Permutation Functions (P0 and P1)
```
P0(X) = X ⊕ ROTL(X, 9) ⊕ ROTL(X, 17)
P1(X) = X ⊕ ROTL(X, 15) ⊕ ROTL(X, 23)
```

#### Message Expansion
For each 512-bit message block W[0..15]:
```
W[j] = P1(W[j-16] ⊕ W[j-9] ⊕ ROTL(W[j-3], 15)) ⊕ ROTL(W[j-13], 7) ⊕ W[j-6]  (16 ≤ j ≤ 67)
W'[j] = W[j] ⊕ W[j+4]  (0 ≤ j ≤ 63)
```

#### Compression Function
For each round j (0 ≤ j ≤ 63):
```
SS1 = ROTL((ROTL(A, 12) + E + ROTL(T_j, j)), 7)
SS2 = SS1 ⊕ ROTL(A, 12)
TT1 = FF_j(A, B, C) + D + SS2 + W'[j]
TT2 = GG_j(E, F, G) + H + SS1 + W[j]
D = C
C = ROTL(B, 9)
B = A
A = TT1
H = G
G = ROTL(F, 19)
F = E
E = P0(TT2)
```

Where T_j are round constants:
```
T_j = 0x79cc4519  (0 ≤ j ≤ 15)
T_j = 0x7a879d8a  (16 ≤ j ≤ 63)
```

## Implementation Features

### Multi-Architecture Support

1. **Basic Implementation** (`sm3_basic.c`)
   - Portable C implementation
   - Optimized for code clarity and correctness
   - Compatible with all architectures

2. **x86-64 SIMD Implementation** (`sm3_simd.c`)
   - AVX2 vectorization for parallel processing
   - Optimized memory access patterns
   - Register allocation optimizations

3. **ARM64 NEON Implementation** (`sm3_neon.c`)
   - NEON intrinsics for ARM processors
   - Optimized for mobile and embedded systems
   - Power-efficient operations

### Performance Optimizations

#### Algorithmic Optimizations
- **Loop Unrolling**: Reduces branching overhead
- **Instruction Scheduling**: Optimal pipeline utilization
- **Register Allocation**: Minimizes memory access
- **Cache-Friendly Access**: Sequential memory patterns

#### Architecture-Specific Optimizations
- **x86-64**: AVX2 256-bit vector operations
- **ARM64**: NEON 128-bit parallel processing
- **Generic**: Compiler auto-vectorization hints

## Build System

The project uses an intelligent Makefile that automatically detects the target architecture and applies appropriate optimizations:

```bash
# Build all implementations
make all

# Build specific targets
make basic      # Basic implementation only
make optimized  # Architecture-optimized version
make tests      # Test suite
make benchmark  # Performance benchmark

# Clean build artifacts
make clean
```

### Architecture Detection
The build system automatically detects:
- **x86-64**: Enables AVX2 optimizations
- **ARM64**: Enables NEON optimizations  
- **Other**: Falls back to portable implementation

### Optimization Flags
- **Release**: `-O3 -march=native -flto`
- **Debug**: `-O0 -g -fsanitize=address`
- **Profile**: `-O2 -pg -fno-omit-frame-pointer`

## Usage Examples

### Command-Line Interface

```bash
# Build the demo application
make demo

# Hash a string
./demo/sm3_demo "hello world"

# Hash a file
./demo/sm3_demo -f /path/to/file

# Run test vectors
./demo/sm3_demo -t

# Run performance benchmark
./demo/sm3_demo -b

# Verbose output
./demo/sm3_demo -v "test string"
```

### Programming Interface

```c
#include "src/sm3.h"

// One-shot hashing
uint8_t digest[SM3_DIGEST_SIZE];
const char *message = "Hello, SM3!";
sm3_hash((uint8_t*)message, strlen(message), digest);

// Incremental hashing
sm3_ctx_t ctx;
sm3_init(&ctx);
sm3_update(&ctx, data1, len1);
sm3_update(&ctx, data2, len2);
sm3_final(&ctx, digest);
```

## Performance Analysis

### Benchmark Results

The implementation has been tested across multiple architectures with the following performance characteristics:

![Performance Comparison](performance_comparison.png)

#### Throughput Analysis
- **Basic Implementation**: ~150-200 MB/s
- **SIMD Optimized (x86-64)**: ~400-600 MB/s  
- **NEON Optimized (ARM64)**: ~250-350 MB/s

#### Optimization Impact
- **SIMD Vectorization**: 2.5-3x performance improvement
- **Loop Unrolling**: 15-20% additional speedup
- **Register Optimization**: 10-15% improvement
- **Cache Optimization**: 5-10% improvement

### Memory Efficiency
- **Context Size**: 104 bytes (minimal state)
- **Stack Usage**: <1KB for all operations
- **Cache Performance**: Optimized for L1/L2 cache efficiency

## Testing and Validation

### Test Coverage
- **Standard Test Vectors**: GM/T 0004-2012 compliance
- **Edge Cases**: Empty input, single byte, large files
- **Stress Testing**: Multi-GB file processing
- **Cross-Platform**: Verified on x86-64, ARM64, ARM32

### Correctness Verification
```bash
# Run all tests
make test

# Specific test categories
./tests/test_sm3 --basic      # Basic functionality
./tests/test_sm3 --vectors    # Standard test vectors
./tests/test_sm3 --stress     # Stress testing
```

## Security Considerations

### Implementation Security
- **Constant-Time Operations**: Resistant to timing attacks
- **Memory Safety**: Bounds checking and sanitization
- **Side-Channel Resistance**: Uniform execution paths
- **Secure Memory**: Explicit clearing of sensitive data

### Cryptographic Properties
- **Collision Resistance**: 2^128 security level
- **Preimage Resistance**: 2^256 security level
- **Avalanche Effect**: Single bit change affects 50% of output
- **Uniform Distribution**: Output statistically random

## Project Structure

```
project4/
├── src/               # Source implementations
│   ├── sm3.h         # Header and constants
│   ├── sm3_basic.c   # Basic implementation
│   ├── sm3_simd.c    # x86-64 AVX2 optimized
│   └── sm3_neon.c    # ARM64 NEON optimized
├── tests/            # Test suite
│   └── test_sm3.c    # Comprehensive tests
├── benchmarks/       # Performance testing
│   └── benchmark.c   # Detailed benchmarks
├── demo/             # Command-line interface
│   └── demo.c        # User-friendly demo
├── docs/             # Documentation
├── Makefile          # Build system
├── generate_charts.py # Performance visualization
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Dependencies

### Build Dependencies
- **GCC/Clang**: C99 compatible compiler
- **Make**: GNU Make or compatible
- **Python 3**: For chart generation (optional)

### Runtime Dependencies
- **libc**: Standard C library
- **libm**: Math library (for benchmarks)

### Optional Dependencies
```bash
# Install Python charting dependencies
pip install -r requirements.txt
```

## Contributing

### Development Guidelines
1. **Code Style**: Follow existing formatting conventions
2. **Testing**: Add tests for new features
3. **Documentation**: Update README for significant changes
4. **Performance**: Benchmark new optimizations

### Adding New Architectures
1. Create `sm3_<arch>.c` implementation
2. Add detection to Makefile
3. Include in test suite
4. Document optimization techniques

## License

This implementation is provided for educational and research purposes. The SM3 algorithm specification is defined in the Chinese national standard GM/T 0004-2012.

## References

- **GM/T 0004-2012**: SM3 Cryptographic Hash Algorithm
- **RFC Draft**: SM3 Hash Function (draft-oscca-cfrg-sm3-02)
- **Performance Analysis**: "Efficient Implementation of SM3 Hash Algorithm"
- **Security Analysis**: "Cryptanalysis of the SM3 Hash Function"

---

*Last updated: 2024*
*Performance benchmarks generated automatically*
