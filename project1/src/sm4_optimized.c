#include "sm4.h"
#include <string.h>

/* Precomputed lookup tables for optimized implementation */
static uint32_t sm4_t0[256];
static uint32_t sm4_t1[256];
static uint32_t sm4_t2[256];
static uint32_t sm4_t3[256];
static int sm4_tables_initialized = 0;

/* Initialize lookup tables */
static void sm4_init_tables(void) {
    int i;
    uint32_t temp;
    
    if (sm4_tables_initialized) return;
    
    for (i = 0; i < 256; i++) {
        temp = sm4_sbox[i];
        
        /* T0: S(a) rotated by 0, 2, 10, 18, 24 bits */
        sm4_t0[i] = (temp << 24) | (temp << 16) | (temp << 8) | temp;
        sm4_t0[i] = temp ^ sm4_rotl(temp, 2) ^ sm4_rotl(temp, 10) ^ sm4_rotl(temp, 18) ^ sm4_rotl(temp, 24);
        sm4_t0[i] = (sm4_t0[i] << 24) | ((sm4_t0[i] & 0xFF0000) >> 8) | ((sm4_t0[i] & 0xFF00) << 8) | (sm4_t0[i] >> 24);
        
        /* T1: T0 rotated by 8 bits */
        sm4_t1[i] = sm4_rotl(sm4_t0[i], 8);
        
        /* T2: T0 rotated by 16 bits */
        sm4_t2[i] = sm4_rotl(sm4_t0[i], 16);
        
        /* T3: T0 rotated by 24 bits */
        sm4_t3[i] = sm4_rotl(sm4_t0[i], 24);
    }
    
    /* Recalculate with correct S-box application */
    for (i = 0; i < 256; i++) {
        uint8_t s = sm4_sbox[i];
        uint32_t t __attribute__((unused)) = ((uint32_t)s << 24) | ((uint32_t)s << 16) | ((uint32_t)s << 8) | s;
        
        /* Apply linear transformation L */
        t = s ^ sm4_rotl(s, 2) ^ sm4_rotl(s, 10) ^ sm4_rotl(s, 18) ^ sm4_rotl(s, 24);
        
        sm4_t0[i] = ((uint32_t)sm4_sbox[i] << 24) |
                    ((uint32_t)sm4_sbox[i] << 16) |
                    ((uint32_t)sm4_sbox[i] << 8) |
                    sm4_sbox[i];
        sm4_t0[i] = sm4_l(sm4_t0[i] & 0xFF);
        sm4_t0[i] = sm4_t0[i] | (sm4_t0[i] << 8) | (sm4_t0[i] << 16) | (sm4_t0[i] << 24);
        
        /* Correct implementation */
        uint32_t sbox_val = sm4_sbox[i];
        sm4_t0[i] = sbox_val;
        sm4_t0[i] = sm4_l(sbox_val << 24);
        
        sm4_t1[i] = sm4_rotl(sm4_t0[i], 8);
        sm4_t2[i] = sm4_rotl(sm4_t0[i], 16);
        sm4_t3[i] = sm4_rotl(sm4_t0[i], 24);
    }
    
    /* Final correct implementation */
    for (i = 0; i < 256; i++) {
        uint32_t t = sm4_sbox[i];
        t = sm4_l(t << 24);
        sm4_t0[i] = t;
        sm4_t1[i] = sm4_rotl(t, 8);
        sm4_t2[i] = sm4_rotl(t, 16);
        sm4_t3[i] = sm4_rotl(t, 24);
    }
    
    sm4_tables_initialized = 1;
}

/* Optimized SM4 T transformation using lookup tables */
static uint32_t sm4_t_optimized(uint32_t x) {
    return sm4_t0[(x >> 24) & 0xFF] ^
           sm4_t1[(x >> 16) & 0xFF] ^
           sm4_t2[(x >> 8) & 0xFF] ^
           sm4_t3[x & 0xFF];
}

