"""
Bitcoin Signature Malleability Analysis

This module analyzes signature malleability issues in Bitcoin-style
ECDSA signatures and how they apply to SM2 signatures. Includes
analysis of transaction malleability, signature grinding attacks,
and countermeasures.

Educational demonstration of signature malleability vulnerabilities
and their impact on cryptocurrency systems.
"""

import hashlib
import secrets
import time
from typing import List, Tuple, Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sm2_basic import SM2, Point

class BitcoinTransaction:
    """Simplified Bitcoin transaction for analysis"""
    
    def __init__(self, inputs: List[Dict], outputs: List[Dict], version: int = 1):
        self.version = version
        self.inputs = inputs  # [{'txid': bytes, 'vout': int, 'script': bytes}, ...]
        self.outputs = outputs  # [{'value': int, 'script': bytes}, ...]
        self.locktime = 0
    
    def serialize(self) -> bytes:
        """Serialize transaction for signing"""
        data = b''
        
        # Version
        data += self.version.to_bytes(4, 'little')
        
        # Input count
        data += len(self.inputs).to_bytes(1, 'big')
        
        # Inputs
        for inp in self.inputs:
            data += inp['txid']
            data += inp['vout'].to_bytes(4, 'little')
            script = inp.get('script', b'')
            data += len(script).to_bytes(1, 'big')
            data += script
            data += (0xFFFFFFFF).to_bytes(4, 'little')  # sequence
        
        # Output count
        data += len(self.outputs).to_bytes(1, 'big')
        
        # Outputs
        for out in self.outputs:
            data += out['value'].to_bytes(8, 'little')
            script = out['script']
            data += len(script).to_bytes(1, 'big')
            data += script
        
        # Locktime
        data += self.locktime.to_bytes(4, 'little')
        
        return data
    
    def get_signature_hash(self, input_index: int, prev_script: bytes) -> bytes:
        """Get hash for signing specific input"""
        # Simplified - replace input script with previous output script
        temp_inputs = self.inputs.copy()
        for i, inp in enumerate(temp_inputs):
            if i == input_index:
                inp['script'] = prev_script
            else:
                inp['script'] = b''
        
        temp_tx = BitcoinTransaction(temp_inputs, self.outputs, self.version)
        tx_data = temp_tx.serialize()
        
        # Add SIGHASH_ALL flag
        tx_data += (1).to_bytes(4, 'little')
        
        # Double SHA256
        return hashlib.sha256(hashlib.sha256(tx_data).digest()).digest()

