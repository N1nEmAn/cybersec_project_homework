#ifndef SM4_H
#define SM4_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* SM4 Constants */
#define SM4_BLOCK_SIZE 16
#define SM4_KEY_SIZE   16
#define SM4_ROUNDS     32

/* SM4 Context Structure */
typedef struct {
    uint32_t rk[SM4_ROUNDS]; // Round keys
} sm4_ctx_t;

/* SM4 S-Box */
extern const uint8_t sm4_sbox[256];
extern const uint8_t sm4_inv_sbox[256];

/* SM4 System Parameters */
extern const uint32_t sm4_fk[4];
extern const uint32_t sm4_ck[32];

/* Function Prototypes */

/* Key Schedule */
void sm4_setkey_enc(sm4_ctx_t *ctx, const uint8_t key[SM4_KEY_SIZE]);
void sm4_setkey_dec(sm4_ctx_t *ctx, const uint8_t key[SM4_KEY_SIZE]);

/* Basic Implementation */
void sm4_encrypt_basic(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]);
void sm4_decrypt_basic(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]);

/* Optimized Implementation with Lookup Table */
void sm4_encrypt_optimized(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]);
void sm4_decrypt_optimized(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]);

/* SIMD Optimized Implementation */
#ifdef __x86_64__
void sm4_encrypt_simd(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]);
void sm4_decrypt_simd(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]);
#endif

/* ARM NEON Optimized Implementation */
#ifdef __aarch64__
void sm4_encrypt_neon(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]);
void sm4_decrypt_neon(const sm4_ctx_t *ctx, const uint8_t input[SM4_BLOCK_SIZE], uint8_t output[SM4_BLOCK_SIZE]);
#endif

/* Utility Functions */
uint32_t sm4_rotl(uint32_t x, int n);
uint32_t sm4_tau(uint32_t a);
uint32_t sm4_l(uint32_t b);
uint32_t sm4_l_prime(uint32_t b);

/* Mode of Operation */
typedef enum {
    SM4_ECB,
    SM4_CBC,
    SM4_CFB,
    SM4_OFB,
    SM4_CTR
} sm4_mode_t;

/* ECB Mode */
int sm4_ecb_encrypt(const sm4_ctx_t *ctx, const uint8_t *input, size_t length, uint8_t *output);
int sm4_ecb_decrypt(const sm4_ctx_t *ctx, const uint8_t *input, size_t length, uint8_t *output);

/* CBC Mode */
int sm4_cbc_encrypt(const sm4_ctx_t *ctx, uint8_t iv[SM4_BLOCK_SIZE], 
                    const uint8_t *input, size_t length, uint8_t *output);
int sm4_cbc_decrypt(const sm4_ctx_t *ctx, uint8_t iv[SM4_BLOCK_SIZE], 
                    const uint8_t *input, size_t length, uint8_t *output);

/* CTR Mode */
int sm4_ctr_crypt(const sm4_ctx_t *ctx, uint8_t iv[SM4_BLOCK_SIZE], 
                  const uint8_t *input, size_t length, uint8_t *output);

/* Padding */
size_t sm4_pkcs7_padding_add(uint8_t *data, size_t length, size_t buffer_size);
size_t sm4_pkcs7_padding_remove(const uint8_t *data, size_t length);

/* High-level Interface */
int sm4_encrypt_data(const uint8_t key[SM4_KEY_SIZE], const uint8_t *input, 
                     size_t length, uint8_t *output, sm4_mode_t mode, uint8_t *iv);
int sm4_decrypt_data(const uint8_t key[SM4_KEY_SIZE], const uint8_t *input, 
                     size_t length, uint8_t *output, sm4_mode_t mode, uint8_t *iv);

#ifdef __cplusplus
}
#endif

#endif /* SM4_H */
