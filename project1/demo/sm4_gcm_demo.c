#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "../src/sm4_gcm.c"

int main() {
    uint8_t key[16] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
                       0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10};
    uint8_t iv[12] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B};
    uint8_t aad[16] = "Additional Data";
    uint8_t plaintext[32] = "Hello, this is a test for SM4-GCM!";
    uint8_t ciphertext[32];
    uint8_t decrypted[32];
    uint8_t tag[16];

    printf("Original plaintext: %s\n", plaintext);

    // Encrypt
    sm4_gcm_encrypt(key, iv, 12, aad, 15, plaintext, 32, ciphertext, tag, 16);
    printf("Ciphertext: ");
    for (int i = 0; i < 32; i++) printf("%02X", ciphertext[i]);
    printf("\nTag: ");
    for (int i = 0; i < 16; i++) printf("%02X", tag[i]);
    printf("\n");

    // Decrypt
    int ret = sm4_gcm_decrypt(key, iv, 12, aad, 15, ciphertext, 32, tag, 16, decrypted);
    if (ret == 0) {
        printf("Decrypted plaintext: %s\n", decrypted);
    } else {
        printf("Decryption failed!\n");
    }

    return 0;
}
