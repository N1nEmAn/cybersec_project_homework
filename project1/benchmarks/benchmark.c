#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include "../src/sm4.h"

/* High-resolution timer */
static double get_time(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1000000.0;
}

/* Benchmark function pointer type */
typedef void (*sm4_encrypt_func_t)(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]);

/* Benchmark structure */
typedef struct {
    const char *name;
    sm4_encrypt_func_t encrypt_func;
    void (*setkey_func)(sm4_ctx_t *ctx, const uint8_t key[SM4_KEY_SIZE]);
} benchmark_t;

/* Available benchmarks */
static const benchmark_t benchmarks[] = {
    {"Basic Implementation", sm4_encrypt_basic, sm4_setkey_enc},
    {"Optimized Implementation", sm4_encrypt_optimized, sm4_setkey_enc},
#ifdef __x86_64__
    {"SIMD (AVX2) Implementation", sm4_encrypt_simd, sm4_setkey_enc},
#endif
#ifdef __aarch64__
    {"NEON Implementation", sm4_encrypt_neon, sm4_setkey_enc},
#endif
};

static const int num_benchmarks = sizeof(benchmarks) / sizeof(benchmarks[0]);

/* Single block benchmark */
double benchmark_single_block(const benchmark_t *bench, int iterations) {
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
    
    bench->setkey_func(&ctx, key);
    
    double start = get_time();
    
    for (int i = 0; i < iterations; i++) {
        bench->encrypt_func(&ctx, input, output);
    }
    
    double end = get_time();
    return end - start;
}

/* Large data benchmark */
double benchmark_large_data(const benchmark_t *bench, size_t data_size, int iterations) {
    sm4_ctx_t ctx;
    uint8_t key[SM4_KEY_SIZE] = {
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
        0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
    };
    
    uint8_t *input = malloc(data_size);
    uint8_t *output = malloc(data_size);
    
    if (!input || !output) {
        free(input);
        free(output);
        return -1.0;
    }
    
    /* Initialize test data */
    for (size_t i = 0; i < data_size; i++) {
        input[i] = (uint8_t)(i & 0xFF);
    }
    
    bench->setkey_func(&ctx, key);
    
    double start = get_time();
    
    for (int iter = 0; iter < iterations; iter++) {
        for (size_t i = 0; i < data_size; i += SM4_BLOCK_SIZE) {
            bench->encrypt_func(&ctx, input + i, output + i);
        }
    }
    
    double end = get_time();
    
    free(input);
    free(output);
    
    return end - start;
}

/* Memory bandwidth test */
double benchmark_memory_bandwidth(size_t data_size) {
    uint8_t *src = malloc(data_size);
    uint8_t *dst = malloc(data_size);
    
    if (!src || !dst) {
        free(src);
        free(dst);
        return -1.0;
    }
    
    /* Initialize source data */
    for (size_t i = 0; i < data_size; i++) {
        src[i] = (uint8_t)(i & 0xFF);
    }
    
    double start = get_time();
    memcpy(dst, src, data_size);
    double end = get_time();
    
    free(src);
    free(dst);
    
    return end - start;
}

void run_single_block_benchmarks(void) {
    printf("Single Block Performance Benchmark\n");
    printf("==================================\n");
    
    const int iterations = 1000000;
    
    printf("Testing with %d iterations\n\n", iterations);
    printf("%-30s %15s %15s %15s\n", "Implementation", "Time (μs)", "Throughput (MB/s)", "Cycles/Byte");
    printf("%-30s %15s %15s %15s\n", "---------------", "--------", "----------------", "-----------");
    
    for (int i = 0; i < num_benchmarks; i++) {
        double time = benchmark_single_block(&benchmarks[i], iterations);
        
        if (time > 0) {
            double time_per_block_us = (time * 1000000.0) / iterations;
            double throughput_mbps = (SM4_BLOCK_SIZE / (1024.0 * 1024.0)) / (time / iterations);
            double cycles_per_byte = (time_per_block_us * 2400.0) / SM4_BLOCK_SIZE; /* Assume 2.4GHz CPU */
            
            printf("%-30s %15.2f %15.2f %15.2f\n", 
                   benchmarks[i].name, time_per_block_us, throughput_mbps, cycles_per_byte);
        } else {
            printf("%-30s %15s %15s %15s\n", benchmarks[i].name, "ERROR", "ERROR", "ERROR");
        }
    }
    printf("\n");
}

void run_large_data_benchmarks(void) {
    printf("Large Data Performance Benchmark\n");
    printf("================================\n");
    
    const size_t data_sizes[] = {1024, 8192, 65536, 1048576}; /* 1KB, 8KB, 64KB, 1MB */
    const int iterations[] = {10000, 1000, 100, 10};
    const int num_sizes = sizeof(data_sizes) / sizeof(data_sizes[0]);
    
    for (int size_idx = 0; size_idx < num_sizes; size_idx++) {
        size_t data_size = data_sizes[size_idx];
        int iter = iterations[size_idx];
        
        printf("Data size: %zu bytes, Iterations: %d\n", data_size, iter);
        printf("%-30s %15s %15s\n", "Implementation", "Time (ms)", "Throughput (MB/s)");
        printf("%-30s %15s %15s\n", "---------------", "---------", "----------------");
        
        for (int i = 0; i < num_benchmarks; i++) {
            double time = benchmark_large_data(&benchmarks[i], data_size, iter);
            
            if (time > 0) {
                double time_ms = time * 1000.0;
                double total_data_mb = (data_size * iter) / (1024.0 * 1024.0);
                double throughput_mbps = total_data_mb / time;
                
                printf("%-30s %15.2f %15.2f\n", 
                       benchmarks[i].name, time_ms, throughput_mbps);
            } else {
                printf("%-30s %15s %15s\n", benchmarks[i].name, "ERROR", "ERROR");
            }
        }
        printf("\n");
    }
}

