"""
SM2 Side-Channel Attack Simulations

This module simulates various side-channel attacks against SM2 implementations,
including timing attacks, power analysis, and cache attacks. These simulations
help understand implementation vulnerabilities and test countermeasures.

Educational purposes only - demonstrates why constant-time implementations
and side-channel countermeasures are critical for cryptographic security.
"""

import time
import random
import secrets
import statistics
from typing import List, Tuple, Dict, Any, Optional, Callable
import sys
import os
from collections import defaultdict
import hashlib

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sm2_basic import SM2, Point

class TimingAttack:
    """Simulation of timing attacks against SM2 scalar multiplication"""
    
    def __init__(self):
        self.sm2 = SM2()
        self.timing_samples = []
    
    def vulnerable_point_multiply(self, scalar: int, point: Point) -> Tuple[Point, float]:
        """
        Vulnerable scalar multiplication with timing variations
        Simulates non-constant time implementation
        """
        start_time = time.perf_counter()
        
        if scalar == 0:
            end_time = time.perf_counter()
            return Point(None, None), end_time - start_time
        
        result = Point(None, None)  # Point at infinity
        addend = point
        
        # Vulnerable binary method - timing depends on number of 1-bits
        while scalar > 0:
            if scalar & 1:
                # Addition operation (expensive)
                if result.x is None:
                    result = addend
                else:
                    result = self.sm2.point_add(result, addend)
                # Simulate variable timing based on operand values
                time.sleep(self._simulate_addition_timing(result, addend))
            
            # Doubling operation
            addend = self.sm2.point_double(addend)
            scalar >>= 1
            
            # Simulate variable timing based on point coordinates
            time.sleep(self._simulate_doubling_timing(addend))
        
        end_time = time.perf_counter()
        return result, end_time - start_time
    
    def _simulate_addition_timing(self, p1: Point, p2: Point) -> float:
        """Simulate timing variations in point addition"""
        if p1.x is None or p2.x is None:
            return 0.00001  # Fast case
        
        # Timing depends on coordinate values (simulation)
        coord_complexity = (bin(p1.x).count('1') + bin(p2.x).count('1')) / 64
        return 0.00001 + coord_complexity * 0.00002
    
    def _simulate_doubling_timing(self, point: Point) -> float:
        """Simulate timing variations in point doubling"""
        if point.x is None:
            return 0.00001
        
        # Timing depends on coordinate complexity
        coord_complexity = bin(point.x).count('1') / 32
        return 0.00001 + coord_complexity * 0.00001
    
    def constant_time_point_multiply(self, scalar: int, point: Point) -> Tuple[Point, float]:
        """
        Constant-time scalar multiplication using Montgomery ladder
        """
        start_time = time.perf_counter()
        
        if scalar == 0:
            # Simulate constant time even for zero
            time.sleep(0.001)
            end_time = time.perf_counter()
            return Point(None, None), end_time - start_time
        
        # Montgomery ladder implementation
        R0 = Point(None, None)  # Point at infinity
        R1 = point
        
        # Process bits from most significant to least significant
        bit_length = scalar.bit_length()
        for i in range(bit_length - 1, -1, -1):
            bit = (scalar >> i) & 1
            
            # Constant-time conditional swap
            if bit == 0:
                R1 = self.sm2.point_add(R0, R1)
                R0 = self.sm2.point_double(R0)
            else:
                R0 = self.sm2.point_add(R0, R1)
                R1 = self.sm2.point_double(R1)
            
            # Constant delay regardless of bit value
            time.sleep(0.00003)
        
        end_time = time.perf_counter()
        return R0, end_time - start_time
    
    def collect_timing_samples(self, scalars: List[int], 
                              vulnerable: bool = True) -> List[Tuple[int, float, int]]:
        """
        Collect timing samples for analysis
        Returns list of (scalar, timing, hamming_weight) tuples
        """
        samples = []
        point = self.sm2.G
        
        multiply_func = (self.vulnerable_point_multiply if vulnerable 
                        else self.constant_time_point_multiply)
        
        for scalar in scalars:
            _, timing = multiply_func(scalar, point)
            hamming_weight = bin(scalar).count('1')
            samples.append((scalar, timing, hamming_weight))
        
        return samples
    
    def analyze_timing_correlation(self, samples: List[Tuple[int, float, int]]) -> Dict[str, Any]:
        """Analyze correlation between timing and scalar properties"""
        if len(samples) < 2:
            return {'error': 'Insufficient samples'}
        
        timings = [s[1] for s in samples]
        hamming_weights = [s[2] for s in samples]
        
        # Calculate correlation coefficient
        n = len(samples)
        mean_timing = statistics.mean(timings)
        mean_hamming = statistics.mean(hamming_weights)
        
        numerator = sum((t - mean_timing) * (h - mean_hamming) 
                       for t, h in zip(timings, hamming_weights))
        
        timing_variance = sum((t - mean_timing) ** 2 for t in timings)
        hamming_variance = sum((h - mean_hamming) ** 2 for h in hamming_weights)
        
        denominator = (timing_variance * hamming_variance) ** 0.5
        
        correlation = numerator / denominator if denominator > 0 else 0
        
        return {
            'correlation_coefficient': correlation,
            'timing_mean': mean_timing,
            'timing_std': statistics.stdev(timings) if len(timings) > 1 else 0,
            'hamming_mean': mean_hamming,
            'hamming_std': statistics.stdev(hamming_weights) if len(hamming_weights) > 1 else 0,
            'sample_count': n,
            'vulnerability': 'HIGH' if abs(correlation) > 0.5 else 
                           'MEDIUM' if abs(correlation) > 0.2 else 'LOW'
        }
    
    def demonstrate_timing_attack(self, sample_count: int = 1000):
        """Demonstrate timing attack effectiveness"""
        print("=== SM2 Timing Attack Demonstration ===\n")
        
        # Generate test scalars with varying Hamming weights
        scalars = []
        
        # Low Hamming weight scalars (few 1-bits)
        for _ in range(sample_count // 3):
            scalar = 0
            for _ in range(random.randint(1, 10)):  # Few bits set
                scalar |= (1 << random.randint(0, 255))
            scalars.append(scalar)
        
        # High Hamming weight scalars (many 1-bits)
        for _ in range(sample_count // 3):
            scalar = (1 << 256) - 1  # All bits set
            for _ in range(random.randint(1, 50)):  # Remove some bits
                scalar &= ~(1 << random.randint(0, 255))
            scalars.append(scalar)
        
        # Random scalars
        for _ in range(sample_count // 3):
            scalars.append(secrets.randbelow(self.sm2.curve.n))
        
        print(f"Testing {len(scalars)} scalar multiplications...\n")
        
        # Test vulnerable implementation
        print("1. Vulnerable Implementation:")
        vulnerable_samples = self.collect_timing_samples(scalars, vulnerable=True)
        vulnerable_analysis = self.analyze_timing_correlation(vulnerable_samples)
        
        print(f"   Correlation coefficient: {vulnerable_analysis['correlation_coefficient']:.4f}")
        print(f"   Timing variance: {vulnerable_analysis['timing_std']:.6f}s")
        print(f"   Vulnerability level: {vulnerable_analysis['vulnerability']}")
        print()
        
        # Test constant-time implementation
        print("2. Constant-time Implementation:")
        secure_samples = self.collect_timing_samples(scalars, vulnerable=False)
        secure_analysis = self.analyze_timing_correlation(secure_samples)
        
        print(f"   Correlation coefficient: {secure_analysis['correlation_coefficient']:.4f}")
        print(f"   Timing variance: {secure_analysis['timing_std']:.6f}s")
        print(f"   Vulnerability level: {secure_analysis['vulnerability']}")
        print()
        
        # Attack success simulation
        if abs(vulnerable_analysis['correlation_coefficient']) > 0.3:
            print("⚠️  Timing attack feasible against vulnerable implementation!")
            print("   Attacker could potentially recover private key bits")
        else:
            print("✓ Timing attack not feasible with current measurements")
        
        return vulnerable_analysis, secure_analysis

class PowerAnalysisAttack:
    """Simulation of power analysis attacks against SM2"""
    
    def __init__(self):
        self.sm2 = SM2()
    
    def simulate_power_trace(self, scalar: int, operation: str = 'multiply') -> List[float]:
        """
        Simulate power consumption trace during scalar multiplication
        Returns normalized power values over time
        """
        trace = []
        
        if operation == 'multiply':
            # Simulate power trace for scalar multiplication
            while scalar > 0:
                if scalar & 1:
                    # Point addition - higher power consumption
                    trace.extend(self._generate_addition_trace())
                else:
                    # No addition - lower power consumption
                    trace.extend(self._generate_idle_trace())
                
                # Point doubling - consistent power
                trace.extend(self._generate_doubling_trace())
                scalar >>= 1
        
        # Add noise
        noise_level = 0.1
        trace = [t + random.gauss(0, noise_level) for t in trace]
        
        return trace
    
    def _generate_addition_trace(self) -> List[float]:
        """Generate power trace for point addition"""
        # Simulate field operations with varying power consumption
        base_power = 0.8
        return [
            base_power + random.gauss(0, 0.05) for _ in range(10)
        ]
    
    def _generate_doubling_trace(self) -> List[float]:
        """Generate power trace for point doubling"""
        base_power = 0.6
        return [
            base_power + random.gauss(0, 0.03) for _ in range(8)
        ]
    
    def _generate_idle_trace(self) -> List[float]:
        """Generate power trace for idle periods"""
        base_power = 0.2
        return [
            base_power + random.gauss(0, 0.02) for _ in range(3)
        ]
    
    def simple_power_analysis(self, traces: List[List[float]], 
                             known_scalars: List[int]) -> Dict[str, Any]:
        """
        Perform Simple Power Analysis (SPA)
        Attempts to recover scalar bits from power traces
        """
        if len(traces) != len(known_scalars):
            return {'error': 'Mismatched traces and scalars'}
        
        # Analyze trace patterns
        pattern_analysis = {}
        
        for trace, scalar in zip(traces, known_scalars):
            bits = bin(scalar)[2:]  # Remove '0b' prefix
            
            # Segment trace based on expected bit operations
            segments_per_bit = len(trace) // len(bits) if bits else 1
            
            for i, bit in enumerate(bits):
                start_idx = i * segments_per_bit
                end_idx = (i + 1) * segments_per_bit
                segment = trace[start_idx:end_idx]
                
                avg_power = statistics.mean(segment) if segment else 0
                
                if bit not in pattern_analysis:
                    pattern_analysis[bit] = []
                pattern_analysis[bit].append(avg_power)
        
        # Calculate distinguishability
        if '0' in pattern_analysis and '1' in pattern_analysis:
            power_0 = statistics.mean(pattern_analysis['0'])
            power_1 = statistics.mean(pattern_analysis['1'])
            std_0 = statistics.stdev(pattern_analysis['0']) if len(pattern_analysis['0']) > 1 else 0
            std_1 = statistics.stdev(pattern_analysis['1']) if len(pattern_analysis['1']) > 1 else 0
            
            # Signal-to-noise ratio
            signal_diff = abs(power_1 - power_0)
            noise_level = (std_0 + std_1) / 2
            snr = signal_diff / noise_level if noise_level > 0 else float('inf')
            
            return {
                'power_bit_0': power_0,
                'power_bit_1': power_1,
                'signal_difference': signal_diff,
                'noise_level': noise_level,
                'snr': snr,
                'attack_feasibility': 'HIGH' if snr > 3 else 'MEDIUM' if snr > 1 else 'LOW'
            }
        
        return {'error': 'Insufficient data for analysis'}
    
    def differential_power_analysis(self, traces: List[List[float]], 
                                   hypotheses: List[int]) -> Dict[str, Any]:
        """
        Perform Differential Power Analysis (DPA)
        Uses statistical analysis to recover key bits
        """
        if len(traces) != len(hypotheses):
            return {'error': 'Mismatched traces and hypotheses'}
        
        # Group traces by hypothesis
        group_0 = []
        group_1 = []
        
        for trace, hypothesis in zip(traces, hypotheses):
            if hypothesis == 0:
                group_0.append(trace)
            else:
                group_1.append(trace)
        
        if not group_0 or not group_1:
            return {'error': 'Need traces for both hypothesis groups'}
        
        # Calculate average traces for each group
        min_length = min(min(len(t) for t in group_0), min(len(t) for t in group_1))
        
        avg_trace_0 = [
            statistics.mean(trace[i] for trace in group_0)
            for i in range(min_length)
        ]
        
        avg_trace_1 = [
            statistics.mean(trace[i] for trace in group_1)
            for i in range(min_length)
        ]
        
        # Calculate differential trace
        diff_trace = [avg_trace_1[i] - avg_trace_0[i] for i in range(min_length)]
        
        # Find peak in differential trace
        max_diff = max(abs(d) for d in diff_trace)
        peak_location = diff_trace.index(max(diff_trace, key=abs))
        
        return {
            'max_differential': max_diff,
            'peak_location': peak_location,
            'avg_trace_0': avg_trace_0,
            'avg_trace_1': avg_trace_1,
            'differential_trace': diff_trace,
            'attack_success': max_diff > 0.1  # Threshold for successful attack
        }
    
    def demonstrate_power_analysis(self):
        """Demonstrate power analysis attacks"""
        print("=== SM2 Power Analysis Attack Demonstration ===\n")
        
        # Generate test scalars
        test_scalars = [secrets.randbelow(2**20) for _ in range(100)]
        
        print("Collecting power traces...")
        traces = [self.simulate_power_trace(scalar) for scalar in test_scalars]
        
        # Simple Power Analysis
        print("\n1. Simple Power Analysis (SPA):")
        spa_result = self.simple_power_analysis(traces, test_scalars)
        
        if 'error' not in spa_result:
            print(f"   Power consumption for bit 0: {spa_result['power_bit_0']:.3f}")
            print(f"   Power consumption for bit 1: {spa_result['power_bit_1']:.3f}")
            print(f"   Signal-to-noise ratio: {spa_result['snr']:.2f}")
            print(f"   Attack feasibility: {spa_result['attack_feasibility']}")
        else:
            print(f"   Error: {spa_result['error']}")
        
        # Differential Power Analysis
        print("\n2. Differential Power Analysis (DPA):")
        # Create hypothesis based on LSB of scalar
        hypotheses = [scalar & 1 for scalar in test_scalars]
        
        dpa_result = self.differential_power_analysis(traces, hypotheses)
        
        if 'error' not in dpa_result:
            print(f"   Maximum differential: {dpa_result['max_differential']:.4f}")
            print(f"   Peak at sample: {dpa_result['peak_location']}")
            print(f"   Attack successful: {dpa_result['attack_success']}")
        else:
            print(f"   Error: {dpa_result['error']}")

class CacheAttack:
    """Simulation of cache-based side-channel attacks"""
    
    def __init__(self):
        self.sm2 = SM2()
        self.cache_lines = 64  # Simulate cache line size
        self.cache_sets = 1024  # Simulate cache sets
    
    def simulate_cache_access(self, address: int) -> bool:
        """
        Simulate cache access pattern
        Returns True if cache hit, False if cache miss
        """
        # Simulate cache behavior with some randomness
        cache_line = (address // self.cache_lines) % self.cache_sets
        
        # Simulate temporal locality - recent accesses more likely to hit
        hit_probability = 0.8 if random.random() < 0.7 else 0.2
        return random.random() < hit_probability
    
    def vulnerable_table_lookup(self, index: int, table_base: int = 0x10000) -> Tuple[int, bool]:
        """
        Simulate vulnerable table lookup with cache side effects
        Returns (value, cache_hit)
        """
        address = table_base + (index * 4)  # 4 bytes per entry
        cache_hit = self.simulate_cache_access(address)
        
        # Simulate table lookup timing
        if cache_hit:
            time.sleep(0.00001)  # Fast cache access
        else:
            time.sleep(0.00005)  # Slow memory access
        
        return index ^ 0xDEADBEEF, cache_hit  # Dummy value
    
    def secure_table_lookup(self, index: int, table_size: int = 256) -> int:
        """
        Simulate secure table lookup with cache attack countermeasures
        """
        # Access all table entries to eliminate cache-based information leakage
        dummy_sum = 0
        for i in range(table_size):
            value, _ = self.vulnerable_table_lookup(i)
            if i == index:
                result = value
            dummy_sum += value  # Prevent optimization
        
        return result
    
    def collect_cache_traces(self, indices: List[int], secure: bool = False) -> List[Tuple[int, bool, float]]:
        """
        Collect cache access patterns
        Returns list of (index, cache_hit, timing) tuples
        """
        traces = []
        
        for index in indices:
            start_time = time.perf_counter()
            
            if secure:
                self.secure_table_lookup(index)
                cache_hit = True  # Always appears as hit due to countermeasures
            else:
                _, cache_hit = self.vulnerable_table_lookup(index)
            
            end_time = time.perf_counter()
            timing = end_time - start_time
            
            traces.append((index, cache_hit, timing))
        
        return traces
    
    def analyze_cache_patterns(self, traces: List[Tuple[int, bool, float]]) -> Dict[str, Any]:
        """Analyze cache access patterns for information leakage"""
        hit_timings = [t[2] for t in traces if t[1]]
        miss_timings = [t[2] for t in traces if not t[1]]
        
        if not hit_timings or not miss_timings:
            return {'error': 'Insufficient cache hit/miss data'}
        
        hit_mean = statistics.mean(hit_timings)
        miss_mean = statistics.mean(miss_timings)
        hit_std = statistics.stdev(hit_timings) if len(hit_timings) > 1 else 0
        miss_std = statistics.stdev(miss_timings) if len(miss_timings) > 1 else 0
        
        # Calculate separability
        timing_diff = abs(miss_mean - hit_mean)
        combined_std = (hit_std + miss_std) / 2
        separability = timing_diff / combined_std if combined_std > 0 else float('inf')
        
        return {
            'hit_rate': len(hit_timings) / len(traces),
            'hit_timing_mean': hit_mean,
            'miss_timing_mean': miss_mean,
            'timing_difference': timing_diff,
            'separability': separability,
            'attack_feasibility': 'HIGH' if separability > 3 else 'MEDIUM' if separability > 1 else 'LOW'
        }
    
    def demonstrate_cache_attack(self):
        """Demonstrate cache-based side-channel attacks"""
        print("=== SM2 Cache Attack Demonstration ===\n")
        
        # Generate test indices (simulating secret-dependent table lookups)
        test_indices = [secrets.randbelow(256) for _ in range(1000)]
        
        print("Collecting cache access patterns...\n")
        
        # Test vulnerable implementation
        print("1. Vulnerable Table Lookups:")
        vulnerable_traces = self.collect_cache_traces(test_indices, secure=False)
        vulnerable_analysis = self.analyze_cache_patterns(vulnerable_traces)
        
        if 'error' not in vulnerable_analysis:
            print(f"   Cache hit rate: {vulnerable_analysis['hit_rate']:.3f}")
            print(f"   Hit timing: {vulnerable_analysis['hit_timing_mean']:.6f}s")
            print(f"   Miss timing: {vulnerable_analysis['miss_timing_mean']:.6f}s")
            print(f"   Timing difference: {vulnerable_analysis['timing_difference']:.6f}s")
            print(f"   Attack feasibility: {vulnerable_analysis['attack_feasibility']}")
        else:
            print(f"   Error: {vulnerable_analysis['error']}")
        
        print()
        
        # Test secure implementation
        print("2. Secure Table Lookups:")
        secure_traces = self.collect_cache_traces(test_indices, secure=True)
        secure_analysis = self.analyze_cache_patterns(secure_traces)
        
        if 'error' not in secure_analysis:
            print(f"   Cache hit rate: {secure_analysis['hit_rate']:.3f}")
            print(f"   Hit timing: {secure_analysis['hit_timing_mean']:.6f}s")
            print(f"   Miss timing: {secure_analysis['miss_timing_mean']:.6f}s")
            print(f"   Timing difference: {secure_analysis['timing_difference']:.6f}s")
            print(f"   Attack feasibility: {secure_analysis['attack_feasibility']}")
        else:
            print(f"   Error: {secure_analysis['error']}")

def main():
    """Main demonstration of side-channel attacks"""
    print("SM2 Side-Channel Attack Simulation Suite\n")
    print("Choose attack type:")
    print("1. Timing Attack")
    print("2. Power Analysis Attack")
    print("3. Cache Attack")
    print("4. All attacks")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        attack = TimingAttack()
        attack.demonstrate_timing_attack()
    elif choice == "2":
        attack = PowerAnalysisAttack()
        attack.demonstrate_power_analysis()
    elif choice == "3":
        attack = CacheAttack()
        attack.demonstrate_cache_attack()
    elif choice == "4":
        print("Running all side-channel attack demonstrations...\n")
        
        timing_attack = TimingAttack()
        timing_attack.demonstrate_timing_attack()
        print("\n" + "="*60 + "\n")
        
        power_attack = PowerAnalysisAttack()
        power_attack.demonstrate_power_analysis()
        print("\n" + "="*60 + "\n")
        
        cache_attack = CacheAttack()
        cache_attack.demonstrate_cache_attack()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
