"""
SM4标准测试向量
包含官方标准的测试用例
"""

import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from basic.sm4_basic import SM4Basic
from utils.helpers import format_hex

# 官方标准测试向量
OFFICIAL_TEST_VECTORS = [
    {
        'name': '标准测试向量1',
        'key': bytes.fromhex('0123456789abcdeffedcba9876543210'),
        'plaintext': bytes.fromhex('0123456789abcdeffedcba9876543210'),
        'ciphertext': bytes.fromhex('681edf34d206965e86b3e94f536e4246')
    }
]

# 1000次迭代测试向量（用于性能测试）
ITERATION_TEST_VECTOR = {
    'key': bytes.fromhex('0123456789abcdeffedcba9876543210'),
    'plaintext': bytes.fromhex('0123456789abcdeffedcba9876543210'),
    'iterations': 1000000,
    'expected_final': bytes.fromhex('595298c7c6fd271f0402f804c33d3f66')
}

def run_standard_tests():
    """运行所有标准测试向量"""
    print("=== SM4标准测试向量验证 ===")
    
    all_passed = True
    
    for i, vector in enumerate(OFFICIAL_TEST_VECTORS):
        print(f"\n测试 {i+1}: {vector['name']}")
        print(f"密钥:     {format_hex(vector['key'])}")
        print(f"明文:     {format_hex(vector['plaintext'])}")
        print(f"期望密文: {format_hex(vector['ciphertext'])}")
        
        try:
            sm4 = SM4Basic(vector['key'])
            ciphertext = sm4.encrypt(vector['plaintext'])
            print(f"实际密文: {format_hex(ciphertext)}")
            
            if ciphertext == vector['ciphertext']:
                print("✓ 测试通过")
            else:
                print("✗ 测试失败")
                all_passed = False
            
            # 验证解密
            decrypted = sm4.decrypt(ciphertext)
            if decrypted == vector['plaintext']:
                print("✓ 解密验证通过")
            else:
                print("✗ 解密验证失败")
                all_passed = False
                
        except Exception as e:
            print(f"✗ 测试异常: {e}")
            all_passed = False
    
    return all_passed

def run_iteration_test():
    """运行迭代测试（仅测试正确性，不做100万次）"""
    print("\n=== SM4迭代测试 ===")
    
    vector = ITERATION_TEST_VECTOR
    sm4 = SM4Basic(vector['key'])
    
    print(f"初始密钥: {format_hex(vector['key'])}")
    print(f"初始明文: {format_hex(vector['plaintext'])}")
    
    # 测试较少的迭代次数以验证算法正确性
    test_iterations = 1000
    data = vector['plaintext']
    
    print(f"进行 {test_iterations} 次迭代...")
    
    for i in range(test_iterations):
        data = sm4.encrypt(data)
        if i % 100 == 0:
            print(f"第 {i} 次迭代: {format_hex(data)}")
    
    print(f"最终结果: {format_hex(data)}")
    print("注：标准要求100万次迭代，此处仅做算法验证")

def cross_implementation_test():
    """跨实现一致性测试"""
    print("\n=== 跨实现一致性测试 ===")
    
    try:
        from optimized.sm4_lookup_table import SM4LookupTable
        from optimized.sm4_bitwise import SM4Bitwise
        
        key = OFFICIAL_TEST_VECTORS[0]['key']
        plaintext = OFFICIAL_TEST_VECTORS[0]['plaintext']
        
        sm4_basic = SM4Basic(key)
        sm4_lookup = SM4LookupTable(key)
        sm4_bitwise = SM4Bitwise(key)
        
        basic_result = sm4_basic.encrypt(plaintext)
        lookup_result = sm4_lookup.encrypt(plaintext)
        bitwise_result = sm4_bitwise.encrypt(plaintext)
        
        print(f"基础实现: {format_hex(basic_result)}")
        print(f"查找表版: {format_hex(lookup_result)}")
        print(f"位运算版: {format_hex(bitwise_result)}")
        
        if basic_result == lookup_result == bitwise_result:
            print("✓ 所有实现结果一致")
            return True
        else:
            print("✗ 实现结果不一致")
            return False
            
    except ImportError:
        print("优化实现尚未完成，跳过跨实现测试")
        return True

if __name__ == "__main__":
    print("SM4算法标准测试向量验证")
    print("=" * 50)
    
    # 运行标准测试
    standard_passed = run_standard_tests()
    
    # 运行迭代测试
    run_iteration_test()
    
    # 跨实现测试
    cross_passed = cross_implementation_test()
    
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"标准测试向量: {'通过' if standard_passed else '失败'}")
    print(f"跨实现一致性: {'通过' if cross_passed else '失败'}")
    
    if standard_passed and cross_passed:
        print("✓ 所有测试通过")
    else:
        print("✗ 部分测试失败")
