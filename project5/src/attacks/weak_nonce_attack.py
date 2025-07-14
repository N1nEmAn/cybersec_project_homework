"""
SM2 Weak Nonce Attack Implementation

This module demonstrates attacks against SM2 signatures when weak or
predictable nonces are used. Includes various attack scenarios:
- Predictable nonce patterns (sequential, time-based)
- Low entropy nonces (small bit patterns)
- Biased nonce generation
- Known nonce attacks

Educational demonstration of why cryptographically secure random
number generation is critical for digital signature security.
"""

import secrets
import time
import math
from typing import List, Tuple, Optional, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sm2_basic import SM2, Point
from attacks.nonce_reuse_attack import NonceReuseAttack, SignatureData

class WeakNonceAttack:
    """Implementation of weak nonce attacks against SM2"""
    
    def __init__(self):
        self.sm2 = SM2()
        self.nonce_reuse_attack = NonceReuseAttack()
    
    def generate_weak_sequential_nonces(self, start_nonce: int, count: int) -> List[int]:
        """Generate sequential nonces (very weak)"""
        return [(start_nonce + i) % self.sm2.curve.n for i in range(count)]
    
    def generate_weak_time_based_nonces(self, base_time: int, count: int) -> List[int]:
        """Generate time-based nonces (weak)"""
        nonces = []
        for i in range(count):
            # Simulate nonce based on timestamp
            timestamp = base_time + i
            nonce = (timestamp * 12345) % self.sm2.curve.n
            nonces.append(nonce)
        return nonces
    
    def generate_low_entropy_nonces(self, bit_length: int, count: int) -> List[int]:
        """Generate nonces with limited entropy (weak)"""
        max_value = (1 << bit_length) - 1
        return [secrets.randbelow(max_value) + 1 for _ in range(count)]
    
    def generate_biased_nonces(self, bias_factor: float, count: int) -> List[int]:
        """
        Generate nonces with statistical bias
        bias_factor: 0.0 (no bias) to 1.0 (maximum bias toward small values)
        """
        nonces = []
        for _ in range(count):
            if secrets.random() < bias_factor:
                # Generate small biased nonce
                nonce = secrets.randbelow(self.sm2.curve.n // 1000) + 1
            else:
                # Generate normal nonce
                nonce = secrets.randbelow(self.sm2.curve.n - 1) + 1
            nonces.append(nonce)
        return nonces
    
    def sign_with_weak_nonces(self, messages: List[bytes], private_key: int, 
                             nonces: List[int]) -> List[SignatureData]:
        """Create signatures using provided weak nonces"""
        signatures = []
        
        for message, nonce in zip(messages, nonces):
            sig_data = self.nonce_reuse_attack.vulnerable_sign(message, private_key, nonce)
            signatures.append(sig_data)
        
        return signatures
    
    def analyze_nonce_patterns(self, nonces: List[int]) -> Dict[str, Any]:
        """Analyze nonces for patterns and weaknesses"""
        analysis = {
            'total_nonces': len(nonces),
            'unique_nonces': len(set(nonces)),
            'duplicates': len(nonces) - len(set(nonces)),
            'patterns': []
        }
        
        if len(nonces) < 2:
            return analysis
        
        # Check for sequential patterns
        differences = [nonces[i+1] - nonces[i] for i in range(len(nonces)-1)]
        
        # Arithmetic progression check
        if len(set(differences)) == 1:
            analysis['patterns'].append({
                'type': 'arithmetic_progression',
                'common_difference': differences[0]
            })
        
        # Small difference check (indicating weak randomness)
        avg_diff = sum(abs(d) for d in differences) / len(differences)
        expected_diff = self.sm2.curve.n // 2  # Expected for true randomness
        
        if avg_diff < expected_diff / 1000:  # Much smaller than expected
            analysis['patterns'].append({
                'type': 'small_differences',
                'average_difference': avg_diff,
                'weakness_ratio': avg_diff / expected_diff
            })
        
        # Check for clustering (multiple nonces in small ranges)
        sorted_nonces = sorted(nonces)
        clusters = []
        current_cluster = [sorted_nonces[0]]
        cluster_threshold = self.sm2.curve.n // 10000  # 0.01% of range
        
        for i in range(1, len(sorted_nonces)):
            if sorted_nonces[i] - sorted_nonces[i-1] < cluster_threshold:
                current_cluster.append(sorted_nonces[i])
            else:
                if len(current_cluster) > 1:
                    clusters.append(current_cluster)
                current_cluster = [sorted_nonces[i]]
        
        if len(current_cluster) > 1:
            clusters.append(current_cluster)
        
        if clusters:
            analysis['patterns'].append({
                'type': 'clustering',
                'cluster_count': len(clusters),
                'largest_cluster_size': max(len(c) for c in clusters)
            })
        
        # Entropy analysis (simplified)
        bit_length = max(nonces).bit_length()
        theoretical_entropy = bit_length
        
        # Calculate actual entropy (simplified Shannon entropy)
        from collections import Counter
        nonce_counts = Counter(nonces)
        total = len(nonces)
        actual_entropy = -sum((count/total) * math.log2(count/total) 
                             for count in nonce_counts.values())
        
        analysis['entropy'] = {
            'theoretical_max': theoretical_entropy,
            'actual': actual_entropy,
            'efficiency': actual_entropy / theoretical_entropy if theoretical_entropy > 0 else 0
        }
        
        return analysis
    
    def attack_sequential_nonces(self, signatures: List[SignatureData]) -> Optional[int]:
        """
        Attack sequential nonces by predicting the pattern
        If nonces follow k, k+1, k+2, ... we can recover k and then the private key
        """
        if len(signatures) < 2:
            return None
        
        print("Analyzing signatures for sequential nonce patterns...")
        
        # Try to find the pattern in r values (which depend on nonces)
        r_values = [sig.signature[0] for sig in signatures]
        
        # For sequential nonces k, k+1, k+2, the r values should have a predictable relationship
        # This is a simplified analysis - full attack would be more complex
        
        # Check if we can recover nonces using adjacent signatures
        for i in range(len(signatures) - 1):
            # Try assuming nonces are k and k+1
            recovered_key = self._attempt_sequential_recovery(signatures[i], signatures[i+1])
            if recovered_key:
                print(f"✓ Found sequential pattern at signatures {i} and {i+1}")
                return recovered_key
        
        return None
    
    def _attempt_sequential_recovery(self, sig1: SignatureData, sig2: SignatureData) -> Optional[int]:
        """
        Attempt to recover private key assuming nonces are k and k+1
        """
        # This is a simplified approach
        # In practice, this requires solving the system of equations for sequential nonces
        
        r1, s1 = sig1.signature
        r2, s2 = sig2.signature
        z1 = sig1.message_hash
        z2 = sig2.message_hash
        
        # Try different sequential assumptions
        for delta in range(1, 100):  # Try small deltas
            # Assume k2 = k1 + delta
            # This leads to a system of equations that can potentially be solved
            
            # For now, use the nonce reuse attack as a fallback
            if r1 == r2:  # Same nonce (delta = 0)
                recovered_nonce = self.nonce_reuse_attack.recover_nonce(sig1, sig2)
                if recovered_nonce:
                    return self.nonce_reuse_attack.recover_private_key(sig1, recovered_nonce)
        
        return None
    
    def attack_time_based_nonces(self, signatures: List[SignatureData], 
                                timestamps: List[int]) -> Optional[int]:
        """
        Attack time-based nonces by predicting the time-based pattern
        """
        if len(signatures) != len(timestamps) or len(signatures) < 2:
            return None
        
        print("Analyzing time-based nonce patterns...")
        
        # Try to reverse-engineer the time-based nonce generation
        for i in range(len(signatures) - 1):
            timestamp1, timestamp2 = timestamps[i], timestamps[i+1]
            
            # Common time-based patterns to try
            patterns = [
                lambda t: (t * 12345) % self.sm2.curve.n,
                lambda t: (t * 67890) % self.sm2.curve.n,
                lambda t: ((t * 1000) % self.sm2.curve.n),
                lambda t: (hash(str(t)) % self.sm2.curve.n),
            ]
            
            for pattern_func in patterns:
                predicted_nonce1 = pattern_func(timestamp1)
                predicted_nonce2 = pattern_func(timestamp2)
                
                # Test if these nonces work
                if self._verify_nonce_prediction(signatures[i], predicted_nonce1):
                    print(f"✓ Found time-based pattern")
                    # Recover private key using known nonce
                    return self.nonce_reuse_attack.recover_private_key(signatures[i], predicted_nonce1)
        
        return None
    
    def _verify_nonce_prediction(self, sig_data: SignatureData, predicted_nonce: int) -> bool:
        """Verify if a predicted nonce matches the signature"""
        # Compute expected r value from predicted nonce
        R = self.sm2.point_multiply(predicted_nonce, self.sm2.G)
        expected_r = R.x % self.sm2.curve.n
        
        actual_r = sig_data.signature[0]
        return expected_r == actual_r
    
    def attack_low_entropy_nonces(self, signatures: List[SignatureData], 
                                 max_entropy_bits: int = 32) -> Optional[int]:
        """
        Brute force attack against low entropy nonces
        """
        if not signatures:
            return None
        
        print(f"Brute forcing nonces with ≤{max_entropy_bits} bits of entropy...")
        
        max_nonce = 1 << max_entropy_bits
        
        for sig in signatures:
            print(f"Trying signature with r={sig.signature[0]:x}")
            
            # Brute force nonces
            for nonce in range(1, min(max_nonce, 1000000)):  # Limit for demo
                if self._verify_nonce_prediction(sig, nonce):
                    print(f"✓ Found weak nonce: {nonce}")
                    return self.nonce_reuse_attack.recover_private_key(sig, nonce)
                
                if nonce % 100000 == 0:
                    print(f"  Tried {nonce} nonces...")
        
        print("Brute force unsuccessful within limited range")
        return None
    
    def demonstrate_weak_nonce_attacks(self):
        """Comprehensive demonstration of weak nonce attacks"""
        print("=== SM2 Weak Nonce Attack Demonstration ===\n")
        
        # Generate victim's keys
        private_key = secrets.randbelow(self.sm2.curve.n - 1) + 1
        public_key = self.sm2.point_multiply(private_key, self.sm2.G)
        
        print(f"Victim's private key: {private_key:x}")
        print(f"Victim's public key: ({public_key.x:x}, {public_key.y:x})\n")
        
        # Test messages
        messages = [
            b"Transaction 1: Send 100 coins to Alice",
            b"Transaction 2: Send 200 coins to Bob", 
            b"Transaction 3: Send 50 coins to Charlie",
            b"Transaction 4: Send 300 coins to David",
            b"Transaction 5: Send 150 coins to Eve"
        ]
        
        # Scenario 1: Sequential nonces
        print("1. Sequential Nonce Attack:")
        start_nonce = secrets.randbelow(self.sm2.curve.n // 2)
        sequential_nonces = self.generate_weak_sequential_nonces(start_nonce, len(messages))
        sequential_sigs = self.sign_with_weak_nonces(messages, private_key, sequential_nonces)
        
        print(f"   Using nonces: {start_nonce:x}, {start_nonce+1:x}, {start_nonce+2:x}, ...")
        
        seq_analysis = self.analyze_nonce_patterns(sequential_nonces)
        print(f"   Pattern analysis: {seq_analysis['patterns']}")
        
        recovered_key = self.attack_sequential_nonces(sequential_sigs)
        if recovered_key and recovered_key == private_key:
            print("   ✓ Sequential nonce attack successful!")
        else:
            print("   ✗ Sequential nonce attack failed")
        print()
        
        # Scenario 2: Time-based nonces
        print("2. Time-based Nonce Attack:")
        base_time = int(time.time())
        timestamps = [base_time + i for i in range(len(messages))]
        time_nonces = self.generate_weak_time_based_nonces(base_time, len(messages))
        time_sigs = self.sign_with_weak_nonces(messages, private_key, time_nonces)
        
        print(f"   Using time-based nonces from timestamp {base_time}")
        
        recovered_key = self.attack_time_based_nonces(time_sigs, timestamps)
        if recovered_key and recovered_key == private_key:
            print("   ✓ Time-based nonce attack successful!")
        else:
            print("   ✗ Time-based nonce attack failed")
        print()
        
        # Scenario 3: Low entropy nonces
        print("3. Low Entropy Nonce Attack:")
        low_entropy_bits = 24  # Only 24 bits of entropy
        low_entropy_nonces = self.generate_low_entropy_nonces(low_entropy_bits, 3)
        low_entropy_sigs = self.sign_with_weak_nonces(messages[:3], private_key, low_entropy_nonces)
        
        print(f"   Using nonces with only {low_entropy_bits} bits of entropy")
        
        recovered_key = self.attack_low_entropy_nonces(low_entropy_sigs, low_entropy_bits)
        if recovered_key and recovered_key == private_key:
            print("   ✓ Low entropy nonce attack successful!")
        else:
            print("   ✗ Low entropy nonce attack failed")
        print()
        
        # Scenario 4: Biased nonces
        print("4. Biased Nonce Analysis:")
        biased_nonces = self.generate_biased_nonces(0.7, len(messages))
        biased_sigs = self.sign_with_weak_nonces(messages, private_key, biased_nonces)
        
        bias_analysis = self.analyze_nonce_patterns(biased_nonces)
        print(f"   Entropy efficiency: {bias_analysis['entropy']['efficiency']:.3f}")
        print(f"   Detected patterns: {len(bias_analysis['patterns'])}")
        
        if bias_analysis['entropy']['efficiency'] < 0.5:
            print("   ⚠️  Significant bias detected - vulnerable to statistical attacks")
        else:
            print("   ✓ Bias within acceptable range")
        print()
    
    def generate_attack_report(self, nonces: List[int]) -> Dict[str, Any]:
        """Generate comprehensive attack feasibility report"""
        analysis = self.analyze_nonce_patterns(nonces)
        
        report = {
            'nonce_analysis': analysis,
            'attack_vectors': [],
            'risk_level': 'LOW',
            'recommendations': []
        }
        
        # Assess attack vectors
        if analysis['duplicates'] > 0:
            report['attack_vectors'].append({
                'type': 'nonce_reuse',
                'description': f"{analysis['duplicates']} duplicate nonces detected",
                'severity': 'CRITICAL'
            })
            report['risk_level'] = 'CRITICAL'
        
        for pattern in analysis['patterns']:
            if pattern['type'] == 'arithmetic_progression':
                report['attack_vectors'].append({
                    'type': 'sequential_nonces',
                    'description': 'Sequential nonce pattern detected',
                    'severity': 'HIGH'
                })
                if report['risk_level'] != 'CRITICAL':
                    report['risk_level'] = 'HIGH'
            
            elif pattern['type'] == 'small_differences':
                report['attack_vectors'].append({
                    'type': 'weak_randomness',
                    'description': f"Weak randomness detected (ratio: {pattern['weakness_ratio']:.6f})",
                    'severity': 'MEDIUM'
                })
                if report['risk_level'] not in ['CRITICAL', 'HIGH']:
                    report['risk_level'] = 'MEDIUM'
            
            elif pattern['type'] == 'clustering':
                report['attack_vectors'].append({
                    'type': 'nonce_clustering',
                    'description': f"{pattern['cluster_count']} clusters detected",
                    'severity': 'MEDIUM'
                })
        
        if analysis['entropy']['efficiency'] < 0.5:
            report['attack_vectors'].append({
                'type': 'low_entropy',
                'description': f"Low entropy efficiency: {analysis['entropy']['efficiency']:.3f}",
                'severity': 'HIGH'
            })
            if report['risk_level'] != 'CRITICAL':
                report['risk_level'] = 'HIGH'
        
        # Generate recommendations
        if report['risk_level'] == 'CRITICAL':
            report['recommendations'].extend([
                "IMMEDIATE ACTION REQUIRED: Stop using current nonce generation",
                "Revoke all signatures created with compromised nonces",
                "Implement cryptographically secure random number generation"
            ])
        elif report['risk_level'] == 'HIGH':
            report['recommendations'].extend([
                "Upgrade nonce generation mechanism immediately",
                "Audit all existing signatures for compromise",
                "Implement additional entropy sources"
            ])
        elif report['risk_level'] == 'MEDIUM':
            report['recommendations'].extend([
                "Review and improve nonce generation quality",
                "Monitor for patterns in future signatures",
                "Consider using deterministic nonce generation (RFC 6979)"
            ])
        else:
            report['recommendations'].append("Nonce generation appears secure")
        
        return report

def main():
    """Main demonstration"""
    attack = WeakNonceAttack()
    
    print("SM2 Weak Nonce Attack Analysis Tool\n")
    print("Choose analysis type:")
    print("1. Full demonstration")
    print("2. Nonce pattern analysis")
    print("3. Custom nonce testing")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        attack.demonstrate_weak_nonce_attacks()
    elif choice == "2":
        # Generate sample nonces with various patterns
        print("\nGenerating sample nonces with different patterns...")
        
        # Mix of patterns
        nonces = []
        nonces.extend(attack.generate_weak_sequential_nonces(12345, 5))
        nonces.extend(attack.generate_weak_time_based_nonces(int(time.time()), 3))
        nonces.extend(attack.generate_low_entropy_nonces(20, 4))
        nonces.extend(attack.generate_biased_nonces(0.8, 6))
        
        analysis = attack.analyze_nonce_patterns(nonces)
        report = attack.generate_attack_report(nonces)
        
        print(f"\nNonce Analysis Report:")
        print(f"Risk Level: {report['risk_level']}")
        print(f"Attack Vectors: {len(report['attack_vectors'])}")
        
        for vector in report['attack_vectors']:
            print(f"  - {vector['type']}: {vector['description']} ({vector['severity']})")
        
        print(f"\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
            
    elif choice == "3":
        print("Custom nonce testing not implemented in this demo")
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
