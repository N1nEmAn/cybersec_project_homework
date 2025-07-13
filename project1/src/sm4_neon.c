#include "sm4.h"

#ifdef __aarch64__
#include <arm_neon.h>

/* ARM NEON optimized implementation */

/* NEON helper functions */
static inline uint32x4_t sm4_rotl_neon(const uint32x4_t x, int n) {
    return vorrq_u32(vshlq_n_u32(x, n), vshrq_n_u32(x, 32 - n));
}

/* Vectorized S-box lookup using NEON */
static inline uint32x4_t sm4_sbox_neon(const uint32x4_t input) {
    uint8_t bytes[16];
    uint8_t result[16];
    int i;
    
    vst1q_u8(bytes, vreinterpretq_u8_u32(input));
    
    for (i = 0; i < 16; i++) {
        result[i] = sm4_sbox[bytes[i]];
    }
    
    return vreinterpretq_u32_u8(vld1q_u8(result));
}

/* Vectorized linear transformation L using NEON */
static inline uint32x4_t sm4_l_neon(const uint32x4_t b) {
    uint32x4_t result = b;
    result = veorq_u32(result, sm4_rotl_neon(b, 2));
    result = veorq_u32(result, sm4_rotl_neon(b, 10));
    result = veorq_u32(result, sm4_rotl_neon(b, 18));
    result = veorq_u32(result, sm4_rotl_neon(b, 24));
    return result;
}

/* Vectorized T transformation using NEON */
static inline uint32x4_t sm4_t_neon(const uint32x4_t x) {
    return sm4_l_neon(sm4_sbox_neon(x));
}

/* NEON SM4 encryption for 4 blocks in parallel */
void sm4_encrypt_neon_4blocks(const sm4_ctx_t *ctx, const uint8_t *input, uint8_t *output) {
    uint32x4_t x0, x1, x2, x3;
    uint32x4_t temp, rk_vec;
    int round, block, i;
    
    /* Load 4 blocks */
    uint32_t blocks[4][4];
    for (block = 0; block < 4; block++) {
        for (i = 0; i < 4; i++) {
            blocks[block][i] = ((uint32_t)input[block * 16 + i * 4] << 24) |
                              ((uint32_t)input[block * 16 + i * 4 + 1] << 16) |
                              ((uint32_t)input[block * 16 + i * 4 + 2] << 8) |
                              ((uint32_t)input[block * 16 + i * 4 + 3]);
        }
    }
    
    /* Load into NEON registers (4 blocks parallel) */
    x0 = vld1q_u32((uint32_t[]){blocks[0][0], blocks[1][0], blocks[2][0], blocks[3][0]});
    x1 = vld1q_u32((uint32_t[]){blocks[0][1], blocks[1][1], blocks[2][1], blocks[3][1]});
    x2 = vld1q_u32((uint32_t[]){blocks[0][2], blocks[1][2], blocks[2][2], blocks[3][2]});
    x3 = vld1q_u32((uint32_t[]){blocks[0][3], blocks[1][3], blocks[2][3], blocks[3][3]});
    
    /* 32 rounds of SM4 */
    for (round = 0; round < SM4_ROUNDS; round++) {
        /* Broadcast round key */
        rk_vec = vdupq_n_u32(ctx->rk[round]);
        
        /* Compute x1 ^ x2 ^ x3 ^ rk */
        temp = veorq_u32(x1, x2);
        temp = veorq_u32(temp, x3);
        temp = veorq_u32(temp, rk_vec);
        
        /* Apply T transformation */
        temp = sm4_t_neon(temp);
        
        /* x0 ^= T(x1 ^ x2 ^ x3 ^ rk) */
        x0 = veorq_u32(x0, temp);
        
        /* Rotate registers */
        uint32x4_t temp_reg = x0;
        x0 = x1;
        x1 = x2;
        x2 = x3;
        x3 = temp_reg;
    }
    
    /* Reverse final transformation */
    temp = x0; x0 = x3; x3 = temp;
    temp = x1; x1 = x2; x2 = temp;
    
    /* Store results back to blocks */
    vst1q_u32((uint32_t[]){blocks[0][0], blocks[1][0], blocks[2][0], blocks[3][0]}, x0);
    vst1q_u32((uint32_t[]){blocks[0][1], blocks[1][1], blocks[2][1], blocks[3][1]}, x1);
    vst1q_u32((uint32_t[]){blocks[0][2], blocks[1][2], blocks[2][2], blocks[3][2]}, x2);
    vst1q_u32((uint32_t[]){blocks[0][3], blocks[1][3], blocks[2][3], blocks[3][3]}, x3);
    
    /* Store output */
    for (block = 0; block < 4; block++) {
        for (i = 0; i < 4; i++) {
            output[block * 16 + i * 4] = (blocks[block][i] >> 24) & 0xFF;
            output[block * 16 + i * 4 + 1] = (blocks[block][i] >> 16) & 0xFF;
            output[block * 16 + i * 4 + 2] = (blocks[block][i] >> 8) & 0xFF;
            output[block * 16 + i * 4 + 3] = blocks[block][i] & 0xFF;
        }
    }
}

