#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <time.h>
#include "../src/sm3.h"

void print_usage(const char *program_name) {
    printf("SM3 Hash Calculator\n");
    printf("==================\n\n");
    printf("Usage: %s [OPTIONS] [INPUT]\n\n", program_name);
    printf("Options:\n");
    printf("  -h, --help     Show this help message\n");
    printf("  -f, --file     Hash contents of file\n");
    printf("  -t, --test     Run built-in test vectors\n");
    printf("  -b, --bench    Run performance benchmark\n");
    printf("  -v, --verbose  Show detailed output\n");
    printf("  -x, --hex      Output in hexadecimal (default)\n");
    printf("  -B, --binary   Output in binary format\n");
    printf("\n");
    printf("Examples:\n");
    printf("  %s \"hello world\"           # Hash string\n", program_name);
    printf("  %s -f /path/to/file        # Hash file\n", program_name);
    printf("  %s -t                      # Run tests\n", program_name);
    printf("  echo \"test\" | %s           # Hash from stdin\n", program_name);
}

void print_hash_hex(const uint8_t *hash) {
    for (int i = 0; i < SM3_DIGEST_SIZE; i++) {
        printf("%02x", hash[i]);
    }
    printf("\n");
}

void print_hash_binary(const uint8_t *hash) {
    fwrite(hash, 1, SM3_DIGEST_SIZE, stdout);
}

int hash_file(const char *filename, int verbose) {
    FILE *file = fopen(filename, "rb");
    if (!file) {
        fprintf(stderr, "Error: Cannot open file '%s'\n", filename);
        return 1;
    }
    
    sm3_ctx_t ctx;
    uint8_t buffer[8192];
    uint8_t digest[SM3_DIGEST_SIZE];
    size_t bytes_read;
    size_t total_bytes = 0;
    
    sm3_init(&ctx);
    
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        sm3_update(&ctx, buffer, bytes_read);
        total_bytes += bytes_read;
    }
    
    sm3_final(&ctx, digest);
    fclose(file);
    
    if (verbose) {
        printf("File: %s\n", filename);
        printf("Size: %zu bytes\n", total_bytes);
        printf("SM3: ");
    }
    
    print_hash_hex(digest);
    return 0;
}

int hash_string(const char *input, int verbose) {
    uint8_t digest[SM3_DIGEST_SIZE];
    
    sm3_hash((const uint8_t*)input, strlen(input), digest);
    
    if (verbose) {
        printf("Input: \"%s\"\n", input);
        printf("Length: %zu bytes\n", strlen(input));
        printf("SM3: ");
    }
    
    print_hash_hex(digest);
    return 0;
}

int hash_stdin(int verbose) {
    sm3_ctx_t ctx;
    uint8_t buffer[8192];
    uint8_t digest[SM3_DIGEST_SIZE];
    size_t bytes_read;
    size_t total_bytes = 0;
    
    sm3_init(&ctx);
    
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), stdin)) > 0) {
        sm3_update(&ctx, buffer, bytes_read);
        total_bytes += bytes_read;
    }
    
    sm3_final(&ctx, digest);
    
    if (verbose) {
        printf("Input: <stdin>\n");
        printf("Size: %zu bytes\n", total_bytes);
        printf("SM3: ");
    }
    
    print_hash_hex(digest);
    return 0;
}

