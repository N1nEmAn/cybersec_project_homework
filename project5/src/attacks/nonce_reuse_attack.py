"""
SM2 Nonce Reuse Attack Implementation

This module demonstrates how nonce reuse in SM2 signatures can lead to 
private key recovery. This is a critical vulnerability that occurs when
the same random number k is used for multiple signatures.

Mathematical foundation:
- Given two signatures (r1, s1) and (r2, s2) with the same k
- We can compute k = (z1 - z2) / (s1 - s2) mod n
- Then recover private key d = (s1 * k - z1) / r1 mod n

Educational use only - demonstrates why proper nonce generation is critical.
"""

import hashlib
import secrets
from typing import Tuple, List, Optional
from dataclasses import dataclass
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sm2_basic import SM2, Point, CurveParams

@dataclass
class SignatureData:
    """Container for signature and related data"""
    message: bytes
    signature: Tuple[int, int]  # (r, s)
    message_hash: int
    nonce: Optional[int] = None  # For demonstration purposes

class NonceReuseAttack:
    """Implementation of nonce reuse attack against SM2"""
    
    def __init__(self):
        self.sm2 = SM2()
    
    def vulnerable_sign(self, message: bytes, private_key: int, 
                       fixed_nonce: int, user_id: bytes = b"1234567812345678") -> SignatureData:
        """
        Create a signature using a fixed nonce (vulnerable implementation)
        This simulates the vulnerability - DO NOT use in production
        """
        # Compute message hash
        z = self.sm2._compute_z(user_id, self.sm2.point_multiply(private_key, self.sm2.G))
        message_hash = int.from_bytes(hashlib.sha256(z + message).digest(), byteorder='big')
        message_hash = message_hash % self.sm2.curve.n
        
        # Use fixed nonce instead of random (vulnerability)
        k = fixed_nonce
        
        # Compute signature
        R = self.sm2.point_multiply(k, self.sm2.G)
        r = R.x % self.sm2.curve.n
        
        if r == 0:
            raise ValueError("Invalid r value")
        
        s = (self.sm2.mod_inverse(k, self.sm2.curve.n) * 
             (message_hash + private_key * r)) % self.sm2.curve.n
        
        if s == 0:
            raise ValueError("Invalid s value")
        
        return SignatureData(
            message=message,
            signature=(r, s),
            message_hash=message_hash,
            nonce=k
        )
    
    def detect_nonce_reuse(self, sig1: SignatureData, sig2: SignatureData) -> bool:
        """Detect if two signatures used the same nonce"""
        r1, s1 = sig1.signature
        r2, s2 = sig2.signature
        
        # If r values are the same, likely same nonce was used
        return r1 == r2
    
    def recover_nonce(self, sig1: SignatureData, sig2: SignatureData) -> Optional[int]:
        """
        Recover the nonce k from two signatures with nonce reuse
        Formula: k = (z1 - z2) / (s1 - s2) mod n
        """
        if not self.detect_nonce_reuse(sig1, sig2):
            return None
        
        r1, s1 = sig1.signature
        r2, s2 = sig2.signature
        z1 = sig1.message_hash
        z2 = sig2.message_hash
        
        # Compute k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % self.sm2.curve.n
        denominator = (s1 - s2) % self.sm2.curve.n
        
        if denominator == 0:
            return None  # Cannot recover if s1 == s2
        
        k = (numerator * self.sm2.mod_inverse(denominator, self.sm2.curve.n)) % self.sm2.curve.n
        return k
    
    def recover_private_key(self, sig: SignatureData, recovered_nonce: int) -> int:
        """
        Recover private key using known nonce
        Formula: d = (s * k - z) / r mod n
        """
        r, s = sig.signature
        z = sig.message_hash
        k = recovered_nonce
        
        # d = (s * k - z) / r mod n
        numerator = (s * k - z) % self.sm2.curve.n
        denominator = r
        
        private_key = (numerator * self.sm2.mod_inverse(denominator, self.sm2.curve.n)) % self.sm2.curve.n
        return private_key
    
    def full_attack(self, sig1: SignatureData, sig2: SignatureData) -> Optional[int]:
        """
        Perform complete nonce reuse attack
        Returns recovered private key if successful
        """
        print("=== SM2 Nonce Reuse Attack ===")
        print(f"Signature 1: r={sig1.signature[0]:x}, s={sig1.signature[1]:x}")
        print(f"Signature 2: r={sig2.signature[0]:x}, s={sig2.signature[1]:x}")
        
        # Step 1: Check for nonce reuse
        if not self.detect_nonce_reuse(sig1, sig2):
            print("No nonce reuse detected (r values differ)")
            return None
        
        print("✓ Nonce reuse detected (same r value)")
        
        # Step 2: Recover nonce
        recovered_nonce = self.recover_nonce(sig1, sig2)
        if recovered_nonce is None:
            print("✗ Failed to recover nonce")
            return None
        
        print(f"✓ Recovered nonce: {recovered_nonce:x}")
        if sig1.nonce:
            print(f"  Original nonce: {sig1.nonce:x}")
            print(f"  Recovery correct: {recovered_nonce == sig1.nonce}")
        
        # Step 3: Recover private key
        recovered_private_key = self.recover_private_key(sig1, recovered_nonce)
        print(f"✓ Recovered private key: {recovered_private_key:x}")
        
        return recovered_private_key
    
    def verify_recovered_key(self, recovered_key: int, known_public_key: Point) -> bool:
        """Verify that recovered private key is correct"""
        computed_public_key = self.sm2.point_multiply(recovered_key, self.sm2.G)
        return (computed_public_key.x == known_public_key.x and 
                computed_public_key.y == known_public_key.y)
    
    def demonstrate_attack(self):
        """Complete demonstration of nonce reuse attack"""
        print("=== SM2 Nonce Reuse Attack Demonstration ===\n")
        
        # Generate victim's keys
        private_key = secrets.randbelow(self.sm2.curve.n - 1) + 1
        public_key = self.sm2.point_multiply(private_key, self.sm2.G)
        
        print(f"1. Victim's Setup:")
        print(f"   Private key: {private_key:x}")
        print(f"   Public key: ({public_key.x:x}, {public_key.y:x})")
        print()
        
        # Create two signatures with same nonce (vulnerability)
        fixed_nonce = secrets.randbelow(self.sm2.curve.n - 1) + 1
        message1 = b"Transfer $100 to Alice"
        message2 = b"Transfer $500 to Bob" 
        
        print(f"2. Vulnerable Signing (same nonce {fixed_nonce:x}):")
        sig1 = self.vulnerable_sign(message1, private_key, fixed_nonce)
        sig2 = self.vulnerable_sign(message2, private_key, fixed_nonce)
        
        print(f"   Message 1: {message1.decode()}")
        print(f"   Signature 1: (r={sig1.signature[0]:x}, s={sig1.signature[1]:x})")
        print(f"   Message 2: {message2.decode()}")
        print(f"   Signature 2: (r={sig2.signature[0]:x}, s={sig2.signature[1]:x})")
        print()
        
        # Perform attack
        print("3. Attack Execution:")
        recovered_key = self.full_attack(sig1, sig2)
        print()
        
        # Verify attack success
        if recovered_key:
            print("4. Attack Verification:")
            is_correct = self.verify_recovered_key(recovered_key, public_key)
            print(f"   Original private key: {private_key:x}")
            print(f"   Recovered private key: {recovered_key:x}")
            print(f"   Attack successful: {is_correct}")
            
            if is_correct:
                print("   ⚠️  CRITICAL: Private key completely compromised!")
                print("   ⚠️  Attacker can now forge any signature!")
        else:
            print("4. Attack failed")
        
        print()
    
    def analyze_real_world_signatures(self, signatures: List[SignatureData]) -> List[Tuple[int, int, int]]:
        """
        Analyze a collection of signatures for nonce reuse
        Returns list of (index1, index2, recovered_private_key) tuples
        """
        vulnerabilities = []
        
        print(f"Analyzing {len(signatures)} signatures for nonce reuse...")
        
        for i in range(len(signatures)):
            for j in range(i + 1, len(signatures)):
                if self.detect_nonce_reuse(signatures[i], signatures[j]):
                    print(f"Nonce reuse detected: signatures {i} and {j}")
                    
                    recovered_key = self.full_attack(signatures[i], signatures[j])
                    if recovered_key:
                        vulnerabilities.append((i, j, recovered_key))
        
        return vulnerabilities
    
    def simulate_bitcoin_scenario(self):
        """
        Simulate the famous Bitcoin nonce reuse incident
        This demonstrates how nonce reuse led to private key recovery
        """
        print("=== Bitcoin-style Nonce Reuse Scenario ===\n")
        
        # Simulate a wallet that improperly reuses nonces
        private_key = secrets.randbelow(self.sm2.curve.n - 1) + 1
        public_key = self.sm2.point_multiply(private_key, self.sm2.G)
        
        # Multiple transactions with same nonce (implementation bug)
        bad_nonce = 12345  # Predictable/reused nonce
        
        transactions = [
            b"tx1: send 1.5 BTC to address A",
            b"tx2: send 0.8 BTC to address B", 
            b"tx3: send 2.1 BTC to address C"
        ]
        
        signatures = []
        for tx in transactions:
            sig = self.vulnerable_sign(tx, private_key, bad_nonce)
            signatures.append(sig)
        
        print("Blockchain transactions with vulnerable signatures:")
        for i, (tx, sig) in enumerate(zip(transactions, signatures)):
            print(f"  TX{i+1}: {tx.decode()}")
            print(f"       Sig: (r={sig.signature[0]:x}, s={sig.signature[1]:x})")
        print()
        
        # Attacker analyzes blockchain for nonce reuse
        vulnerabilities = self.analyze_real_world_signatures(signatures)
        
        if vulnerabilities:
            print("⚠️  WALLET COMPROMISED!")
            print("   All funds can be stolen by attacker")
            print("   Private key is fully known")
        else:
            print("No vulnerabilities detected")

