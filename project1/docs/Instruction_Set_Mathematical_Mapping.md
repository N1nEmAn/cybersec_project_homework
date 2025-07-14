# 现代指令集数学映射与SM4优化

## 1. 指令集优化概述

现代x86-64处理器提供了多种专用指令集，可以显著加速密码学运算：

- **AESNI**：AES专用指令集
- **GFNI**：有限域指令集（Galois Field New Instructions）
- **VPROLD**：变长向量循环移位指令
- **CLMUL**：无进位乘法指令

## 2. AESNI指令集数学原理

### 2.1 AES与SM4的S盒相似性

**AES S盒构造**：
1. 有限域GF(2⁸)乘法逆元：y = x⁻¹
2. 仿射变换：z = Ay + b

**SM4 S盒构造**：
1. 有限域GF(2⁸)乘法逆元：y = x⁻¹（同AES）
2. 仿射变换：z = A'y + b'（参数不同）

### 2.2 AESNI指令数学描述

**AESENC指令**：
```
AESENC(state, round_key) = ShiftRows(MixColumns(SubBytes(state))) ⊕ round_key
```

**AESENCLAST指令**：
```
AESENCLAST(state, round_key) = ShiftRows(SubBytes(state)) ⊕ round_key
```

**AESIMC指令**：
```
AESIMC(state) = InvMixColumns(state)
```

### 2.3 SM4中的AESNI应用

**S盒加速策略**：
利用AESENC的SubBytes部分：

```c
__m128i aes_sbox_sm4(__m128i input) {
    // 使用AESENC的S盒变换，但需要调整
    __m128i temp = _mm_aesenc_si128(input, _mm_setzero_si128());
    // 需要逆转MixColumns和ShiftRows的影响
    temp = _mm_aesimc_si128(temp);
    // 应用仿射变换差异补偿
    return adjust_affine_transform(temp);
}
```

**数学推导**：
设AES仿射变换为A_aes·x + b_aes，SM4仿射变换为A_sm4·x + b_sm4

则需要计算：
```
SM4_sbox(x) = A_sm4·x⁻¹ + b_sm4
            = A_sm4·A_aes⁻¹·(A_aes·x⁻¹ + b_aes - b_aes) + b_sm4
            = A_sm4·A_aes⁻¹·AES_sbox(x) + adjustment
```

## 3. GFNI指令集数学原理

### 3.1 GFNI指令数学基础

**GF2P8AFFINEQB指令**：
执行8×8二进制矩阵与8维向量的仿射变换：

```
y = Ax + b (mod GF(2⁸))
```

其中：
- A：8×8二进制矩阵
- x：8位输入向量
- b：8位常数向量
- 运算在GF(2)上进行（即模2运算）

### 3.2 SM4 S盒的GFNI实现

**直接仿射变换**：
SM4的S盒可以表示为：
```
SM4_sbox(x) = A_sm4 · x⁻¹ + b_sm4
```

**分步实现**：
1. 计算乘法逆元：`inv_x = gf256_inverse(x)`
2. 应用仿射变换：`result = GF2P8AFFINEQB(inv_x, matrix, constant)`

**矩阵和常数计算**：
```c
// SM4仿射变换矩阵（行优先存储）
uint64_t sm4_affine_matrix = 0x8F1F3F7FEFDFDCBC;

// SM4仿射变换常数
uint8_t sm4_affine_constant = 0x63;

__m256i gfni_sm4_sbox(__m256i input) {
    // 首先计算乘法逆元（需要查表或专用算法）
    __m256i inverse = gf256_inverse_vector(input);
    
    // 应用仿射变换
    __m256i matrix = _mm256_set1_epi64x(sm4_affine_matrix);
    __m256i constant = _mm256_set1_epi8(sm4_affine_constant);
    
    return _mm256_gf2p8affine_epi64_epi8(inverse, matrix, constant);
}
```

### 3.3 GF(2⁸)乘法逆元的高效计算

**扩展欧几里得算法**：
```c
uint8_t gf256_inverse(uint8_t x) {
    if (x == 0) return 0;
    
    // 使用扩展欧几里得算法
    uint16_t a = x, b = 0x11B;  // 0x11B = x^8 + x^4 + x^3 + x + 1
    uint16_t u = 1, v = 0;
    
    while (a != 1) {
        uint8_t q = 0;
        uint16_t temp_a = a;
        while (temp_a >= b) {
            temp_a ^= b;
            q++;
        }
        
        a = temp_a;
        u ^= gf256_multiply(q, v);  // GF(2^8)乘法
        
        // 交换 (a,u) 和 (b,v)
        uint16_t temp = a; a = b; b = temp;
        temp = u; u = v; v = temp;
    }
    
    return (uint8_t)u;
}
```

## 4. VPROLD指令集优化

### 4.1 VPROLD指令数学描述

**VPROLD指令功能**：
```
VPROLD(src, count) = (src << count) | (src >> (32 - count))
```

支持向量化的变长循环左移，每个32位元素可以有不同的移位量。

### 4.2 SM4线性变换的VPROLD优化

