#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <time.h>
#include "../src/sm4.h"

/* Test vectors for SM4 */
typedef struct {
    const char *description;
    uint8_t key[SM4_KEY_SIZE];
    uint8_t plaintext[SM4_BLOCK_SIZE];
    uint8_t ciphertext[SM4_BLOCK_SIZE];
} sm4_test_vector_t;

/* Standard SM4 test vectors */
static const sm4_test_vector_t test_vectors[] = {
    {
        "Standard Test Vector 1",
        {0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF, 0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10},
        {0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF, 0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10},
        {0x68, 0x1E, 0xDF, 0x34, 0xD2, 0x06, 0x96, 0x5E, 0x86, 0xB3, 0xE9, 0x4F, 0x53, 0x6E, 0x42, 0x46}
    },
    {
        "Standard Test Vector 2",
        {0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10, 0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF},
        {0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10, 0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF},
        {0xFC, 0xAD, 0x24, 0xD1, 0x1B, 0xE5, 0xED, 0x6F, 0x50, 0x85, 0x68, 0x71, 0x9E, 0xAB, 0x14, 0x62}
    }
};

void print_hex(const char *label, const uint8_t *data, size_t len) {
    printf("%s: ", label);
    for (size_t i = 0; i < len; i++) {
        printf("%02X", data[i]);
    }
    printf("\n");
}

int test_basic_encryption(void) {
    printf("Testing Basic SM4 Encryption/Decryption\n");
    printf("=======================================\n");
    
    int passed = 0;
    int total = sizeof(test_vectors) / sizeof(test_vectors[0]);
    
    for (int i = 0; i < total; i++) {
        sm4_ctx_t ctx;
        uint8_t output[SM4_BLOCK_SIZE];
        uint8_t decrypted[SM4_BLOCK_SIZE];
        
        printf("\nTest %d: %s\n", i + 1, test_vectors[i].description);
        
        /* Test encryption */
        sm4_setkey_enc(&ctx, test_vectors[i].key);
        sm4_encrypt_basic(&ctx, test_vectors[i].plaintext, output);
        
        print_hex("Key       ", test_vectors[i].key, SM4_KEY_SIZE);
        print_hex("Plaintext ", test_vectors[i].plaintext, SM4_BLOCK_SIZE);
        print_hex("Expected  ", test_vectors[i].ciphertext, SM4_BLOCK_SIZE);
        print_hex("Computed  ", output, SM4_BLOCK_SIZE);
        
        if (memcmp(output, test_vectors[i].ciphertext, SM4_BLOCK_SIZE) == 0) {
            printf("Encryption: PASS ✓\n");
        } else {
            printf("Encryption: FAIL ✗\n");
            continue;
        }
        
        /* Test decryption */
        sm4_setkey_dec(&ctx, test_vectors[i].key);
        sm4_decrypt_basic(&ctx, test_vectors[i].ciphertext, decrypted);
        
        print_hex("Decrypted ", decrypted, SM4_BLOCK_SIZE);
        
        if (memcmp(decrypted, test_vectors[i].plaintext, SM4_BLOCK_SIZE) == 0) {
            printf("Decryption: PASS ✓\n");
            passed++;
        } else {
            printf("Decryption: FAIL ✗\n");
        }
    }
    
    printf("\nBasic Tests: %d/%d passed\n", passed, total);
    return passed == total;
}

