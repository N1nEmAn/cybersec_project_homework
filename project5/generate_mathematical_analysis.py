#!/usr/bin/env python3
"""
Mathematical Analysis Generator
Generate mathematical formulas and analysis for README
"""

import matplotlib.pyplot as plt
import numpy as np
import json

def generate_mathematical_analysis():
    """Generate mathematical analysis for SM2 algorithm"""
    
    analysis = {
        "elliptic_curve": {
            "equation": "y² ≡ x³ + ax + b (mod p)",
            "sm2_curve": "y² ≡ x³ - 3x + b (mod p)",
            "parameters": {
                "p": "FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF",
                "a": "FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC",
                "b": "28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93",
                "n": "FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B61C6AF347D568AEDCE6AF48A03",
                "Gx": "32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7",
                "Gy": "BC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0"
            }
        },
        "complexity": {
            "key_generation": "O(k²) where k is bit length",
            "signing": "O(k²) for point multiplication",
            "verification": "O(k²) for two point multiplications"
        },
        "security": {
            "ecdlp": "Elliptic Curve Discrete Logarithm Problem",
            "security_level": "256-bit equivalent to 3072-bit RSA",
            "attacks": ["Pollard's rho", "Baby-step giant-step", "Pohlig-Hellman"]
        }
    }
    
    return analysis

def create_algorithm_flowchart():
    """Create algorithm flowchart visualization"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('SM2 算法流程与数学分析', fontsize=16, fontweight='bold')
    
    # 1. Key Generation Flow
    ax1.text(0.5, 0.9, '密钥生成算法', ha='center', va='center', 
             fontsize=14, fontweight='bold', transform=ax1.transAxes)
    
    steps = [
        '1. 选择随机数 d ∈ [1, n-1]',
        '2. 计算 P = [d]G',
        '3. 输出 (d, P)',
        '   私钥: d',
        '   公钥: P = (x, y)'
    ]
    
    for i, step in enumerate(steps):
        ax1.text(0.1, 0.8 - i*0.15, step, ha='left', va='center',
                fontsize=10, transform=ax1.transAxes)
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    
    # 2. Signing Algorithm
    ax2.text(0.5, 0.9, '数字签名算法', ha='center', va='center',
             fontsize=14, fontweight='bold', transform=ax2.transAxes)
    
    sign_steps = [
        '1. e = H(M) 哈希消息',
        '2. 选择随机数 k ∈ [1, n-1]',
        '3. (x₁, y₁) = [k]G',
        '4. r = (e + x₁) mod n',
        '5. s = (1 + d)⁻¹(k - rd) mod n',
        '6. 输出签名 (r, s)'
    ]
    
    for i, step in enumerate(sign_steps):
        ax2.text(0.1, 0.8 - i*0.12, step, ha='left', va='center',
                fontsize=10, transform=ax2.transAxes)
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    
    # 3. Verification Algorithm
    ax3.text(0.5, 0.9, '签名验证算法', ha='center', va='center',
             fontsize=14, fontweight='bold', transform=ax3.transAxes)
    
    verify_steps = [
        '1. 检查 r, s ∈ [1, n-1]',
        '2. e = H(M) 计算消息哈希',
        '3. t = (r + s) mod n',
        '4. (x₁, y₁) = [s]G + [t]P',
        '5. R = (e + x₁) mod n',
        '6. 验证 R ≟ r'
    ]
    
    for i, step in enumerate(verify_steps):
        ax3.text(0.1, 0.8 - i*0.12, step, ha='left', va='center',
                fontsize=10, transform=ax3.transAxes)
    
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.axis('off')
    
    # 4. Performance Analysis
    ax4.text(0.5, 0.9, '性能分析', ha='center', va='center',
             fontsize=14, fontweight='bold', transform=ax4.transAxes)
    
    # Real performance data from our test
    operations = ['密钥生成', '数字签名', '签名验证']
    times = [22.4, 22.3, 42.8]  # ms
    colors = ['#2E8B57', '#4169E1', '#DC143C']
    
    bars = ax4.bar(operations, times, color=colors, alpha=0.7)
    ax4.set_ylabel('时间 (毫秒)')
    ax4.set_title('实际性能测试结果')
    
    # Add value labels on bars
    for bar, time in zip(bars, times):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{time:.1f}ms', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/S3vn/Public/cybersec_project_homework/project5/charts/algorithm_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_security_analysis():
    """Create security analysis chart"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('SM2 安全性分析', fontsize=16, fontweight='bold')
    
    # Security comparison
    algorithms = ['RSA-1024', 'RSA-2048', 'RSA-3072', 'ECC-160', 'ECC-224', 'SM2-256']
    security_bits = [80, 112, 128, 80, 112, 128]
    colors = ['red' if 'RSA' in alg else 'green' if 'SM2' in alg else 'blue' for alg in algorithms]
    
    bars = ax1.bar(range(len(algorithms)), security_bits, color=colors, alpha=0.7)
    ax1.set_xlabel('算法')
    ax1.set_ylabel('等效安全位数')
    ax1.set_title('不同算法安全强度对比')
    ax1.set_xticks(range(len(algorithms)))
    ax1.set_xticklabels(algorithms, rotation=45)
    
    for bar, bits in zip(bars, security_bits):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{bits}位', ha='center', va='bottom')
    
    # Key size comparison
    key_sizes = [1024, 2048, 3072, 160, 224, 256]
    bars2 = ax2.bar(range(len(algorithms)), key_sizes, color=colors, alpha=0.7)
    ax2.set_xlabel('算法')
    ax2.set_ylabel('密钥长度 (位)')
    ax2.set_title('密钥长度对比')
    ax2.set_xticks(range(len(algorithms)))
    ax2.set_xticklabels(algorithms, rotation=45)
    ax2.set_yscale('log')
    
    for bar, size in zip(bars2, key_sizes):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height * 1.1,
                f'{size}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('/home/S3vn/Public/cybersec_project_homework/project5/charts/security_analysis.png',
                dpi=300, bbox_inches='tight')
    plt.close()

