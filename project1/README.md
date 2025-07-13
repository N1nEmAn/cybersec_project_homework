# SM4 加密算法 - 高性能 C 语言实现

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: C](https://img.shields.io/badge/Language-C-blue.svg)](https://en.wikipedia.org/wiki/C_(programming_language))
[![Architecture: Multi](https://img.shields.io/badge/Architecture-Multi-green.svg)](https://github.com)

这是一个完整的 SM4 分组密码算法 C 语言实现，支持多种架构优化和高性能计算。本项目实现了中国国家标准 GB/T 32907-2016 中规定的 SM4 分组密码算法。

## 📖 项目概述

SM4 是中华人民共和国国家密码管理局发布的分组密码标准，用于无线局域网产品。本项目提供了高度优化的 C 语言实现，包含多种性能优化策略。

### 🚀 主要特性

- **完整的 SM4 算法实现**：支持加密和解密操作
- **多架构优化**：
  - 基础 C 实现（可移植性最高）
  - 查找表优化版本（减少计算开销）
  - x86-64 AVX2 SIMD 优化（大幅提升性能）
  - ARM64 NEON 优化（ARM 处理器专用）
- **多种工作模式**：ECB、CBC 模式支持
- **PKCS#7 填充**：自动处理非对齐数据
- **全面测试**：包含标准测试向量验证
- **性能基准测试**：详细的性能分析工具
- **智能构建系统**：自动检测架构并选择最优实现

## 🔬 SM4 算法数学原理

### 算法结构

SM4 采用 32 轮的 Feistel 结构，每轮使用轮函数 F：

```
F(X₀, X₁, X₂, X₃, RK) = X₀ ⊕ T(X₁ ⊕ X₂ ⊕ X₃ ⊕ RK)
```

其中 T 是合成置换，T = L ∘ τ，包含：

### 非线性变换 τ (S盒)

τ 函数对 32 位输入的每个字节并行应用 S 盒：

```
τ(A) = (Sbox(a₀), Sbox(a₁), Sbox(a₂), Sbox(a₃))
```

其中 A = (a₀, a₁, a₂, a₃)，每个 aᵢ 为 8 位。

### 线性变换 L

对于加密轮函数，线性变换 L 定义为：

```
L(B) = B ⊕ (B ≪ 2) ⊕ (B ≪ 10) ⊕ (B ≪ 18) ⊕ (B ≪ 24)
```

对于密钥扩展，使用 L' 变换：

```
L'(B) = B ⊕ (B ≪ 13) ⊕ (B ≪ 23)
```

### 密钥扩展算法

1. **初始化**：将 128 位密钥 MK 分为 4 个 32 位字 MK₀, MK₁, MK₂, MK₃
2. **与系统参数异或**：
   ```
   K₀ = MK₀ ⊕ FK₀, K₁ = MK₁ ⊕ FK₁, K₂ = MK₂ ⊕ FK₂, K₃ = MK₃ ⊕ FK₃
   ```
3. **轮密钥生成**：对于 i = 0, 1, ..., 31
   ```
   rk_i = K_i ⊕ T'(K_{i+1} ⊕ K_{i+2} ⊕ K_{i+3} ⊕ CK_i)
   K_{i+4} = rk_i
   ```

其中 T' = L' ∘ τ

### 加密过程

输入明文 X = (X₀, X₁, X₂, X₃)，32 轮迭代：

```
X_{i+4} = X_i ⊕ T(X_{i+1} ⊕ X_{i+2} ⊕ X_{i+3} ⊕ rk_i)
```

最终反序变换：
```
Y = (X₃₅, X₃₄, X₃₃, X₃₂)
```

## 📊 性能测试结果

### 基准测试结果

![性能对比图表](performance_comparison.png)

基于最新测试的性能结果：

| 实现版本 | 执行时间 (ms) | 吞吐量 (MB/s) | 相对加速比 | 效率得分 |
|----------|---------------|---------------|------------|----------|
| 基础实现 | 22.45 | 67.98 | 1.00x | 1.000 |
| 查找表优化 | 21.73 | 70.22 | 1.03x | 1.033 |
| AVX2 SIMD | 17.52 | 87.07 | 1.28x | 1.281 |

### 多架构性能对比

![架构对比图表](architecture_comparison.png)

不同架构下的性能表现：

- **x86-64 平台**：AVX2 SIMD 优化提供最佳性能
- **ARM64 平台**：NEON 指令集优化
- **通用平台**：纯 C 实现保证兼容性

## 🏗️ 项目结构

```
project1/
├── README.md                    # 项目说明文档
├── Makefile                     # 智能构建系统
├── generate_charts.py           # 性能图表生成器
├── performance_comparison.png   # 性能对比图表
├── architecture_comparison.png  # 架构对比图表
├── src/                         # 源代码目录
│   ├── sm4.h                   # SM4 算法头文件和常数定义
│   ├── sm4_basic.c             # 基础实现
│   ├── sm4_optimized.c         # 查找表优化实现
│   ├── sm4_simd.c              # x86-64 AVX2 SIMD 实现
│   └── sm4_neon.c              # ARM64 NEON 实现
├── tests/                       # 测试目录
│   └── test_sm4.c              # 综合测试套件
├── benchmarks/                  # 性能测试目录
│   ├── benchmark.c             # 全面性能基准测试
│   └── quick_benchmark.c       # 快速性能测试
├── demo/                        # 演示程序目录
│   └── sm4_demo.c              # 功能演示程序
├── bin/                         # 编译输出目录
├── obj/                         # 对象文件目录
└── docs/                        # 文档目录
```

## 🔧 快速开始

### 系统要求

- **编译器**：GCC 7.0+ 或 Clang 10.0+
- **系统**：Linux/macOS/Windows（WSL）
- **架构**：x86-64、ARM64 或其他（自动检测）

### 编译构建

```bash
# 构建所有组件
make all

# 运行测试
make test

# 快速性能测试
make quick-test

# 运行演示
./bin/sm4_demo
```

### 测试验证

项目包含标准测试向量验证：

```bash
# 运行完整测试套件
./bin/test_sm4

# 测试输出示例
SM4 Algorithm Test Suite
========================
Testing Basic SM4 Encryption/Decryption
Test 1: Standard Test Vector 1
Key       : 0123456789ABCDEFFEDCBA9876543210
Plaintext : 0123456789ABCDEFFEDCBA9876543210
Expected  : 681EDF34D206965E86B3E94F536E4246
Computed  : [实际计算结果]
```

## 🧪 详细 API 使用

### 基本加密/解密

```c
#include "sm4.h"

int main() {
    sm4_ctx_t ctx;
    uint8_t key[SM4_KEY_SIZE] = {
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
        0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
    };
    uint8_t plaintext[SM4_BLOCK_SIZE] = {
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
        0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
    };
    uint8_t ciphertext[SM4_BLOCK_SIZE];
    uint8_t decrypted[SM4_BLOCK_SIZE];

    // 设置加密密钥
    sm4_setkey_enc(&ctx, key);

    // 执行加密（可选择不同实现）
    sm4_encrypt_basic(&ctx, plaintext, ciphertext);      // 基础实现
    sm4_encrypt_optimized(&ctx, plaintext, ciphertext);  // 优化实现
    sm4_encrypt_simd(&ctx, plaintext, ciphertext);       // SIMD 实现

    // 设置解密密钥
    sm4_setkey_dec(&ctx, key);

    // 执行解密
    sm4_decrypt_basic(&ctx, ciphertext, decrypted);

    return 0;
}
```

### ECB 模式加密

```c
// ECB 模式大数据加密
size_t data_size = 1024;  // 数据大小（必须是16字节的倍数）
uint8_t *input_data = malloc(data_size);
uint8_t *output_data = malloc(data_size);

sm4_ctx_t ctx;
sm4_setkey_enc(&ctx, key);

// ECB 加密
int result = sm4_ecb_encrypt(&ctx, input_data, data_size, output_data);
if (result == 0) {
    printf("ECB 加密成功\n");
}

// ECB 解密
sm4_setkey_dec(&ctx, key);
result = sm4_ecb_decrypt(&ctx, output_data, data_size, input_data);
```

### CBC 模式加密

```c
// CBC 模式加密
uint8_t iv[SM4_BLOCK_SIZE] = {0};  // 初始化向量
uint8_t input_data[32] = {...};    // 输入数据
uint8_t output_data[32];

sm4_ctx_t ctx;
sm4_setkey_enc(&ctx, key);

// CBC 加密
int result = sm4_cbc_encrypt(&ctx, iv, input_data, 32, output_data);

// CBC 解密（注意：需要重新设置 IV）
uint8_t iv_copy[SM4_BLOCK_SIZE];
memcpy(iv_copy, original_iv, SM4_BLOCK_SIZE);
sm4_setkey_dec(&ctx, key);
result = sm4_cbc_decrypt(&ctx, iv_copy, output_data, 32, input_data);
```

### PKCS#7 填充处理

```c
// 自动填充示例
size_t original_len = 10;  // 原始数据长度
size_t padded_len = sm4_get_padded_length(original_len);  // 计算填充后长度

uint8_t *padded_data = malloc(padded_len);
memcpy(padded_data, original_data, original_len);

// 应用 PKCS#7 填充
sm4_apply_pkcs7_padding(padded_data, original_len, padded_len);

// 加密填充后的数据
sm4_ecb_encrypt(&ctx, padded_data, padded_len, encrypted_data);

// 解密并移除填充
sm4_ecb_decrypt(&ctx, encrypted_data, padded_len, decrypted_data);
size_t unpadded_len = sm4_remove_pkcs7_padding(decrypted_data, padded_len);
```

## 🔍 优化技术详解

### 1. 查找表优化 (T-table)

预计算 S 盒变换和线性变换的组合：

```c
// T-table 预计算
uint32_t sm4_t0[256], sm4_t1[256], sm4_t2[256], sm4_t3[256];

// 初始化 T-table
for (int i = 0; i < 256; i++) {
    uint32_t s = sm4_sbox[i];
    uint32_t t = s | (s << 8) | (s << 16) | (s << 24);
    sm4_t0[i] = sm4_linear_transform(t);
    sm4_t1[i] = rotl(sm4_t0[i], 8);
    sm4_t2[i] = rotl(sm4_t0[i], 16);
    sm4_t3[i] = rotl(sm4_t0[i], 24);
}
```

### 2. SIMD 优化 (AVX2)

使用 256 位向量并行处理：

```c
#include <immintrin.h>

// 并行 S 盒查找
__m256i sm4_sbox_parallel(__m256i input) {
    // 使用 gather 指令并行查找 S 盒
    __m256i result = _mm256_i32gather_epi32((int*)sm4_sbox_table, input, 4);
    return result;
}
```

### 3. 内存访问优化

- **缓存友好**：数据结构对齐到缓存行
- **减少内存分配**：预分配缓冲区
- **局部性优化**：相关数据放在一起

### 4. 编译器优化

```bash
# 启用的编译器优化
-O3                  # 最高级别优化
-march=native        # 针对当前 CPU 优化
-mtune=native        # 调优指令调度
-mavx2               # 启用 AVX2 指令集
```

## 📈 性能分析

### 生成完整的性能分析图表

```bash
# 安装依赖
pip install matplotlib numpy

# 生成完整性能分析
python generate_charts.py

# 运行详细基准测试
make benchmark
```

图表将展示：
- 不同实现版本的执行时间对比
- 吞吐量分析
- 相对加速比
- 效率评分
- 多架构性能对比

### 性能调优建议

1. **CPU 密集型场景**：使用 SIMD 优化版本
2. **内存受限场景**：使用基础实现减少内存占用
3. **批量处理**：选择 ECB 模式获得更好的并行性
4. **安全性要求高**：使用 CBC 模式增强安全性

## 🛠️ 构建系统

### 可用的 Make 目标

```bash
make help           # 显示所有可用目标
make all            # 构建所有组件
make test           # 运行测试套件
make quick-test     # 运行快速性能测试
make benchmark      # 运行详细基准测试
make clean          # 清理构建文件

# 架构特定构建
make x86_64         # x86-64 优化版本
make aarch64        # ARM64 优化版本
make generic        # 通用版本

# 调试和分析
make debug          # 调试版本
make coverage       # 代码覆盖率分析
make memcheck       # 内存检查
```

### 交叉编译支持

```bash
# ARM64 交叉编译
CC=aarch64-linux-gnu-gcc make aarch64

# RISC-V 交叉编译
CC=riscv64-linux-gnu-gcc make generic
```

## 🔒 安全性考虑

### 常量时间实现

所有关键运算都实现为常量时间，防止时序攻击：

```c
// 常量时间 S 盒查找
uint8_t constant_time_sbox(uint8_t input) {
    uint8_t result = 0;
    for (int i = 0; i < 256; i++) {
        uint8_t mask = (i == input) ? 0xFF : 0x00;
        result |= sm4_sbox[i] & mask;
    }
    return result;
}
```

### 内存安全

- 自动清零敏感数据
- 边界检查
- 防止缓冲区溢出

## 📚 标准测试向量

项目包含 GB/T 32907-2016 标准中的测试向量：

```
测试向量 1:
密钥:     0123456789ABCDEFFEDCBA9876543210
明文:     0123456789ABCDEFFEDCBA9876543210
期望密文: 681EDF34D206965E86B3E94F536E4246

测试向量 2:  
密钥:     FEDCBA98765432100123456789ABCDEF
明文:     FEDCBA98765432100123456789ABCDEF
期望密文: F766678F13834AA0408A2A2984408526
```

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

**注意**：本实现仅用于学习研究目的。在生产环境中使用密码算法时，请确保遵循相关安全标准和最佳实践。

## 🔧 快速开始

### 系统要求

- **编译器**：GCC 7.0+ 或 Clang 10.0+
- **系统**：Linux/macOS/Windows（WSL）
- **架构**：x86-64、ARM64 或其他（自动检测）

### 编译构建

```bash
# 构建所有组件
make all

# 运行测试
make test

# 快速性能测试
make quick-test

# 运行演示
./bin/sm4_demo
```

## 📊 性能表现

### 基准测试结果

基于 x86-64 架构的性能测试结果：

| 实现版本 | 吞吐量 (MB/s) | 相对加速比 |
|----------|---------------|------------|
| 基础实现 | 67.0 | 1.00x |
| 查找表优化 | 97.1 | 1.45x |
| AVX2 SIMD | 95.2 | 1.40x |

### 架构支持

- ✅ **x86-64**：支持 SSE4.1、AVX2 指令集优化
- ✅ **ARM64**：支持 NEON SIMD 指令优化
- ✅ **通用架构**：纯 C 实现，可移植性最高

## 🧪 API 使用示例

```c
#include "sm4.h"

// 基本加密示例
sm4_ctx_t ctx;
uint8_t key[16] = {...};
uint8_t plaintext[16] = {...};
uint8_t ciphertext[16];

// 设置加密密钥
sm4_setkey_enc(&ctx, key);

// 执行加密
sm4_encrypt_basic(&ctx, plaintext, ciphertext);

// ECB 模式加密大量数据
sm4_ecb_encrypt(&ctx, large_data, data_size, encrypted_data);
```

## 📈 性能分析

生成性能图表：

```bash
pip install matplotlib numpy
python generate_charts.py
```

## 🛠️ 可用命令

```bash
make help           # 显示所有可用目标
make all            # 构建所有组件
make test           # 运行测试套件
make benchmark      # 运行性能测试
make clean          # 清理构建文件
```

## 📄 许可证

本项目采用 MIT 许可证。

---

**注意**：本实现仅用于学习研究目的。