int test_optimized_encryption(void) {
    printf("\nTesting Optimized SM4 Encryption/Decryption\n");
    printf("==========================================\n");
    
    int passed = 0;
    int total = sizeof(test_vectors) / sizeof(test_vectors[0]);
    
    for (int i = 0; i < total; i++) {
        sm4_ctx_t ctx;
        uint8_t output[SM4_BLOCK_SIZE];
        uint8_t decrypted[SM4_BLOCK_SIZE];
        
        printf("\nTest %d: %s\n", i + 1, test_vectors[i].description);
        
        /* Test encryption */
        sm4_setkey_enc(&ctx, test_vectors[i].key);
        sm4_encrypt_optimized(&ctx, test_vectors[i].plaintext, output);
        
        if (memcmp(output, test_vectors[i].ciphertext, SM4_BLOCK_SIZE) == 0) {
            printf("Optimized Encryption: PASS ✓\n");
        } else {
            printf("Optimized Encryption: FAIL ✗\n");
            print_hex("Expected  ", test_vectors[i].ciphertext, SM4_BLOCK_SIZE);
            print_hex("Computed  ", output, SM4_BLOCK_SIZE);
            continue;
        }
        
        /* Test decryption */
        sm4_setkey_dec(&ctx, test_vectors[i].key);
        sm4_decrypt_optimized(&ctx, test_vectors[i].ciphertext, decrypted);
        
        if (memcmp(decrypted, test_vectors[i].plaintext, SM4_BLOCK_SIZE) == 0) {
            printf("Optimized Decryption: PASS ✓\n");
            passed++;
        } else {
            printf("Optimized Decryption: FAIL ✗\n");
            print_hex("Expected  ", test_vectors[i].plaintext, SM4_BLOCK_SIZE);
            print_hex("Computed  ", decrypted, SM4_BLOCK_SIZE);
        }
    }
    
    printf("\nOptimized Tests: %d/%d passed\n", passed, total);
    return passed == total;
}

int test_ecb_mode(void) {
    printf("\nTesting ECB Mode\n");
    printf("===============\n");
    
    const uint8_t key[SM4_KEY_SIZE] = {
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
        0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
    };
    
    const uint8_t plaintext[32] = {
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF, 0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10,
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF, 0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
    };
    
    sm4_ctx_t ctx;
    uint8_t encrypted[32];
    uint8_t decrypted[32];
    
    /* Test ECB encryption */
    sm4_setkey_enc(&ctx, key);
    if (sm4_ecb_encrypt(&ctx, plaintext, 32, encrypted) != 0) {
        printf("ECB encryption failed\n");
        return 0;
    }
    
    /* Test ECB decryption */
    sm4_setkey_dec(&ctx, key);
    if (sm4_ecb_decrypt(&ctx, encrypted, 32, decrypted) != 0) {
        printf("ECB decryption failed\n");
        return 0;
    }
    
    if (memcmp(plaintext, decrypted, 32) == 0) {
        printf("ECB Mode: PASS ✓\n");
        return 1;
    } else {
        printf("ECB Mode: FAIL ✗\n");
        print_hex("Original ", plaintext, 32);
        print_hex("Decrypted", decrypted, 32);
        return 0;
    }
}

int test_cbc_mode(void) {
    printf("\nTesting CBC Mode\n");
    printf("===============\n");
    
    const uint8_t key[SM4_KEY_SIZE] = {
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
        0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
    };
    
    uint8_t iv_enc[SM4_BLOCK_SIZE] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F
    };
    
    uint8_t iv_dec[SM4_BLOCK_SIZE] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F
    };
    
    const uint8_t plaintext[32] = {
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF, 0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10,
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF, 0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
    };
    
    sm4_ctx_t ctx;
    uint8_t encrypted[32];
    uint8_t decrypted[32];
    
    /* Test CBC encryption */
    sm4_setkey_enc(&ctx, key);
    if (sm4_cbc_encrypt(&ctx, iv_enc, plaintext, 32, encrypted) != 0) {
        printf("CBC encryption failed\n");
        return 0;
    }
    
    /* Test CBC decryption */
    sm4_setkey_dec(&ctx, key);
    if (sm4_cbc_decrypt(&ctx, iv_dec, encrypted, 32, decrypted) != 0) {
        printf("CBC decryption failed\n");
        return 0;
    }
    
    if (memcmp(plaintext, decrypted, 32) == 0) {
        printf("CBC Mode: PASS ✓\n");
        return 1;
    } else {
        printf("CBC Mode: FAIL ✗\n");
        print_hex("Original ", plaintext, 32);
        print_hex("Decrypted", decrypted, 32);
        return 0;
    }
}