**传统线性变换**：
```
L(B) = B ⊕ (B ≪ 2) ⊕ (B ≪ 10) ⊕ (B ≪ 18) ⊕ (B ≪ 24)
```

**VPROLD优化实现**：
```c
__m256i vprold_linear_transform(__m256i B) {
    // 创建移位量向量：[2, 10, 18, 24, 2, 10, 18, 24]
    __m256i shifts_2_10 = _mm256_set_epi32(10, 2, 10, 2, 10, 2, 10, 2);
    __m256i shifts_18_24 = _mm256_set_epi32(24, 18, 24, 18, 24, 18, 24, 18);
    
    // 并行计算多个移位
    __m256i rot_2_10 = _mm256_prolvd_epi32(B, shifts_2_10);
    __m256i rot_18_24 = _mm256_prolvd_epi32(B, shifts_18_24);
    
    // 重新排列和组合
    __m256i rot_2 = _mm256_shuffle_epi32(rot_2_10, 0xA0);   // 提取2位移位结果
    __m256i rot_10 = _mm256_shuffle_epi32(rot_2_10, 0xF5);  // 提取10位移位结果
    __m256i rot_18 = _mm256_shuffle_epi32(rot_18_24, 0xA0); // 提取18位移位结果
    __m256i rot_24 = _mm256_shuffle_epi32(rot_18_24, 0xF5); // 提取24位移位结果
    
    // 计算最终结果
    return _mm256_xor_si256(_mm256_xor_si256(B, rot_2),
                           _mm256_xor_si256(_mm256_xor_si256(rot_10, rot_18), rot_24));
}
```

### 4.3 性能分析

**指令数量对比**：
```
传统实现：5次32位移位 + 4次XOR = 9条指令
VPROLD优化：2次VPROLD + 数据重排 + 4次XOR ≈ 8条指令
```

**延迟分析**：
```
VPROLD延迟：1周期
数据重排延迟：1周期
总体减少约11%的执行时间
```

## 5. CLMUL指令在GCM模式中的应用

### 5.1 CLMUL数学原理

**无进位乘法**：
CLMUL执行两个64位多项式的乘法，不考虑进位：

```
CLMUL(a, b) = ∑ᵢ∑ⱼ aᵢbⱼ·x^(i+j)
```

结果是一个最多127次的多项式。

### 5.2 GF(2¹²⁸)乘法的CLMUL实现

**128位乘法分解**：
设a = a_H||a_L, b = b_H||b_L（各64位）

```
a(x)·b(x) = (a_H·x⁶⁴ + a_L)·(b_H·x⁶⁴ + b_L)
          = a_H·b_H·x¹²⁸ + (a_H·b_L + a_L·b_H)·x⁶⁴ + a_L·b_L
```

**Karatsuba算法优化**：
```c
__m128i gf128_multiply_clmul(__m128i a, __m128i b) {
    // 分离高低64位
    __m128i a_low = a;
    __m128i a_high = _mm_shuffle_epi32(a, 0x4E);
    __m128i b_low = b;
    __m128i b_high = _mm_shuffle_epi32(b, 0x4E);
    
    // 计算三个CLMUL
    __m128i low_product = _mm_clmulepi64_si128(a_low, b_low, 0x00);
    __m128i high_product = _mm_clmulepi64_si128(a_high, b_high, 0x11);
    
    // Karatsuba中间项
    __m128i a_xor = _mm_xor_si128(a_low, a_high);
    __m128i b_xor = _mm_xor_si128(b_low, b_high);
    __m128i middle = _mm_clmulepi64_si128(a_xor, b_xor, 0x00);
    middle = _mm_xor_si128(middle, _mm_xor_si128(low_product, high_product));
    
    // 组合结果并约简
    return gf128_reduce(low_product, middle, high_product);
}
```

### 5.3 模约简算法

**快速约简**：
利用约简多项式r(x) = x¹²⁸ + x⁷ + x² + x + 1的稀疏性：

```c
__m128i gf128_reduce(__m128i low, __m128i middle, __m128i high) {
    // r(x) = x^128 + x^7 + x^2 + x + 1
    // 约简多项式的低位表示
    const __m128i reduction_poly = _mm_set_epi32(0, 0, 0, 0x87);  // x^7 + x^2 + x + 1
    
    // 第一步约简：处理high部分
    __m128i high_reduced = _mm_clmulepi64_si128(high, reduction_poly, 0x01);
    
    // 第二步约简：处理middle的高位部分
    __m128i temp = _mm_xor_si128(middle, high_reduced);
    __m128i middle_high = _mm_shuffle_epi32(temp, 0x4E);
    __m128i middle_reduced = _mm_clmulepi64_si128(middle_high, reduction_poly, 0x01);
    
    // 最终结果
    __m128i result = _mm_xor_si128(low, _mm_xor_si128(temp, middle_reduced));
    
    return result;
}
```

## 6. 综合优化策略

### 6.1 指令集特性检测

