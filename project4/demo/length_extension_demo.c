/**
 * Length Extension Attack Demonstration Program
 * 
 * This program demonstrates the length extension attack against SM3 hash function
 * in a practical scenario. It simulates various attack scenarios including:
 * - Simple MAC bypass
 * - Authentication token forgery
 * - File integrity bypass
 * - Message authentication bypass
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

// Include the length extension attack implementation
#include "../src/length_extension.c"

/**
 * Colors for console output
 */
#define COLOR_RED     "\x1b[31m"
#define COLOR_GREEN   "\x1b[32m"
#define COLOR_YELLOW  "\x1b[33m"
#define COLOR_BLUE    "\x1b[34m"
#define COLOR_MAGENTA "\x1b[35m"
#define COLOR_CYAN    "\x1b[36m"
#define COLOR_RESET   "\x1b[0m"

/**
 * Print colored text
 */
void print_colored(const char* color, const char* text) {
    printf("%s%s%s", color, text, COLOR_RESET);
}

/**
 * Print header
 */
void print_header(const char* title) {
    printf("\n");
    print_colored(COLOR_CYAN, "=================================================\n");
    print_colored(COLOR_CYAN, title);
    printf("\n");
    print_colored(COLOR_CYAN, "=================================================\n");
}

/**
 * Print hex data with formatting
 */
void print_hex_data(const char* label, const uint8_t* data, size_t len) {
    printf("%s: ", label);
    for (size_t i = 0; i < len; i++) {
        printf("%02x", data[i]);
        if (i > 0 && (i + 1) % 16 == 0 && i + 1 < len) {
            printf("\n%*s", (int)strlen(label) + 2, "");
        }
    }
    printf("\n");
}

/**
 * Simulate a banking authentication system vulnerable to length extension
 */
void demo_banking_scenario(void) {
    print_header("Banking Authentication Bypass Scenario");
    
    printf("Scenario: Online banking system uses MAC = SM3(secret || transaction)\n");
    printf("for transaction authentication.\n\n");
    
    // Bank's secret key (unknown to attacker)
    const char* bank_secret = "BANK_SECRET_KEY_ULTRA_SECURE";
    
    // Original legitimate transaction
    const char* legit_transaction = "TRANSFER:100.00:USD:FROM:12345:TO:67890";
    
    // Create the full message that bank will hash
    char bank_message[512];
    snprintf(bank_message, sizeof(bank_message), "%s%s", bank_secret, legit_transaction);
    
    // Bank computes MAC
    uint8_t legit_mac[32];
    sm3_hash((uint8_t*)bank_message, strlen(bank_message), legit_mac);
    
    printf("1. Legitimate Transaction:\n");
    printf("   Transaction: %s\n", legit_transaction);
    printf("   Secret key: %s (unknown to attacker)\n", bank_secret);
    print_hex_data("   MAC", legit_mac, 32);
    printf("\n");
    
    // Attacker scenario: knows transaction and MAC, wants to modify
    printf("2. Attacker's Knowledge:\n");
    printf("   Known transaction: %s\n", legit_transaction);
    printf("   Known MAC: ");
    for (int i = 0; i < 32; i++) printf("%02x", legit_mac[i]);
    printf("\n");
    printf("   Known total length: %zu bytes\n", strlen(bank_message));
    printf("\n");
    
    // Attacker wants to append malicious data
    const char* malicious_addition = ":ADDTX:TRANSFER:999999.99:USD:FROM:67890:TO:ATTACKER";
    
    printf("3. Attack Execution:\n");
    printf("   Malicious addition: %s\n", malicious_addition);
    
    // Perform length extension attack
    uint8_t extended_suffix[512];
    uint8_t forged_mac[32];
    size_t suffix_len = sm3_length_extension_attack(
        legit_mac,
        strlen(bank_message),
        (uint8_t*)malicious_addition,
        strlen(malicious_addition),
        extended_suffix,
        forged_mac
    );
    
    printf("   Generated suffix length: %zu bytes\n", suffix_len);
    print_hex_data("   Forged MAC", forged_mac, 32);
    printf("\n");
    
    // Verify the attack by reconstructing the full forged message
    char forged_transaction[1024];
    size_t base_len = strlen(legit_transaction);
    memcpy(forged_transaction, legit_transaction, base_len);
    memcpy(forged_transaction + base_len, extended_suffix, suffix_len);
    forged_transaction[base_len + suffix_len] = '\0';
    
    printf("4. Verification:\n");
    printf("   Forged transaction: %s", legit_transaction);
    printf("[padding]%s\n", malicious_addition);
    
    // Bank would verify this by computing MAC of full message
    char full_forged_message[1024];
    snprintf(full_forged_message, sizeof(full_forged_message), "%s%s", 
             bank_secret, forged_transaction);
    
    uint8_t verification_mac[32];
    sm3_hash((uint8_t*)full_forged_message, strlen(full_forged_message), verification_mac);
    
    int attack_success = memcmp(forged_mac, verification_mac, 32) == 0;
    
    if (attack_success) {
        print_colored(COLOR_RED, "   ⚠️  ATTACK SUCCESSFUL! ⚠️\n");
        printf("   The forged transaction will be accepted by the bank!\n");
        printf("   Attacker can steal $999,999.99 without knowing the secret key!\n");
    } else {
        print_colored(COLOR_GREEN, "   Attack failed.\n");
    }
}

