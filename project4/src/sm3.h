#ifndef SM3_H
#define SM3_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// SM3 constants
#define SM3_DIGEST_SIZE     32  // 256 bits
#define SM3_BLOCK_SIZE      64  // 512 bits
#define SM3_STATE_SIZE      8   // 8 x 32-bit words

// SM3 context structure
typedef struct {
    uint32_t state[SM3_STATE_SIZE];
    uint64_t count;
    uint8_t buffer[SM3_BLOCK_SIZE];
} sm3_ctx_t;

// Basic SM3 functions
void sm3_init(sm3_ctx_t *ctx);
void sm3_update(sm3_ctx_t *ctx, const uint8_t *data, size_t len);
void sm3_final(sm3_ctx_t *ctx, uint8_t *digest);
void sm3_hash(const uint8_t *data, size_t len, uint8_t *digest);

// Optimized implementations
void sm3_compress_basic(uint32_t state[8], const uint8_t block[64]);
void sm3_compress_optimized(uint32_t state[8], const uint8_t block[64]);

#ifdef __x86_64__
void sm3_compress_simd(uint32_t state[8], const uint8_t block[64]);
#endif

#ifdef __aarch64__
void sm3_compress_neon(uint32_t state[8], const uint8_t block[64]);
#endif

// Utility macros
#define ROTL32(x, n) (((x) << (n)) | ((x) >> (32 - (n))))
#define ROTR32(x, n) (((x) >> (n)) | ((x) << (32 - (n))))

// SM3 permutation functions
#define P0(x) ((x) ^ ROTL32((x), 9) ^ ROTL32((x), 17))
#define P1(x) ((x) ^ ROTL32((x), 15) ^ ROTL32((x), 23))

// SM3 boolean functions
#define FF(x, y, z, j) ((j) < 16 ? ((x) ^ (y) ^ (z)) : (((x) & (y)) | ((x) & (z)) | ((y) & (z))))
#define GG(x, y, z, j) ((j) < 16 ? ((x) ^ (y) ^ (z)) : (((x) & (y)) | ((~(x)) & (z))))

// SM3 constants
#define T(j) ((j) < 16 ? 0x79CC4519 : 0x7A879D8A)

#ifdef __cplusplus
}
#endif

#endif // SM3_H
