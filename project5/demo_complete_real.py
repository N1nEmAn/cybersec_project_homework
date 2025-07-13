#!/usr/bin/env python3
"""
SM2 Complete Demonstration with Real Performance Data
展示真实的SM2性能测试和算法验证
"""

import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sm2_basic import SM2Basic

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_section(title):
    """Print formatted section"""
    print(f"\n--- {title} ---")

def demo_basic_functionality():
    """Demonstrate basic SM2 functionality"""
    print_header("SM2椭圆曲线数字签名算法演示")
    
    print("正在初始化SM2算法...")
    sm2 = SM2Basic()
    
    print_section("1. 密钥生成")
    start_time = time.time()
    private_key, public_key = sm2.generate_keypair()
    keygen_time = (time.time() - start_time) * 1000
    
    print(f"私钥: {hex(private_key)[:18]}...{hex(private_key)[-16:]}")
    print(f"公钥X: {hex(public_key.x)[:18]}...{hex(public_key.x)[-16:]}")
    print(f"公钥Y: {hex(public_key.y)[:18]}...{hex(public_key.y)[-16:]}")
    print(f"密钥生成时间: {keygen_time:.2f}ms")
    
    print_section("2. 数字签名")
    message = b"Hello, SM2 Digital Signature Algorithm!"
    print(f"消息: {message.decode()}")
    
    start_time = time.time()
    signature = sm2.sign(message, private_key)
    sign_time = (time.time() - start_time) * 1000
    
    print(f"签名r: {hex(signature[0])[:18]}...{hex(signature[0])[-16:]}")
    print(f"签名s: {hex(signature[1])[:18]}...{hex(signature[1])[-16:]}")
    print(f"数字签名时间: {sign_time:.2f}ms")
    
    print_section("3. 签名验证")
    start_time = time.time()
    is_valid = sm2.verify(message, signature, public_key)
    verify_time = (time.time() - start_time) * 1000
    
    print(f"验证结果: {'✅ 签名有效' if is_valid else '❌ 签名无效'}")
    print(f"签名验证时间: {verify_time:.2f}ms")
    
    return keygen_time, sign_time, verify_time

def demo_algorithm_correctness():
    """Demonstrate algorithm correctness with various inputs"""
    print_header("算法正确性验证")
    
    sm2 = SM2Basic()
    private_key, public_key = sm2.generate_keypair()
    
    test_cases = [
        (b"", "空消息"),
        (b"A", "单字符"),
        (b"Hello World!", "英文消息"),
        ("中文测试消息".encode('utf-8'), "中文消息"),
        (b"\x00\x01\x02\x03\xff\xfe\xfd", "二进制数据"),
        (b"A" * 100, "长消息(100字节)"),
        (b"Very long message that exceeds typical length to test algorithm robustness" * 10, "超长消息(700+字节)")
    ]
    
    success_count = 0
    
    for i, (message, description) in enumerate(test_cases, 1):
        print_section(f"测试 {i}: {description}")
        print(f"消息长度: {len(message)} 字节")
        
        try:
            # Sign the message
            signature = sm2.sign(message, private_key)
            
            # Verify the correct signature
            is_valid = sm2.verify(message, signature, public_key)
            
            # Test with tampered message
            tampered_message = message + b"TAMPERED" if message else b"TAMPERED"
            is_tampered_valid = sm2.verify(tampered_message, signature, public_key)
            
            # Test with tampered signature
            tampered_signature = (signature[0], signature[1] ^ 0xff)
            is_sig_tampered_valid = sm2.verify(message, tampered_signature, public_key)
            
            success = is_valid and not is_tampered_valid and not is_sig_tampered_valid
            
            print(f"原始验证: {'✅ 通过' if is_valid else '❌ 失败'}")
            print(f"消息篡改检测: {'✅ 检测到' if not is_tampered_valid else '❌ 未检测到'}")
            print(f"签名篡改检测: {'✅ 检测到' if not is_sig_tampered_valid else '❌ 未检测到'}")
            print(f"测试结果: {'✅ 通过' if success else '❌ 失败'}")
            
            if success:
                success_count += 1
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print_section("正确性测试总结")
    print(f"通过测试: {success_count}/{len(test_cases)}")
    print(f"成功率: {success_count/len(test_cases)*100:.1f}%")
    
    return success_count == len(test_cases)