def generate_test_signatures(num_signatures: int = 10, reuse_probability: float = 0.1) -> List[SignatureData]:
    """
    Generate test signatures with some nonce reuse for analysis
    """
    attack = NonceReuseAttack()
    signatures = []
    used_nonces = []
    
    private_key = secrets.randbelow(attack.sm2.curve.n - 1) + 1
    
    for i in range(num_signatures):
        message = f"Test message {i}".encode()
        
        # Sometimes reuse nonce based on probability
        if secrets.random() < reuse_probability and used_nonces:
            nonce = secrets.choice(used_nonces)
        else:
            nonce = secrets.randbelow(attack.sm2.curve.n - 1) + 1
            used_nonces.append(nonce)
        
        sig = attack.vulnerable_sign(message, private_key, nonce)
        signatures.append(sig)
    
    return signatures

def main():
    """Main demonstration function"""
    attack = NonceReuseAttack()
    
    print("SM2 Nonce Reuse Attack Analysis Tool\n")
    print("Choose demonstration:")
    print("1. Basic nonce reuse attack")
    print("2. Bitcoin-style scenario") 
    print("3. Batch signature analysis")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        attack.demonstrate_attack()
    elif choice == "2":
        attack.simulate_bitcoin_scenario()
    elif choice == "3":
        print("\nGenerating test signatures with some nonce reuse...")
        signatures = generate_test_signatures(20, 0.3)
        vulnerabilities = attack.analyze_real_world_signatures(signatures)
        print(f"\nFound {len(vulnerabilities)} vulnerable signature pairs")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
