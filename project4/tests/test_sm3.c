#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "../src/sm3.h"

// SM3 test vectors
typedef struct {
    const char *message;
    const char *expected_hex;
} test_vector_t;

static const test_vector_t test_vectors[] = {
    {
        "abc",
        "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0"
    },
    {
        "",
        "1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b"
    },
    {
        "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
        "debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732"
    },
    {
        "a",
        "623476ac18f65a2909e43c7fec61b49c7e764a91a18ccb82f1917a29c86c5e88"
    }
};

// Convert hex string to bytes
static void hex_to_bytes(const char *hex, uint8_t *bytes) {
    size_t len = strlen(hex);
    for (size_t i = 0; i < len; i += 2) {
        sscanf(hex + i, "%2hhx", &bytes[i / 2]);
    }
}

// Convert bytes to hex string
static void bytes_to_hex(const uint8_t *bytes, size_t len, char *hex) {
    for (size_t i = 0; i < len; i++) {
        sprintf(hex + i * 2, "%02x", bytes[i]);
    }
}

int main(void) {
    printf("SM3 Algorithm Test Suite\n");
    printf("========================\n\n");
    
    int total_tests = sizeof(test_vectors) / sizeof(test_vectors[0]);
    int passed = 0;
    
    for (int i = 0; i < total_tests; i++) {
        const test_vector_t *tv = &test_vectors[i];
        uint8_t computed_hash[SM3_DIGEST_SIZE];
        uint8_t expected_hash[SM3_DIGEST_SIZE];
        char computed_hex[65];
        
        printf("Test %d: ", i + 1);
        
        // Compute hash
        sm3_hash((const uint8_t*)tv->message, strlen(tv->message), computed_hash);
        
        // Convert to hex for comparison
        bytes_to_hex(computed_hash, SM3_DIGEST_SIZE, computed_hex);
        hex_to_bytes(tv->expected_hex, expected_hash);
        
        // Check result
        if (memcmp(computed_hash, expected_hash, SM3_DIGEST_SIZE) == 0) {
            printf("PASS\n");
            passed++;
        } else {
            printf("FAIL\n");
            printf("  Message: \"%s\"\n", tv->message);
            printf("  Expected: %s\n", tv->expected_hex);
            printf("  Computed: %s\n", computed_hex);
        }
    }
    
    printf("\n");
    printf("Results: %d/%d tests passed\n", passed, total_tests);
    
    // Additional functionality tests
    printf("\nFunctionality Tests:\n");
    printf("===================\n");
    
    // Test incremental hashing
    printf("Incremental hashing test: ");
    sm3_ctx_t ctx;
    uint8_t digest1[SM3_DIGEST_SIZE], digest2[SM3_DIGEST_SIZE];
    const char *msg = "The quick brown fox jumps over the lazy dog";
    
    // One-shot hash
    sm3_hash((const uint8_t*)msg, strlen(msg), digest1);
    
    // Incremental hash
    sm3_init(&ctx);
    sm3_update(&ctx, (const uint8_t*)"The quick brown fox ", 20);
    sm3_update(&ctx, (const uint8_t*)"jumps over the lazy dog", 23);
    sm3_final(&ctx, digest2);
    
    if (memcmp(digest1, digest2, SM3_DIGEST_SIZE) == 0) {
        printf("PASS\n");
    } else {
        printf("FAIL\n");
    }
    
    // Test large data
    printf("Large data test: ");
    uint8_t *large_data = malloc(1000000); // 1MB
    if (large_data) {
        memset(large_data, 0xAA, 1000000);
        sm3_hash(large_data, 1000000, digest1);
        printf("PASS (computed hash for 1MB data)\n");
        free(large_data);
    } else {
        printf("SKIP (memory allocation failed)\n");
    }
    
    return (passed == total_tests) ? 0 : 1;
}