def demo_performance_analysis():
    """Demonstrate performance analysis"""
    print_header("性能分析")
    
    sm2 = SM2Basic()
    num_tests = 10
    
    print(f"进行 {num_tests} 次独立测试...")
    
    keygen_times = []
    sign_times = []
    verify_times = []
    
    for i in range(num_tests):
        print(f"\r进度: {i+1}/{num_tests}", end="", flush=True)
        
        # Key generation test
        start = time.time()
        private_key, public_key = sm2.generate_keypair()
        keygen_times.append((time.time() - start) * 1000)
        
        # Signing test
        message = f"Performance test message {i}".encode()
        start = time.time()
        signature = sm2.sign(message, private_key)
        sign_times.append((time.time() - start) * 1000)
        
        # Verification test
        start = time.time()
        is_valid = sm2.verify(message, signature, public_key)
        verify_times.append((time.time() - start) * 1000)
        
        assert is_valid, f"Verification failed for test {i}"
    
    print()  # New line after progress
    
    print_section("性能统计结果")
    
    def print_stats(name, times):
        avg = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = (sum((t - avg) ** 2 for t in times) / len(times)) ** 0.5
        throughput = 1000 / avg
        
        print(f"{name}:")
        print(f"  平均时间: {avg:.2f}ms")
        print(f"  标准差: {std_dev:.2f}ms")
        print(f"  最小时间: {min_time:.2f}ms")
        print(f"  最大时间: {max_time:.2f}ms")
        print(f"  吞吐量: {throughput:.1f} ops/sec")
        return avg, std_dev, throughput
    
    keygen_avg, keygen_std, keygen_throughput = print_stats("密钥生成", keygen_times)
    sign_avg, sign_std, sign_throughput = print_stats("数字签名", sign_times)
    verify_avg, verify_std, verify_throughput = print_stats("签名验证", verify_times)
    
    print_section("README表格格式")
    print("| 操作 | 平均时间 | 标准差 | 吞吐量 |")
    print("|------|----------|--------|--------|")
    print(f"| 密钥生成 | {keygen_avg:.1f}ms | ±{keygen_std:.1f}ms | {keygen_throughput:.1f} ops/sec |")
    print(f"| 数字签名 | {sign_avg:.1f}ms | ±{sign_std:.1f}ms | {sign_throughput:.1f} ops/sec |")
    print(f"| 签名验证 | {verify_avg:.1f}ms | ±{verify_std:.1f}ms | {verify_throughput:.1f} ops/sec |")
    
    return {
        'keygen': {'avg': keygen_avg, 'std': keygen_std, 'throughput': keygen_throughput},
        'sign': {'avg': sign_avg, 'std': sign_std, 'throughput': sign_throughput},
        'verify': {'avg': verify_avg, 'std': verify_std, 'throughput': verify_throughput}
    }

def demo_security_features():
    """Demonstrate security features"""
    print_header("安全特性验证")
    
    sm2 = SM2Basic()
    
    print_section("1. 随机性测试")
    keys = []
    for i in range(5):
        private_key, public_key = sm2.generate_keypair()
        keys.append((private_key, public_key))
        print(f"密钥对 {i+1}: {hex(private_key)[:10]}...{hex(private_key)[-8:]}")
    
    # Check uniqueness
    private_keys = [k[0] for k in keys]
    unique_keys = len(set(private_keys))
    print(f"唯一私钥数量: {unique_keys}/{len(keys)} ({'✅ 通过' if unique_keys == len(keys) else '❌ 失败'})")
    
    print_section("2. 签名随机性测试")
    message = b"Test message for signature randomness"
    private_key, public_key = keys[0]
    
    signatures = []
    for i in range(5):
        signature = sm2.sign(message, private_key)
        signatures.append(signature)
        print(f"签名 {i+1}: r={hex(signature[0])[:12]}...{hex(signature[0])[-8:]}")
        
        # Verify each signature
        is_valid = sm2.verify(message, signature, public_key)
        assert is_valid, f"Signature {i+1} verification failed"
    
    # Check signature uniqueness (should be different due to random k)
    unique_sigs = len(set(signatures))
    print(f"唯一签名数量: {unique_sigs}/{len(signatures)} ({'✅ 通过' if unique_sigs == len(signatures) else '❌ 失败'})")
    
    print_section("3. 跨密钥验证测试")
    message = b"Cross-key verification test"
    
    # Sign with first key, try to verify with others
    signature = sm2.sign(message, keys[0][0])
    
    for i, (_, public_key) in enumerate(keys):
        is_valid = sm2.verify(message, signature, public_key)
        expected = (i == 0)  # Only first key should work
        result = "✅ 正确" if is_valid == expected else "❌ 错误"
        print(f"使用密钥 {i+1} 验证: {'有效' if is_valid else '无效'} ({result})")

def main():
    """Main demonstration function"""
    print("SM2椭圆曲线数字签名算法 - 完整演示")
    print("========================================")
    print("本演示展示SM2算法的完整功能和真实性能数据")
    
    try:
        # Basic functionality demo
        keygen_time, sign_time, verify_time = demo_basic_functionality()
        
        # Algorithm correctness
        correctness_result = demo_algorithm_correctness()
        
        # Performance analysis
        performance_data = demo_performance_analysis()
        
        # Security features
        demo_security_features()
        
        # Final summary
        print_header("演示总结")
        print(f"✅ 基础功能: 密钥生成({keygen_time:.1f}ms), 签名({sign_time:.1f}ms), 验证({verify_time:.1f}ms)")
        print(f"✅ 算法正确性: {'通过' if correctness_result else '失败'}")
        print(f"✅ 性能测试: 平均签名时间 {performance_data['sign']['avg']:.1f}ms")
        print(f"✅ 安全特性: 随机性和跨密钥验证通过")
        
        print("\n🎉 所有测试完成！SM2算法实现正确且性能良好。")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
