#!/usr/bin/env python3
"""
水印系统性能基准测试
测试不同算法在各种图像尺寸下的性能表现
"""

import time
import numpy as np
import cv2
from pathlib import Path
import json
import argparse
from src.algorithms import AlgorithmRegistry

class PerformanceBenchmark:
    def __init__(self):
        self.algorithm_registry = AlgorithmRegistry()
        self.results = {}
    
    def generate_test_data(self, size):
        """生成测试用的图像和水印"""
        # 生成随机测试图像
        host_image = np.random.randint(0, 256, (size, size, 3), dtype=np.uint8)
        
        # 生成简单的水印
        watermark_size = min(size // 4, 64)
        watermark = np.random.randint(0, 2, (watermark_size, watermark_size), dtype=np.uint8) * 255
        
        return host_image, watermark
    
    def benchmark_algorithm(self, algorithm_name, image_sizes, iterations=5):
        """对特定算法进行性能基准测试"""
        print(f"\n测试算法: {algorithm_name}")
        algorithm = self.algorithm_registry.get_algorithm(algorithm_name)
        
        results = {}
        for size in image_sizes:
            print(f"  测试图像尺寸: {size}x{size}")
            
            # 生成测试数据
            host_image, watermark = self.generate_test_data(size)
            
            # 嵌入性能测试
            embed_times = []
            for i in range(iterations):
                start_time = time.time()
                watermarked = algorithm.embed(host_image, watermark, strength=0.1)
                end_time = time.time()
                embed_times.append(end_time - start_time)
            
            # 提取性能测试
            extract_times = []
            for i in range(iterations):
                start_time = time.time()
                extracted = algorithm.extract(watermarked, watermark_size=(watermark.shape[0], watermark.shape[1]))
                end_time = time.time()
                extract_times.append(end_time - start_time)
            
            # 计算统计数据
            avg_embed_time = np.mean(embed_times)
            avg_extract_time = np.mean(extract_times)
            
            results[size] = {
                'embed_time': avg_embed_time,
                'extract_time': avg_extract_time,
                'total_time': avg_embed_time + avg_extract_time,
                'pixels_per_second': (size * size) / (avg_embed_time + avg_extract_time),
                'embed_times': embed_times,
                'extract_times': extract_times
            }
            
            print(f"    嵌入: {avg_embed_time:.4f}s, 提取: {avg_extract_time:.4f}s")
        
        return results
    
    def run_benchmark(self, algorithms=None, image_sizes=None):
        """运行完整的性能基准测试"""
        if algorithms is None:
            algorithms = ['lsb', 'dct']
        if image_sizes is None:
            image_sizes = [128, 256, 512]
        
        print("开始性能基准测试...")
        
        for algorithm in algorithms:
            try:
                self.results[algorithm] = self.benchmark_algorithm(algorithm, image_sizes)
            except Exception as e:
                print(f"算法 {algorithm} 测试失败: {e}")
        
        return self.results
    
    def save_results(self, output_file='benchmark_results.json'):
        """保存测试结果到文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到: {output_file}")
    
    def print_summary(self):
        """打印测试结果摘要"""
        print("\n=== 性能基准测试摘要 ===")
        for algorithm, sizes in self.results.items():
            print(f"\n{algorithm.upper()} 算法:")
            for size, metrics in sizes.items():
                speed = metrics['pixels_per_second'] / 1000  # K pixels/sec
                print(f"  {size}x{size}: {metrics['total_time']:.4f}s, {speed:.1f}K像素/秒")

def main():
    parser = argparse.ArgumentParser(description='水印系统性能基准测试')
    parser.add_argument('--algorithms', nargs='+', default=['lsb', 'dct'],
                       help='要测试的算法列表')
    parser.add_argument('--sizes', nargs='+', type=int, default=[128, 256, 512],
                       help='要测试的图像尺寸列表')
    parser.add_argument('--iterations', type=int, default=5,
                       help='每个测试的重复次数')
    parser.add_argument('--output', type=str, default='benchmark_results.json',
                       help='结果输出文件')
    
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark()
    results = benchmark.run_benchmark(args.algorithms, args.sizes)
    benchmark.print_summary()
    benchmark.save_results(args.output)

if __name__ == '__main__':
    main()
