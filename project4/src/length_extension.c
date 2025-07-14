/**
 * SM3 Length Extension Attack Implementation
 * 
 * This file demonstrates the length extension attack against SM3 hash function.
 * The attack exploits the Merkle-Damgård construction to append data to a message
 * without knowing the original message, only its hash and length.
 * 
 * Attack scenario: 
 * - Attacker knows hash(secret || known_data) and len(secret || known_data)
 * - Attacker can compute hash(secret || known_data || padding || malicious_data)
 * - This breaks authentication schemes that use hash(secret || message)
 */

#include "sm3.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

/**
 * SM3 padding function implementation
 * This replicates the padding used in SM3 to construct the malicious payload
 */
size_t sm3_padding(size_t message_len, uint8_t* padding, size_t max_padding_len) {
    size_t bit_len = message_len * 8;
    size_t padding_len = 64 - ((message_len + 9) % 64);
    if (padding_len == 64) padding_len = 0;
    padding_len += 9; // 1 byte for 0x80 + 8 bytes for length
    
    if (padding_len > max_padding_len) {
        return 0; // Not enough space
    }
    
    // Add padding bit
    padding[0] = 0x80;
    
    // Add zero padding
    memset(padding + 1, 0, padding_len - 9);
    
    // Add original length in bits (big-endian)
    for (int i = 0; i < 8; i++) {
        padding[padding_len - 8 + i] = (bit_len >> (56 - i * 8)) & 0xFF;
    }
    
    return padding_len;
}

/**
 * Extract internal state from SM3 hash output
 * Since SM3 outputs the internal state directly, we can use it to continue hashing
 */
void extract_sm3_state(const uint8_t hash[32], uint32_t state[8]) {
    for (int i = 0; i < 8; i++) {
        state[i] = (hash[i*4] << 24) | (hash[i*4+1] << 16) | 
                   (hash[i*4+2] << 8) | hash[i*4+3];
    }
}

/**
 * Continue SM3 hashing from a known internal state
 * This is the core of the length extension attack
 */
void sm3_continue_from_state(const uint32_t initial_state[8], 
                            const uint8_t* additional_data, size_t data_len,
                            size_t original_length, uint8_t result_hash[32]) {
    sm3_context_t ctx;
    
    // Set the internal state to the extracted state
    memcpy(ctx.state, initial_state, sizeof(ctx.state));
    
    // Set the count to the length after padding of the original message
    size_t padded_length = original_length;
    padded_length += 1; // for 0x80 byte
    padded_length += (64 - ((original_length + 9) % 64)) % 64; // zero padding
    padded_length += 8; // for length field
    ctx.count = padded_length;
    
    // Process the additional data
    sm3_update(&ctx, additional_data, data_len);
    
    // Finalize to get the extended hash
    sm3_final(&ctx, result_hash);
}

/**
 * Perform length extension attack
 * 
 * @param known_hash: The hash we want to extend (32 bytes)
 * @param original_length: Length of the original message (including secret)
 * @param additional_data: Data to append after the padding
 * @param additional_len: Length of additional data
 * @param extended_message: Output buffer for the full extended message
 * @param extended_hash: Output buffer for the hash of extended message
 * @return: Length of the extended message, or 0 on error
 */
size_t sm3_length_extension_attack(const uint8_t known_hash[32], 
                                  size_t original_length,
                                  const uint8_t* additional_data, size_t additional_len,
                                  uint8_t* extended_message, uint8_t extended_hash[32]) {
    
    // Step 1: Calculate the padding that was used in the original hash
    uint8_t padding[128];
    size_t padding_len = sm3_padding(original_length, padding, sizeof(padding));
    if (padding_len == 0) {
        return 0; // Error in padding calculation
    }
    
    // Step 2: Construct the extended message
    // extended_message = original_message || padding || additional_data
    // We don't know original_message, but we can provide padding || additional_data
    size_t extended_length = padding_len + additional_len;
    memcpy(extended_message, padding, padding_len);
    memcpy(extended_message + padding_len, additional_data, additional_len);
    
    // Step 3: Extract internal state from known hash
    uint32_t state[8];
    extract_sm3_state(known_hash, state);
    
    // Step 4: Continue hashing from the extracted state
    sm3_continue_from_state(state, additional_data, additional_len, 
                           original_length, extended_hash);
    
    return extended_length;
}

