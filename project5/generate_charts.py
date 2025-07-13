"""
SM2 Performance Visualization and Chart Generation
Generate comprehensive performance charts and analysis visualizations
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from typing import Dict, List, Any
import os
import sys

# Set style for professional charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Add benchmarks directory to path
sys.path.append(os.path.dirname(__file__))

class SM2ChartGenerator:
    """Generate professional charts for SM2 performance analysis"""
    
    def __init__(self, output_dir: str = "charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Professional color scheme
        self.colors = {
            'Basic': '#FF6B6B',      # Red
            'Optimized': '#4ECDC4',   # Teal  
            'SIMD': '#45B7D1',        # Blue
            'Background': '#F8F9FA',
            'Grid': '#E9ECEF',
            'Text': '#495057'
        }
        
        # Configure matplotlib for better output
        plt.rcParams.update({
            'figure.figsize': (12, 8),
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 14,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'legend.fontsize': 12,
            'figure.titlesize': 18
        })
    
    def generate_all_charts(self, benchmark_results: Dict[str, Any]):
        """Generate all performance charts"""
        print("Generating performance charts...")
        
        # Performance comparison charts
        self.create_operations_comparison_chart(benchmark_results)
        self.create_speedup_analysis_chart(benchmark_results)
        self.create_throughput_comparison_chart(benchmark_results)
        
        # Detailed analysis charts
        self.create_operation_breakdown_chart(benchmark_results)
        self.create_batch_performance_chart(benchmark_results)
        self.create_efficiency_radar_chart(benchmark_results)
        
        # Mathematical analysis charts
        self.create_complexity_analysis_chart()
        self.create_optimization_impact_chart(benchmark_results)
        
        print(f"Charts saved to {self.output_dir}/")
    
    def create_operations_comparison_chart(self, results: Dict[str, Any]):
        """Create comprehensive operations comparison chart"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('SM2 Algorithm Performance Comparison', fontsize=20, fontweight='bold')
        
        operations = ['key_generation', 'signing', 'verification']
        operation_names = ['Key Generation', 'Signing', 'Verification']
        
        for idx, (op, op_name) in enumerate(zip(operations, operation_names)):
            row = idx // 2
            col = idx % 2
            ax = axes[row, col]
            
            implementations = list(results[op].keys())
            times_ms = [results[op][impl]['avg_time'] * 1000 for impl in implementations]
            colors = [self.colors[impl] for impl in implementations]
            
            bars = ax.bar(implementations, times_ms, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
            
            # Add value labels on bars
            for bar, time_ms in zip(bars, times_ms):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{time_ms:.2f}ms', ha='center', va='bottom', fontweight='bold')
            
            ax.set_title(f'{op_name} Performance', fontsize=14, fontweight='bold')
            ax.set_ylabel('Time (milliseconds)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor(self.colors['Background'])
        
        # Remove empty subplot
        axes[1, 1].remove()
        
        # Add overall comparison in the fourth subplot
        ax = fig.add_subplot(2, 2, 4)
        self._create_overall_comparison_subplot(ax, results)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/operations_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_overall_comparison_subplot(self, ax, results):
        """Create overall performance comparison subplot"""
        operations = ['key_generation', 'signing', 'verification']
        implementations = ['Basic', 'Optimized', 'SIMD']
        
        x = np.arange(len(operations))
        width = 0.25
        
        for i, impl in enumerate(implementations):
            times = [results[op][impl]['avg_time'] * 1000 for op in operations]
            bars = ax.bar(x + i*width, times, width, label=impl, 
                         color=self.colors[impl], alpha=0.8)
            
            # Add value labels
            for bar, time in zip(bars, times):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{time:.1f}', ha='center', va='bottom', fontsize=10)
        
        ax.set_title('Overall Performance Comparison', fontweight='bold')
        ax.set_ylabel('Time (milliseconds)')
        ax.set_xticks(x + width)
        ax.set_xticklabels(['Key Gen', 'Sign', 'Verify'])
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_facecolor(self.colors['Background'])
    
    def create_speedup_analysis_chart(self, results: Dict[str, Any]):
        """Create speedup analysis chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('SM2 Optimization Speedup Analysis', fontsize=18, fontweight='bold')
        
        operations = ['key_generation', 'signing', 'verification']
        operation_names = ['Key Generation', 'Signing', 'Verification']
        
        # Calculate speedups relative to basic implementation
        basic_times = [results[op]['Basic']['avg_time'] for op in operations]
        opt_speedups = [basic_times[i] / results[operations[i]]['Optimized']['avg_time'] 
                       for i in range(len(operations))]
        simd_speedups = [basic_times[i] / results[operations[i]]['SIMD']['avg_time'] 
                        for i in range(len(operations))]
        
        # Speedup bar chart
        x = np.arange(len(operations))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, opt_speedups, width, label='Optimized vs Basic',
                       color=self.colors['Optimized'], alpha=0.8)
        bars2 = ax1.bar(x + width/2, simd_speedups, width, label='SIMD vs Basic',
                       color=self.colors['SIMD'], alpha=0.8)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                        f'{height:.2f}x', ha='center', va='bottom', fontweight='bold')
        
        ax1.set_title('Speedup Comparison', fontweight='bold')
        ax1.set_ylabel('Speedup Factor')
        ax1.set_xticks(x)
        ax1.set_xticklabels(operation_names)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Baseline')
        
        # Throughput comparison (operations per second)
        throughputs = {
            'Basic': [results[op]['Basic']['ops_per_sec'] for op in operations],
            'Optimized': [results[op]['Optimized']['ops_per_sec'] for op in operations],
            'SIMD': [results[op]['SIMD']['ops_per_sec'] for op in operations]
        }
        
        x_pos = np.arange(len(operations))
        for i, (impl, values) in enumerate(throughputs.items()):
            ax2.bar(x_pos + i*0.25, values, 0.25, label=impl, 
                   color=self.colors[impl], alpha=0.8)
        
        ax2.set_title('Throughput Comparison', fontweight='bold')
        ax2.set_ylabel('Operations per Second')
        ax2.set_xticks(x_pos + 0.25)
        ax2.set_xticklabels(operation_names)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')  # Log scale for better visualization
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/speedup_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_throughput_comparison_chart(self, results: Dict[str, Any]):
        """Create detailed throughput comparison chart"""
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Prepare data for heatmap
        operations = ['Key Generation', 'Signing', 'Verification']
        implementations = ['Basic', 'Optimized', 'SIMD']
        
        # Create throughput matrix
        throughput_matrix = []
        for impl in implementations:
            row = []
            for op in ['key_generation', 'signing', 'verification']:
                ops_per_sec = results[op][impl]['ops_per_sec']
                row.append(ops_per_sec)
            throughput_matrix.append(row)
        
        # Create heatmap
        im = ax.imshow(throughput_matrix, cmap='YlOrRd', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(operations)))
        ax.set_yticks(np.arange(len(implementations)))
        ax.set_xticklabels(operations)
        ax.set_yticklabels(implementations)
        
        # Add text annotations
        for i in range(len(implementations)):
            for j in range(len(operations)):
                text = ax.text(j, i, f'{throughput_matrix[i][j]:.2f}',
                             ha="center", va="center", color="black", fontweight='bold')
        
        ax.set_title('SM2 Implementation Throughput Heatmap (ops/sec)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Operations per Second', rotation=270, labelpad=20)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/throughput_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_operation_breakdown_chart(self, results: Dict[str, Any]):
        """Create operation time breakdown chart"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Operation Time Distribution Analysis', fontsize=16, fontweight='bold')
        
        operations = ['key_generation', 'signing', 'verification']
        operation_names = ['Key Generation', 'Signing', 'Verification']
        
        for idx, (op, op_name) in enumerate(zip(operations, operation_names)):
            ax = axes[idx]
            
            implementations = list(results[op].keys())
            avg_times = [results[op][impl]['avg_time'] * 1000 for impl in implementations]
            std_devs = [results[op][impl]['std_dev'] * 1000 for impl in implementations]
            min_times = [results[op][impl]['min_time'] * 1000 for impl in implementations]
            max_times = [results[op][impl]['max_time'] * 1000 for impl in implementations]
            
            x_pos = np.arange(len(implementations))
            
            # Create error bars showing min/max range
            bars = ax.bar(x_pos, avg_times, yerr=std_devs, 
                         color=[self.colors[impl] for impl in implementations],
                         alpha=0.8, capsize=5, error_kw={'linewidth': 2})
            
            # Add min/max indicators
            for i, (impl, avg, min_t, max_t) in enumerate(zip(implementations, avg_times, min_times, max_times)):
                ax.plot([i, i], [min_t, max_t], 'k-', alpha=0.5, linewidth=1)
                ax.plot(i, min_t, 'kv', markersize=4)
                ax.plot(i, max_t, 'k^', markersize=4)
                
                # Add average time label
                ax.text(i, avg + std_devs[i] + (max_t-min_t)*0.05, 
                       f'{avg:.2f}ms', ha='center', va='bottom', fontweight='bold')
            
            ax.set_title(f'{op_name}', fontweight='bold')
            ax.set_ylabel('Time (milliseconds)')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(implementations)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor(self.colors['Background'])
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/operation_breakdown.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_batch_performance_chart(self, results: Dict[str, Any]):
        """Create batch performance analysis chart"""
        if 'batch_operations' not in results or not results['batch_operations']:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('Batch Operations Performance Analysis', fontsize=16, fontweight='bold')
        
        batch_data = results['batch_operations']['SIMD_batch']
        batch_sizes = list(batch_data.keys())
        speedups = [batch_data[size]['speedup'] for size in batch_sizes]
        batch_throughput = [batch_data[size]['batch_ops_per_sec'] for size in batch_sizes]
        individual_throughput = [batch_data[size]['individual_ops_per_sec'] for size in batch_sizes]
        
        # Speedup vs batch size
        ax1.plot(batch_sizes, speedups, 'o-', color=self.colors['SIMD'], 
                linewidth=3, markersize=8, label='Batch Speedup')
        ax1.fill_between(batch_sizes, speedups, alpha=0.3, color=self.colors['SIMD'])
        
        for size, speedup in zip(batch_sizes, speedups):
            ax1.annotate(f'{speedup:.2f}x', (size, speedup), 
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        ax1.set_title('Batch Operation Speedup', fontweight='bold')
        ax1.set_xlabel('Batch Size')
        ax1.set_ylabel('Speedup Factor')
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor(self.colors['Background'])
        
        # Throughput comparison
        x_pos = np.arange(len(batch_sizes))
        width = 0.35
        
        bars1 = ax2.bar(x_pos - width/2, individual_throughput, width,
                       label='Individual Operations', color=self.colors['Basic'], alpha=0.8)
        bars2 = ax2.bar(x_pos + width/2, batch_throughput, width,
                       label='Batch Operations', color=self.colors['SIMD'], alpha=0.8)
        
        ax2.set_title('Throughput Comparison', fontweight='bold')
        ax2.set_xlabel('Batch Size')
        ax2.set_ylabel('Operations per Second')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(batch_sizes)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor(self.colors['Background'])
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/batch_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_efficiency_radar_chart(self, results: Dict[str, Any]):
        """Create radar chart showing efficiency across different metrics"""
        fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))
        
        # Metrics for radar chart (normalized to 0-1 scale)
        metrics = ['Key Gen Speed', 'Sign Speed', 'Verify Speed', 
                  'Memory Efficiency', 'Code Complexity', 'Security Level']
        
        # Calculate normalized scores (higher is better)
        basic_keygen = results['key_generation']['Basic']['ops_per_sec']
        basic_sign = results['signing']['Basic']['ops_per_sec'] 
        basic_verify = results['verification']['Basic']['ops_per_sec']
        
        implementations_data = {
            'Basic': [
                1.0,  # Key gen (baseline)
                1.0,  # Sign (baseline)
                1.0,  # Verify (baseline)
                1.0,  # Memory efficiency (baseline)
                1.0,  # Code complexity (simplest)
                1.0   # Security level (same for all)
            ],
            'Optimized': [
                results['key_generation']['Optimized']['ops_per_sec'] / basic_keygen,
                results['signing']['Optimized']['ops_per_sec'] / basic_sign,
                results['verification']['Optimized']['ops_per_sec'] / basic_verify,
                0.8,  # Memory efficiency (slightly worse due to precomputation)
                0.7,  # Code complexity (more complex)
                1.0   # Security level (same)
            ],
            'SIMD': [
                results['key_generation']['SIMD']['ops_per_sec'] / basic_keygen,
                results['signing']['SIMD']['ops_per_sec'] / basic_sign,
                results['verification']['SIMD']['ops_per_sec'] / basic_verify,
                0.6,  # Memory efficiency (more tables)
                0.5,  # Code complexity (most complex)
                1.0   # Security level (same)
            ]
        }
        
        # Number of variables
        N = len(metrics)
        
        # Angle for each metric
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Complete the circle
        
        # Plot each implementation
        for impl_name, values in implementations_data.items():
            values += values[:1]  # Complete the circle
            ax.plot(angles, values, 'o-', linewidth=2, 
                   label=impl_name, color=self.colors[impl_name])
            ax.fill(angles, values, alpha=0.25, color=self.colors[impl_name])
        
        # Add metric labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 3)  # Allow for up to 3x improvement
        
        # Add grid and labels
        ax.grid(True)
        ax.set_title('SM2 Implementation Efficiency Comparison', 
                    fontsize=16, fontweight='bold', pad=30)
        
        # Add legend
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/efficiency_radar.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_complexity_analysis_chart(self):
        """Create theoretical complexity analysis chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('SM2 Algorithm Complexity Analysis', fontsize=16, fontweight='bold')
        
        # Key sizes for analysis
        key_sizes = np.array([160, 192, 224, 256, 384, 521])
        
        # Theoretical complexity (simplified)
        basic_complexity = key_sizes ** 3  # O(n³) for basic implementation
        optimized_complexity = key_sizes ** 2.5  # Better due to optimizations
        simd_complexity = key_sizes ** 2.2  # Best with SIMD
        
        ax1.loglog(key_sizes, basic_complexity, 'o-', label='Basic O(n³)', 
                  color=self.colors['Basic'], linewidth=2, markersize=8)
        ax1.loglog(key_sizes, optimized_complexity, 's-', label='Optimized O(n^2.5)', 
                  color=self.colors['Optimized'], linewidth=2, markersize=8)
        ax1.loglog(key_sizes, simd_complexity, '^-', label='SIMD O(n^2.2)', 
                  color=self.colors['SIMD'], linewidth=2, markersize=8)
        
        ax1.set_title('Theoretical Time Complexity', fontweight='bold')
        ax1.set_xlabel('Key Size (bits)')
        ax1.set_ylabel('Relative Operations')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Memory complexity
        basic_memory = key_sizes / 8  # Basic storage
        optimized_memory = key_sizes / 8 * 2  # Some precomputation
        simd_memory = key_sizes / 8 * 4  # More precomputation tables
        
        ax2.semilogy(key_sizes, basic_memory, 'o-', label='Basic', 
                    color=self.colors['Basic'], linewidth=2, markersize=8)
        ax2.semilogy(key_sizes, optimized_memory, 's-', label='Optimized', 
                    color=self.colors['Optimized'], linewidth=2, markersize=8)
        ax2.semilogy(key_sizes, simd_memory, '^-', label='SIMD', 
                    color=self.colors['SIMD'], linewidth=2, markersize=8)
        
        ax2.set_title('Memory Usage Comparison', fontweight='bold')
        ax2.set_xlabel('Key Size (bits)')
        ax2.set_ylabel('Memory Usage (bytes)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/complexity_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_optimization_impact_chart(self, results: Dict[str, Any]):
        """Create optimization impact analysis chart"""
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Optimization techniques and their impact
        optimizations = [
            'Affine Coordinates',
            'Jacobian Coordinates', 
            'Precomputed Tables',
            'Montgomery Ladder',
            'Windowing Method',
            'Batch Operations',
            'SIMD Instructions'
        ]
        
        # Estimated performance impact (relative improvement)
        impact_factors = [1.0, 1.8, 2.2, 1.5, 2.8, 3.5, 4.2]
        complexity_increase = [1.0, 1.2, 1.5, 1.3, 2.0, 2.5, 3.0]
        
        # Create scatter plot
        scatter = ax.scatter(complexity_increase, impact_factors, 
                           s=[200 + i*50 for i in range(len(optimizations))],
                           c=range(len(optimizations)), cmap='viridis',
                           alpha=0.7, edgecolors='black', linewidth=2)
        
        # Add labels for each point
        for i, opt in enumerate(optimizations):
            ax.annotate(opt, (complexity_increase[i], impact_factors[i]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=11, fontweight='bold')
        
        # Add trend line
        z = np.polyfit(complexity_increase, impact_factors, 1)
        p = np.poly1d(z)
        ax.plot(complexity_increase, p(complexity_increase), "--", 
               alpha=0.8, color='red', linewidth=2)
        
        ax.set_title('Optimization Techniques: Performance vs Complexity Trade-off', 
                    fontsize=16, fontweight='bold')
        ax.set_xlabel('Implementation Complexity Factor')
        ax.set_ylabel('Performance Improvement Factor')
        ax.grid(True, alpha=0.3)
        ax.set_facecolor(self.colors['Background'])
        
        # Add quadrant labels
        ax.axhline(y=2, color='gray', linestyle=':', alpha=0.5)
        ax.axvline(x=2, color='gray', linestyle=':', alpha=0.5)
        ax.text(1.1, 3.8, 'High Performance\nLow Complexity', ha='center', 
               bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.5))
        ax.text(2.8, 3.8, 'High Performance\nHigh Complexity', ha='center',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/optimization_impact.png', dpi=300, bbox_inches='tight')
        plt.close()


def main():
    """Generate sample charts with mock data"""
    # Mock benchmark results for demonstration
    mock_results = {
        'key_generation': {
            'Basic': {'avg_time': 0.045, 'std_dev': 0.003, 'min_time': 0.041, 'max_time': 0.052, 'ops_per_sec': 22.2},
            'Optimized': {'avg_time': 0.025, 'std_dev': 0.002, 'min_time': 0.022, 'max_time': 0.029, 'ops_per_sec': 40.0},
            'SIMD': {'avg_time': 0.018, 'std_dev': 0.001, 'min_time': 0.016, 'max_time': 0.021, 'ops_per_sec': 55.6}
        },
        'signing': {
            'Basic': {'avg_time': 0.038, 'std_dev': 0.004, 'min_time': 0.033, 'max_time': 0.045, 'ops_per_sec': 26.3},
            'Optimized': {'avg_time': 0.021, 'std_dev': 0.002, 'min_time': 0.018, 'max_time': 0.025, 'ops_per_sec': 47.6},
            'SIMD': {'avg_time': 0.015, 'std_dev': 0.001, 'min_time': 0.013, 'max_time': 0.018, 'ops_per_sec': 66.7}
        },
        'verification': {
            'Basic': {'avg_time': 0.042, 'std_dev': 0.003, 'min_time': 0.038, 'max_time': 0.048, 'ops_per_sec': 23.8},
            'Optimized': {'avg_time': 0.023, 'std_dev': 0.002, 'min_time': 0.020, 'max_time': 0.027, 'ops_per_sec': 43.5},
            'SIMD': {'avg_time': 0.016, 'std_dev': 0.001, 'min_time': 0.014, 'max_time': 0.019, 'ops_per_sec': 62.5}
        },
        'batch_operations': {
            'SIMD_batch': {
                10: {'batch_time': 0.12, 'individual_time': 0.16, 'speedup': 1.33, 'batch_ops_per_sec': 83.3, 'individual_ops_per_sec': 62.5},
                25: {'batch_time': 0.28, 'individual_time': 0.40, 'speedup': 1.43, 'batch_ops_per_sec': 89.3, 'individual_ops_per_sec': 62.5},
                50: {'batch_time': 0.52, 'individual_time': 0.80, 'speedup': 1.54, 'batch_ops_per_sec': 96.2, 'individual_ops_per_sec': 62.5}
            }
        }
    }
    
    # Generate charts
    chart_generator = SM2ChartGenerator()
    chart_generator.generate_all_charts(mock_results)
    print("Sample charts generated successfully!")


if __name__ == "__main__":
    main()
