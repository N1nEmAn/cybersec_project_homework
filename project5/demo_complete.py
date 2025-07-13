#!/usr/bin/env python3
"""
SM2 Complete Demonstration Script
Runs all implementations and generates comprehensive results
"""

import sys
import os
import time
import json

# Add src and benchmarks to path
current_dir = os.path.dirname(__file__)
sys.path.extend([
    os.path.join(current_dir, 'src'),
    os.path.join(current_dir, 'benchmarks')
])

from sm2_basic import SM2Basic
from sm2_optimized import SM2Optimized
from sm2_simd import SM2SIMD
from performance_benchmark import SM2Benchmark
from generate_charts import SM2ChartGenerator


def demo_basic_functionality():
    """Demonstrate basic SM2 functionality"""
    print("=" * 60)
    print("SM2 ELLIPTIC CURVE DIGITAL SIGNATURE ALGORITHM DEMO")
    print("=" * 60)
    
    implementations = {
        'Basic': SM2Basic(),
        'Optimized': SM2Optimized(),
        'SIMD': SM2SIMD()
    }
    
    test_message = b"Hello, SM2 Digital Signature!"
    
    for name, impl in implementations.items():
        print(f"\n--- {name} Implementation Demo ---")
        
        # Key generation
        print("1. Generating key pair...")
        start_time = time.time()
        private_key, public_key = impl.generate_keypair()
        keygen_time = time.time() - start_time
        
        print(f"   Private key: {hex(private_key)[:50]}...")
        print(f"   Public key X: {hex(public_key[0])[:50]}...")
        print(f"   Public key Y: {hex(public_key[1])[:50]}...")
        print(f"   Key generation time: {keygen_time:.4f} seconds")
        
        # Signing
        print("\n2. Signing message...")
        start_time = time.time()
        signature = impl.sign(test_message, private_key)
        sign_time = time.time() - start_time
        
        print(f"   Message: {test_message}")
        print(f"   Signature r: {hex(signature[0])[:50]}...")
        print(f"   Signature s: {hex(signature[1])[:50]}...")
        print(f"   Signing time: {sign_time:.4f} seconds")
        
        # Verification
        print("\n3. Verifying signature...")
        start_time = time.time()
        is_valid = impl.verify(test_message, signature, public_key)
        verify_time = time.time() - start_time
        
        print(f"   Verification result: {'✓ VALID' if is_valid else '✗ INVALID'}")
        print(f"   Verification time: {verify_time:.4f} seconds")
        
        # Test with tampered message
        print("\n4. Testing tampered message...")
        tampered_message = test_message + b" [TAMPERED]"
        is_tampered_valid = impl.verify(tampered_message, signature, public_key)
        print(f"   Tampered message: {tampered_message}")
        print(f"   Verification result: {'✗ VALID (ERROR!)' if is_tampered_valid else '✓ INVALID (CORRECT)'}")


def demo_performance_comparison():
    """Demonstrate performance comparison"""
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON DEMO")
    print("=" * 60)
    
    implementations = {
        'Basic': SM2Basic(),
        'Optimized': SM2Optimized(),
        'SIMD': SM2SIMD()
    }
    
    operations = ['Key Generation', 'Signing', 'Verification']
    num_iterations = 20
    
    results = {}
    
    for name, impl in implementations.items():
        print(f"\n--- Benchmarking {name} Implementation ---")
        results[name] = {}
        
        # Prepare for signing and verification tests
        private_key, public_key = impl.generate_keypair()
        message = b"Performance test message"
        signature = impl.sign(message, private_key)
        
        # Key Generation Test
        print(f"Testing key generation ({num_iterations} iterations)...")
        times = []
        for _ in range(num_iterations):
            start = time.time()
            impl.generate_keypair()
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        results[name]['keygen'] = avg_time
        print(f"   Average time: {avg_time:.4f} seconds")
        print(f"   Throughput: {1/avg_time:.2f} ops/sec")
        
        # Signing Test
        print(f"Testing signing ({num_iterations} iterations)...")
        times = []
        for _ in range(num_iterations):
            start = time.time()
            impl.sign(message, private_key)
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        results[name]['sign'] = avg_time
        print(f"   Average time: {avg_time:.4f} seconds")
        print(f"   Throughput: {1/avg_time:.2f} ops/sec")
        
        # Verification Test
        print(f"Testing verification ({num_iterations} iterations)...")
        times = []
        for _ in range(num_iterations):
            start = time.time()
            impl.verify(message, signature, public_key)
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        results[name]['verify'] = avg_time
        print(f"   Average time: {avg_time:.4f} seconds")
        print(f"   Throughput: {1/avg_time:.2f} ops/sec")
    
    # Performance Summary
    print("\n--- Performance Summary ---")
    print(f"{'Operation':<15} {'Basic':<12} {'Optimized':<12} {'SIMD':<12} {'Opt Speedup':<12} {'SIMD Speedup':<12}")
    print("-" * 80)
    
    operations_map = {
        'Key Gen': 'keygen',
        'Signing': 'sign', 
        'Verification': 'verify'
    }
    
    for op_name, op_key in operations_map.items():
        basic_time = results['Basic'][op_key] * 1000  # Convert to ms
        opt_time = results['Optimized'][op_key] * 1000
        simd_time = results['SIMD'][op_key] * 1000
        
        opt_speedup = basic_time / opt_time
        simd_speedup = basic_time / simd_time
        
        print(f"{op_name:<15} {basic_time:<12.2f} {opt_time:<12.2f} {simd_time:<12.2f} "
              f"{opt_speedup:<12.2f}x {simd_speedup:<12.2f}x")


