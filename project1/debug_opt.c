#include <stdio.h>
#include <stdint.h>
#include "../src/sm4.h"

extern uint32_t sm4_t0[256];
extern uint32_t sm4_t1[256];
extern uint32_t sm4_t2[256];
extern uint32_t sm4_t3[256];
extern int sm4_tables_initialized;

static uint32_t sm4_t_optimized(uint32_t x) {
    return sm4_t0[(x >> 24) & 0xFF] ^
           sm4_t1[(x >> 16) & 0xFF] ^
           sm4_t2[(x >> 8) & 0xFF] ^
           sm4_t3[x & 0xFF];
}

int main() {
    uint8_t key[16] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF, 
                       0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10};
    uint8_t plaintext[16] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF, 
                             0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10};
    
    sm4_ctx_t ctx;
    sm4_setkey_enc(&ctx, key);
    
    // 比较第一轮的计算
    uint32_t x[4];
    for (int i = 0; i < 4; i++) {
        x[i] = ((uint32_t)plaintext[i * 4] << 24) |
               ((uint32_t)plaintext[i * 4 + 1] << 16) |
               ((uint32_t)plaintext[i * 4 + 2] << 8) |
               ((uint32_t)plaintext[i * 4 + 3]);
    }
    
    printf("Input words: %08X %08X %08X %08X\n", x[0], x[1], x[2], x[3]);
    printf("Round key 0: %08X\n", ctx.rk[0]);
    
    uint32_t temp1 = x[1] ^ x[2] ^ x[3] ^ ctx.rk[0];
    printf("XOR result: %08X\n", temp1);
    
    uint32_t temp2_basic = sm4_l(sm4_tau(temp1));
    printf("Basic T result: %08X\n", temp2_basic);
    
    // Force table initialization
    sm4_encrypt_optimized(&ctx, plaintext, plaintext);  // dummy call to init tables
    uint32_t temp2_opt = sm4_t_optimized(temp1);
    printf("Optimized T result: %08X\n", temp2_opt);
    
    return 0;
}
