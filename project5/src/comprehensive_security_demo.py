"""
Comprehensive SM2 Security Analysis Demo

This script demonstrates various security aspects and attack scenarios
against SM2 implementations, including:
- Nonce reuse attacks
- Weak nonce attacks  
- Side-channel attacks
- Bitcoin-style signature analysis
- Signature malleability

Educational tool for understanding SM2 security considerations.
"""

import sys
import os
import time
import secrets
from typing import Dict, Any

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attacks'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bitcoin_signature_analysis'))

try:
    from attacks.nonce_reuse_attack import NonceReuseAttack
    from attacks.weak_nonce_attack import WeakNonceAttack
    from attacks.side_channel_attacks import TimingAttack, PowerAnalysisAttack, CacheAttack
    from bitcoin_signature_analysis.satoshi_signature import SatoshiSignatureAnalysis
    from bitcoin_signature_analysis.signature_malleability import SignatureMalleability
    from sm2_utils import SM2KeyManager, SM2Benchmarker
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are in the correct paths")
    sys.exit(1)

class SM2SecurityAnalyzer:
    """Comprehensive SM2 security analysis suite"""
    
    def __init__(self):
        """Initialize all attack modules"""
        self.nonce_reuse_attack = NonceReuseAttack()
        self.weak_nonce_attack = WeakNonceAttack()
        self.timing_attack = TimingAttack()
        self.power_attack = PowerAnalysisAttack()
        self.cache_attack = CacheAttack()
        self.satoshi_analysis = SatoshiSignatureAnalysis()
        self.malleability_analysis = SignatureMalleability()
        self.key_manager = SM2KeyManager()
        self.benchmarker = SM2Benchmarker()
    
    def run_nonce_security_analysis(self) -> Dict[str, Any]:
        """Comprehensive nonce security analysis"""
        print("=== Nonce Security Analysis ===\n")
        
        results = {
            'nonce_reuse': {},
            'weak_nonces': {},
            'recommendations': []
        }
        
        # Generate test keys
        private_key = secrets.randbelow(self.nonce_reuse_attack.sm2.curve.n - 1) + 1
        
        # Test nonce reuse vulnerability
        print("1. Testing nonce reuse vulnerability...")
        messages = [
            b"Transaction 1: Payment to Alice",
            b"Transaction 2: Payment to Bob"
        ]
        
        # Simulate nonce reuse
        reused_nonce = secrets.randbelow(self.nonce_reuse_attack.sm2.curve.n - 1) + 1
        signatures = []
        for msg in messages:
            sig_data = self.nonce_reuse_attack.vulnerable_sign(msg, private_key, reused_nonce)
            signatures.append(sig_data)
        
        # Attempt attack
        recovered_nonce = self.nonce_reuse_attack.recover_nonce(signatures[0], signatures[1])
        recovered_key = None
        if recovered_nonce:
            recovered_key = self.nonce_reuse_attack.recover_private_key(signatures[0], recovered_nonce)
        
        results['nonce_reuse'] = {
            'attack_successful': recovered_key == private_key,
            'recovered_nonce': recovered_nonce,
            'original_private_key': private_key,
            'recovered_private_key': recovered_key
        }
        
        if recovered_key == private_key:
            print("   ⚠️  CRITICAL: Nonce reuse attack successful!")
            results['recommendations'].append("CRITICAL: Never reuse nonces in signature generation")
        else:
            print("   ✓ Nonce reuse attack failed")
        
        # Test weak nonce patterns
        print("\n2. Testing weak nonce patterns...")
        
        # Generate signatures with sequential nonces
        start_nonce = secrets.randbelow(self.weak_nonce_attack.sm2.curve.n // 2)
        sequential_nonces = self.weak_nonce_attack.generate_weak_sequential_nonces(start_nonce, 5)
        sequential_sigs = self.weak_nonce_attack.sign_with_weak_nonces(
            [f"Message {i}".encode() for i in range(5)], private_key, sequential_nonces
        )
        
        # Analyze patterns
        pattern_analysis = self.weak_nonce_attack.analyze_nonce_patterns(sequential_nonces)
        
        results['weak_nonces'] = {
            'pattern_analysis': pattern_analysis,
            'entropy_efficiency': pattern_analysis['entropy']['efficiency'],
            'patterns_detected': len(pattern_analysis['patterns'])
        }
        
        if pattern_analysis['entropy']['efficiency'] < 0.8:
            print("   ⚠️  WARNING: Weak nonce entropy detected!")
            results['recommendations'].append("WARNING: Improve nonce generation entropy")
        else:
            print("   ✓ Nonce entropy appears adequate")
        
        return results
    
    def run_side_channel_analysis(self) -> Dict[str, Any]:
        """Comprehensive side-channel attack analysis"""
        print("\n=== Side-Channel Attack Analysis ===\n")
        
        results = {
            'timing_attack': {},
            'power_attack': {},
            'cache_attack': {},
            'recommendations': []
        }
        
        # Timing attack analysis
        print("1. Timing attack analysis...")
        timing_results = self.timing_attack.demonstrate_timing_attack(sample_count=100)
        
        vulnerable_analysis, secure_analysis = timing_results
        
        results['timing_attack'] = {
            'vulnerable_correlation': vulnerable_analysis['correlation_coefficient'],
            'secure_correlation': secure_analysis['correlation_coefficient'],
            'vulnerable_risk': vulnerable_analysis['vulnerability'],
            'secure_risk': secure_analysis['vulnerability']
        }
        
        if vulnerable_analysis['vulnerability'] == 'HIGH':
            print("   ⚠️  HIGH: Timing attack vulnerability detected!")
            results['recommendations'].append("HIGH: Implement constant-time algorithms")
        else:
            print("   ✓ Timing attack risk appears low")
        
        # Power analysis simulation
        print("\n2. Power analysis simulation...")
        test_scalars = [secrets.randbelow(2**20) for _ in range(50)]
        power_traces = [self.power_attack.simulate_power_trace(scalar) for scalar in test_scalars]
        
        spa_result = self.power_attack.simple_power_analysis(power_traces, test_scalars)
        
        if 'error' not in spa_result:
            results['power_attack'] = {
                'snr': spa_result['snr'],
                'attack_feasibility': spa_result['attack_feasibility']
            }
            
            if spa_result['attack_feasibility'] == 'HIGH':
                print("   ⚠️  HIGH: Power analysis attack feasible!")
                results['recommendations'].append("HIGH: Implement power analysis countermeasures")
            else:
                print("   ✓ Power analysis attack risk appears low")
        
        # Cache attack simulation
        print("\n3. Cache attack simulation...")
        test_indices = [secrets.randbelow(256) for _ in range(100)]
        cache_traces = self.cache_attack.collect_cache_traces(test_indices, secure=False)
        cache_analysis = self.cache_attack.analyze_cache_patterns(cache_traces)
        
        if 'error' not in cache_analysis:
            results['cache_attack'] = {
                'separability': cache_analysis['separability'],
                'attack_feasibility': cache_analysis['attack_feasibility']
            }
            
            if cache_analysis['attack_feasibility'] == 'HIGH':
                print("   ⚠️  HIGH: Cache attack vulnerability detected!")
                results['recommendations'].append("HIGH: Implement cache attack countermeasures")
            else:
                print("   ✓ Cache attack risk appears low")
        
        return results
    
    def run_signature_analysis(self) -> Dict[str, Any]:
        """Comprehensive signature security analysis"""
        print("\n=== Signature Security Analysis ===\n")
        
        results = {
            'entropy_analysis': {},
            'malleability_analysis': {},
            'bitcoin_analysis': {},
            'recommendations': []
        }
        
        # Generate test signatures
        private_key = secrets.randbelow(self.malleability_analysis.sm2.curve.n - 1) + 1
        test_signatures = []
        
        print("1. Generating test signatures for analysis...")
        for i in range(100):
            message = f"Test message {i}".encode()
            sig = self.malleability_analysis.sm2.sign_message(message, private_key)
            test_signatures.append(sig)
        
        # Entropy analysis
        entropy_analysis = self.malleability_analysis.analyze_signature_entropy(test_signatures)
        results['entropy_analysis'] = entropy_analysis
        
        print(f"   Canonical signature ratio: {entropy_analysis['canonical_ratio']:.2%}")
        
        if entropy_analysis['canonical_ratio'] < 0.5:
            print("   ⚠️  WARNING: Low canonical signature ratio!")
            results['recommendations'].append("WARNING: Consider enforcing canonical signatures")
        
        # Malleability analysis
        print("\n2. Signature malleability analysis...")
        sample_sig = test_signatures[0]
        malleable_sig = self.malleability_analysis.create_malleable_signature(sample_sig)
        
        is_canonical_orig = self.malleability_analysis.is_signature_canonical(sample_sig)
        is_canonical_mall = self.malleability_analysis.is_signature_canonical(malleable_sig)
        
        results['malleability_analysis'] = {
            'original_canonical': is_canonical_orig,
            'malleable_canonical': is_canonical_mall,
            'malleability_possible': sample_sig != malleable_sig
        }
        
        if not is_canonical_orig:
            print("   ⚠️  WARNING: Non-canonical signatures detected!")
            results['recommendations'].append("WARNING: Enforce canonical signature format")
        else:
            print("   ✓ Signatures appear canonical")
        
        # Bitcoin-style analysis
        print("\n3. Bitcoin-style signature analysis...")
        bitcoin_analysis = self.satoshi_analysis.analyze_early_bitcoin_patterns(test_signatures[:10])
        
        results['bitcoin_analysis'] = bitcoin_analysis
        
        if bitcoin_analysis['suspicious_patterns'] > 0:
            print(f"   ⚠️  WARNING: {bitcoin_analysis['suspicious_patterns']} suspicious patterns detected!")
            results['recommendations'].append("WARNING: Review signature generation for suspicious patterns")
        else:
            print("   ✓ No suspicious signature patterns detected")
        
        return results
    
    def run_performance_security_analysis(self) -> Dict[str, Any]:
        """Performance and security trade-off analysis"""
        print("\n=== Performance vs Security Analysis ===\n")
        
        results = {
            'performance': {},
            'security_overhead': {},
            'recommendations': []
        }
        
        # Benchmark different implementations
        print("1. Benchmarking signature operations...")
        
        # Standard implementation
        start_time = time.time()
        for _ in range(100):
            private_key = secrets.randbelow(self.benchmarker.sm2.curve.n - 1) + 1
            message = secrets.token_bytes(32)
            signature = self.benchmarker.sm2.sign_message(message, private_key)
        standard_time = time.time() - start_time
        
        # Simulated secure implementation (with countermeasures)
        start_time = time.time()
        for _ in range(100):
            private_key = secrets.randbelow(self.benchmarker.sm2.curve.n - 1) + 1
            message = secrets.token_bytes(32)
            # Simulate additional security checks
            time.sleep(0.0001)  # Simulated constant-time operations
            signature = self.benchmarker.sm2.sign_message(message, private_key)
        secure_time = time.time() - start_time
        
        results['performance'] = {
            'standard_time': standard_time,
            'secure_time': secure_time,
            'overhead_ratio': secure_time / standard_time,
            'signatures_per_second_standard': 100 / standard_time,
            'signatures_per_second_secure': 100 / secure_time
        }
        
        print(f"   Standard implementation: {100/standard_time:.1f} signatures/second")
        print(f"   Secure implementation: {100/secure_time:.1f} signatures/second")
        print(f"   Security overhead: {((secure_time/standard_time - 1) * 100):.1f}%")
        
        if (secure_time / standard_time) > 2.0:
            print("   ⚠️  WARNING: High security overhead detected!")
            results['recommendations'].append("Consider optimizing security countermeasures")
        else:
            print("   ✓ Security overhead appears reasonable")
        
        return results
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security analysis report"""
        print("SM2 Comprehensive Security Analysis")
        print("=" * 50)
        
        report = {
            'timestamp': time.time(),
            'nonce_security': self.run_nonce_security_analysis(),
            'side_channel_security': self.run_side_channel_analysis(),
            'signature_security': self.run_signature_analysis(),
            'performance_analysis': self.run_performance_security_analysis(),
            'overall_recommendations': []
        }
        
        # Consolidate recommendations
        all_recommendations = []
        for section in ['nonce_security', 'side_channel_security', 'signature_security', 'performance_analysis']:
            if 'recommendations' in report[section]:
                all_recommendations.extend(report[section]['recommendations'])
        
        # Remove duplicates and prioritize
        unique_recommendations = list(set(all_recommendations))
        critical_recs = [r for r in unique_recommendations if 'CRITICAL' in r]
        high_recs = [r for r in unique_recommendations if 'HIGH' in r and r not in critical_recs]
        warning_recs = [r for r in unique_recommendations if 'WARNING' in r and r not in critical_recs + high_recs]
        other_recs = [r for r in unique_recommendations if r not in critical_recs + high_recs + warning_recs]
        
        report['overall_recommendations'] = critical_recs + high_recs + warning_recs + other_recs
        
        # Print summary
        print(f"\n=== Security Analysis Summary ===")
        print(f"Critical issues: {len(critical_recs)}")
        print(f"High priority issues: {len(high_recs)}")
        print(f"Warnings: {len(warning_recs)}")
        print(f"Other recommendations: {len(other_recs)}")
        
        if critical_recs:
            print(f"\n🔴 CRITICAL ISSUES:")
            for rec in critical_recs:
                print(f"   • {rec}")
        
        if high_recs:
            print(f"\n🟠 HIGH PRIORITY:")
            for rec in high_recs:
                print(f"   • {rec}")
        
        if warning_recs:
            print(f"\n🟡 WARNINGS:")
            for rec in warning_recs:
                print(f"   • {rec}")
        
        return report
    
    def run_interactive_analysis(self):
        """Interactive security analysis menu"""
        while True:
            print("\n" + "="*50)
            print("SM2 Security Analysis Suite")
            print("="*50)
            print("1. Nonce Security Analysis")
            print("2. Side-Channel Attack Analysis")  
            print("3. Signature Security Analysis")
            print("4. Performance vs Security Analysis")
            print("5. Generate Comprehensive Report")
            print("6. Bitcoin Signature Analysis")
            print("7. Attack Demonstration Suite")
            print("8. Exit")
            
            choice = input("\nSelect analysis type (1-8): ").strip()
            
            if choice == "1":
                self.run_nonce_security_analysis()
            elif choice == "2":
                self.run_side_channel_analysis()
            elif choice == "3":
                self.run_signature_analysis()
            elif choice == "4":
                self.run_performance_security_analysis()
            elif choice == "5":
                report = self.generate_security_report()
                print(f"\nReport generated with {len(report['overall_recommendations'])} recommendations")
            elif choice == "6":
                print("\nRunning Bitcoin signature analysis...")
                self.satoshi_analysis.demonstrate_bitcoin_analysis()
            elif choice == "7":
                print("\nRunning attack demonstration suite...")
                self.nonce_reuse_attack.demonstrate_attack()
                print("\n" + "-"*50 + "\n")
                self.weak_nonce_attack.demonstrate_weak_nonce_attacks()
            elif choice == "8":
                print("Exiting security analysis suite...")
                break
            else:
                print("Invalid choice. Please select 1-8.")

def main():
    """Main entry point"""
    try:
        analyzer = SM2SecurityAnalyzer()
        
        print("SM2 Comprehensive Security Analysis Tool")
        print("Educational tool for understanding SM2 security considerations\n")
        
        mode = input("Choose mode:\n1. Interactive analysis\n2. Generate full report\n3. Quick security check\n\nEnter choice (1-3): ").strip()
        
        if mode == "1":
            analyzer.run_interactive_analysis()
        elif mode == "2":
            report = analyzer.generate_security_report()
            print(f"\nFull security report completed with {len(report['overall_recommendations'])} total recommendations")
        elif mode == "3":
            print("\nRunning quick security check...")
            
            # Quick checks
            nonce_results = analyzer.run_nonce_security_analysis()
            timing_results = analyzer.timing_attack.demonstrate_timing_attack(sample_count=50)
            
            print(f"\nQuick Security Assessment:")
            print(f"Nonce reuse vulnerability: {'DETECTED' if nonce_results['nonce_reuse']['attack_successful'] else 'OK'}")
            print(f"Timing attack risk: {timing_results[0]['vulnerability']}")
            print(f"Weak nonce patterns: {'DETECTED' if nonce_results['weak_nonces']['patterns_detected'] > 0 else 'OK'}")
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
