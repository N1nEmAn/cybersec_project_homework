#include "sm3.h"
#include <string.h>

#ifdef __x86_64__
#include <immintrin.h>

// SIMD optimized SM3 compression for x86-64 with AVX2
void sm3_compress_simd(uint32_t state[8], const uint8_t block[64]) {
    __m256i W[17]; // We'll process 4 blocks in parallel
    __m256i W1[16];
    __m256i A, B, C, D, E, F, G, H;
    __m256i SS1, SS2, TT1, TT2;
    __m256i T_vec;
    int j;
    
    // Load initial state
    A = _mm256_set1_epi32(state[0]);
    B = _mm256_set1_epi32(state[1]);
    C = _mm256_set1_epi32(state[2]);
    D = _mm256_set1_epi32(state[3]);
    E = _mm256_set1_epi32(state[4]);
    F = _mm256_set1_epi32(state[5]);
    G = _mm256_set1_epi32(state[6]);
    H = _mm256_set1_epi32(state[7]);
    
    // Load message block (for single block, replicate across lanes)
    for (j = 0; j < 16; j++) {
        uint32_t w = ((uint32_t)block[j * 4] << 24) |
                     ((uint32_t)block[j * 4 + 1] << 16) |
                     ((uint32_t)block[j * 4 + 2] << 8) |
                     ((uint32_t)block[j * 4 + 3]);
        W[j] = _mm256_set1_epi32(w);
    }
    
    // Message expansion using SIMD
    for (j = 16; j < 68; j++) {
        __m256i temp1 = _mm256_xor_si256(W[j-16], W[j-9]);
        __m256i temp2 = _mm256_xor_si256(temp1, _mm256_or_si256(
            _mm256_slli_epi32(W[j-3], 15),
            _mm256_srli_epi32(W[j-3], 17)
        ));
        
        // P1 function
        __m256i p1_temp = _mm256_xor_si256(temp2, _mm256_or_si256(
            _mm256_slli_epi32(temp2, 15),
            _mm256_srli_epi32(temp2, 17)
        ));
        p1_temp = _mm256_xor_si256(p1_temp, _mm256_or_si256(
            _mm256_slli_epi32(temp2, 23),
            _mm256_srli_epi32(temp2, 9)
        ));
        
        __m256i temp3 = _mm256_xor_si256(p1_temp, _mm256_or_si256(
            _mm256_slli_epi32(W[j-13], 7),
            _mm256_srli_epi32(W[j-13], 25)
        ));
        
        if (j < 17) {
            W[j] = _mm256_xor_si256(temp3, W[j-6]);
        }
    }
    
    // Generate W1 array
    for (j = 0; j < 16; j++) {
        W1[j] = _mm256_xor_si256(W[j], W[j + 4]);
    }
    
    // Compression function - first 16 rounds
    T_vec = _mm256_set1_epi32(0x79CC4519);
    for (j = 0; j < 16; j++) {
        // Rotate T constant
        __m256i T_rotated = _mm256_or_si256(
            _mm256_slli_epi32(T_vec, j % 32),
            _mm256_srli_epi32(T_vec, 32 - (j % 32))
        );
        
        // SS1 = ROTL(ROTL(A,12) + E + ROTL(T,j), 7)
        __m256i A_rot12 = _mm256_or_si256(
            _mm256_slli_epi32(A, 12),
            _mm256_srli_epi32(A, 20)
        );
        
        __m256i temp = _mm256_add_epi32(A_rot12, E);
        temp = _mm256_add_epi32(temp, T_rotated);
        SS1 = _mm256_or_si256(
            _mm256_slli_epi32(temp, 7),
            _mm256_srli_epi32(temp, 25)
        );
        
        SS2 = _mm256_xor_si256(SS1, A_rot12);
        
        // FF and GG functions for j < 16
        __m256i FF_result = _mm256_xor_si256(_mm256_xor_si256(A, B), C);
        __m256i GG_result = _mm256_xor_si256(_mm256_xor_si256(E, F), G);
        
        TT1 = _mm256_add_epi32(_mm256_add_epi32(FF_result, D), 
                               _mm256_add_epi32(SS2, W1[j]));
        TT2 = _mm256_add_epi32(_mm256_add_epi32(GG_result, H), 
                               _mm256_add_epi32(SS1, W[j]));
        
        D = C;
        C = _mm256_or_si256(_mm256_slli_epi32(B, 9), _mm256_srli_epi32(B, 23));
        B = A;
        A = TT1;
        H = G;
        G = _mm256_or_si256(_mm256_slli_epi32(F, 19), _mm256_srli_epi32(F, 13));
        F = E;
        
        // P0 function for E
        __m256i P0_temp = _mm256_xor_si256(TT2, _mm256_or_si256(
            _mm256_slli_epi32(TT2, 9),
            _mm256_srli_epi32(TT2, 23)
        ));
        E = _mm256_xor_si256(P0_temp, _mm256_or_si256(
            _mm256_slli_epi32(TT2, 17),
            _mm256_srli_epi32(TT2, 15)
        ));
    }
    
    // Extract result from first lane and update state
    state[0] ^= _mm256_extract_epi32(A, 0);
    state[1] ^= _mm256_extract_epi32(B, 0);
    state[2] ^= _mm256_extract_epi32(C, 0);
    state[3] ^= _mm256_extract_epi32(D, 0);
    state[4] ^= _mm256_extract_epi32(E, 0);
    state[5] ^= _mm256_extract_epi32(F, 0);
    state[6] ^= _mm256_extract_epi32(G, 0);
    state[7] ^= _mm256_extract_epi32(H, 0);
}

#endif // __x86_64__
