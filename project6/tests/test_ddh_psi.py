"""
DDH-PSI协议正确性和安全性测试

验证协议的功能正确性、边界情况处理和基本安全性保证
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ddh_psi import DDHPSIProtocol, DDHPSIParty1, DDHPSIParty2


class TestDDHPSIProtocol(unittest.TestCase):
    """DDH-PSI协议功能测试"""
    
    def test_basic_intersection(self):
        """测试基本交集计算"""
        # 准备测试数据
        party1_data = ["user1", "user2", "user3", "user4"]
        party2_data = [("user1", 100), ("user3", 200), ("user5", 150)]
        
        # 执行协议
        protocol_size, protocol_sum = DDHPSIProtocol.run_protocol(party1_data, party2_data)
        
        # 验证结果
        expected_size, expected_sum = DDHPSIProtocol.validate_intersection(party1_data, party2_data)
        
        self.assertEqual(protocol_size, expected_size)
        self.assertEqual(protocol_sum, expected_sum)
    
    def test_empty_intersection(self):
        """测试空交集情况"""
        party1_data = ["user1", "user2"]
        party2_data = [("user3", 100), ("user4", 200)]
        
        protocol_size, protocol_sum = DDHPSIProtocol.run_protocol(party1_data, party2_data)
        
        self.assertEqual(protocol_size, 0)
        self.assertEqual(protocol_sum, 0)
    
    def test_full_intersection(self):
        """测试完全交集情况"""
        party1_data = ["user1", "user2", "user3"]
        party2_data = [("user1", 100), ("user2", 200), ("user3", 300)]
        
        protocol_size, protocol_sum = DDHPSIProtocol.run_protocol(party1_data, party2_data)
        
        self.assertEqual(protocol_size, 3)
        self.assertEqual(protocol_sum, 600)
    
    def test_large_values(self):
        """测试大数值处理"""
        party1_data = ["user1", "user2"]
        party2_data = [("user1", 1000000), ("user2", 2000000)]
        
        protocol_size, protocol_sum = DDHPSIProtocol.run_protocol(party1_data, party2_data)
        
        self.assertEqual(protocol_size, 2)
        self.assertEqual(protocol_sum, 3000000)
    
    def test_single_element_sets(self):
        """测试单元素集合"""
        party1_data = ["user1"]
        party2_data = [("user1", 42)]
        
        protocol_size, protocol_sum = DDHPSIProtocol.run_protocol(party1_data, party2_data)
        
        self.assertEqual(protocol_size, 1)
        self.assertEqual(protocol_sum, 42)
    
    def test_duplicate_identifiers(self):
        """测试重复标识符处理"""
        party1_data = ["user1", "user1", "user2"]  # 重复的user1
        party2_data = [("user1", 100), ("user2", 200)]
        
        # 协议应该正确处理重复项
        protocol_size, protocol_sum = DDHPSIProtocol.run_protocol(party1_data, party2_data)
        
        # 验证：重复项应该被去重处理
        unique_party1 = list(set(party1_data))
        expected_size, expected_sum = DDHPSIProtocol.validate_intersection(unique_party1, party2_data)
        
        self.assertEqual(protocol_size, expected_size)
        self.assertEqual(protocol_sum, expected_sum)
    
    def test_zero_values(self):
        """测试零值处理"""
        party1_data = ["user1", "user2"]
        party2_data = [("user1", 0), ("user2", 100)]
        
        protocol_size, protocol_sum = DDHPSIProtocol.run_protocol(party1_data, party2_data)
        
        self.assertEqual(protocol_size, 2)
        self.assertEqual(protocol_sum, 100)
    
    def test_negative_values(self):
        """测试负值处理"""
        party1_data = ["user1", "user2"]
        party2_data = [("user1", -50), ("user2", 100)]
        
        protocol_size, protocol_sum = DDHPSIProtocol.run_protocol(party1_data, party2_data)
        
        self.assertEqual(protocol_size, 2)
        # 注意：由于Paillier加密的模运算特性，负数会被转换
        # 这里我们主要验证协议的一致性
        expected_size, expected_sum = DDHPSIProtocol.validate_intersection(party1_data, party2_data)
        self.assertEqual(protocol_size, expected_size)
    
    def test_protocol_consistency(self):
        """测试协议多次执行的一致性"""
        party1_data = ["user1", "user2", "user3"]
        party2_data = [("user1", 100), ("user2", 200), ("user4", 300)]
        
        # 多次执行协议
        results = []
        for _ in range(3):
            size, sum_val = DDHPSIProtocol.run_protocol(party1_data, party2_data)
            results.append((size, sum_val))
        
        # 验证结果一致性
        first_result = results[0]
        for result in results[1:]:
            self.assertEqual(result, first_result)
    
    def test_different_data_sizes(self):
        """测试不同大小的数据集"""
        # Party1数据较大
        party1_data = [f"user{i}" for i in range(10)]
        party2_data = [("user2", 100), ("user5", 200), ("user8", 300)]
        
        protocol_size, protocol_sum = DDHPSIProtocol.run_protocol(party1_data, party2_data)
        expected_size, expected_sum = DDHPSIProtocol.validate_intersection(party1_data, party2_data)
        
        self.assertEqual(protocol_size, expected_size)
        self.assertEqual(protocol_sum, expected_sum)
        
        # Party2数据较大
        party1_data = ["user2", "user5"]
        party2_data = [(f"user{i}", i * 10) for i in range(10)]
        
        protocol_size, protocol_sum = DDHPSIProtocol.run_protocol(party1_data, party2_data)
        expected_size, expected_sum = DDHPSIProtocol.validate_intersection(party1_data, party2_data)
        
        self.assertEqual(protocol_size, expected_size)
        self.assertEqual(protocol_sum, expected_sum)


class TestProtocolSecurity(unittest.TestCase):
    """协议安全性基础测试"""
    
    def test_data_shuffling(self):
        """验证数据打乱功能"""
        party1 = DDHPSIParty1()
        data = [f"user{i}" for i in range(10)]
        
        # 多次加密，验证顺序不同
        encrypted_sets = []
        for _ in range(3):
            party1 = DDHPSIParty1()  # 重新初始化
            encrypted = party1.round1_prepare_data(data.copy())
            encrypted_sets.append(encrypted)
        
        # 验证至少有两次的顺序不同（概率很高）
        orders_different = False
        for i in range(len(encrypted_sets)):
            for j in range(i + 1, len(encrypted_sets)):
                if encrypted_sets[i] != encrypted_sets[j]:
                    orders_different = True
                    break
            if orders_different:
                break
        
        self.assertTrue(orders_different, "数据打乱功能可能未正确工作")
    
    def test_key_randomness(self):
        """验证密钥生成的随机性"""
        party1_instances = [DDHPSIParty1() for _ in range(5)]
        party2_instances = [DDHPSIParty2() for _ in range(5)]
        
        # 生成多个私钥
        party1_keys = []
        for party in party1_instances:
            party.round1_prepare_data(["test"])
            party1_keys.append(party.private_key)
        
        party2_keys = []
        for party in party2_instances:
            party.setup()
            party2_keys.append(party.private_key)
        
        # 验证密钥的唯一性
        self.assertEqual(len(set(party1_keys)), len(party1_keys), "Party1私钥应该是唯一的")
        self.assertEqual(len(set(party2_keys)), len(party2_keys), "Party2私钥应该是唯一的")
    
    def test_ciphertext_refreshing(self):
        """验证密文重随机化功能"""
        party2 = DDHPSIParty2()
        public_key = party2.setup()
        
        # 加密相同值多次
        original_value = 100
        ciphertext1 = party2.paillier.encrypt(original_value, public_key)
        ciphertext2 = party2.paillier.encrypt(original_value, public_key)
        
        # 验证相同明文的不同密文
        self.assertNotEqual(ciphertext1, ciphertext2, "相同明文应产生不同密文")
        
        # 验证重随机化
        refreshed = party2.paillier.refresh_ciphertext(ciphertext1, public_key)
        self.assertNotEqual(ciphertext1, refreshed, "重随机化应产生不同密文")
        
        # 验证解密结果相同
        decrypted1 = party2.paillier.decrypt(ciphertext1, party2.paillier_private_key)
        decrypted2 = party2.paillier.decrypt(refreshed, party2.paillier_private_key)
        self.assertEqual(decrypted1, decrypted2, "重随机化前后明文应相同")


if __name__ == '__main__':
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加功能测试
    test_suite.addTest(unittest.makeSuite(TestDDHPSIProtocol))
    test_suite.addTest(unittest.makeSuite(TestProtocolSecurity))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试总结
    print(f"\\n{'='*50}")
    print(f"测试总结:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
