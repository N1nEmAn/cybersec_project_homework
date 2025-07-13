#include "sm3.h"

#ifdef __x86_64__
#include <immintrin.h>

// Simplified SIMD implementation that falls back to basic operations
void sm3_compress_simd(uint32_t state[8], const uint8_t block[64]) {
    // For now, use the basic compression function to avoid compilation issues
    sm3_compress_basic(state, block);
}

void sm3_hash_simd(const uint8_t *input, size_t len, uint8_t output[32]) {
    // Use basic implementation
    sm3_hash(input, len, output);
}

#else

// Non-x86 fallback
void sm3_compress_simd(uint32_t state[8], const uint8_t block[64]) {
    sm3_compress_basic(state, block);
}

void sm3_hash_simd(const uint8_t *input, size_t len, uint8_t output[32]) {
    sm3_hash(input, len, output);
}

#endif
