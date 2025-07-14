#ifndef SM4_GCM_H
#define SM4_GCM_H

#include <stdint.h>

typedef struct {
    uint8_t key[16];
} sm4_ctx_t;

void sm4_setkey_enc(sm4_ctx_t *ctx, const uint8_t key[16]);
void sm4_encrypt_block_optimized(sm4_ctx_t *ctx, const uint8_t input[16], uint8_t output[16]);

#endif // SM4_GCM_H
