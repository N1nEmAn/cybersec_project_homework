#include "sm4_gcm.h"
#include <stdio.h>

int main() {
    sm4_ctx_t ctx;
    uint8_t key[16] = {0};
    uint8_t input[16] = {0};
    uint8_t output[16] = {0};

    sm4_setkey_enc(&ctx, key);
    sm4_encrypt_block_optimized(&ctx, input, output);

    printf("Encryption successful\n");
    return 0;
}