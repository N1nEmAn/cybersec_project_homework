"""
DDH-PSI协议核心实现

实现基于DDH假设的私有交集和协议：
- Party1和Party2的协议逻辑
- 三轮通信协议
- 交集识别和聚合计算
- 安全性保证
"""

import random
from typing import List, Tuple, Dict, Union, Optional
from .elliptic_curve import EllipticCurveGroup
from .paillier_encryption import PaillierEncryption
from .crypto_utils import hash_to_curve


class DDHPSIParty1:
    """
    DDH-PSI协议的参与方1
    
    Party1持有标识符集合V，参与协议计算交集大小和交集中关联值的总和。
    在协议中，Party1负责：
    1. 对自己的数据进行第一次加密
    2. 接收Party2的数据并进行第二次加密
    3. 识别交集并计算聚合结果
    """
    
    def __init__(self):
        """初始化Party1"""
        self.ec_group = EllipticCurveGroup()
        self.private_key = None
        self.encrypted_own_data = []  # 自己数据的加密结果
        self.received_z_set = []      # 从Party2接收的Z集合
        self.received_w_data = []     # 从Party2接收的W数据
        
    def round1_prepare_data(self, data_set: List[str]) -> List[Tuple[int, int]]:
        """
        第一轮：准备自己的数据
        
        对数据集V中的每个元素v_i计算H(v_i)^k1，并打乱顺序
        
        Args:
            data_set: 标识符集合V = {v_i}
            
        Returns:
            加密后的数据点列表（已打乱顺序）
        """
        # 生成私钥k1
        self.private_key = self.ec_group.generate_private_key()
        
        # 对每个数据点进行加密：H(v_i)^k1
        encrypted_points = []
        for item in data_set:
            # 将字符串哈希到椭圆曲线点
            point = hash_to_curve(item)
            # 计算H(v_i)^k1
            encrypted_point = self.ec_group.point_power(point, self.private_key)
            encrypted_points.append(encrypted_point)
        
        # 打乱顺序以保护隐私
        random.shuffle(encrypted_points)
        
        # 保存用于后续使用
        self.encrypted_own_data = encrypted_points.copy()
        
        return encrypted_points
    
    def round2_receive_data(self, z_set: List[Tuple[int, int]], 
                           w_data: List[Tuple[Tuple[int, int], int]]):
        """
        第二轮：接收Party2的数据
        
        Args:
            z_set: Party2发送的Z集合，包含H(v_i)^(k1*k2)
            w_data: Party2发送的W数据，包含(H(w_j)^k2, Enc(t_j))
        """
        self.received_z_set = z_set
        self.received_w_data = w_data
    
    def round3_compute_intersection(self, paillier_public_key: dict) -> Tuple[int, int]:
        """
        第三轮：计算交集并生成聚合结果
        
        Args:
            paillier_public_key: Paillier公钥
            
        Returns:
            (交集大小, 重随机化后的聚合密文)
        """
        paillier = PaillierEncryption()
        
        # 对接收到的W数据进行第二次加密：H(w_j)^(k1*k2)
        double_encrypted_w = []
        encrypted_values = []
        
        for w_point, encrypted_value in self.received_w_data:
            # 计算H(w_j)^(k1*k2)
            double_encrypted = self.ec_group.point_power(w_point, self.private_key)
            double_encrypted_w.append(double_encrypted)
            encrypted_values.append(encrypted_value)
        
        # 识别交集：找到在Z集合中的点
        intersection_indices = []
        for i, double_encrypted in enumerate(double_encrypted_w):
            if double_encrypted in self.received_z_set:
                intersection_indices.append(i)
        
        # 计算交集大小
        intersection_size = len(intersection_indices)
        
        # 同态计算交集中关联值的总和
        if intersection_indices:
            intersection_ciphertexts = [encrypted_values[i] for i in intersection_indices]
            aggregated_ciphertext = paillier.sum_ciphertexts(intersection_ciphertexts, paillier_public_key)
        else:
            # 如果没有交集，加密0
            aggregated_ciphertext = paillier.encrypt(0, paillier_public_key)
        
        # 重随机化密文以提供额外安全性
        refreshed_ciphertext = paillier.refresh_ciphertext(aggregated_ciphertext, paillier_public_key)
        
        return intersection_size, refreshed_ciphertext