int test_padding(void) {
    printf("\nTesting PKCS#7 Padding\n");
    printf("=====================\n");
    
    uint8_t data[32] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A};
    size_t original_len = 10;
    size_t padded_len;
    size_t unpadded_len;
    
    /* Add padding */
    padded_len = sm4_pkcs7_padding_add(data, original_len, 32);
    if (padded_len == 0) {
        printf("Padding addition failed\n");
        return 0;
    }
    
    printf("Original length: %zu\n", original_len);
    printf("Padded length: %zu\n", padded_len);
    print_hex("Padded data", data, padded_len);
    
    /* Remove padding */
    unpadded_len = sm4_pkcs7_padding_remove(data, padded_len);
    if (unpadded_len != original_len) {
        printf("Padding removal failed: expected %zu, got %zu\n", original_len, unpadded_len);
        return 0;
    }
    
    printf("Unpadded length: %zu\n", unpadded_len);
    printf("PKCS#7 Padding: PASS ✓\n");
    return 1;
}

int test_large_data(void) {
    printf("\nTesting Large Data Processing\n");
    printf("============================\n");
    
    const size_t test_size = 1024 * 1024; /* 1MB */
    uint8_t *plaintext = malloc(test_size);
    uint8_t *encrypted = malloc(test_size);
    uint8_t *decrypted = malloc(test_size);
    
    if (!plaintext || !encrypted || !decrypted) {
        printf("Memory allocation failed\n");
        free(plaintext);
        free(encrypted);
        free(decrypted);
        return 0;
    }
    
    /* Initialize test data */
    for (size_t i = 0; i < test_size; i++) {
        plaintext[i] = (uint8_t)(i & 0xFF);
    }
    
    const uint8_t key[SM4_KEY_SIZE] = {
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
        0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
    };
    
    sm4_ctx_t ctx;
    clock_t start, end;
    
    /* Test encryption */
    sm4_setkey_enc(&ctx, key);
    start = clock();
    if (sm4_ecb_encrypt(&ctx, plaintext, test_size, encrypted) != 0) {
        printf("Large data encryption failed\n");
        goto cleanup;
    }
    end = clock();
    double encrypt_time = ((double)(end - start)) / CLOCKS_PER_SEC;
    
    /* Test decryption */
    sm4_setkey_dec(&ctx, key);
    start = clock();
    if (sm4_ecb_decrypt(&ctx, encrypted, test_size, decrypted) != 0) {
        printf("Large data decryption failed\n");
        goto cleanup;
    }
    end = clock();
    double decrypt_time = ((double)(end - start)) / CLOCKS_PER_SEC;
    
    /* Verify */
    if (memcmp(plaintext, decrypted, test_size) == 0) {
        printf("Large Data Test: PASS ✓\n");
        printf("Data size: %zu bytes\n", test_size);
        printf("Encryption time: %.3f seconds (%.2f MB/s)\n", 
               encrypt_time, (test_size / (1024.0 * 1024.0)) / encrypt_time);
        printf("Decryption time: %.3f seconds (%.2f MB/s)\n", 
               decrypt_time, (test_size / (1024.0 * 1024.0)) / decrypt_time);
        
        free(plaintext);
        free(encrypted);
        free(decrypted);
        return 1;
    } else {
        printf("Large Data Test: FAIL ✗\n");
    }
    
cleanup:
    free(plaintext);
    free(encrypted);
    free(decrypted);
    return 0;
}

int main(void) {
    printf("SM4 Algorithm Test Suite\n");
    printf("========================\n\n");
    
    int total_tests = 0;
    int passed_tests = 0;
    
    /* Run all tests */
    if (test_basic_encryption()) passed_tests++;
    total_tests++;
    
    if (test_optimized_encryption()) passed_tests++;
    total_tests++;
    
    if (test_ecb_mode()) passed_tests++;
    total_tests++;
    
    if (test_cbc_mode()) passed_tests++;
    total_tests++;
    
    if (test_padding()) passed_tests++;
    total_tests++;
    
    if (test_large_data()) passed_tests++;
    total_tests++;
    
    printf("\n==================================================\n");
    printf("Test Results: %d/%d tests passed\n", passed_tests, total_tests);
    
    if (passed_tests == total_tests) {
        printf("All tests PASSED! ✓\n");
        return 0;
    } else {
        printf("Some tests FAILED! ✗\n");
        return 1;
    }
}