/**
 * Demonstrate a practical length extension attack scenario
 * Simulates an authentication bypass where MAC = hash(secret || message)
 */
void demonstrate_length_extension_attack(void) {
    printf("=== SM3 Length Extension Attack Demonstration ===\n\n");
    
    // Step 1: Simulate the original scenario
    const char* secret = "mysecretkey123";
    const char* original_message = "transfer $100 to Alice";
    char original_full[256];
    snprintf(original_full, sizeof(original_full), "%s%s", secret, original_message);
    
    uint8_t original_hash[32];
    sm3_hash((uint8_t*)original_full, strlen(original_full), original_hash);
    
    printf("1. Original scenario:\n");
    printf("   Secret: %s\n", secret);
    printf("   Message: %s\n", original_message);
    printf("   Full input: %s\n", original_full);
    printf("   Hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02x", original_hash[i]);
    }
    printf("\n\n");
    
    // Step 2: Attacker's scenario (only knows hash and length)
    size_t known_length = strlen(original_full);
    const char* malicious_data = " and $1000 to Mallory";
    
    printf("2. Attacker's knowledge:\n");
    printf("   Known hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02x", original_hash[i]);
    }
    printf("\n");
    printf("   Known total length: %zu\n", known_length);
    printf("   Malicious addition: %s\n", malicious_data);
    printf("\n");
    
    // Step 3: Perform the length extension attack
    uint8_t extended_suffix[256];
    uint8_t extended_hash[32];
    size_t suffix_len = sm3_length_extension_attack(
        original_hash, known_length,
        (uint8_t*)malicious_data, strlen(malicious_data),
        extended_suffix, extended_hash
    );
    
    printf("3. Attack result:\n");
    printf("   Extended hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02x", extended_hash[i]);
    }
    printf("\n");
    printf("   Extension suffix length: %zu bytes\n", suffix_len);
    printf("   Extension suffix (hex): ");
    for (size_t i = 0; i < suffix_len && i < 64; i++) {
        printf("%02x", extended_suffix[i]);
    }
    if (suffix_len > 64) printf("...");
    printf("\n\n");
    
    // Step 4: Verify the attack by computing the full extended message hash
    char full_extended[512];
    snprintf(full_extended, sizeof(full_extended), "%s", original_full);
    memcpy(full_extended + strlen(original_full), extended_suffix, suffix_len);
    size_t full_extended_len = strlen(original_full) + suffix_len;
    
    uint8_t verification_hash[32];
    sm3_hash((uint8_t*)full_extended, full_extended_len, verification_hash);
    
    printf("4. Verification:\n");
    printf("   Full extended message length: %zu\n", full_extended_len);
    printf("   Computed hash: ");
    for (int i = 0; i < 32; i++) {
        printf("%02x", verification_hash[i]);
    }
    printf("\n");
    
    // Check if hashes match
    int match = memcmp(extended_hash, verification_hash, 32) == 0;
    printf("   Attack successful: %s\n", match ? "YES" : "NO");
    
    if (match) {
        printf("\n   The attacker can now present:\n");
        printf("   - Message: %s[padding]%s\n", original_message, malicious_data);
        printf("   - Hash: ");
        for (int i = 0; i < 32; i++) {
            printf("%02x", extended_hash[i]);
        }
        printf("\n");
        printf("   This will be accepted as a valid MAC!\n");
    }
    
    printf("\n");
}

/**
 * Analyze the vulnerability in different authentication schemes
 */