def demo_batch_operations():
    """Demonstrate batch operations"""
    print("\n" + "=" * 60)
    print("BATCH OPERATIONS DEMO")
    print("=" * 60)
    
    simd_impl = SM2SIMD()
    
    batch_sizes = [5, 10, 20]
    
    for batch_size in batch_sizes:
        print(f"\n--- Batch Size: {batch_size} ---")
        
        # Prepare batch data
        batch_data = []
        individual_times = []
        
        print("Preparing batch data...")
        for i in range(batch_size):
            message = f"Batch message {i}".encode()
            private_key, public_key = simd_impl.generate_keypair()
            signature = simd_impl.sign(message, private_key)
            batch_data.append((message, signature, public_key))
        
        # Test batch verification
        print("Testing batch verification...")
        start_time = time.time()
        batch_results = simd_impl.batch_verify(batch_data)
        batch_time = time.time() - start_time
        
        # Test individual verification for comparison
        print("Testing individual verification...")
        start_time = time.time()
        individual_results = []
        for message, signature, public_key in batch_data:
            result = simd_impl.verify(message, signature, public_key)
            individual_results.append(result)
        individual_time = time.time() - start_time
        
        # Results
        speedup = individual_time / batch_time if batch_time > 0 else 0
        batch_throughput = batch_size / batch_time
        individual_throughput = batch_size / individual_time
        
        print(f"   Batch verification time: {batch_time:.4f} seconds")
        print(f"   Individual verification time: {individual_time:.4f} seconds")
        print(f"   Speedup: {speedup:.2f}x")
        print(f"   Batch throughput: {batch_throughput:.2f} ops/sec")
        print(f"   Individual throughput: {individual_throughput:.2f} ops/sec")
        print(f"   All signatures valid: {all(batch_results)}")


def demo_security_features():
    """Demonstrate security features"""
    print("\n" + "=" * 60)
    print("SECURITY FEATURES DEMO")
    print("=" * 60)
    
    impl = SM2Optimized()  # Use optimized version with security features
    
    print("1. Testing signature randomness...")
    private_key, public_key = impl.generate_keypair()
    message = b"Test message for randomness"
    
    signatures = []
    for i in range(5):
        sig = impl.sign(message, private_key)
        signatures.append(sig)
        print(f"   Signature {i+1}: r={hex(sig[0])[:20]}..., s={hex(sig[1])[:20]}...")
    
    # Check that all signatures are different
    unique_sigs = set(signatures)
    print(f"   Unique signatures: {len(unique_sigs)}/{len(signatures)} ({'✓ Good randomness' if len(unique_sigs) == len(signatures) else '✗ Poor randomness'})")
    
    print("\n2. Testing message integrity...")
    original_message = b"Important message"
    signature = impl.sign(original_message, private_key)
    
    test_cases = [
        (original_message, "Original message"),
        (original_message + b" ", "Added space"),
        (original_message[:-1], "Removed character"),
        (original_message.replace(b"Important", b"Modified"), "Modified word"),
        (b"", "Empty message"),
    ]
    
    for test_msg, description in test_cases:
        is_valid = impl.verify(test_msg, signature, public_key)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        expected = "✓" if test_msg == original_message else "✗"
        result = "CORRECT" if (is_valid and test_msg == original_message) or (not is_valid and test_msg != original_message) else "ERROR"
        print(f"   {description:<20}: {status} ({result})")


def generate_comprehensive_report():
    """Generate comprehensive performance report and charts"""
    print("\n" + "=" * 60)
    print("GENERATING COMPREHENSIVE REPORT")
    print("=" * 60)
    
    print("1. Running comprehensive benchmark...")
    benchmark = SM2Benchmark()
    results = benchmark.run_comprehensive_benchmark()
    
    print("\n2. Generating performance charts...")
    chart_generator = SM2ChartGenerator("charts")
    chart_generator.generate_all_charts(results)
    
    print("\n3. Saving results...")
    benchmark.save_results_csv("performance_results.csv")
    
    # Save detailed results as JSON
    with open("detailed_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n4. Printing final report...")
    benchmark.print_results()
    
    print(f"\nReports generated:")
    print(f"   - Performance charts: charts/")
    print(f"   - CSV results: performance_results.csv")
    print(f"   - Detailed JSON: detailed_results.json")


def main():
    """Main demonstration function"""
    print("SM2 Elliptic Curve Digital Signature Algorithm")
    print("Complete Implementation and Optimization Demo")
    print("=" * 60)
    
    try:
        # Basic functionality demo
        demo_basic_functionality()
        
        # Performance comparison
        demo_performance_comparison()
        
        # Batch operations demo
        demo_batch_operations()
        
        # Security features demo
        demo_security_features()
        
        # Generate comprehensive report
        generate_comprehensive_report()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nFiles generated:")
        print("   - charts/: Performance visualization charts")
        print("   - performance_results.csv: Benchmark data")
        print("   - detailed_results.json: Complete results")
        print("\nFor detailed technical information, see:")
        print("   - docs/mathematical_derivation.md")
        print("   - docs/optimization_report.md")
        print("   - README.md")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