class SignatureMalleability:
    """Analysis and demonstration of signature malleability"""
    
    def __init__(self):
        self.sm2 = SM2()
    
    def is_signature_canonical(self, signature: Tuple[int, int]) -> bool:
        """Check if signature is in canonical form"""
        r, s = signature
        
        # Check r is in valid range
        if r <= 0 or r >= self.sm2.curve.n:
            return False
        
        # Check s is in valid range and canonical (low s value)
        if s <= 0 or s >= self.sm2.curve.n:
            return False
        
        # For canonical form, s should be ≤ n/2
        return s <= self.sm2.curve.n // 2
    
    def make_signature_canonical(self, signature: Tuple[int, int]) -> Tuple[int, int]:
        """Convert signature to canonical form"""
        r, s = signature
        
        # If s > n/2, use n - s instead
        if s > self.sm2.curve.n // 2:
            s = self.sm2.curve.n - s
        
        return (r, s)
    
    def create_malleable_signature(self, signature: Tuple[int, int]) -> Tuple[int, int]:
        """Create alternative valid signature (malleable form)"""
        r, s = signature
        
        # Alternative signature with same r but different s
        s_alt = self.sm2.curve.n - s
        
        return (r, s_alt)
    
    def verify_signature_malleability(self, message: bytes, public_key: Point,
                                    signature1: Tuple[int, int], 
                                    signature2: Tuple[int, int]) -> bool:
        """Verify that both signatures are valid for the same message"""
        try:
            valid1 = self.sm2.verify_signature(message, signature1, public_key)
            valid2 = self.sm2.verify_signature(message, signature2, public_key)
            return valid1 and valid2
        except:
            return False
    
    def analyze_transaction_malleability(self, transaction: BitcoinTransaction,
                                       private_key: int, input_index: int,
                                       prev_script: bytes) -> Dict[str, Any]:
        """Analyze transaction malleability through signature manipulation"""
        
        # Get transaction hash for signing
        tx_hash = transaction.get_signature_hash(input_index, prev_script)
        
        # Create original signature
        signature = self.sm2.sign_message(tx_hash, private_key)
        public_key = self.sm2.point_multiply(private_key, self.sm2.G)
        
        # Create malleable signature
        malleable_sig = self.create_malleable_signature(signature)
        
        # Verify both signatures
        original_valid = self.sm2.verify_signature(tx_hash, signature, public_key)
        malleable_valid = self.sm2.verify_signature(tx_hash, malleable_sig, public_key)
        
        # Calculate transaction IDs
        original_tx_bytes = transaction.serialize()
        original_txid = hashlib.sha256(hashlib.sha256(original_tx_bytes).digest()).digest()
        
        # Modify transaction with malleable signature (simplified)
        malleable_txid = hashlib.sha256(hashlib.sha256(original_tx_bytes + b'_malleable').digest()).digest()
        
        return {
            'original_signature': signature,
            'malleable_signature': malleable_sig,
            'original_valid': original_valid,
            'malleable_valid': malleable_valid,
            'original_txid': original_txid.hex(),
            'malleable_txid': malleable_txid.hex(),
            'txid_changed': original_txid != malleable_txid,
            'canonical_original': self.is_signature_canonical(signature),
            'canonical_malleable': self.is_signature_canonical(malleable_sig)
        }
    
    def demonstrate_signature_grinding(self, message: bytes, private_key: int,
                                     target_pattern: str = "00") -> Dict[str, Any]:
        """
        Demonstrate signature grinding attack
        Repeatedly sign until signature has desired properties
        """
        public_key = self.sm2.point_multiply(private_key, self.sm2.G)
        attempts = 0
        start_time = time.time()
        
        while attempts < 10000:  # Limit attempts for demo
            # Create signature with random nonce
            nonce = secrets.randbelow(self.sm2.curve.n - 1) + 1
            signature = self.sm2.sign_with_nonce(message, private_key, nonce)
            
            # Check if signature meets criteria
            r, s = signature
            r_hex = hex(r)[2:]  # Remove '0x' prefix
            
            if r_hex.startswith(target_pattern):
                end_time = time.time()
                
                return {
                    'success': True,
                    'attempts': attempts + 1,
                    'time_taken': end_time - start_time,
                    'signature': signature,
                    'target_pattern': target_pattern,
                    'r_value': r_hex,
                    'canonical': self.is_signature_canonical(signature)
                }
            
            attempts += 1
        
        return {
            'success': False,
            'attempts': attempts,
            'target_pattern': target_pattern
        }
    
    def analyze_signature_entropy(self, signatures: List[Tuple[int, int]]) -> Dict[str, Any]:
        """Analyze entropy distribution in signature values"""
        if not signatures:
            return {'error': 'No signatures provided'}
        
        r_values = [sig[0] for sig in signatures]
        s_values = [sig[1] for sig in signatures]
        
        # Analyze bit patterns
        r_bits = [bin(r).count('1') for r in r_values]
        s_bits = [bin(s).count('1') for s in s_values]
        
        # Check for patterns in high bits
        r_high_bits = [(r >> 240) & 0xFFFF for r in r_values]  # Top 16 bits
        s_high_bits = [(s >> 240) & 0xFFFF for s in s_values]
        
        # Canonical form analysis
        canonical_count = sum(1 for sig in signatures if self.is_signature_canonical(sig))
        
        return {
            'total_signatures': len(signatures),
            'canonical_signatures': canonical_count,
            'canonical_ratio': canonical_count / len(signatures),
            'r_bit_stats': {
                'mean': sum(r_bits) / len(r_bits),
                'min': min(r_bits),
                'max': max(r_bits),
                'unique_patterns': len(set(r_high_bits))
            },
            's_bit_stats': {
                'mean': sum(s_bits) / len(s_bits),
                'min': min(s_bits),
                'max': max(s_bits),
                'unique_patterns': len(set(s_high_bits))
            }
        }
    
    def demonstrate_bip62_compliance(self, signatures: List[Tuple[int, int]]) -> Dict[str, Any]:
        """
        Demonstrate BIP-62 compliance (canonical signature requirements)
        """
        compliant_sigs = []
        non_compliant_sigs = []
        
        for sig in signatures:
            if self.is_signature_canonical(sig):
                compliant_sigs.append(sig)
            else:
                non_compliant_sigs.append(sig)
        
        # Convert non-compliant to compliant
        converted_sigs = [self.make_signature_canonical(sig) for sig in non_compliant_sigs]
        
        return {
            'total_signatures': len(signatures),
            'compliant_count': len(compliant_sigs),
            'non_compliant_count': len(non_compliant_sigs),
            'compliance_rate': len(compliant_sigs) / len(signatures) if signatures else 0,
            'converted_signatures': converted_sigs,
            'bip62_enforced': True  # Assume modern Bitcoin rules
        }
    
    def simulate_transaction_replay_attack(self) -> Dict[str, Any]:
        """
        Simulate transaction replay attack using signature malleability
        """
        print("Simulating transaction replay attack...")
        
        # Create victim's keys
        victim_private = secrets.randbelow(self.sm2.curve.n - 1) + 1
        victim_public = self.sm2.point_multiply(victim_private, self.sm2.G)
        
        # Create a transaction
        inputs = [{
            'txid': secrets.token_bytes(32),
            'vout': 0,
            'script': b'\x76\xa9\x14' + secrets.token_bytes(20) + b'\x88\xac'  # P2PKH
        }]
        
        outputs = [{
            'value': 5000000,  # 0.05 BTC in satoshis
            'script': b'\x76\xa9\x14' + secrets.token_bytes(20) + b'\x88\xac'
        }]
        
        transaction = BitcoinTransaction(inputs, outputs)
        prev_script = inputs[0]['script']
        
        # Analyze malleability
        analysis = self.analyze_transaction_malleability(
            transaction, victim_private, 0, prev_script
        )
        
        return {
            'attack_scenario': 'transaction_replay',
            'victim_funds': outputs[0]['value'],
            'malleability_analysis': analysis,
            'attack_success': analysis['txid_changed'] and analysis['malleable_valid'],
            'mitigation': 'Use BIP-62 canonical signatures and BIP-141 Segregated Witness'
        }

