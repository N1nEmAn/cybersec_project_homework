"""
SM2 Bitcoin Signature Analysis

This module analyzes Bitcoin's early signature implementations and demonstrates
potential vulnerabilities in ECDSA that could apply to SM2. It focuses on
signature malleability, nonce predictability, and other historical issues.

Educational analysis of early Bitcoin signatures including:
- Signature malleability issues
- Predictable nonce patterns  
- R-value grinding attacks
- Transaction signature analysis

For educational and research purposes only.
"""

import hashlib
import secrets
import struct
import time
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import sys
import os

# Add parent directory to path for imports  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sm2_basic import SM2, Point

class SignatureType(Enum):
    """Bitcoin signature hash types"""
    SIGHASH_ALL = 0x01
    SIGHASH_NONE = 0x02
    SIGHASH_SINGLE = 0x03
    SIGHASH_ANYONECANPAY = 0x80

@dataclass
class BitcoinTransaction:
    """Simplified Bitcoin transaction structure"""
    version: int
    inputs: List[Dict[str, Any]]
    outputs: List[Dict[str, Any]]
    locktime: int
    
    def serialize(self) -> bytes:
        """Serialize transaction for signing"""
        data = struct.pack('<I', self.version)
        
        # Inputs
        data += struct.pack('<B', len(self.inputs))
        for inp in self.inputs:
            data += bytes.fromhex(inp['txid'])[::-1]  # Reverse for little-endian
            data += struct.pack('<I', inp['vout'])
            script = inp.get('script', b'')
            data += struct.pack('<B', len(script)) + script
            data += struct.pack('<I', inp.get('sequence', 0xffffffff))
        
        # Outputs
        data += struct.pack('<B', len(self.outputs))
        for out in self.outputs:
            data += struct.pack('<Q', out['value'])
            script = out['script']
            data += struct.pack('<B', len(script)) + script
        
        data += struct.pack('<I', self.locktime)
        return data

@dataclass  
class SatoshiSignatureAnalysis:
    """Analysis results for early Bitcoin signatures"""
    signature: Tuple[int, int]
    nonce_entropy: float
    r_value_pattern: str
    s_value_pattern: str
    malleability_risk: bool
    estimated_nonce_source: str

