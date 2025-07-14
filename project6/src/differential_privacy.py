#!/usr/bin/env python3
"""
差分隐私机制实现
"""

import random
import math
from typing import List, Union

class DifferentialPrivacy:
    """差分隐私机制实现"""
    
    def __init__(self, epsilon: float = 1.0):
        self.epsilon = epsilon
    
    def laplace_mechanism(self, true_value: float, sensitivity: float = 1.0) -> float:
        """Laplace机制"""
        scale = sensitivity / self.epsilon
        noise = random.laplace(0, scale)
        return true_value + noise
    
    def exponential_mechanism(self, options: List, utility_function, sensitivity: float = 1.0):
        """指数机制"""
        scores = [utility_function(option) for option in options]
        max_score = max(scores)
        
        # 计算概率权重
        weights = []
        for score in scores:
            weight = math.exp(self.epsilon * score / (2 * sensitivity))
            weights.append(weight)
        
        # 随机选择
        total_weight = sum(weights)
        r = random.random() * total_weight
        
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return options[i]
        
        return options[-1]
    
    def randomized_response(self, true_answer: bool, p: float = None) -> bool:
        """随机化响应机制"""
        if p is None:
            p = math.exp(self.epsilon) / (math.exp(self.epsilon) + 1)
        
        if random.random() < p:
            return true_answer
        else:
            return not true_answer

def demo_differential_privacy():
    """差分隐私演示"""
    print("🎭 差分隐私机制演示")
    print("=" * 30)
    
    dp = DifferentialPrivacy(epsilon=1.0)
    
    # Laplace机制演示
    true_count = 42
    noisy_count = dp.laplace_mechanism(true_count)
    print(f"Laplace机制: {true_count} -> {noisy_count:.2f}")
    
    # 随机化响应演示
    true_answer = True
    noisy_answer = dp.randomized_response(true_answer)
    print(f"随机化响应: {true_answer} -> {noisy_answer}")
    
    print("✅ 差分隐私演示完成")
    return True

if __name__ == "__main__":
    demo_differential_privacy()
