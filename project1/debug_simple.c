#include <stdio.h>
#include <stdint.h>
#include "../src/sm4.h"

int main() {
    // 简单测试查找表是否正确
    // 测试T变换：输入0x12345678
    uint32_t test_input = 0x12345678;
    
    // 基本实现
    uint32_t basic_result = sm4_l(sm4_tau(test_input));
    
    printf("Test T transform with input: %08X\n", test_input);
    printf("Basic result: %08X\n", basic_result);
    
    // 测试S盒单个字节
    printf("S-box test:\n");
    printf("S[0x12] = %02X\n", sm4_sbox[0x12]);
    printf("S[0x34] = %02X\n", sm4_sbox[0x34]);
    printf("S[0x56] = %02X\n", sm4_sbox[0x56]);
    printf("S[0x78] = %02X\n", sm4_sbox[0x78]);
    
    // 计算tau变换的预期结果
    uint32_t tau_result = sm4_tau(test_input);
    printf("Tau result: %08X\n", tau_result);
    
    // 计算L变换的预期结果
    uint32_t l_result = sm4_l(tau_result);
    printf("L result: %08X\n", l_result);
    
    return 0;
}