/**
 * Simulate file integrity checking bypass
 */
void demo_file_integrity_scenario(void) {
    print_header("File Integrity Checking Bypass");
    
    printf("Scenario: System uses SM3(secret || file_content) to verify file integrity.\n\n");
    
    const char* system_secret = "FILE_INTEGRITY_SECRET";
    const char* original_file = "SYSTEM_CONFIG_VERSION_1.0\nSECURITY_LEVEL=HIGH\nADMIN_ACCESS=RESTRICTED\n";
    
    // System computes integrity hash
    char integrity_input[1024];
    snprintf(integrity_input, sizeof(integrity_input), "%s%s", system_secret, original_file);
    
    uint8_t integrity_hash[32];
    sm3_hash((uint8_t*)integrity_input, strlen(integrity_input), integrity_hash);
    
    printf("1. Original File:\n");
    printf("   Content: %s", original_file);
    printf("   Secret: %s (unknown to attacker)\n", system_secret);
    print_hex_data("   Integrity hash", integrity_hash, 32);
    printf("\n");
    
    // Attacker wants to modify file
    const char* malicious_config = "ADMIN_ACCESS=FULL\nBACKDOOR_ENABLED=TRUE\n";
    
    printf("2. Attack: Append malicious configuration\n");
    printf("   Malicious addition: %s", malicious_config);
    
    // Perform attack
    uint8_t extended_data[512];
    uint8_t forged_hash[32];
    size_t extension_len = sm3_length_extension_attack(
        integrity_hash,
        strlen(integrity_input),
        (uint8_t*)malicious_config,
        strlen(malicious_config),
        extended_data,
        forged_hash
    );
    
    printf("   Extension length: %zu bytes\n", extension_len);
    print_hex_data("   Forged integrity hash", forged_hash, 32);
    
    // Verify attack
    char forged_file[1024];
    size_t original_len = strlen(original_file);
    memcpy(forged_file, original_file, original_len);
    memcpy(forged_file + original_len, extended_data, extension_len);
    forged_file[original_len + extension_len] = '\0';
    
    char full_forged_input[1024];
    snprintf(full_forged_input, sizeof(full_forged_input), "%s%s", system_secret, forged_file);
    
    uint8_t verification_hash[32];
    sm3_hash((uint8_t*)full_forged_input, strlen(full_forged_input), verification_hash);
    
    if (memcmp(forged_hash, verification_hash, 32) == 0) {
        print_colored(COLOR_RED, "\n   ⚠️  FILE INTEGRITY BYPASS SUCCESSFUL! ⚠️\n");
        printf("   Attacker can modify system files without detection!\n");
    }
}

/**
 * Simulate API authentication token forgery
 */
void demo_api_token_scenario(void) {
    print_header("API Authentication Token Forgery");
    
    printf("Scenario: API uses tokens with format TOKEN = SM3(secret || user_data)\n\n");
    
    const char* api_secret = "API_SECRET_KEY_XYZ789";
    const char* user_data = "user=alice&role=user&expires=1234567890";
    
    // Generate legitimate token
    char token_input[512];
    snprintf(token_input, sizeof(token_input), "%s%s", api_secret, user_data);
    
    uint8_t legit_token[32];
    sm3_hash((uint8_t*)token_input, strlen(token_input), legit_token);
    
    printf("1. Legitimate API Token:\n");
    printf("   User data: %s\n", user_data);
    printf("   Secret: %s (unknown to attacker)\n", api_secret);
    print_hex_data("   Token", legit_token, 32);
    printf("\n");
    
    // Attacker wants to escalate privileges
    const char* privilege_escalation = "&role=admin&can_delete=true&super_user=true";
    
    printf("2. Privilege Escalation Attack:\n");
    printf("   Additional data: %s\n", privilege_escalation);
    
    // Perform attack
    uint8_t token_extension[256];
    uint8_t forged_token[32];
    size_t ext_len = sm3_length_extension_attack(
        legit_token,
        strlen(token_input),
        (uint8_t*)privilege_escalation,
        strlen(privilege_escalation),
        token_extension,
        forged_token
    );
    
    print_hex_data("   Forged token", forged_token, 32);
    printf("   Extension length: %zu bytes\n", ext_len);
    
    // Construct forged user data
    char forged_user_data[1024];
    size_t base_len = strlen(user_data);
    memcpy(forged_user_data, user_data, base_len);
    memcpy(forged_user_data + base_len, token_extension, ext_len);
    forged_user_data[base_len + ext_len] = '\0';
    
    printf("\n   Forged user data: %s[padding]%s\n", user_data, privilege_escalation);
    
    // Verify token
    char verification_input[1024];
    snprintf(verification_input, sizeof(verification_input), "%s%s", api_secret, forged_user_data);
    
    uint8_t verification_token[32];
    sm3_hash((uint8_t*)verification_input, strlen(verification_input), verification_token);
    
    if (memcmp(forged_token, verification_token, 32) == 0) {
        print_colored(COLOR_RED, "\n   ⚠️  PRIVILEGE ESCALATION SUCCESSFUL! ⚠️\n");
        printf("   Attacker gained admin privileges without knowing the secret!\n");
    }
}

