#include "sm3.h"
#include <string.h>

// SM3 initial hash values
static const uint32_t sm3_iv[8] = {
    0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
    0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E
};

// Initialize SM3 context
void sm3_init(sm3_ctx_t *ctx) {
    memcpy(ctx->state, sm3_iv, sizeof(sm3_iv));
    ctx->count = 0;
    memset(ctx->buffer, 0, SM3_BLOCK_SIZE);
}

// Basic SM3 compression function
void sm3_compress_basic(uint32_t state[8], const uint8_t block[64]) {
    uint32_t W[68], W1[64];
    uint32_t A, B, C, D, E, F, G, H;
    uint32_t SS1, SS2, TT1, TT2;
    int j;
    
    // Message expansion
    for (j = 0; j < 16; j++) {
        W[j] = ((uint32_t)block[j * 4] << 24) |
               ((uint32_t)block[j * 4 + 1] << 16) |
               ((uint32_t)block[j * 4 + 2] << 8) |
               ((uint32_t)block[j * 4 + 3]);
    }
    
    for (j = 16; j < 68; j++) {
        W[j] = P1(W[j-16] ^ W[j-9] ^ ROTL32(W[j-3], 15)) ^ ROTL32(W[j-13], 7) ^ W[j-6];
    }
    
    for (j = 0; j < 64; j++) {
        W1[j] = W[j] ^ W[j + 4];
    }
    
    // Initialize working variables
    A = state[0];
    B = state[1];
    C = state[2];
    D = state[3];
    E = state[4];
    F = state[5];
    G = state[6];
    H = state[7];
    
    // Main compression loop
    for (j = 0; j < 64; j++) {
        SS1 = ROTL32(ROTL32(A, 12) + E + ROTL32(T(j), j % 32), 7);
        SS2 = SS1 ^ ROTL32(A, 12);
        TT1 = FF(A, B, C, j) + D + SS2 + W1[j];
        TT2 = GG(E, F, G, j) + H + SS1 + W[j];
        D = C;
        C = ROTL32(B, 9);
        B = A;
        A = TT1;
        H = G;
        G = ROTL32(F, 19);
        F = E;
        E = P0(TT2);
    }
    
    // Update state
    state[0] ^= A;
    state[1] ^= B;
    state[2] ^= C;
    state[3] ^= D;
    state[4] ^= E;
    state[5] ^= F;
    state[6] ^= G;
    state[7] ^= H;
}

