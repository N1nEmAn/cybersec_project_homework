#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include "../src/sm4.h"

static double get_time(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1000000.0;
}

void quick_benchmark(void) {
    printf("SM4 Quick Performance Test\n");
    printf("=========================\n\n");
    
    sm4_ctx_t ctx;
    uint8_t key[SM4_KEY_SIZE] = {
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
        0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
    };
    uint8_t input[SM4_BLOCK_SIZE] = {
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
        0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
    };
    uint8_t output[SM4_BLOCK_SIZE];
    
    sm4_setkey_enc(&ctx, key);
    
    const int iterations = 100000;
    
    /* Basic implementation test */
    double start = get_time();
    for (int i = 0; i < iterations; i++) {
        sm4_encrypt_basic(&ctx, input, output);
    }
    double basic_time = get_time() - start;
    
    /* Optimized implementation test */
    start = get_time();
    for (int i = 0; i < iterations; i++) {
        sm4_encrypt_optimized(&ctx, input, output);
    }
    double optimized_time = get_time() - start;
    
    printf("Basic Implementation:\n");
    printf("  Time: %.2f ms\n", basic_time * 1000);
    printf("  Throughput: %.2f MB/s\n", (SM4_BLOCK_SIZE * iterations / (1024.0 * 1024.0)) / basic_time);
    printf("\n");
    
    printf("Optimized Implementation:\n");
    printf("  Time: %.2f ms\n", optimized_time * 1000);
    printf("  Throughput: %.2f MB/s\n", (SM4_BLOCK_SIZE * iterations / (1024.0 * 1024.0)) / optimized_time);
    printf("  Speedup: %.2fx\n", basic_time / optimized_time);
    printf("\n");
    
#ifdef __x86_64__
    /* SIMD implementation test */
    start = get_time();
    for (int i = 0; i < iterations; i++) {
        sm4_encrypt_simd(&ctx, input, output);
    }
    double simd_time = get_time() - start;
    
    printf("SIMD (AVX2) Implementation:\n");
    printf("  Time: %.2f ms\n", simd_time * 1000);
    printf("  Throughput: %.2f MB/s\n", (SM4_BLOCK_SIZE * iterations / (1024.0 * 1024.0)) / simd_time);
    printf("  Speedup: %.2fx\n", basic_time / simd_time);
    printf("\n");
#endif

#ifdef __aarch64__
    /* NEON implementation test */
    start = get_time();
    for (int i = 0; i < iterations; i++) {
        sm4_encrypt_neon(&ctx, input, output);
    }
    double neon_time = get_time() - start;
    
    printf("NEON Implementation:\n");
    printf("  Time: %.2f ms\n", neon_time * 1000);
    printf("  Throughput: %.2f MB/s\n", (SM4_BLOCK_SIZE * iterations / (1024.0 * 1024.0)) / neon_time);
    printf("  Speedup: %.2fx\n", basic_time / neon_time);
    printf("\n");
#endif
}

int main(void) {
    quick_benchmark();
    return 0;
}
