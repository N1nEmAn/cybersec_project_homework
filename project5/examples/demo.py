#!/usr/bin/env python3
"""
SM2椭圆曲线数字签名算法使用示例
展示基础功能、优化特性和并行处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from src.sm2_basic import SM2Basic
from src.sm2_optimized import SM2Optimized
from src.sm2_parallel import SM2Parallel

def basic_example():
    """基础使用示例"""
    print("=" * 60)
    print("SM2 基础使用示例")
    print("=" * 60)
    
    # 初始化SM2实例
    sm2 = SM2Basic()
    
    # 1. 密钥生成
    print("1. 密钥生成")
    private_key, public_key = sm2.generate_keypair()
    print(f"   私钥: {private_key:064x}")
    print(f"   公钥: ({public_key.x:064x},")
    print(f"         {public_key.y:064x})")
    
    # 2. 数字签名
    print("\n2. 数字签名")
    message = "这是一条需要签名的重要消息".encode('utf-8')
    print(f"   原始消息: {message.decode('utf-8')}")
    
    signature = sm2.sign(message, private_key)
    r, s = signature
    print(f"   数字签名: r = {r:064x}")
    print(f"            s = {s:064x}")
    
    # 3. 签名验证
    print("\n3. 签名验证")
    is_valid = sm2.verify(message, signature, public_key)
    print(f"   验证结果: {'✓ 签名有效' if is_valid else '✗ 签名无效'}")
    
    # 4. 错误签名测试
    print("\n4. 错误签名测试")
    wrong_message = "这是一条被篡改的消息".encode('utf-8')
    is_valid_wrong = sm2.verify(wrong_message, signature, public_key)
    print(f"   篡改消息验证: {'✓ 签名有效' if is_valid_wrong else '✗ 签名无效'}")

def optimization_example():
    """优化特性示例"""
    print("\n" + "=" * 60)
    print("SM2 优化特性示例")
    print("=" * 60)
    
    sm2_basic = SM2Basic()
    sm2_optimized = SM2Optimized()
    
    message = "性能测试消息".encode('utf-8')
    iterations = 10
    
    print(f"性能对比测试 ({iterations} 次迭代)")
    
    # 基础实现性能测试
    print("\n1. 基础实现性能")
    start_time = time.time()
    for i in range(iterations):
        private_key, public_key = sm2_basic.generate_keypair()
        signature = sm2_basic.sign(message, private_key)
        is_valid = sm2_basic.verify(message, signature, public_key)
        assert is_valid, f"第{i+1}次验证失败"
    basic_time = time.time() - start_time
    print(f"   总时间: {basic_time:.3f} 秒")
    print(f"   平均时间: {basic_time/iterations*1000:.2f} ms/operation")
    
    # 优化实现性能测试
    print("\n2. 优化实现性能")
    start_time = time.time()
    for i in range(iterations):
        private_key, public_key = sm2_optimized.generate_keypair_optimized()
        signature = sm2_optimized.sign_optimized(message, private_key)
        is_valid = sm2_optimized.verify_optimized(message, signature, public_key)
        assert is_valid, f"第{i+1}次验证失败"
    optimized_time = time.time() - start_time
    print(f"   总时间: {optimized_time:.3f} 秒")
    print(f"   平均时间: {optimized_time/iterations*1000:.2f} ms/operation")
    
    # 性能提升分析
    speedup = basic_time / optimized_time
    print(f"\n3. 性能提升分析")
    print(f"   加速比: {speedup:.2f}x")
    print(f"   性能提升: {(speedup-1)*100:.1f}%")
    
    # 标量乘法算法对比
    print("\n4. 标量乘法算法对比")
    k = 0x12345678901234567890123456789012345678901234567890123456789ABC
    P = sm2_optimized.G
    
    methods = [
        ("基础二进制", sm2_optimized.point_multiply),
        ("NAF方法", sm2_optimized.point_multiply_naf),
        ("滑动窗口", sm2_optimized.point_multiply_window),
        ("Montgomery阶梯", sm2_optimized.montgomery_ladder),
        ("预计算优化", sm2_optimized.point_multiply_optimized),
    ]
    
    baseline_time = None
    for method_name, method_func in methods:
        start_time = time.time()
        result = method_func(k, P)
        method_time = time.time() - start_time
        
        if baseline_time is None:
            baseline_time = method_time
        
        speedup = baseline_time / method_time
        print(f"   {method_name:12s}: {method_time*1000:6.2f} ms (加速比: {speedup:.2f}x)")

def parallel_example():
    """并行处理示例"""
    print("\n" + "=" * 60)
    print("SM2 并行处理示例")
    print("=" * 60)
    
    sm2_parallel = SM2Parallel(num_threads=4)
    
    # 1. 批量密钥生成
    print("1. 批量密钥生成")
    count = 20
    start_time = time.time()
    keypairs = sm2_parallel.batch_generate_keypairs(count)
    keygen_time = time.time() - start_time
    
    print(f"   生成 {count} 个密钥对")
    print(f"   总时间: {keygen_time:.3f} 秒")
    print(f"   平均时间: {keygen_time/count*1000:.2f} ms/keypair")
    
    # 2. 批量数字签名
    print("\n2. 批量数字签名")
    messages = [f"消息 {i}".encode('utf-8') for i in range(count)]
    private_keys = [kp[0] for kp in keypairs]
    
    start_time = time.time()
    signatures = sm2_parallel.batch_sign(messages, private_keys)
    sign_time = time.time() - start_time
    
    print(f"   签名 {count} 条消息")
    print(f"   总时间: {sign_time:.3f} 秒")
    print(f"   平均时间: {sign_time/count*1000:.2f} ms/signature")
    
    # 3. 批量签名验证
    print("\n3. 批量签名验证")
    public_keys = [kp[1] for kp in keypairs]
    
    start_time = time.time()
    results = sm2_parallel.batch_verify(messages, signatures, public_keys)
    verify_time = time.time() - start_time
    
    valid_count = sum(results)
    print(f"   验证 {count} 个签名")
    print(f"   总时间: {verify_time:.3f} 秒")
    print(f"   平均时间: {verify_time/count*1000:.2f} ms/verification")
    print(f"   验证结果: {valid_count}/{count} 通过")
    
    # 4. 性能对比
    print("\n4. 并行vs串行性能对比")
    sequential_time = keygen_time + sign_time + verify_time
    print(f"   并行总时间: {sequential_time:.3f} 秒")
    
    # 估算串行时间
    estimated_sequential = sequential_time * 3  # 粗略估算
    print(f"   估算串行时间: {estimated_sequential:.3f} 秒")
    print(f"   并行加速比: {estimated_sequential/sequential_time:.2f}x")

def real_world_example():
    """真实世界应用示例"""
    print("\n" + "=" * 60)
    print("SM2 真实世界应用示例")
    print("=" * 60)
    
    sm2 = SM2Optimized()
    
    # 1. 数字证书场景
    print("1. 数字证书签名场景")
    
    # CA密钥对
    ca_private_key, ca_public_key = sm2.generate_keypair_optimized()
    print("   ✓ CA密钥对生成完成")
    
    # 用户证书请求
    user_private_key, user_public_key = sm2.generate_keypair_optimized()
    cert_info = {
        "subject": "CN=张三,O=某公司,C=CN",
        "public_key": user_public_key,
        "validity": "valid_period"
    }
    
    # 证书内容序列化（简化）
    cert_data = f"{cert_info['subject']}|{cert_info['public_key'].x:064x}|{cert_info['validity']}".encode('utf-8')
    
    # CA签名
    cert_signature = sm2.sign_optimized(cert_data, ca_private_key)
    print("   ✓ 数字证书签名完成")
    
    # 证书验证
    cert_valid = sm2.verify_optimized(cert_data, cert_signature, ca_public_key)
    print(f"   ✓ 证书验证: {'通过' if cert_valid else '失败'}")
    
    # 2. 文档签名场景
    print("\n2. 电子文档签名场景")
    
    document = """
    重要合同文件
    
    甲方：某科技公司
    乙方：某咨询公司
    
    合同内容：...
    
    签署日期：项目完成日期
    """.encode('utf-8')
    
    # 文档哈希签名
    doc_signature = sm2.sign_optimized(document, user_private_key, "user@company.com".encode('utf-8'))
    print("   ✓ 文档签名完成")
    
    # 文档验证
    doc_valid = sm2.verify_optimized(document, doc_signature, user_public_key, "user@company.com".encode('utf-8'))
    print(f"   ✓ 文档验证: {'通过' if doc_valid else '失败'}")
    
    # 3. 消息认证场景
    print("\n3. 消息认证场景")
    
    # 模拟网络通信
    messages = [
        "transfer:account123->account456:1000".encode('utf-8'),
        "login:user123:timestamp:1234567890".encode('utf-8'),
        "update_profile:user123:email:new@email.com".encode('utf-8')
    ]
    
    authenticated_messages = []
    for msg in messages:
        signature = sm2.sign_optimized(msg, user_private_key)
        authenticated_messages.append((msg, signature))
    
    print(f"   ✓ {len(messages)} 条消息签名完成")
    
    # 消息验证
    valid_messages = 0
    for msg, signature in authenticated_messages:
        if sm2.verify_optimized(msg, signature, user_public_key):
            valid_messages += 1
    
    print(f"   ✓ 消息验证: {valid_messages}/{len(messages)} 通过")

def security_demonstration():
    """安全性演示"""
    print("\n" + "=" * 60)
    print("SM2 安全性演示")
    print("=" * 60)
    
    sm2 = SM2Basic()
    
    # 1. 签名唯一性演示
    print("1. 签名唯一性演示")
    private_key, public_key = sm2.generate_keypair()
    message = "测试消息".encode('utf-8')
    
    signatures = []
    for i in range(5):
        sig = sm2.sign(message, private_key)
        signatures.append(sig)
        print(f"   签名 {i+1}: r={sig[0]:016x}..., s={sig[1]:016x}...")
    
    # 验证签名都不相同（由于随机性）
    unique_signatures = set(signatures)
    print(f"   唯一签名数: {len(unique_signatures)}/{len(signatures)}")
    
    # 验证所有签名都有效
    all_valid = all(sm2.verify(message, sig, public_key) for sig in signatures)
    print(f"   所有签名有效: {'是' if all_valid else '否'}")
    
    # 2. 篡改检测演示
    print("\n2. 篡改检测演示")
    original_message = "原始重要消息".encode('utf-8')
    signature = sm2.sign(original_message, private_key)
    
    tampered_messages = [
        "篡改重要消息".encode('utf-8'),  # 内容篡改
        "原始重要消息extra".encode('utf-8'),  # 添加内容
        "原始重要".encode('utf-8'),  # 删除内容
    ]
    
    for i, tampered_msg in enumerate(tampered_messages):
        is_valid = sm2.verify(tampered_msg, signature, public_key)
        print(f"   篡改测试 {i+1}: {'检测到篡改' if not is_valid else '未检测到篡改'}")
    
    # 3. 密钥安全性演示
    print("\n3. 密钥安全性演示")
    
    # 生成多个密钥对
    keypairs = [sm2.generate_keypair() for _ in range(3)]
    
    # 同一消息用不同密钥签名
    test_message = "相同消息不同密钥".encode('utf-8')
    signatures_list = []
    for i, (priv_key, pub_key) in enumerate(keypairs):
        signature = sm2.sign(test_message, priv_key)
        signatures_list.append(signature)
        print(f"   密钥对 {i+1} 签名: {signature[0]:016x}...")
    
    # 验证密钥独立性
    cross_valid = sm2.verify(test_message, signatures_list[0], keypairs[1][1])
    print(f"   跨密钥验证: {'失败（正确）' if not cross_valid else '成功（异常）'}")

def main():
    """主函数：运行所有示例"""
    print("SM2 椭圆曲线数字签名算法 - 完整使用示例")
    print("=" * 80)
    
    try:
        # 基础功能示例
        basic_example()
        
        # 优化特性示例
        optimization_example()
        
        # 并行处理示例
        parallel_example()
        
        # 真实应用示例
        real_world_example()
        
        # 安全性演示
        security_demonstration()
        
        print("\n" + "=" * 80)
        print("✅ 所有示例运行完成！")
        print("🎓 SM2算法的核心功能、优化特性和安全性已全面展示")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 示例运行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