**运行时检测**：
```c
typedef struct {
    bool has_aesni;
    bool has_gfni;
    bool has_vprold;
    bool has_avx2;
    bool has_clmul;
} cpu_features_t;

cpu_features_t detect_cpu_features() {
    cpu_features_t features = {0};
    
    uint32_t eax, ebx, ecx, edx;
    
    // 检测AESNI (CPUID.01H:ECX.AES[bit 25])
    __cpuid(1, eax, ebx, ecx, edx);
    features.has_aesni = (ecx >> 25) & 1;
    
    // 检测AVX2 (CPUID.(EAX=07H,ECX=0H):EBX.AVX2[bit 5])
    __cpuidex(7, 0, eax, ebx, ecx, edx);
    features.has_avx2 = (ebx >> 5) & 1;
    
    // 检测GFNI (CPUID.(EAX=07H,ECX=0H):ECX.GFNI[bit 8])
    features.has_gfni = (ecx >> 8) & 1;
    
    // 检测VPROLD (CPUID.(EAX=07H,ECX=0H):ECX.AVX512VBMI2[bit 6])
    features.has_vprold = (ecx >> 6) & 1;
    
    // 检测CLMUL (CPUID.01H:ECX.PCLMULQDQ[bit 1])
    __cpuid(1, eax, ebx, ecx, edx);
    features.has_clmul = (ecx >> 1) & 1;
    
    return features;
}
```

### 6.2 自适应实现选择

**优先级策略**：
```c
sm4_impl_t select_optimal_implementation(cpu_features_t features) {
    // 优先级从高到低
    if (features.has_gfni && features.has_vprold && features.has_avx2) {
        return SM4_IMPL_GFNI_VPROLD_AVX2;  // 最高性能
    }
    
    if (features.has_vprold && features.has_avx2) {
        return SM4_IMPL_VPROLD_AVX2;       // 次优选择
    }
    
    if (features.has_aesni && features.has_avx2) {
        return SM4_IMPL_AESNI_AVX2;        // 中等性能
    }
    
    if (features.has_avx2) {
        return SM4_IMPL_AVX2_TTABLE;       // SIMD + T-table
    }
    
    return SM4_IMPL_TTABLE;                // 基础优化
}
```

### 6.3 性能预测模型

**理论性能分析**：
```c
typedef struct {
    double base_performance;     // 基础性能 (MB/s)
    double ttable_speedup;      // T-table加速比
    double simd_speedup;        // SIMD加速比
    double aesni_speedup;       // AESNI加速比
    double gfni_speedup;        // GFNI加速比
    double vprold_speedup;      // VPROLD加速比
} performance_model_t;

double predict_performance(cpu_features_t features, performance_model_t model) {
    double perf = model.base_performance;
    
    perf *= model.ttable_speedup;  // T-table始终启用
    
    if (features.has_avx2) {
        perf *= model.simd_speedup;
    }
    
    if (features.has_aesni) {
        perf *= model.aesni_speedup;
    }
    
    if (features.has_gfni) {
        perf *= model.gfni_speedup;
    }
    
    if (features.has_vprold) {
        perf *= model.vprold_speedup;
    }
    
    return perf;
}
```

## 7. 实现验证与测试

### 7.1 正确性验证

**跨实现一致性测试**：
```c
void test_implementation_consistency() {
    uint8_t plaintext[16] = {/* 测试向量 */};
    uint8_t key[16] = {/* 测试密钥 */};
    uint8_t result_basic[16], result_optimized[16];
    
    // 测试所有可用实现
    sm4_encrypt_basic(plaintext, key, result_basic);
    sm4_encrypt_gfni_vprold(plaintext, key, result_optimized);
    
    assert(memcmp(result_basic, result_optimized, 16) == 0);
}
```

### 7.2 性能基准测试

**分层性能测试**：
```c
void benchmark_all_implementations() {
    cpu_features_t features = detect_cpu_features();
    
    printf("CPU Features: AESNI=%d, GFNI=%d, VPROLD=%d, AVX2=%d\n",
           features.has_aesni, features.has_gfni, 
           features.has_vprold, features.has_avx2);
    
    // 测试各种实现
    double perf_basic = benchmark_implementation(SM4_IMPL_BASIC);
    double perf_ttable = benchmark_implementation(SM4_IMPL_TTABLE);
    
    if (features.has_avx2) {
        double perf_simd = benchmark_implementation(SM4_IMPL_AVX2);
        printf("SIMD speedup: %.2fx\n", perf_simd / perf_basic);
    }
    
    if (features.has_gfni && features.has_vprold) {
        double perf_gfni = benchmark_implementation(SM4_IMPL_GFNI_VPROLD);
        printf("GFNI+VPROLD speedup: %.2fx\n", perf_gfni / perf_basic);
    }
}
```

## 结论

现代指令集为SM4算法优化提供了强大的工具：

1. **AESNI**：利用相似的S盒结构，但需要仔细处理仿射变换差异
2. **GFNI**：提供直接的S盒仿射变换加速，但乘法逆元计算仍是瓶颈
3. **VPROLD**：显著简化线性变换计算，减少指令数量
4. **CLMUL**：为GCM模式提供高效的有限域乘法

综合使用这些指令集可以实现显著的性能提升，理论上可达到基础实现的2-3倍性能。
