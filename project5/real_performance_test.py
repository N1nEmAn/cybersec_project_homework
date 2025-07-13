#!/usr/bin/env python3
"""
Real Performance Testing Script
Generate actual performance data for README documentation
"""

import sys
import os
import time
import statistics

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sm2_basic import SM2Basic

def test_basic_performance():
    """Test basic SM2 implementation performance"""
    print("=== 实际性能测试 ===")
    
    sm2 = SM2Basic()
    num_tests = 10  # 减少测试次数以加快速度
    
    # Test key generation
    print("测试密钥生成...")
    keygen_times = []
    for i in range(num_tests):
        start = time.time()
        private_key, public_key = sm2.generate_keypair()
        end = time.time()
        keygen_times.append((end - start) * 1000)  # Convert to ms
        print(f"  密钥生成 {i+1}: {keygen_times[-1]:.2f}ms")
    
    avg_keygen = statistics.mean(keygen_times)
    std_keygen = statistics.stdev(keygen_times) if len(keygen_times) > 1 else 0
    
    # Test signing
    print("\n测试数字签名...")
    message = b"Performance test message for SM2 digital signature"
    sign_times = []
    signatures = []
    
    for i in range(num_tests):
        start = time.time()
        signature = sm2.sign(message, private_key)
        end = time.time()
        sign_times.append((end - start) * 1000)
        signatures.append(signature)
        print(f"  签名 {i+1}: {sign_times[-1]:.2f}ms")
    
    avg_sign = statistics.mean(sign_times)
    std_sign = statistics.stdev(sign_times) if len(sign_times) > 1 else 0
    
    # Test verification
    print("\n测试签名验证...")
    verify_times = []
    
    for i, signature in enumerate(signatures):
        start = time.time()
        is_valid = sm2.verify(message, signature, public_key)
        end = time.time()
        verify_times.append((end - start) * 1000)
        print(f"  验证 {i+1}: {verify_times[-1]:.2f}ms, 结果: {'有效' if is_valid else '无效'}")
    
    avg_verify = statistics.mean(verify_times)
    std_verify = statistics.stdev(verify_times) if len(verify_times) > 1 else 0
    
    # Print summary
    print("\n=== 性能测试总结 ===")
    print(f"密钥生成: {avg_keygen:.2f}ms ± {std_keygen:.2f}ms ({1000/avg_keygen:.1f} ops/sec)")
    print(f"数字签名: {avg_sign:.2f}ms ± {std_sign:.2f}ms ({1000/avg_sign:.1f} ops/sec)")
    print(f"签名验证: {avg_verify:.2f}ms ± {std_verify:.2f}ms ({1000/avg_verify:.1f} ops/sec)")
    
    return {
        'keygen': {'avg': avg_keygen, 'std': std_keygen, 'ops_sec': 1000/avg_keygen},
        'sign': {'avg': avg_sign, 'std': std_sign, 'ops_sec': 1000/avg_sign},
        'verify': {'avg': avg_verify, 'std': std_verify, 'ops_sec': 1000/avg_verify}
    }

def test_algorithm_correctness():
    """Test algorithm correctness with different message types"""
    print("\n=== 算法正确性测试 ===")
    
    sm2 = SM2Basic()
    private_key, public_key = sm2.generate_keypair()
    
    test_messages = [
        b"Hello, SM2!",
        b"",  # Empty message
        b"A" * 100,  # Long message
        b"\x00\x01\x02\x03\xff\xfe\xfd",  # Binary data
        "中文测试消息".encode('utf-8'),  # Chinese characters
    ]
    
    success_count = 0
    total_tests = len(test_messages)
    
    for i, message in enumerate(test_messages):
        try:
            # Sign
            signature = sm2.sign(message, private_key)
            
            # Verify correct signature
            is_valid = sm2.verify(message, signature, public_key)
            
            # Test with tampered message
            tampered_message = message + b"X" if message else b"X"
            is_tampered_valid = sm2.verify(tampered_message, signature, public_key)
            
            success = is_valid and not is_tampered_valid
            success_count += success
            
            print(f"测试 {i+1}: {'通过' if success else '失败'}")
            print(f"  消息: {message[:50]}{'...' if len(message) > 50 else ''}")
            print(f"  正常验证: {'通过' if is_valid else '失败'}")
            print(f"  篡改验证: {'失败(正确)' if not is_tampered_valid else '通过(错误)'}")
            
        except Exception as e:
            print(f"测试 {i+1}: 错误 - {e}")
    
    print(f"\n正确性测试结果: {success_count}/{total_tests} 通过")
    return success_count == total_tests

def main():
    """Main test function"""
    print("SM2椭圆曲线数字签名算法 - 实际性能测试")
    print("=" * 50)
    
    # Performance test
    perf_results = test_basic_performance()
    
    # Correctness test
    correctness_result = test_algorithm_correctness()
    
    # Generate markdown table for README
    print("\n=== README表格数据 ===")
    print("| 操作 | 平均时间 | 标准差 | 吞吐量 |")
    print("|------|----------|--------|--------|")
    print(f"| 密钥生成 | {perf_results['keygen']['avg']:.1f}ms | ±{perf_results['keygen']['std']:.1f}ms | {perf_results['keygen']['ops_sec']:.1f} ops/sec |")
    print(f"| 数字签名 | {perf_results['sign']['avg']:.1f}ms | ±{perf_results['sign']['std']:.1f}ms | {perf_results['sign']['ops_sec']:.1f} ops/sec |")
    print(f"| 签名验证 | {perf_results['verify']['avg']:.1f}ms | ±{perf_results['verify']['std']:.1f}ms | {perf_results['verify']['ops_sec']:.1f} ops/sec |")
    
    print(f"\n算法正确性: {'✅ 通过' if correctness_result else '❌ 失败'}")
    
    return perf_results, correctness_result

if __name__ == "__main__":
    main()
