#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../src/sm4.h"

void print_hex(const char *label, const uint8_t *data, size_t len) {
    printf("%s: ", label);
    for (size_t i = 0; i < len; i++) {
        printf("%02X", data[i]);
    }
    printf("\n");
}

void demo_basic_encryption(void) {
    printf("SM4 Basic Encryption Demo\n");
    printf("========================\n\n");
    
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
    
    /* Set up encryption key */
    sm4_setkey_enc(&ctx, key);
    
    print_hex("Key      ", key, SM4_KEY_SIZE);
    print_hex("Plaintext", plaintext, SM4_BLOCK_SIZE);
    
    /* Encrypt */
    sm4_encrypt_basic(&ctx, plaintext, ciphertext);
    print_hex("Encrypted", ciphertext, SM4_BLOCK_SIZE);
    
    /* Set up decryption key */
    sm4_setkey_dec(&ctx, key);
    
    /* Decrypt */
    sm4_decrypt_basic(&ctx, ciphertext, decrypted);
    print_hex("Decrypted", decrypted, SM4_BLOCK_SIZE);
    
    /* Verify */
    if (memcmp(plaintext, decrypted, SM4_BLOCK_SIZE) == 0) {
        printf("✓ Encryption/Decryption successful!\n");
    } else {
        printf("✗ Encryption/Decryption failed!\n");
    }
    printf("\n");
}

void demo_performance_comparison(void) {
    printf("Performance Comparison Demo\n");
    printf("==========================\n\n");
    
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
    
    const int iterations = 10000;
    clock_t start, end;
    
    printf("Testing %d iterations...\n\n", iterations);
    
    /* Basic implementation */
    start = clock();
    for (int i = 0; i < iterations; i++) {
        sm4_encrypt_basic(&ctx, input, output);
    }
    end = clock();
    double basic_time = ((double)(end - start)) / CLOCKS_PER_SEC * 1000;
    
    /* Optimized implementation */
    start = clock();
    for (int i = 0; i < iterations; i++) {
        sm4_encrypt_optimized(&ctx, input, output);
    }
    end = clock();
    double optimized_time = ((double)(end - start)) / CLOCKS_PER_SEC * 1000;
    
#ifdef __x86_64__
    /* SIMD implementation */
    start = clock();
    for (int i = 0; i < iterations; i++) {
        sm4_encrypt_simd(&ctx, input, output);
    }
    end = clock();
    double simd_time = ((double)(end - start)) / CLOCKS_PER_SEC * 1000;
#endif
    
    printf("Basic Implementation:     %.2f ms\n", basic_time);
    printf("Optimized Implementation: %.2f ms (%.2fx speedup)\n", 
           optimized_time, basic_time / optimized_time);
#ifdef __x86_64__
    printf("SIMD Implementation:      %.2f ms (%.2fx speedup)\n", 
           simd_time, basic_time / simd_time);
#endif
    printf("\n");
}

void demo_ecb_mode(void) {
    printf("ECB Mode Demo\n");
    printf("============\n\n");
    
    sm4_ctx_t ctx;
    uint8_t key[SM4_KEY_SIZE] = {
        0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
        0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
    };
    
    const char *message = "Hello SM4 World!";
    size_t msg_len = strlen(message);
    
    /* Add PKCS#7 padding */
    size_t padded_len = ((msg_len / SM4_BLOCK_SIZE) + 1) * SM4_BLOCK_SIZE;
    uint8_t *padded_msg = malloc(padded_len);
    uint8_t *encrypted = malloc(padded_len);
    uint8_t *decrypted = malloc(padded_len);
    
    /* Apply padding */
    memcpy(padded_msg, message, msg_len);
    uint8_t pad_value = padded_len - msg_len;
    for (size_t i = msg_len; i < padded_len; i++) {
        padded_msg[i] = pad_value;
    }
    
    printf("Original message: \"%s\"\n", message);
    printf("Message length: %zu bytes\n", msg_len);
    printf("Padded length: %zu bytes\n", padded_len);
    print_hex("Padded data", padded_msg, padded_len);
    
    /* Encrypt */
    sm4_setkey_enc(&ctx, key);
    sm4_ecb_encrypt(&ctx, padded_msg, padded_len, encrypted);
    print_hex("Encrypted  ", encrypted, padded_len);
    
    /* Decrypt */
    sm4_setkey_dec(&ctx, key);
    sm4_ecb_decrypt(&ctx, encrypted, padded_len, decrypted);
    print_hex("Decrypted  ", decrypted, padded_len);
    
    /* Remove padding */
    uint8_t pad_len = decrypted[padded_len - 1];
    if (pad_len <= SM4_BLOCK_SIZE) {
        decrypted[padded_len - pad_len] = '\0';
        printf("Recovered message: \"%s\"\n", (char*)decrypted);
    }
    
    free(padded_msg);
    free(encrypted);
    free(decrypted);
    printf("\n");
}

int main(void) {
    printf("SM4 Encryption Algorithm Demonstration\n");
    printf("======================================\n\n");
    
    printf("Architecture: ");
#ifdef __x86_64__
    printf("x86-64 (AVX2 support available)\n");
#elif defined(__aarch64__)
    printf("ARM64 (NEON support available)\n");
#else
    printf("Generic\n");
#endif
    printf("\n");
    
    demo_basic_encryption();
    demo_performance_comparison();
    demo_ecb_mode();
    
    printf("Demo completed successfully!\n");
    
    return 0;
}
