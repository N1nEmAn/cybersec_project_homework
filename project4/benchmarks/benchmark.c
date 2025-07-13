#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include "../src/sm3.h"

#define TEST_DATA_SIZE (1024 * 1024)  // 1MB
#define NUM_ITERATIONS 1000

// Get current time in microseconds
static double get_time_us(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000000.0 + tv.tv_usec;
}

// Performance measurement structure
typedef struct {
    const char *name;
    void (*compress_func)(uint32_t state[8], const uint8_t block[64]);
    double time_us;
    double throughput_mbps;
    double cycles_per_byte;
} perf_result_t;

// CPU frequency estimation (simplified)
static double estimate_cpu_freq_ghz(void) {
    double start_time = get_time_us();
    volatile uint64_t cycles = 0;
    
    while (get_time_us() - start_time < 100000) { // 100ms
        cycles++;
    }
    
    double elapsed = get_time_us() - start_time;
    return (cycles / elapsed) * 1e-3; // Rough estimate
}

// Benchmark a specific SM3 implementation
static void benchmark_implementation(perf_result_t *result, const uint8_t *data, size_t len) {
    sm3_ctx_t ctx;
    uint8_t digest[SM3_DIGEST_SIZE];
    double start_time, end_time;
    int i;
    
    // Warm up
    for (i = 0; i < 10; i++) {
        sm3_init(&ctx);
        sm3_update(&ctx, data, len);
        sm3_final(&ctx, digest);
    }
    
    // Measure performance
    start_time = get_time_us();
    
    for (i = 0; i < NUM_ITERATIONS; i++) {
        sm3_init(&ctx);
        
        // Use specific compression function if provided
        if (result->compress_func) {
            const uint8_t *ptr = data;
            size_t remaining = len;
            uint32_t state[8];
            memcpy(state, ctx.state, sizeof(state));
            
            while (remaining >= SM3_BLOCK_SIZE) {
                result->compress_func(state, ptr);
                ptr += SM3_BLOCK_SIZE;
                remaining -= SM3_BLOCK_SIZE;
            }
        } else {
            sm3_update(&ctx, data, len);
            sm3_final(&ctx, digest);
        }
    }
    
    end_time = get_time_us();
    
    result->time_us = (end_time - start_time) / NUM_ITERATIONS;
    result->throughput_mbps = (len / (1024.0 * 1024.0)) / (result->time_us / 1000000.0);
    result->cycles_per_byte = (result->time_us * estimate_cpu_freq_ghz() * 1000) / len;
}

int main(void) {
    uint8_t *test_data;
    perf_result_t results[4];
    int i;
    
    printf("SM3 Performance Benchmark\n");
    printf("=========================\n\n");
    
    // Allocate test data
    test_data = malloc(TEST_DATA_SIZE);
    if (!test_data) {
        fprintf(stderr, "Failed to allocate test data\n");
        return 1;
    }
    
    // Initialize test data with pseudo-random pattern
    for (i = 0; i < TEST_DATA_SIZE; i++) {
        test_data[i] = (uint8_t)(i ^ (i >> 8) ^ (i >> 16));
    }
    
    // Setup benchmark configurations
    results[0].name = "Basic Implementation";
    results[0].compress_func = sm3_compress_basic;
    
    results[1].name = "Optimized Implementation";
    results[1].compress_func = sm3_compress_optimized;
    
#ifdef __x86_64__
    results[2].name = "SIMD (AVX2) Implementation";
    results[2].compress_func = sm3_compress_simd;
#elif __aarch64__
    results[2].name = "NEON Implementation";
    results[2].compress_func = sm3_compress_neon;
#else
    results[2].name = "Architecture-specific (Not Available)";
    results[2].compress_func = NULL;
#endif
    
    results[3].name = "Complete Hash Function";
    results[3].compress_func = NULL; // Use full hash function
    
    printf("Testing with %d MB of data, %d iterations\n\n", 
           TEST_DATA_SIZE / (1024 * 1024), NUM_ITERATIONS);
    
    // Run benchmarks
    for (i = 0; i < 4; i++) {
        if (results[i].compress_func || i == 3) {
            printf("Benchmarking: %s...", results[i].name);
            fflush(stdout);
            
            benchmark_implementation(&results[i], test_data, TEST_DATA_SIZE);
            
            printf(" Done\n");
        } else {
            printf("Skipping: %s (Not available on this platform)\n", results[i].name);
            results[i].time_us = 0;
            results[i].throughput_mbps = 0;
            results[i].cycles_per_byte = 0;
        }
    }
    
    // Print results
    printf("\nPerformance Results:\n");
    printf("====================\n");
    printf("%-30s %12s %15s %12s\n", 
           "Implementation", "Time (μs)", "Throughput (MB/s)", "Cycles/Byte");
    printf("%-30s %12s %15s %12s\n", 
           "---------------", "--------", "----------------", "-----------");
    
    for (i = 0; i < 4; i++) {
        if (results[i].time_us > 0) {
            printf("%-30s %12.2f %15.2f %12.2f\n",
                   results[i].name,
                   results[i].time_us,
                   results[i].throughput_mbps,
                   results[i].cycles_per_byte);
        }
    }
    
    // Calculate speedup ratios
    printf("\nSpeedup Analysis:\n");
    printf("=================\n");
    if (results[0].throughput_mbps > 0) {
        for (i = 1; i < 4; i++) {
            if (results[i].throughput_mbps > 0) {
                double speedup = results[i].throughput_mbps / results[0].throughput_mbps;
                printf("%-30s: %.2fx speedup\n", results[i].name, speedup);
            }
        }
    }
    
    // Test correctness
    printf("\nCorrectness Verification:\n");
    printf("========================\n");
    
    uint8_t digest_basic[SM3_DIGEST_SIZE];
    uint8_t digest_test[SM3_DIGEST_SIZE];
    const char *test_message = "abc";
    
    // Expected hash for "abc"
    const uint8_t expected[] = {
        0x66, 0xC7, 0xF0, 0xF4, 0x62, 0xEE, 0xED, 0xD9,
        0xD1, 0xF2, 0xD4, 0x6B, 0xDC, 0x10, 0xE4, 0xE2,
        0x41, 0x67, 0xC4, 0x87, 0x5C, 0xF2, 0xF7, 0xA2,
        0x29, 0x7D, 0xA0, 0x2B, 0x8F, 0x4B, 0xA8, 0xE0
    };
    
    sm3_hash((const uint8_t*)test_message, strlen(test_message), digest_basic);
    
    printf("Test vector \"abc\":\n");
    printf("Expected: ");
    for (i = 0; i < SM3_DIGEST_SIZE; i++) {
        printf("%02x", expected[i]);
    }
    printf("\nComputed: ");
    for (i = 0; i < SM3_DIGEST_SIZE; i++) {
        printf("%02x", digest_basic[i]);
    }
    printf("\nStatus: %s\n", 
           memcmp(digest_basic, expected, SM3_DIGEST_SIZE) == 0 ? "PASS" : "FAIL");
    
    free(test_data);
    return 0;
}