void run_speedup_analysis(void) {
    printf("Speedup Analysis\n");
    printf("===============\n");
    
    const int iterations = 100000;
    const size_t data_size = 65536; /* 64KB */
    
    double baseline_time = -1.0;
    
    printf("Comparing against basic implementation baseline\n\n");
    printf("%-30s %15s %15s\n", "Implementation", "Time (ms)", "Speedup");
    printf("%-30s %15s %15s\n", "---------------", "---------", "-------");
    
    for (int i = 0; i < num_benchmarks; i++) {
        double time = benchmark_large_data(&benchmarks[i], data_size, iterations);
        
        if (time > 0) {
            double time_ms = time * 1000.0;
            
            if (i == 0) { /* Basic implementation as baseline */
                baseline_time = time;
                printf("%-30s %15.2f %15s\n", benchmarks[i].name, time_ms, "1.00x");
            } else {
                double speedup = baseline_time / time;
                printf("%-30s %15.2f %15.2fx\n", benchmarks[i].name, time_ms, speedup);
            }
        } else {
            printf("%-30s %15s %15s\n", benchmarks[i].name, "ERROR", "ERROR");
        }
    }
    printf("\n");
}

void run_memory_bandwidth_test(void) {
    printf("Memory Bandwidth Analysis\n");
    printf("========================\n");
    
    const size_t test_sizes[] = {1024, 8192, 65536, 1048576}; /* 1KB, 8KB, 64KB, 1MB */
    const int num_sizes = sizeof(test_sizes) / sizeof(test_sizes[0]);
    
    printf("%-15s %15s %15s\n", "Data Size", "Copy Time (ms)", "Bandwidth (MB/s)");
    printf("%-15s %15s %15s\n", "---------", "-------------", "---------------");
    
    for (int i = 0; i < num_sizes; i++) {
        double time = benchmark_memory_bandwidth(test_sizes[i]);
        
        if (time > 0) {
            double time_ms = time * 1000.0;
            double bandwidth = (test_sizes[i] / (1024.0 * 1024.0)) / time;
            
            printf("%-15zu %15.3f %15.2f\n", test_sizes[i], time_ms, bandwidth);
        }
    }
    printf("\n");
}

void run_cache_analysis(void) {
    printf("Cache Performance Analysis\n");
    printf("=========================\n");
    
    /* Test different data sizes to observe cache effects */
    const size_t cache_sizes[] = {
        1024,      /* L1 cache size */
        32768,     /* L2 cache size */
        262144,    /* L3 cache size */
        8388608    /* Main memory */
    };
    const char *cache_names[] = {"L1 Cache", "L2 Cache", "L3 Cache", "Main Memory"};
    const int num_cache_levels = sizeof(cache_sizes) / sizeof(cache_sizes[0]);
    
    printf("Testing cache effects with different data sizes\n\n");
    printf("%-15s %-30s %15s %15s\n", "Cache Level", "Implementation", "Time (ms)", "Throughput (MB/s)");
    printf("%-15s %-30s %15s %15s\n", "-----------", "---------------", "---------", "----------------");
    
    for (int cache_idx = 0; cache_idx < num_cache_levels; cache_idx++) {
        size_t data_size = cache_sizes[cache_idx];
        int iterations = 1000000 / (data_size / 1024); /* Adjust iterations based on size */
        
        for (int impl_idx = 0; impl_idx < num_benchmarks; impl_idx++) {
            double time = benchmark_large_data(&benchmarks[impl_idx], data_size, iterations);
            
            if (time > 0) {
                double time_ms = time * 1000.0;
                double total_data_mb = (data_size * iterations) / (1024.0 * 1024.0);
                double throughput = total_data_mb / time;
                
                const char *cache_name = (impl_idx == 0) ? cache_names[cache_idx] : "";
                printf("%-15s %-30s %15.2f %15.2f\n", 
                       cache_name, benchmarks[impl_idx].name, time_ms, throughput);
            }
        }
        printf("\n");
    }
}

int main(void) {
    printf("SM4 Performance Benchmark Suite\n");
    printf("===============================\n\n");
    
    printf("CPU Architecture: ");
#ifdef __x86_64__
    printf("x86-64 (AVX2 support available)\n");
#elif defined(__aarch64__)
    printf("ARM64 (NEON support available)\n");
#else
    printf("Generic\n");
#endif
    
    printf("Available implementations: %d\n\n", num_benchmarks);
    
    /* Run all benchmark categories */
    run_single_block_benchmarks();
    run_large_data_benchmarks();
    run_speedup_analysis();
    run_memory_bandwidth_test();
    run_cache_analysis();
    
    printf("Benchmark completed successfully!\n");
    
    return 0;
}