/* NEON SM4 Block Encryption */
void sm4_encrypt_neon(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]) {
    /* For single block, fall back to optimized version */
    sm4_encrypt_optimized(ctx, input, output);
}

/* NEON SM4 Block Decryption */
void sm4_decrypt_neon(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]) {
    /* For single block, fall back to optimized version */
    sm4_decrypt_optimized(ctx, input, output);
}

/* Parallel ECB encryption using NEON */
void sm4_ecb_encrypt_neon(const sm4_ctx_t *ctx, const uint8_t *input, size_t num_blocks, uint8_t *output) {
    size_t i;
    
    /* Process blocks in groups of 4 where possible */
    for (i = 0; i + 3 < num_blocks; i += 4) {
        sm4_encrypt_neon_4blocks(ctx, input + i * SM4_BLOCK_SIZE, output + i * SM4_BLOCK_SIZE);
    }
    
    /* Handle remaining blocks */
    for (; i < num_blocks; i++) {
        sm4_encrypt_optimized(ctx, input + i * SM4_BLOCK_SIZE, output + i * SM4_BLOCK_SIZE);
    }
}

void sm4_ecb_decrypt_neon(const sm4_ctx_t *ctx, const uint8_t *input, size_t num_blocks, uint8_t *output) {
    size_t i;
    
    /* Process blocks in groups of 4 where possible */
    for (i = 0; i + 3 < num_blocks; i += 4) {
        sm4_encrypt_neon_4blocks(ctx, input + i * SM4_BLOCK_SIZE, output + i * SM4_BLOCK_SIZE);
    }
    
    /* Handle remaining blocks */
    for (; i < num_blocks; i++) {
        sm4_decrypt_optimized(ctx, input + i * SM4_BLOCK_SIZE, output + i * SM4_BLOCK_SIZE);
    }
}

/* NEON optimized key schedule */
void sm4_setkey_enc_neon(sm4_ctx_t *ctx, const uint8_t key[SM4_KEY_SIZE]) {
    uint32x4_t k_vec, mk_vec, fk_vec, ck_vec;
    uint32_t k[4], mk[4];
    int i;
    
    /* Load key into 32-bit words */
    for (i = 0; i < 4; i++) {
        k[i] = ((uint32_t)key[i * 4] << 24) |
               ((uint32_t)key[i * 4 + 1] << 16) |
               ((uint32_t)key[i * 4 + 2] << 8) |
               ((uint32_t)key[i * 4 + 3]);
    }
    
    /* Load key and FK into NEON registers */
    k_vec = vld1q_u32(k);
    fk_vec = vld1q_u32(sm4_fk);
    
    /* Initialize with FK */
    mk_vec = veorq_u32(k_vec, fk_vec);
    vst1q_u32(mk, mk_vec);
    
    /* Generate round keys */
    for (i = 0; i < SM4_ROUNDS; i++) {
        uint32_t temp = mk[1] ^ mk[2] ^ mk[3] ^ sm4_ck[i];
        temp = sm4_tau(temp);
        temp = sm4_l_prime(temp);
        ctx->rk[i] = mk[0] ^ temp;
        
        mk[0] = mk[1];
        mk[1] = mk[2];
        mk[2] = mk[3];
        mk[3] = ctx->rk[i];
    }
}

#else

/* Fallback implementations for non-ARM64 architectures */
void sm4_encrypt_neon(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]) {
    sm4_encrypt_optimized(ctx, input, output);
}

void sm4_decrypt_neon(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]) {
    sm4_decrypt_optimized(ctx, input, output);
}

#endif /* __aarch64__ */
