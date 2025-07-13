"""
SM2 Performance Benchmarking Suite
Comprehensive benchmarking for different SM2 implementations:
- Basic implementation
- Optimized implementation with Jacobian coordinates
- SIMD-optimized implementation with windowing
"""

import time
import statistics
from typing import List, Dict, Any, Tuple
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sm2_basic import SM2Basic
from sm2_optimized import SM2Optimized  
from sm2_simd import SM2SIMD


class SM2Benchmark:
    """Comprehensive benchmarking suite for SM2 implementations"""
    
    def __init__(self):
        self.implementations = {
            'Basic': SM2Basic(),
            'Optimized': SM2Optimized(),
            'SIMD': SM2SIMD()
        }
        self.results = {}
    
    def benchmark_keygen(self, num_iterations: int = 100) -> Dict[str, float]:
        """Benchmark key generation performance"""
        print(f"Benchmarking key generation ({num_iterations} iterations)...")
        results = {}
        
        for name, impl in self.implementations.items():
            print(f"  Testing {name} implementation...")
            times = []
            
            for _ in range(num_iterations):
                start_time = time.time()
                impl.generate_keypair()
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            results[name] = {
                'avg_time': avg_time,
                'std_dev': std_dev,
                'min_time': min(times),
                'max_time': max(times),
                'ops_per_sec': 1.0 / avg_time
            }
        
        return results
    
    def benchmark_signing(self, num_iterations: int = 100) -> Dict[str, float]:
        """Benchmark signing performance"""
        print(f"Benchmarking signing ({num_iterations} iterations)...")
        results = {}
        
        # Prepare test data
        message = b"Benchmark message for signing performance test"
        
        for name, impl in self.implementations.items():
            print(f"  Testing {name} implementation...")
            
            # Generate a key pair for this implementation
            private_key, public_key = impl.generate_keypair()
            
            times = []
            for _ in range(num_iterations):
                start_time = time.time()
                impl.sign(message, private_key)
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            results[name] = {
                'avg_time': avg_time,
                'std_dev': std_dev,
                'min_time': min(times),
                'max_time': max(times),
                'ops_per_sec': 1.0 / avg_time
            }
        
        return results
    
    def benchmark_verification(self, num_iterations: int = 100) -> Dict[str, float]:
        """Benchmark verification performance"""
        print(f"Benchmarking verification ({num_iterations} iterations)...")
        results = {}
        
        message = b"Benchmark message for verification performance test"
        
        for name, impl in self.implementations.items():
            print(f"  Testing {name} implementation...")
            
            # Prepare signature for verification
            private_key, public_key = impl.generate_keypair()
            signature = impl.sign(message, private_key)
            
            times = []
            for _ in range(num_iterations):
                start_time = time.time()
                impl.verify(message, signature, public_key)
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            results[name] = {
                'avg_time': avg_time,
                'std_dev': std_dev,
                'min_time': min(times),
                'max_time': max(times),
                'ops_per_sec': 1.0 / avg_time
            }
        
        return results
    
    def benchmark_batch_operations(self, batch_sizes: List[int] = [10, 50, 100]) -> Dict[str, Dict[int, float]]:
        """Benchmark batch operations for SIMD implementation"""
        print("Benchmarking batch operations...")
        results = {}
        
        # Only test SIMD implementation which supports batch operations
        if 'SIMD' not in self.implementations:
            return results
        
        simd_impl = self.implementations['SIMD']
        
        for batch_size in batch_sizes:
            print(f"  Testing batch size {batch_size}...")
            
            # Prepare batch data
            batch_data = []
            for i in range(batch_size):
                message = f"Batch message {i}".encode()
                private_key, public_key = simd_impl.generate_keypair()
                signature = simd_impl.sign(message, private_key)
                batch_data.append((message, signature, public_key))
            
            # Benchmark batch verification
            start_time = time.time()
            simd_impl.batch_verify(batch_data)
            batch_time = time.time() - start_time
            
            # Benchmark individual verification for comparison
            start_time = time.time()
            for message, signature, public_key in batch_data:
                simd_impl.verify(message, signature, public_key)
            individual_time = time.time() - start_time
            
            speedup = individual_time / batch_time if batch_time > 0 else 0
            
            if 'SIMD_batch' not in results:
                results['SIMD_batch'] = {}
            
            results['SIMD_batch'][batch_size] = {
                'batch_time': batch_time,
                'individual_time': individual_time,
                'speedup': speedup,
                'batch_ops_per_sec': batch_size / batch_time,
                'individual_ops_per_sec': batch_size / individual_time
            }
        
        return results
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark suite"""
        print("=== SM2 Comprehensive Performance Benchmark ===\n")
        
        # Key generation benchmark
        keygen_results = self.benchmark_keygen(50)
        
        # Signing benchmark  
        signing_results = self.benchmark_signing(50)
        
        # Verification benchmark
        verification_results = self.benchmark_verification(50)
        
        # Batch operations benchmark
        batch_results = self.benchmark_batch_operations([10, 25, 50])
        
        self.results = {
            'key_generation': keygen_results,
            'signing': signing_results,
            'verification': verification_results,
            'batch_operations': batch_results
        }
        
        return self.results
    
    def print_results(self):
        """Print formatted benchmark results"""
        if not self.results:
            print("No benchmark results available. Run benchmark first.")
            return
        
        print("\n" + "="*60)
        print("BENCHMARK RESULTS")
        print("="*60)
        
        # Key Generation Results
        print("\n--- KEY GENERATION PERFORMANCE ---")
        self._print_operation_results(self.results['key_generation'])
        
        # Signing Results
        print("\n--- SIGNING PERFORMANCE ---")
        self._print_operation_results(self.results['signing'])
        
        # Verification Results
        print("\n--- VERIFICATION PERFORMANCE ---")
        self._print_operation_results(self.results['verification'])
        
        # Batch Operations Results
        if self.results['batch_operations']:
            print("\n--- BATCH OPERATIONS PERFORMANCE ---")
            for batch_size, data in self.results['batch_operations']['SIMD_batch'].items():
                print(f"\nBatch Size: {batch_size}")
                print(f"  Batch Time: {data['batch_time']:.4f} sec")
                print(f"  Individual Time: {data['individual_time']:.4f} sec")
                print(f"  Speedup: {data['speedup']:.2f}x")
                print(f"  Batch Throughput: {data['batch_ops_per_sec']:.2f} ops/sec")
        
        # Performance Summary
        self._print_performance_summary()
    
    def _print_operation_results(self, results: Dict[str, Dict[str, float]]):
        """Print results for a specific operation"""
        print(f"{'Implementation':<12} {'Avg Time (ms)':<15} {'Ops/sec':<10} {'Std Dev (ms)':<15}")
        print("-" * 60)
        
        for impl_name, data in results.items():
            avg_ms = data['avg_time'] * 1000
            std_ms = data['std_dev'] * 1000
            ops_per_sec = data['ops_per_sec']
            
            print(f"{impl_name:<12} {avg_ms:<15.3f} {ops_per_sec:<10.2f} {std_ms:<15.3f}")
    
    def _print_performance_summary(self):
        """Print overall performance summary"""
        print("\n--- PERFORMANCE SUMMARY ---")
        
        # Calculate relative performance
        basic_keygen = self.results['key_generation']['Basic']['avg_time']
        basic_sign = self.results['signing']['Basic']['avg_time']
        basic_verify = self.results['verification']['Basic']['avg_time']
        
        print(f"{'Operation':<15} {'Basic':<10} {'Optimized':<12} {'SIMD':<10}")
        print("-" * 50)
        
        # Key generation speedup
        opt_keygen_speedup = basic_keygen / self.results['key_generation']['Optimized']['avg_time']
        simd_keygen_speedup = basic_keygen / self.results['key_generation']['SIMD']['avg_time']
        print(f"{'Key Gen':<15} {'1.00x':<10} {opt_keygen_speedup:<12.2f}x {simd_keygen_speedup:<10.2f}x")
        
        # Signing speedup
        opt_sign_speedup = basic_sign / self.results['signing']['Optimized']['avg_time']
        simd_sign_speedup = basic_sign / self.results['signing']['SIMD']['avg_time']
        print(f"{'Signing':<15} {'1.00x':<10} {opt_sign_speedup:<12.2f}x {simd_sign_speedup:<10.2f}x")
        
        # Verification speedup
        opt_verify_speedup = basic_verify / self.results['verification']['Optimized']['avg_time']
        simd_verify_speedup = basic_verify / self.results['verification']['SIMD']['avg_time']
        print(f"{'Verification':<15} {'1.00x':<10} {opt_verify_speedup:<12.2f}x {simd_verify_speedup:<10.2f}x")
    
    def save_results_csv(self, filename: str = "sm2_benchmark_results.csv"):
        """Save benchmark results to CSV file"""
        if not self.results:
            print("No results to save.")
            return
        
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Operation', 'Implementation', 'Avg_Time_ms', 'Ops_Per_Sec', 'Std_Dev_ms'])
            
            # Write key generation results
            for impl, data in self.results['key_generation'].items():
                writer.writerow(['Key_Generation', impl, 
                               data['avg_time']*1000, data['ops_per_sec'], data['std_dev']*1000])
            
            # Write signing results
            for impl, data in self.results['signing'].items():
                writer.writerow(['Signing', impl,
                               data['avg_time']*1000, data['ops_per_sec'], data['std_dev']*1000])
            
            # Write verification results
            for impl, data in self.results['verification'].items():
                writer.writerow(['Verification', impl,
                               data['avg_time']*1000, data['ops_per_sec'], data['std_dev']*1000])
        
        print(f"Results saved to {filename}")


def main():
    """Main benchmark execution"""
    benchmark = SM2Benchmark()
    
    try:
        # Run comprehensive benchmark
        results = benchmark.run_comprehensive_benchmark()
        
        # Print results
        benchmark.print_results()
        
        # Save results to CSV
        benchmark.save_results_csv()
        
    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
