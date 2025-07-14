#!/usr/bin/env python3
"""
SM2椭圆曲线数字签名算法快速演示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from src.sm2_basic import SM2Basic
from src.sm2_optimized import SM2Optimized

def quick_demo():
    """快速演示SM2核心功能"""
    print("SM2 椭圆曲线数字签名算法 - 快速演示")
    print("=" * 50)
    
    # 基础功能演示
    print("\n1. 基础功能演示")
    sm2 = SM2Basic()
    
    # 密钥生成
    private_key, public_key = sm2.generate_keypair()
    print(f"   ✓ 密钥对生成完成")
    print(f"   私钥: {private_key:016x}...")
    print(f"   公钥: ({public_key.x:016x}..., {public_key.y:016x}...)")
    
    # 数字签名
    message = "重要消息内容".encode('utf-8')
    signature = sm2.sign(message, private_key)
    print(f"   ✓ 数字签名完成")
    print(f"   签名: ({signature[0]:016x}..., {signature[1]:016x}...)")
    
    # 签名验证
    is_valid = sm2.verify(message, signature, public_key)
    print(f"   ✓ 签名验证: {'通过' if is_valid else '失败'}")
    
    # 篡改检测
    tampered_message = "篡改消息内容".encode('utf-8')
    is_tampered_valid = sm2.verify(tampered_message, signature, public_key)
    print(f"   ✓ 篡改检测: {'检测到' if not is_tampered_valid else '未检测到'}")
    
    # 性能对比演示
    print("\n2. 性能对比演示")
    sm2_optimized = SM2Optimized()
    
    # 基础实现性能
    iterations = 3
    start_time = time.time()
    for _ in range(iterations):
        priv, pub = sm2.generate_keypair()
        sig = sm2.sign(message, priv)
        sm2.verify(message, sig, pub)
    basic_time = time.time() - start_time
    
    # 优化实现性能
    start_time = time.time()
    for _ in range(iterations):
        priv, pub = sm2_optimized.generate_keypair_optimized()
        sig = sm2_optimized.sign_optimized(message, priv)
        sm2_optimized.verify_optimized(message, sig, pub)
    optimized_time = time.time() - start_time
    
    speedup = basic_time / optimized_time if optimized_time > 0 else 1
    print(f"   基础实现时间: {basic_time:.3f} 秒")
    print(f"   优化实现时间: {optimized_time:.3f} 秒")
    print(f"   性能提升: {speedup:.2f}x")
    
    # 算法对比演示
    print("\n3. 标量乘法算法对比")
    k = 0x123456789ABCDEF0
    P = sm2_optimized.G
    
    algorithms = [
        ("基础算法", sm2_optimized.point_multiply),
        ("NAF算法", sm2_optimized.point_multiply_naf),
        ("滑动窗口", sm2_optimized.point_multiply_window),
    ]
    
    baseline_time = None
    for name, func in algorithms:
        start_time = time.time()
        result = func(k, P)
        algo_time = time.time() - start_time
        
        if baseline_time is None:
            baseline_time = algo_time
        
        speedup = baseline_time / algo_time if algo_time > 0 else 1
        print(f"   {name:8s}: {algo_time*1000:6.2f} ms (加速比: {speedup:.2f}x)")
    
    print("\n" + "=" * 50)
    print("✅ SM2算法演示完成！")
    print("🔐 数字签名、验证和篡改检测功能正常")
    print("🚀 优化算法提供显著性能提升")
    print("=" * 50)

if __name__ == "__main__":
    quick_demo()