void analyze_vulnerable_schemes(void) {
    printf("=== Vulnerable Authentication Schemes ===\n\n");
    
    printf("1. Vulnerable: MAC = hash(secret || message)\n");
    printf("   - Susceptible to length extension attacks\n");
    printf("   - Attacker can append data without knowing the secret\n\n");
    
    printf("2. Secure: MAC = hash(message || secret)\n");
    printf("   - Not vulnerable to length extension\n");
    printf("   - Secret is processed last, not accessible for extension\n\n");
    
    printf("3. Secure: HMAC = hash(secret ^ opad || hash(secret ^ ipad || message))\n");
    printf("   - Uses nested hashing with different keys\n");
    printf("   - Immune to length extension attacks\n\n");
    
    printf("4. Mitigation strategies:\n");
    printf("   - Use HMAC instead of hash(secret || message)\n");
    printf("   - Use authenticated encryption (AES-GCM, ChaCha20-Poly1305)\n");
    printf("   - Include message length in the MAC computation\n");
    printf("   - Use cryptographic signature schemes\n\n");
}

/**
 * Benchmark the length extension attack performance
 */
double benchmark_length_extension_attack(int iterations) {
    const char* secret = "secret123";
    const char* message = "Hello, World!";
    const char* malicious = " Malicious addition";
    
    char full_msg[256];
    snprintf(full_msg, sizeof(full_msg), "%s%s", secret, message);
    
    uint8_t original_hash[32];
    sm3_hash((uint8_t*)full_msg, strlen(full_msg), original_hash);
    
    clock_t start = clock();
    
    for (int i = 0; i < iterations; i++) {
        uint8_t extended_suffix[256];
        uint8_t extended_hash[32];
        
        sm3_length_extension_attack(
            original_hash, strlen(full_msg),
            (uint8_t*)malicious, strlen(malicious),
            extended_suffix, extended_hash
        );
    }
    
    clock_t end = clock();
    
    double time_taken = ((double)(end - start)) / CLOCKS_PER_SEC;
    return iterations / time_taken; // attacks per second
}

/**
 * Test length extension attack with various message lengths
 */
void test_attack_with_various_lengths(void) {
    printf("=== Testing Attack with Various Message Lengths ===\n\n");
    
    const char* secret = "secret";
    const char* malicious = " appended by attacker";
    
    size_t test_lengths[] = {10, 55, 56, 63, 64, 65, 120, 128, 200};
    int num_tests = sizeof(test_lengths) / sizeof(test_lengths[0]);
    
    for (int i = 0; i < num_tests; i++) {
        size_t msg_len = test_lengths[i];
        
        // Create message of specified length
        char* message = malloc(msg_len + 1);
        memset(message, 'A', msg_len);
        message[msg_len] = '\0';
        
        char* full_msg = malloc(strlen(secret) + msg_len + 1);
        sprintf(full_msg, "%s%s", secret, message);
        
        // Compute original hash
        uint8_t original_hash[32];
        sm3_hash((uint8_t*)full_msg, strlen(full_msg), original_hash);
        
        // Perform attack
        uint8_t extended_suffix[256];
        uint8_t extended_hash[32];
        size_t suffix_len = sm3_length_extension_attack(
            original_hash, strlen(full_msg),
            (uint8_t*)malicious, strlen(malicious),
            extended_suffix, extended_hash
        );
        
        // Verify attack
        char* full_extended = malloc(strlen(full_msg) + suffix_len + 1);
        memcpy(full_extended, full_msg, strlen(full_msg));
        memcpy(full_extended + strlen(full_msg), extended_suffix, suffix_len);
        
        uint8_t verification_hash[32];
        sm3_hash((uint8_t*)full_extended, strlen(full_msg) + suffix_len, verification_hash);
        
        int success = memcmp(extended_hash, verification_hash, 32) == 0;
        
        printf("Length %3zu: %s (suffix: %zu bytes)\n", 
               strlen(full_msg), success ? "SUCCESS" : "FAILED", suffix_len);
        
        free(message);
        free(full_msg);
        free(full_extended);
    }
    
    printf("\n");
}