/**
 * Interactive attack demonstration
 */
void interactive_demo(void) {
    print_header("Interactive Length Extension Attack");
    
    char secret[256], message[256], malicious[256];
    
    printf("Enter secret key (will be hidden from 'attacker'): ");
    if (!fgets(secret, sizeof(secret), stdin)) return;
    secret[strcspn(secret, "\n")] = 0; // Remove newline
    
    printf("Enter original message: ");
    if (!fgets(message, sizeof(message), stdin)) return;
    message[strcspn(message, "\n")] = 0;
    
    printf("Enter malicious data to append: ");
    if (!fgets(malicious, sizeof(malicious), stdin)) return;
    malicious[strcspn(malicious, "\n")] = 0;
    
    // Compute original hash
    char full_message[512];
    snprintf(full_message, sizeof(full_message), "%s%s", secret, message);
    
    uint8_t original_hash[32];
    sm3_hash((uint8_t*)full_message, strlen(full_message), original_hash);
    
    printf("\n--- Simulation ---\n");
    printf("System computes: SM3(\"%s\" || \"%s\")\n", secret, message);
    print_hex_data("Original hash", original_hash, 32);
    
    printf("\n--- Attack ---\n");
    printf("Attacker knows: hash and total length (%zu)\n", strlen(full_message));
    printf("Attacker wants to append: \"%s\"\n", malicious);
    
    // Perform attack
    uint8_t extension[256];
    uint8_t forged_hash[32];
    size_t ext_len = sm3_length_extension_attack(
        original_hash,
        strlen(full_message),
        (uint8_t*)malicious,
        strlen(malicious),
        extension,
        forged_hash
    );
    
    print_hex_data("Forged hash", forged_hash, 32);
    printf("Extension length: %zu bytes\n", ext_len);
    
    // Show the result
    printf("\n--- Result ---\n");
    printf("Forged message: \"%s\"[%zu padding bytes]\"%s\"\n", 
           message, ext_len - strlen(malicious), malicious);
    
    // Verify
    char forged_full[1024];
    size_t msg_len = strlen(message);
    memcpy(forged_full, message, msg_len);
    memcpy(forged_full + msg_len, extension, ext_len);
    
    char verification_input[1024];
    snprintf(verification_input, sizeof(verification_input), "%s", secret);
    memcpy(verification_input + strlen(secret), forged_full, msg_len + ext_len);
    verification_input[strlen(secret) + msg_len + ext_len] = '\0';
    
    uint8_t verification_hash[32];
    sm3_hash((uint8_t*)verification_input, strlen(secret) + msg_len + ext_len, verification_hash);
    
    if (memcmp(forged_hash, verification_hash, 32) == 0) {
        print_colored(COLOR_RED, "✓ Attack successful! Forged hash is valid.\n");
    } else {
        print_colored(COLOR_GREEN, "✗ Attack failed.\n");
    }
}

/**
 * Menu system
 */
void show_menu(void) {
    print_header("SM3 Length Extension Attack Demonstration");
    printf("Choose a demonstration scenario:\n\n");
    printf("1. Banking Authentication Bypass\n");
    printf("2. File Integrity Checking Bypass\n");
    printf("3. API Token Forgery\n");
    printf("4. Interactive Demo\n");
    printf("5. All Scenarios\n");
    printf("6. Attack Theory Explanation\n");
    printf("7. Exit\n\n");
    printf("Enter your choice (1-7): ");
}

/**
 * Main demonstration program
 */
int main(void) {
    int choice;
    
    while (1) {
        show_menu();
        
        if (scanf("%d", &choice) != 1) {
            printf("Invalid input. Please enter a number.\n");
            while (getchar() != '\n'); // Clear input buffer
            continue;
        }
        while (getchar() != '\n'); // Clear input buffer
        
        switch (choice) {
            case 1:
                demo_banking_scenario();
                break;
            case 2:
                demo_file_integrity_scenario();
                break;
            case 3:
                demo_api_token_scenario();
                break;
            case 4:
                interactive_demo();
                break;
            case 5:
                demo_banking_scenario();
                demo_file_integrity_scenario();
                demo_api_token_scenario();
                break;
            case 6:
                explain_attack_mathematics();
                analyze_vulnerable_schemes();
                break;
            case 7:
                print_colored(COLOR_GREEN, "Goodbye!\n");
                return 0;
            default:
                print_colored(COLOR_RED, "Invalid choice. Please try again.\n");
        }
        
        printf("\nPress Enter to continue...");
        getchar();
    }
    
    return 0;
}