class DDHPSIParty2:
    """
    DDH-PSI协议的参与方2
    
    Party2持有标识符与关联值的集合W，参与协议并最终获得结果。
    在协议中，Party2负责：
    1. 生成同态加密密钥对
    2. 对接收到的数据进行加密并发送自己的数据
    3. 解密最终结果
    """
    
    def __init__(self):
        """初始化Party2"""
        self.ec_group = EllipticCurveGroup()
        self.paillier = PaillierEncryption()
        self.private_key = None
        self.paillier_public_key = None
        self.paillier_private_key = None
        
    def setup(self) -> dict:
        """
        协议设置阶段：生成密钥
        
        Returns:
            Paillier公钥
        """
        # 生成椭圆曲线私钥k2
        self.private_key = self.ec_group.generate_private_key()
        
        # 生成Paillier密钥对
        self.paillier_public_key, self.paillier_private_key = self.paillier.generate_keypair()
        
        return self.paillier_public_key
    
    def round2_process_and_respond(self, received_x_data: List[Tuple[int, int]], 
                                  own_data: List[Tuple[str, int]]) -> Tuple[List[Tuple[int, int]], 
                                                                          List[Tuple[Tuple[int, int], int]]]:
        """
        第二轮：处理接收到的数据并发送自己的数据
        
        Args:
            received_x_data: 从Party1接收的X数据，包含H(v_i)^k1
            own_data: 自己的数据集合W = {(w_j, t_j)}
            
        Returns:
            (Z集合, W数据) - 发送给Party1的数据
        """
        # 处理接收到的X数据：计算Z = {H(v_i)^(k1*k2)}
        z_set = []
        for x_point in received_x_data:
            # 计算H(v_i)^(k1*k2)
            z_point = self.ec_group.point_power(x_point, self.private_key)
            z_set.append(z_point)
        
        # 打乱Z集合的顺序
        random.shuffle(z_set)
        
        # 处理自己的数据：计算{(H(w_j)^k2, Enc(t_j))}
        w_data = []
        for identifier, value in own_data:
            # 将标识符哈希到椭圆曲线点
            w_point = hash_to_curve(identifier)
            # 计算H(w_j)^k2
            encrypted_w = self.ec_group.point_power(w_point, self.private_key)
            # 加密关联值t_j
            encrypted_value = self.paillier.encrypt(value, self.paillier_public_key)
            
            w_data.append((encrypted_w, encrypted_value))
        
        # 打乱W数据的顺序
        random.shuffle(w_data)
        
        return z_set, w_data
    
    def round3_decrypt_result(self, aggregated_ciphertext: int) -> int:
        """
        第三轮：解密最终结果
        
        Args:
            aggregated_ciphertext: 来自Party1的聚合密文
            
        Returns:
            交集中关联值的总和
        """
        intersection_sum = self.paillier.decrypt(aggregated_ciphertext, self.paillier_private_key)
        return intersection_sum


class DDHPSIProtocol:
    """
    完整的DDH-PSI协议执行器
    
    提供简化的接口来执行完整的协议流程
    """
    
    @staticmethod
    def run_protocol(party1_data: List[str], 
                    party2_data: List[Tuple[str, int]], 
                    verbose: bool = False) -> Tuple[int, int]:
        """
        执行完整的DDH-PSI协议
        
        Args:
            party1_data: Party1的数据集合V
            party2_data: Party2的数据集合W
            verbose: 是否输出详细信息
            
        Returns:
            (交集大小, 交集中关联值的总和)
        """
        if verbose:
            print("=== DDH-PSI协议执行开始 ===")
            print(f"Party1数据大小: {len(party1_data)}")
            print(f"Party2数据大小: {len(party2_data)}")
        
        # 初始化参与方
        party1 = DDHPSIParty1()
        party2 = DDHPSIParty2()
        
        # 设置阶段
        if verbose:
            print("\\n1. 设置阶段：生成密钥...")
        paillier_public_key = party2.setup()
        
        # 第一轮：Party1准备数据
        if verbose:
            print("2. 第一轮：Party1加密数据...")
        x_data = party1.round1_prepare_data(party1_data)
        
        # 第二轮：Party2处理数据并响应
        if verbose:
            print("3. 第二轮：Party2处理并响应...")
        z_set, w_data = party2.round2_process_and_respond(x_data, party2_data)
        
        # Party1接收Party2的数据
        party1.round2_receive_data(z_set, w_data)
        
        # 第三轮：Party1计算交集并聚合
        if verbose:
            print("4. 第三轮：计算交集和聚合...")
        intersection_size, aggregated_ciphertext = party1.round3_compute_intersection(paillier_public_key)
        
        # Party2解密结果
        intersection_sum = party2.round3_decrypt_result(aggregated_ciphertext)
        
        if verbose:
            print(f"\\n=== 协议执行完成 ===")
            print(f"交集大小: {intersection_size}")
            print(f"交集总和: {intersection_sum}")
        
        return intersection_size, intersection_sum
    
    @staticmethod
    def validate_intersection(party1_data: List[str], 
                            party2_data: List[Tuple[str, int]]) -> Tuple[int, int]:
        """
        直接计算交集用于验证协议正确性（仅用于测试）
        
        Args:
            party1_data: Party1的数据
            party2_data: Party2的数据
            
        Returns:
            (真实交集大小, 真实交集总和)
        """
        party1_set = set(party1_data)
        party2_dict = dict(party2_data)
        
        intersection = party1_set.intersection(set(party2_dict.keys()))
        intersection_size = len(intersection)
        intersection_sum = sum(party2_dict[item] for item in intersection)
        
        return intersection_size, intersection_sum