/**
 * Educational demonstration of the mathematical foundation
 */
void explain_attack_mathematics(void) {
    printf("=== Mathematical Foundation of Length Extension Attack ===\n\n");
    
    printf("SM3 uses the Merkle-Damgård construction:\n");
    printf("  hash(M) = f(f(f(IV, M₁), M₂), M₃, ..., Mₙ)\n\n");
    
    printf("For a message M = secret || known_message:\n");
    printf("  1. Message is padded: M' = M || padding\n");
    printf("  2. M' is split into blocks: M' = M₁ || M₂ || ... || Mₙ\n");
    printf("  3. Hash is computed: H = f(...f(f(IV, M₁), M₂)..., Mₙ)\n\n");
    
    printf("The attack exploits that:\n");
    printf("  1. The hash output reveals the internal state after processing M'\n");
    printf("  2. We can use this state as a new IV for additional blocks\n");
    printf("  3. hash(M' || additional) = f(H, additional_blocks)\n\n");
    
    printf("Attack steps:\n");
    printf("  1. Given: hash(secret || message) and length\n");
    printf("  2. Compute: padding that was used in step 1\n");
    printf("  3. Extract: internal state from known hash\n");
    printf("  4. Continue: hashing from extracted state with malicious data\n");
    printf("  5. Result: hash(secret || message || padding || malicious)\n\n");
}

/**
 * Command-line interface for the length extension attack tool
 */
int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("SM3 Length Extension Attack Tool\n");
        printf("Usage: %s <command> [options]\n\n", argv[0]);
        printf("Commands:\n");
        printf("  demo         - Run interactive demonstration\n");
        printf("  attack       - Perform attack with custom input\n");
        printf("  test         - Run comprehensive tests\n");
        printf("  benchmark    - Performance benchmark\n");
        printf("  explain      - Show mathematical explanation\n");
        return 1;
    }
    
    if (strcmp(argv[1], "demo") == 0) {
        demonstrate_length_extension_attack();
        analyze_vulnerable_schemes();
    }
    else if (strcmp(argv[1], "test") == 0) {
        test_attack_with_various_lengths();
    }
    else if (strcmp(argv[1], "benchmark") == 0) {
        printf("Benchmarking length extension attack...\n");
        double rate = benchmark_length_extension_attack(10000);
        printf("Attack rate: %.2f attacks/second\n", rate);
    }
    else if (strcmp(argv[1], "explain") == 0) {
        explain_attack_mathematics();
    }
    else if (strcmp(argv[1], "attack") == 0) {
        if (argc < 5) {
            printf("Usage: %s attack <known_hash> <original_length> <malicious_data>\n", argv[0]);
            return 1;
        }
        
        // Parse hex hash
        uint8_t known_hash[32];
        for (int i = 0; i < 32; i++) {
            sscanf(argv[2] + i*2, "%2hhx", &known_hash[i]);
        }
        
        size_t original_length = atoi(argv[3]);
        const char* malicious_data = argv[4];
        
        uint8_t extended_suffix[256];
        uint8_t extended_hash[32];
        size_t suffix_len = sm3_length_extension_attack(
            known_hash, original_length,
            (uint8_t*)malicious_data, strlen(malicious_data),
            extended_suffix, extended_hash
        );
        
        printf("Extended hash: ");
        for (int i = 0; i < 32; i++) {
            printf("%02x", extended_hash[i]);
        }
        printf("\n");
        
        printf("Extension suffix (%zu bytes): ", suffix_len);
        for (size_t i = 0; i < suffix_len; i++) {
            printf("%02x", extended_suffix[i]);
        }
        printf("\n");
    }
    else {
        printf("Unknown command: %s\n", argv[1]);
        return 1;
    }
    
    return 0;
}