class BitcoinSignatureAnalyzer:
    """Analyzer for Bitcoin-style signatures"""
    
    def __init__(self):
        self.sm2 = SM2()
        self.known_weak_nonces = self._load_weak_nonces()
    
    def _load_weak_nonces(self) -> List[int]:
        """Load known weak nonces from historical data"""
        # Some historically weak nonces used in Bitcoin
        weak_nonces = [
            1,  # Extremely weak
            2,  # Extremely weak
            0x0000000000000000000000000000000000000000000000000000000000000001,
            0x0000000000000000000000000000000000000000000000000000000000000002,
            # Add more known weak nonces
        ]
        return weak_nonces
    
    def analyze_signature_entropy(self, signature: Tuple[int, int]) -> float:
        """
        Analyze the entropy of signature components
        Low entropy may indicate weak nonce generation
        """
        r, s = signature
        
        # Convert to binary strings
        r_bits = bin(r)[2:].zfill(256)
        s_bits = bin(s)[2:].zfill(256)
        
        # Calculate simple entropy metrics
        r_zeros = r_bits.count('0')
        r_ones = r_bits.count('1')
        s_zeros = s_bits.count('0')
        s_ones = s_bits.count('1')
        
        # Simple entropy calculation
        total_bits = len(r_bits) + len(s_bits)
        total_zeros = r_zeros + s_zeros
        total_ones = r_ones + s_ones
        
        if total_zeros == 0 or total_ones == 0:
            return 0.0
        
        p_zero = total_zeros / total_bits
        p_one = total_ones / total_bits
        
        import math
        entropy = -(p_zero * math.log2(p_zero) + p_one * math.log2(p_one))
        return entropy
    
    def detect_signature_malleability(self, signature: Tuple[int, int]) -> bool:
        """
        Detect if signature is vulnerable to malleability
        High s values can be modified to create valid alternate signatures
        """
        r, s = signature
        
        # Bitcoin's solution: enforce low s values
        # If s > n/2, the signature can be made "canonical" by using n - s
        return s > self.sm2.curve.n // 2
    
    def canonicalize_signature(self, signature: Tuple[int, int]) -> Tuple[int, int]:
        """
        Convert signature to canonical form (low s value)
        This prevents signature malleability
        """
        r, s = signature
        
        if s > self.sm2.curve.n // 2:
            s = self.sm2.curve.n - s
        
        return (r, s)
    
    def analyze_r_value_patterns(self, r: int) -> str:
        """Analyze R value for suspicious patterns"""
        r_hex = f"{r:064x}"
        
        if r_hex.startswith("00000"):
            return "suspicious_leading_zeros"
        elif r_hex.endswith("00000"):
            return "suspicious_trailing_zeros"
        elif len(set(r_hex)) < 8:
            return "low_character_diversity"
        elif r in self.known_weak_nonces:
            return "known_weak_nonce"
        else:
            return "normal"
    
    def estimate_nonce_source(self, signature: Tuple[int, int], 
                             timestamp: Optional[int] = None) -> str:
        """
        Estimate the likely source of nonce generation
        """
        r, s = signature
        
        # Check for time-based patterns
        if timestamp:
            time_based_nonce = (timestamp * 1000) % self.sm2.curve.n
            if abs(r - time_based_nonce) < 1000:
                return "time_based_weak"
        
        # Check for counter-based patterns  
        if r < 1000000:
            return "counter_based_weak"
        
        # Check for PRNG patterns
        entropy = self.analyze_signature_entropy(signature)
        if entropy < 0.9:
            return "poor_entropy_prng"
        
        return "unknown_good"
    
    def comprehensive_signature_analysis(self, signature: Tuple[int, int], 
                                       timestamp: Optional[int] = None) -> SatoshiSignatureAnalysis:
        """
        Perform comprehensive analysis of a signature
        """
        r, s = signature
        
        analysis = SatoshiSignatureAnalysis(
            signature=signature,
            nonce_entropy=self.analyze_signature_entropy(signature),
            r_value_pattern=self.analyze_r_value_patterns(r),
            s_value_pattern=self.analyze_r_value_patterns(s),  # Similar analysis for s
            malleability_risk=self.detect_signature_malleability(signature),
            estimated_nonce_source=self.estimate_nonce_source(signature, timestamp)
        )
        
        return analysis
    
    def simulate_early_bitcoin_signature(self, message: bytes, private_key: int, 
                                       timestamp: int) -> Tuple[int, int]:
        """
        Simulate early Bitcoin signature generation with potential weaknesses
        """
        # Simulate weak nonce generation used in early Bitcoin
        # This is intentionally weak for demonstration
        
        # Method 1: Time-based nonce (weak)
        if timestamp % 3 == 0:
            nonce = (timestamp * 12345) % self.sm2.curve.n
        # Method 2: Pseudo-random with poor seed (weak)
        elif timestamp % 3 == 1:
            import random
            random.seed(timestamp // 1000)  # Poor seed
            nonce = random.randint(1, self.sm2.curve.n - 1)
        # Method 3: Better randomness (stronger)
        else:
            nonce = secrets.randbelow(self.sm2.curve.n - 1) + 1
        
        # Generate signature using potentially weak nonce
        return self._sign_with_nonce(message, private_key, nonce)
    
    def _sign_with_nonce(self, message: bytes, private_key: int, nonce: int) -> Tuple[int, int]:
        """Sign message with specific nonce"""
        # Simplified signing (would use proper SM2 signing in practice)
        message_hash = int.from_bytes(hashlib.sha256(message).digest(), byteorder='big')
        message_hash = message_hash % self.sm2.curve.n
        
        R = self.sm2.point_multiply(nonce, self.sm2.G)
        r = R.x % self.sm2.curve.n
        
        if r == 0:
            raise ValueError("Invalid r value")
        
        s = (self.sm2.mod_inverse(nonce, self.sm2.curve.n) * 
             (message_hash + private_key * r)) % self.sm2.curve.n
        
        if s == 0:
            raise ValueError("Invalid s value")
        
        return (r, s)
    
    def analyze_transaction_signatures(self, transaction: BitcoinTransaction) -> List[SatoshiSignatureAnalysis]:
        """
        Analyze all signatures in a Bitcoin transaction
        """
        analyses = []
        
        # Simulate signature analysis for each input
        for i, inp in enumerate(transaction.inputs):
            if 'signature' in inp:
                signature = inp['signature']
                timestamp = inp.get('timestamp', int(time.time()))
                
                analysis = self.comprehensive_signature_analysis(signature, timestamp)
                analyses.append(analysis)
        
        return analyses
    
    def detect_signature_reuse_patterns(self, signatures: List[Tuple[int, int]]) -> Dict[str, Any]:
        """
        Detect patterns that might indicate signature reuse or weak generation
        """
        r_values = [sig[0] for sig in signatures]
        s_values = [sig[1] for sig in signatures]
        
        # Check for duplicate R values (nonce reuse)
        r_duplicates = []
        for i, r1 in enumerate(r_values):
            for j, r2 in enumerate(r_values[i+1:], i+1):
                if r1 == r2:
                    r_duplicates.append((i, j))
        
        # Check for patterns in values
        r_patterns = self._detect_arithmetic_patterns(r_values)
        s_patterns = self._detect_arithmetic_patterns(s_values)
        
        return {
            'total_signatures': len(signatures),
            'nonce_reuse_count': len(r_duplicates),
            'nonce_reuse_pairs': r_duplicates,
            'r_arithmetic_patterns': r_patterns,
            's_arithmetic_patterns': s_patterns,
            'malleability_count': sum(1 for sig in signatures if self.detect_signature_malleability(sig))
        }
    
    def _detect_arithmetic_patterns(self, values: List[int]) -> Dict[str, Any]:
        """Detect arithmetic progressions or other patterns in values"""
        if len(values) < 3:
            return {'patterns_found': False}
        
        # Check for arithmetic progression
        differences = [values[i+1] - values[i] for i in range(len(values)-1)]
        
        # Check if differences are constant (arithmetic progression)
        if len(set(differences)) == 1:
            return {
                'patterns_found': True,
                'type': 'arithmetic_progression',
                'common_difference': differences[0]
            }
        
        # Check for small differences (weak randomness)
        avg_diff = sum(abs(d) for d in differences) / len(differences)
        max_expected = self.sm2.curve.n // 1000  # Expected large differences
        
        if avg_diff < max_expected:
            return {
                'patterns_found': True,
                'type': 'small_differences',
                'average_difference': avg_diff
            }
        
        return {'patterns_found': False}
    
    def generate_satoshi_era_analysis_report(self) -> Dict[str, Any]:
        """
        Generate analysis report simulating early Bitcoin era signatures
        """
        print("Generating Satoshi-era signature analysis report...")
        
        # Simulate early Bitcoin transactions
        private_key = secrets.randbelow(self.sm2.curve.n - 1) + 1
        
        # Generate signatures from different time periods with different qualities
        signatures = []
        analyses = []
        
        # Early period: weaker nonce generation
        early_period = int(time.time()) - 86400 * 365  # 1 year ago
        for i in range(10):
            timestamp = early_period + i * 3600
            message = f"early_tx_{i}".encode()
            sig = self.simulate_early_bitcoin_signature(message, private_key, timestamp)
            signatures.append(sig)
            
            analysis = self.comprehensive_signature_analysis(sig, timestamp)
            analyses.append(analysis)
        
        # Later period: better nonce generation  
        later_period = int(time.time()) - 86400 * 30  # 30 days ago
        for i in range(10):
            timestamp = later_period + i * 3600
            message = f"later_tx_{i}".encode()
            sig = self.simulate_early_bitcoin_signature(message, private_key, timestamp)
            signatures.append(sig)
            
            analysis = self.comprehensive_signature_analysis(sig, timestamp)
            analyses.append(analysis)
        
        # Analyze patterns across all signatures
        pattern_analysis = self.detect_signature_reuse_patterns(signatures)
        
        # Generate summary statistics
        weak_nonce_count = sum(1 for a in analyses if a.estimated_nonce_source.endswith('weak'))
        malleable_count = sum(1 for a in analyses if a.malleability_risk)
        low_entropy_count = sum(1 for a in analyses if a.nonce_entropy < 0.9)
        
        report = {
            'analysis_timestamp': time.time(),
            'total_signatures_analyzed': len(signatures),
            'vulnerability_summary': {
                'weak_nonce_generation': weak_nonce_count,
                'signature_malleability': malleable_count,
                'low_entropy_signatures': low_entropy_count,
                'nonce_reuse_instances': pattern_analysis['nonce_reuse_count']
            },
            'pattern_analysis': pattern_analysis,
            'individual_analyses': [
                {
                    'signature_index': i,
                    'r_value': f"{a.signature[0]:x}",
                    's_value': f"{a.signature[1]:x}",
                    'entropy': a.nonce_entropy,
                    'malleability_risk': a.malleability_risk,
                    'nonce_source': a.estimated_nonce_source,
                    'r_pattern': a.r_value_pattern
                }
                for i, a in enumerate(analyses)
            ],
            'recommendations': self._generate_security_recommendations(analyses)
        }
        
        return report
    
    def _generate_security_recommendations(self, analyses: List[SatoshiSignatureAnalysis]) -> List[str]:
        """Generate security recommendations based on analysis"""
        recommendations = []
        
        weak_count = sum(1 for a in analyses if a.estimated_nonce_source.endswith('weak'))
        if weak_count > 0:
            recommendations.append(
                f"⚠️  {weak_count} signatures show signs of weak nonce generation. "
                "Use cryptographically secure random number generation."
            )
        
        malleable_count = sum(1 for a in analyses if a.malleability_risk)
        if malleable_count > 0:
            recommendations.append(
                f"⚠️  {malleable_count} signatures are vulnerable to malleability. "
                "Enforce canonical signatures with low s values."
            )
        
        low_entropy_count = sum(1 for a in analyses if a.nonce_entropy < 0.9)
        if low_entropy_count > 0:
            recommendations.append(
                f"⚠️  {low_entropy_count} signatures show low entropy. "
                "Review random number generation implementation."
            )
        
        if not recommendations:
            recommendations.append("✓ No major vulnerabilities detected in signature analysis.")
        
        return recommendations

def demonstrate_bitcoin_analysis():
    """Demonstrate Bitcoin signature analysis"""
    analyzer = BitcoinSignatureAnalyzer()
    
    print("=== Bitcoin Signature Analysis Demonstration ===\n")
    
    # Generate and analyze a sample signature
    private_key = secrets.randbelow(analyzer.sm2.curve.n - 1) + 1
    message = b"Sample Bitcoin transaction"
    timestamp = int(time.time())
    
    # Create signature with potential weakness
    signature = analyzer.simulate_early_bitcoin_signature(message, private_key, timestamp)
    
    print("1. Individual Signature Analysis:")
    analysis = analyzer.comprehensive_signature_analysis(signature, timestamp)
    print(f"   Signature: (r={analysis.signature[0]:x}, s={analysis.signature[1]:x})")
    print(f"   Entropy: {analysis.nonce_entropy:.3f}")
    print(f"   R pattern: {analysis.r_value_pattern}")
    print(f"   Malleability risk: {analysis.malleability_risk}")
    print(f"   Nonce source: {analysis.estimated_nonce_source}")
    
    if analysis.malleability_risk:
        canonical = analyzer.canonicalize_signature(signature)
        print(f"   Canonical form: (r={canonical[0]:x}, s={canonical[1]:x})")
    
    print("\n2. Historical Analysis Report:")
    report = analyzer.generate_satoshi_era_analysis_report()
    
    print(f"   Total signatures: {report['total_signatures_analyzed']}")
    print(f"   Weak nonces: {report['vulnerability_summary']['weak_nonce_generation']}")
    print(f"   Malleable: {report['vulnerability_summary']['signature_malleability']}")
    print(f"   Low entropy: {report['vulnerability_summary']['low_entropy_signatures']}")
    print(f"   Nonce reuse: {report['vulnerability_summary']['nonce_reuse_instances']}")
    
    print("\n3. Security Recommendations:")
    for rec in report['recommendations']:
        print(f"   {rec}")
    
    # Save detailed report
    with open('bitcoin_signature_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n   Detailed report saved to: bitcoin_signature_analysis_report.json")

if __name__ == "__main__":
    demonstrate_bitcoin_analysis()