// Optimized SM3 compression function with loop unrolling
void sm3_compress_optimized(uint32_t state[8], const uint8_t block[64]) {
    uint32_t W[68], W1[64];
    uint32_t A, B, C, D, E, F, G, H;
    uint32_t SS1, SS2, TT1, TT2;
    int j;
    
    // Optimized message expansion
    for (j = 0; j < 16; j++) {
        W[j] = ((uint32_t)block[j * 4] << 24) |
               ((uint32_t)block[j * 4 + 1] << 16) |
               ((uint32_t)block[j * 4 + 2] << 8) |
               ((uint32_t)block[j * 4 + 3]);
    }
    
    // Unroll message expansion loop for better performance
    for (j = 16; j < 68; j += 4) {
        W[j] = P1(W[j-16] ^ W[j-9] ^ ROTL32(W[j-3], 15)) ^ ROTL32(W[j-13], 7) ^ W[j-6];
        W[j+1] = P1(W[j-15] ^ W[j-8] ^ ROTL32(W[j-2], 15)) ^ ROTL32(W[j-12], 7) ^ W[j-5];
        W[j+2] = P1(W[j-14] ^ W[j-7] ^ ROTL32(W[j-1], 15)) ^ ROTL32(W[j-11], 7) ^ W[j-4];
        W[j+3] = P1(W[j-13] ^ W[j-6] ^ ROTL32(W[j], 15)) ^ ROTL32(W[j-10], 7) ^ W[j-3];
    }
    
    for (j = 0; j < 64; j++) {
        W1[j] = W[j] ^ W[j + 4];
    }
    
    A = state[0]; B = state[1]; C = state[2]; D = state[3];
    E = state[4]; F = state[5]; G = state[6]; H = state[7];
    
    // Optimized compression with reduced branching
    for (j = 0; j < 16; j++) {
        SS1 = ROTL32(ROTL32(A, 12) + E + ROTL32(0x79CC4519, j), 7);
        SS2 = SS1 ^ ROTL32(A, 12);
        TT1 = (A ^ B ^ C) + D + SS2 + W1[j];
        TT2 = (E ^ F ^ G) + H + SS1 + W[j];
        D = C; C = ROTL32(B, 9); B = A; A = TT1;
        H = G; G = ROTL32(F, 19); F = E; E = P0(TT2);
    }
    
    for (j = 16; j < 64; j++) {
        SS1 = ROTL32(ROTL32(A, 12) + E + ROTL32(0x7A879D8A, j % 32), 7);
        SS2 = SS1 ^ ROTL32(A, 12);
        TT1 = ((A & B) | (A & C) | (B & C)) + D + SS2 + W1[j];
        TT2 = ((E & F) | ((~E) & G)) + H + SS1 + W[j];
        D = C; C = ROTL32(B, 9); B = A; A = TT1;
        H = G; G = ROTL32(F, 19); F = E; E = P0(TT2);
    }
    
    state[0] ^= A; state[1] ^= B; state[2] ^= C; state[3] ^= D;
    state[4] ^= E; state[5] ^= F; state[6] ^= G; state[7] ^= H;
}

// Update SM3 context with new data
void sm3_update(sm3_ctx_t *ctx, const uint8_t *data, size_t len) {
    size_t left = ctx->count % SM3_BLOCK_SIZE;
    size_t fill = SM3_BLOCK_SIZE - left;
    
    ctx->count += len;
    
    if (left && len >= fill) {
        memcpy(ctx->buffer + left, data, fill);
        sm3_compress_optimized(ctx->state, ctx->buffer);
        data += fill;
        len -= fill;
        left = 0;
    }
    
    while (len >= SM3_BLOCK_SIZE) {
        sm3_compress_optimized(ctx->state, data);
        data += SM3_BLOCK_SIZE;
        len -= SM3_BLOCK_SIZE;
    }
    
    if (len > 0) {
        memcpy(ctx->buffer + left, data, len);
    }
}

// Finalize SM3 hash computation
void sm3_final(sm3_ctx_t *ctx, uint8_t *digest) {
    uint64_t total_bits = ctx->count * 8;
    size_t left = ctx->count % SM3_BLOCK_SIZE;
    size_t pad_len = (left < 56) ? (56 - left) : (120 - left);
    uint8_t padding[128];
    int i;
    
    // Padding
    padding[0] = 0x80;
    memset(padding + 1, 0, pad_len - 1);
    
    // Append length
    for (i = 0; i < 8; i++) {
        padding[pad_len + i] = (uint8_t)(total_bits >> (56 - i * 8));
    }
    
    sm3_update(ctx, padding, pad_len + 8);
    
    // Output hash
    for (i = 0; i < 8; i++) {
        digest[i * 4] = (uint8_t)(ctx->state[i] >> 24);
        digest[i * 4 + 1] = (uint8_t)(ctx->state[i] >> 16);
        digest[i * 4 + 2] = (uint8_t)(ctx->state[i] >> 8);
        digest[i * 4 + 3] = (uint8_t)(ctx->state[i]);
    }
}

// One-shot SM3 hash function
void sm3_hash(const uint8_t *data, size_t len, uint8_t *digest) {
    sm3_ctx_t ctx;
    sm3_init(&ctx);
    sm3_update(&ctx, data, len);
    sm3_final(&ctx, digest);
}