def create_complexity_analysis():
    """Create computational complexity analysis"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('SM2 计算复杂度分析', fontsize=16, fontweight='bold')
    
    # Time complexity growth
    key_sizes = np.array([160, 192, 224, 256, 384, 521])
    # Theoretical O(k²) complexity
    theoretical_ops = (key_sizes / 256) ** 2 * 22.4  # Normalized to our 256-bit result
    
    ax1.plot(key_sizes, theoretical_ops, 'b-', linewidth=2, label='理论复杂度 O(k²)')
    ax1.scatter([256], [22.4], color='red', s=100, label='实测数据 (SM2-256)', zorder=5)
    ax1.set_xlabel('密钥长度 (位)')
    ax1.set_ylabel('签名时间 (毫秒)')
    ax1.set_title('签名时间复杂度')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Operation breakdown
    operations = ['哈希计算', '标量乘法', '模运算', '随机数生成']
    percentages = [5, 80, 10, 5]  # Estimated breakdown
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    wedges, texts, autotexts = ax2.pie(percentages, labels=operations, colors=colors,
                                      autopct='%1.1f%%', startangle=90)
    ax2.set_title('签名操作时间分布')
    
    plt.tight_layout()
    plt.savefig('/home/S3vn/Public/cybersec_project_homework/project5/charts/complexity_analysis.png',
                dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Generate all mathematical analysis and charts"""
    print("生成数学分析和图表...")
    
    # Generate mathematical analysis
    analysis = generate_mathematical_analysis()
    
    # Create charts
    create_algorithm_flowchart()
    print("✓ 算法流程图已生成")
    
    create_security_analysis()
    print("✓ 安全性分析图已生成")
    
    create_complexity_analysis()
    print("✓ 复杂度分析图已生成")
    
    # Save analysis data
    with open('/home/S3vn/Public/cybersec_project_homework/project5/mathematical_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print("✓ 数学分析数据已保存")
    
    print("\n所有分析图表已生成完成！")
    return analysis

if __name__ == "__main__":
    main()