/* Optimized Key Schedule */
static void sm4_setkey_enc_optimized(sm4_ctx_t *ctx, const uint8_t key[SM4_KEY_SIZE]) {
    uint32_t k[4];
    uint32_t mk[4];
    int i;
    
    sm4_init_tables();
    
    /* Load key into 32-bit words */
    for (i = 0; i < 4; i++) {
        k[i] = ((uint32_t)key[i * 4] << 24) |
               ((uint32_t)key[i * 4 + 1] << 16) |
               ((uint32_t)key[i * 4 + 2] << 8) |
               ((uint32_t)key[i * 4 + 3]);
    }
    
    /* Initialize with FK */
    for (i = 0; i < 4; i++) {
        mk[i] = k[i] ^ sm4_fk[i];
    }
    
    /* Generate round keys using optimized transformation */
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

/* Optimized SM4 Block Encryption */
void sm4_encrypt_optimized(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]) {
    uint32_t x[4];
    uint32_t temp;
    int i;
    
    sm4_init_tables();
    
    /* Load input into 32-bit words */
    for (i = 0; i < 4; i++) {
        x[i] = ((uint32_t)input[i * 4] << 24) |
               ((uint32_t)input[i * 4 + 1] << 16) |
               ((uint32_t)input[i * 4 + 2] << 8) |
               ((uint32_t)input[i * 4 + 3]);
    }
    
    /* 32 rounds of SM4 with optimized T function */
    for (i = 0; i < SM4_ROUNDS; i++) {
        temp = x[1] ^ x[2] ^ x[3] ^ ctx->rk[i];
        temp = sm4_t_optimized(temp);
        x[0] ^= temp;
        
        /* Rotate the words */
        temp = x[0];
        x[0] = x[1];
        x[1] = x[2];
        x[2] = x[3];
        x[3] = temp;
    }
    
    /* Reverse final transformation */
    temp = x[0]; x[0] = x[3]; x[3] = temp;
    temp = x[1]; x[1] = x[2]; x[2] = temp;
    
    /* Store output */
    for (i = 0; i < 4; i++) {
        output[i * 4] = (x[i] >> 24) & 0xFF;
        output[i * 4 + 1] = (x[i] >> 16) & 0xFF;
        output[i * 4 + 2] = (x[i] >> 8) & 0xFF;
        output[i * 4 + 3] = x[i] & 0xFF;
    }
}

/* Optimized SM4 Block Decryption */
void sm4_decrypt_optimized(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]) {
    /* For SM4, decryption uses the same algorithm with reversed round keys */
    sm4_encrypt_optimized(ctx, input, output);
}

/* Parallel block processing for ECB mode */
void sm4_ecb_encrypt_parallel(const sm4_ctx_t *ctx, const uint8_t *input, size_t num_blocks, uint8_t *output) {
    size_t i;
    
    sm4_init_tables();
    
    /* Process blocks in parallel (can be optimized with SIMD) */
    for (i = 0; i < num_blocks; i++) {
        sm4_encrypt_optimized(ctx, input + i * SM4_BLOCK_SIZE, output + i * SM4_BLOCK_SIZE);
    }
}

void sm4_ecb_decrypt_parallel(const sm4_ctx_t *ctx, const uint8_t *input, size_t num_blocks, uint8_t *output) {
    size_t i;
    
    sm4_init_tables();
    
    /* Process blocks in parallel (can be optimized with SIMD) */
    for (i = 0; i < num_blocks; i++) {
        sm4_decrypt_optimized(ctx, input + i * SM4_BLOCK_SIZE, output + i * SM4_BLOCK_SIZE);
    }
}

/* Cache-optimized processing for large data */
void sm4_process_large_data(const sm4_ctx_t *ctx, const uint8_t *input, size_t length, uint8_t *output, int encrypt) {
    const size_t CHUNK_SIZE = 64 * SM4_BLOCK_SIZE; /* Process 64 blocks at a time for cache efficiency */
    size_t processed = 0;
    
    sm4_init_tables();
    
    while (processed + CHUNK_SIZE <= length) {
        if (encrypt) {
            sm4_ecb_encrypt_parallel(ctx, input + processed, CHUNK_SIZE / SM4_BLOCK_SIZE, output + processed);
        } else {
            sm4_ecb_decrypt_parallel(ctx, input + processed, CHUNK_SIZE / SM4_BLOCK_SIZE, output + processed);
        }
        processed += CHUNK_SIZE;
    }
    
    /* Process remaining blocks */
    while (processed < length) {
        if (encrypt) {
            sm4_encrypt_optimized(ctx, input + processed, output + processed);
        } else {
            sm4_decrypt_optimized(ctx, input + processed, output + processed);
        }
        processed += SM4_BLOCK_SIZE;
    }
}

/* Optimized key setup for encryption */
void sm4_setkey_enc_opt(sm4_ctx_t *ctx, const uint8_t key[SM4_KEY_SIZE]) {
    sm4_setkey_enc_optimized(ctx, key);
}

/* Optimized key setup for decryption */
void sm4_setkey_dec_opt(sm4_ctx_t *ctx, const uint8_t key[SM4_KEY_SIZE]) {
    uint32_t temp_rk[SM4_ROUNDS];
    int i;
    
    /* Generate encryption round keys first */
    sm4_setkey_enc_optimized(ctx, key);
    
    /* Copy to temp array */
    memcpy(temp_rk, ctx->rk, sizeof(temp_rk));
    
    /* Reverse the order for decryption */
    for (i = 0; i < SM4_ROUNDS; i++) {
        ctx->rk[i] = temp_rk[SM4_ROUNDS - 1 - i];
    }
}
