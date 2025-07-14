#include <stdio.h>
#include <stdint.h>
#include "../src/sm4.h"

int main() {
    uint8_t key[16] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF, 
                       0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10};
    
    sm4_ctx_t ctx;
    sm4_setkey_enc(&ctx, key);
    
    printf("C implementation all round keys:\n");
    for (int i = 0; i < 32; i++) {
        printf("RK[%02d]: %08X\n", i, ctx.rk[i]);
    }
    
    return 0;
}