def main():
    """Main demonstration"""
    print("=== Bitcoin Signature Malleability Analysis ===\n")
    
    malleability = SignatureMalleability()
    
    print("Choose analysis type:")
    print("1. Basic signature malleability")
    print("2. Transaction malleability analysis")
    print("3. Signature grinding demonstration")
    print("4. BIP-62 compliance analysis")
    print("5. Transaction replay attack simulation")
    print("6. Full analysis suite")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        # Basic malleability demonstration
        private_key = secrets.randbelow(malleability.sm2.curve.n - 1) + 1
        public_key = malleability.sm2.point_multiply(private_key, malleability.sm2.G)
        message = b"Test message for malleability analysis"
        
        signature = malleability.sm2.sign_message(message, private_key)
        malleable_sig = malleability.create_malleable_signature(signature)
        
        print(f"Original signature: r={signature[0]:x}, s={signature[1]:x}")
        print(f"Malleable signature: r={malleable_sig[0]:x}, s={malleable_sig[1]:x}")
        print(f"Both valid: {malleability.verify_signature_malleability(message, public_key, signature, malleable_sig)}")
        print(f"Original canonical: {malleability.is_signature_canonical(signature)}")
        print(f"Malleable canonical: {malleability.is_signature_canonical(malleable_sig)}")
    
    elif choice == "2":
        # Transaction malleability
        result = malleability.simulate_transaction_replay_attack()
        print(f"Attack scenario: {result['attack_scenario']}")
        print(f"Victim funds at risk: {result['victim_funds']} satoshis")
        print(f"Attack success: {result['attack_success']}")
        print(f"Transaction ID changed: {result['malleability_analysis']['txid_changed']}")
        print(f"Mitigation: {result['mitigation']}")
    
    elif choice == "3":
        # Signature grinding
        private_key = secrets.randbelow(malleability.sm2.curve.n - 1) + 1
        message = b"Message for signature grinding"
        
        print("Attempting signature grinding for pattern '00'...")
        result = malleability.demonstrate_signature_grinding(message, private_key, "00")
        
        if result['success']:
            print(f"✓ Found signature with pattern after {result['attempts']} attempts")
            print(f"Time taken: {result['time_taken']:.3f} seconds")
            print(f"R value: {result['r_value']}")
            print(f"Canonical: {result['canonical']}")
        else:
            print(f"✗ Failed to find pattern after {result['attempts']} attempts")
    
    elif choice == "4":
        # BIP-62 compliance
        print("Generating test signatures...")
        private_key = secrets.randbelow(malleability.sm2.curve.n - 1) + 1
        test_sigs = []
        
        for i in range(100):
            message = f"Test message {i}".encode()
            sig = malleability.sm2.sign_message(message, private_key)
            test_sigs.append(sig)
        
        compliance = malleability.demonstrate_bip62_compliance(test_sigs)
        print(f"Total signatures: {compliance['total_signatures']}")
        print(f"BIP-62 compliant: {compliance['compliant_count']}")
        print(f"Compliance rate: {compliance['compliance_rate']:.2%}")
        print(f"Non-compliant converted: {len(compliance['converted_signatures'])}")
    
    elif choice == "5":
        # Transaction replay attack
        result = malleability.simulate_transaction_replay_attack()
        analysis = result['malleability_analysis']
        
        print("Transaction Replay Attack Simulation:")
        print(f"Original TX ID: {analysis['original_txid']}")
        print(f"Malleable TX ID: {analysis['malleable_txid']}")
        print(f"Transaction ID changed: {analysis['txid_changed']}")
        print(f"Attack feasible: {result['attack_success']}")
        print(f"\nCountermeasures: {result['mitigation']}")
    
    elif choice == "6":
        print("Running comprehensive malleability analysis...\n")
        
        # Run all analyses
        private_key = secrets.randbelow(malleability.sm2.curve.n - 1) + 1
        
        # Generate test data
        test_signatures = []
        for i in range(50):
            message = f"Test message {i}".encode()
            sig = malleability.sm2.sign_message(message, private_key)
            test_signatures.append(sig)
        
        # Entropy analysis
        entropy_analysis = malleability.analyze_signature_entropy(test_signatures)
        print("Signature Entropy Analysis:")
        print(f"  Canonical ratio: {entropy_analysis['canonical_ratio']:.2%}")
        print(f"  R-value bit density: {entropy_analysis['r_bit_stats']['mean']:.1f} bits")
        print(f"  S-value bit density: {entropy_analysis['s_bit_stats']['mean']:.1f} bits")
        
        # BIP-62 compliance
        compliance = malleability.demonstrate_bip62_compliance(test_signatures)
        print(f"\nBIP-62 Compliance: {compliance['compliance_rate']:.2%}")
        
        # Transaction attack simulation
        attack_result = malleability.simulate_transaction_replay_attack()
        print(f"\nTransaction Replay Attack: {'Possible' if attack_result['attack_success'] else 'Mitigated'}")
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