int run_tests(void) {
    printf("Running SM3 Test Vectors\n");
    printf("========================\n\n");
    
    struct {
        const char *input;
        const char *expected;
        const char *description;
    } test_cases[] = {
        {
            "abc",
            "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0",
            "Standard test vector: 'abc'"
        },
        {
            "",
            "1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b",
            "Empty string"
        },
        {
            "The quick brown fox jumps over the lazy dog",
            "ca27601ec96fa4c2b7e693b0bf9303c8fb8b59b096bd55c4a28a6b16b6b10b0d",
            "Standard phrase"
        }
    };
    
    int passed = 0;
    int total = sizeof(test_cases) / sizeof(test_cases[0]);
    
    for (int i = 0; i < total; i++) {
        uint8_t digest[SM3_DIGEST_SIZE];
        char hex_output[65];
        
        sm3_hash((const uint8_t*)test_cases[i].input, 
                strlen(test_cases[i].input), digest);
        
        for (int j = 0; j < SM3_DIGEST_SIZE; j++) {
            sprintf(hex_output + j * 2, "%02x", digest[j]);
        }
        
        printf("Test %d: %s\n", i + 1, test_cases[i].description);
        printf("Input:    \"%s\"\n", test_cases[i].input);
        printf("Expected: %s\n", test_cases[i].expected);
        printf("Computed: %s\n", hex_output);
        
        if (strcmp(hex_output, test_cases[i].expected) == 0) {
            printf("Result:   PASS ✓\n\n");
            passed++;
        } else {
            printf("Result:   FAIL ✗\n\n");
        }
    }
    
    printf("Test Results: %d/%d passed\n", passed, total);
    return (passed == total) ? 0 : 1;
}

int run_benchmark(void) {
    printf("SM3 Performance Benchmark\n");
    printf("=========================\n\n");
    
    const size_t sizes[] = {1024, 8192, 65536, 1048576}; // 1KB, 8KB, 64KB, 1MB
    const int iterations[] = {10000, 5000, 1000, 100};
    const int num_tests = sizeof(sizes) / sizeof(sizes[0]);
    
    for (int i = 0; i < num_tests; i++) {
        uint8_t *data = malloc(sizes[i]);
        if (!data) {
            fprintf(stderr, "Memory allocation failed\n");
            continue;
        }
        
        // Initialize with test pattern
        for (size_t j = 0; j < sizes[i]; j++) {
            data[j] = (uint8_t)(j & 0xFF);
        }
        
        clock_t start = clock();
        
        for (int iter = 0; iter < iterations[i]; iter++) {
            uint8_t digest[SM3_DIGEST_SIZE];
            sm3_hash(data, sizes[i], digest);
        }
        
        clock_t end = clock();
        double time_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0;
        double throughput = (sizes[i] * iterations[i]) / (1024.0 * 1024.0) / (time_ms / 1000.0);
        
        printf("Data size: %6zu bytes, Iterations: %5d, Time: %8.2f ms, Throughput: %8.2f MB/s\n",
               sizes[i], iterations[i], time_ms, throughput);
        
        free(data);
    }
    
    return 0;
}

int main(int argc, char *argv[]) {
    int opt;
    int verbose = 0;
    int binary_output = 0;
    int file_mode = 0;
    int test_mode = 0;
    int bench_mode = 0;
    
    static struct option long_options[] = {
        {"help",    no_argument,       0, 'h'},
        {"file",    no_argument,       0, 'f'},
        {"test",    no_argument,       0, 't'},
        {"bench",   no_argument,       0, 'b'},
        {"verbose", no_argument,       0, 'v'},
        {"hex",     no_argument,       0, 'x'},
        {"binary",  no_argument,       0, 'B'},
        {0, 0, 0, 0}
    };
    
    while ((opt = getopt_long(argc, argv, "hftbvxB", long_options, NULL)) != -1) {
        switch (opt) {
            case 'h':
                print_usage(argv[0]);
                return 0;
            case 'f':
                file_mode = 1;
                break;
            case 't':
                test_mode = 1;
                break;
            case 'b':
                bench_mode = 1;
                break;
            case 'v':
                verbose = 1;
                break;
            case 'x':
                binary_output = 0;
                break;
            case 'B':
                binary_output = 1;
                break;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }
    
    if (test_mode) {
        return run_tests();
    }
    
    if (bench_mode) {
        return run_benchmark();
    }
    
    if (file_mode) {
        if (optind >= argc) {
            fprintf(stderr, "Error: Filename required with -f option\n");
            return 1;
        }
        return hash_file(argv[optind], verbose);
    }
    
    if (optind < argc) {
        // Hash command line argument
        return hash_string(argv[optind], verbose);
    } else {
        // Hash from stdin
        return hash_stdin(verbose);
    }
}
