#!/usr/bin/env python3
"""
DDH-PSI项目完整演示脚本
演示所有功能和特性的完整使用方法
"""

import time
import sys
import os
from pathlib import Path

# 添加src目录到路径
sys.path.append(str(Path(__file__).parent / "src"))

from ddh_psi import DDHPSIProtocol
from ddh_psi import DDHPSIParty1, DDHPSIParty2
import json

def print_header(title):
    """打印格式化的标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step, description):
    """打印步骤信息"""
    print(f"\n[步骤 {step}] {description}")
    print("-" * 40)

def demo_basic_usage():
    """演示基本使用方法"""
    print_header("基本使用演示")
    
    # 准备测试数据
    party1_data = ["apple", "banana", "cherry", "date", "elderberry"]
    party2_data = [
        ("apple", 100),
        ("banana", 200),
        ("grape", 300),    # 不在party1中
        ("date", 400),
        ("fig", 500)       # 不在party1中
    ]
    
    print_step(1, "准备输入数据")
    print(f"Party1数据: {party1_data}")
    print(f"Party2数据: {party2_data}")
    
    print_step(2, "创建协议实例并执行")
    protocol = DDHPSIProtocol()
    
    start_time = time.time()
    intersection_size, intersection_sum = protocol.run_protocol(party1_data, party2_data)
    end_time = time.time()
    
    print_step(3, "输出结果")
    print(f"交集大小: {intersection_size}")
    print(f"交集总和: {intersection_sum}")
    print(f"执行时间: {end_time - start_time:.4f}秒")
    
    # 验证正确性
    expected_intersection = {"apple", "banana", "date"}
    expected_sum = 100 + 200 + 400  # 700
    
    print_step(4, "结果验证")
    print(f"预期交集: {expected_intersection}")
    print(f"预期总和: {expected_sum}")
    print(f"结果正确: {intersection_size == len(expected_intersection) and intersection_sum == expected_sum}")

def demo_step_by_step():
    """演示分步执行过程"""
    print_header("分步执行演示")
    
    party1_data = ["user1", "user2", "user3"]
    party2_data = [("user1", 50), ("user2", 75), ("user4", 100)]
    
    print_step(1, "创建协议参与方")
    party1 = DDHPSIParty1(party1_data)
    party2 = DDHPSIParty2(party2_data)
    print("✓ 协议参与方创建完成")
    
    print_step(2, "第一轮通信 (Party1 → Party2)")
    round1_message = party1.round1()
    print(f"发送椭圆曲线点数量: {len(round1_message)}")
    print("✓ 第一轮消息生成完成")
    
    print_step(3, "第二轮通信 (Party2 → Party1)")
    round2_message = party2.round2(round1_message)
    print(f"返回数据包含 Z: {len(round2_message[0])} 个点, Y: {len(round2_message[1])} 个对")
    print("✓ 第二轮消息处理完成")
    
    print_step(4, "第三轮通信 (Party1 → Party2)")
    round3_message = party1.round3(round2_message)
    print("✓ 第三轮消息生成完成")
    
    print_step(5, "获取最终结果")
    intersection_size, intersection_sum = party2.get_result(round3_message)
    print(f"交集大小: {intersection_size}")
    print(f"交集总和: {intersection_sum}")

def demo_performance_analysis():
    """演示性能分析"""
    print_header("性能分析演示")
    
    sizes = [10, 50, 100, 500]
    results = []
    
    print_step(1, "不同数据规模的性能测试")
    
    for size in sizes:
        # 生成测试数据
        party1_data = [f"item_{i}" for i in range(size)]
        party2_data = [(f"item_{i}", i*10) for i in range(0, size, 2)]  # 50%交集
        
        protocol = DDHPSIProtocol()
        
        # 性能测试
        start_time = time.time()
        intersection_size, intersection_sum = protocol.run_protocol(party1_data, party2_data)
        end_time = time.time()
        
        execution_time = end_time - start_time
        results.append({
            "size": size,
            "time": execution_time,
            "intersection_size": intersection_size,
            "intersection_sum": intersection_sum
        })
        
        print(f"规模 {size:3d}: 时间 {execution_time:.4f}秒, 交集 {intersection_size:2d}, 总和 {intersection_sum:5d}")
    
    print_step(2, "性能趋势分析")
    for i in range(1, len(results)):
        prev_time = results[i-1]["time"]
        curr_time = results[i]["time"]
        size_ratio = results[i]["size"] / results[i-1]["size"]
        time_ratio = curr_time / prev_time if prev_time > 0 else float('inf')
        
        print(f"规模增加 {size_ratio:.1f}倍, 时间增加 {time_ratio:.2f}倍")

def demo_error_handling():
    """演示错误处理"""
    print_header("错误处理演示")
    
    protocol = DDHPSIProtocol()
    
    print_step(1, "空数据处理")
    try:
        result = protocol.run_protocol([], [])
        print(f"空数据结果: {result}")
    except Exception as e:
        print(f"错误: {e}")
    
    print_step(2, "不匹配数据类型处理")
    try:
        party1_data = ["item1", 123]  # 混合类型
        party2_data = [("item1", 100)]
        result = protocol.run_protocol(party1_data, party2_data)
        print(f"混合类型结果: {result}")
    except Exception as e:
        print(f"错误: {e}")
    
    print_step(3, "大数据量处理")
    try:
        large_data1 = [f"item_{i}" for i in range(1000)]
        large_data2 = [(f"item_{i}", i) for i in range(500, 1500)]
        
        start_time = time.time()
        result = protocol.run_protocol(large_data1, large_data2)
        end_time = time.time()
        
        print(f"大数据量结果: {result}")
        print(f"处理时间: {end_time - start_time:.4f}秒")
    except Exception as e:
        print(f"错误: {e}")

def demo_real_world_scenario():
    """演示真实世界应用场景"""
    print_header("真实应用场景演示")
    
    print_step(1, "广告归因分析场景")
    
    # 模拟广告商的用户数据
    advertiser_users = [
        "user_001", "user_002", "user_003", "user_004", "user_005",
        "user_006", "user_007", "user_008", "user_009", "user_010"
    ]
    
    # 模拟平台的用户转化数据
    platform_conversions = [
        ("user_001", 150),  # 转化价值150元
        ("user_003", 200),  # 转化价值200元
        ("user_005", 300),  # 转化价值300元
        ("user_011", 100),  # 非广告商用户
        ("user_012", 250),  # 非广告商用户
        ("user_007", 180),  # 转化价值180元
    ]
    
    print("广告商用户数:", len(advertiser_users))
    print("平台转化记录数:", len(platform_conversions))
    
    protocol = DDHPSIProtocol()
    attributed_users, total_revenue = protocol.run_protocol(
        advertiser_users, platform_conversions
    )
    
    print_step(2, "归因分析结果")
    print(f"可归因用户数: {attributed_users}")
    print(f"总归因收入: {total_revenue}元")
    
    if attributed_users > 0:
        avg_revenue = total_revenue / attributed_users
        print(f"平均用户价值: {avg_revenue:.2f}元")
        
        # 计算ROI
        assumed_ad_cost = 500  # 假设广告成本500元
        roi = (total_revenue - assumed_ad_cost) / assumed_ad_cost * 100
        print(f"投资回报率: {roi:.1f}%")

def demo_configuration_options():
    """演示配置选项"""
    print_header("配置选项演示")
    
    from elliptic_curve import EllipticCurveGroup
    from paillier_encryption import PaillierEncryption
    
    print_step(1, "默认配置")
    protocol1 = DDHPSIProtocol()
    print("✓ 使用默认椭圆曲线和Paillier参数")
    
    print_step(2, "自定义椭圆曲线")
    curve_group = EllipticCurveGroup(curve_name="prime256v1")
    protocol2 = DDHPSIProtocol(curve_group=curve_group)
    print("✓ 使用prime256v1椭圆曲线")
    
    print_step(3, "自定义Paillier参数")
    paillier = PaillierEncryption(key_size=1024)
    protocol3 = DDHPSIProtocol(paillier_encryption=paillier)
    print("✓ 使用1024位Paillier密钥")
    
    print_step(4, "完全自定义配置")
    protocol4 = DDHPSIProtocol(
        curve_group=curve_group,
        paillier_encryption=paillier
    )
    print("✓ 使用完全自定义的配置")
    
    # 用同样的数据测试不同配置
    test_data1 = ["a", "b", "c"]
    test_data2 = [("a", 1), ("b", 2), ("d", 3)]
    
    print_step(5, "验证不同配置的一致性")
    for i, protocol in enumerate([protocol1, protocol2, protocol3, protocol4], 1):
        result = protocol.run_protocol(test_data1, test_data2)
        print(f"配置{i}结果: {result}")

def generate_performance_report():
    """生成性能报告"""
    print_header("性能报告生成")
    
    print_step(1, "运行性能基准测试")
    
    # 导入并运行基准测试
    try:
        sys.path.append("benchmarks")
        from performance_benchmark import DDHPSIBenchmark
        
        benchmark = DDHPSIBenchmark()
        results = benchmark.run_comprehensive_benchmark()
        
        print_step(2, "保存性能报告")
        report_file = "performance_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 性能报告已保存到: {report_file}")
        
        print_step(3, "报告摘要")
        for category, data in results.items():
            if isinstance(data, dict) and "execution_times" in data:
                avg_time = sum(data["execution_times"]) / len(data["execution_times"])
                print(f"{category}: 平均执行时间 {avg_time:.4f}秒")
                
    except ImportError:
        print("基准测试模块未找到，跳过性能报告生成")

def main():
    """主演示函数"""
    print("DDH-PSI项目完整功能演示")
    print("=" * 60)
    print("本演示将展示DDH-PSI协议的所有功能和特性")
    print("包括基本使用、分步执行、性能分析、错误处理等")
    
    try:
        # 基本功能演示
        demo_basic_usage()
        
        # 分步执行演示
        demo_step_by_step()
        
        # 性能分析演示
        demo_performance_analysis()
        
        # 错误处理演示
        demo_error_handling()
        
        # 真实应用场景演示
        demo_real_world_scenario()
        
        # 配置选项演示
        demo_configuration_options()
        
        # 性能报告生成
        generate_performance_report()
        
        print_header("演示完成")
        print("✅ 所有功能演示成功完成！")
        print("📊 性能数据已收集")
        print("📝 详细文档请查看 docs/ 目录")
        print("🧪 更多测试请运行 tests/ 目录下的测试文件")
        print("📈 图表生成请运行 generate_charts.py")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  演示被用户中断")
    except Exception as e:
        print(f"\n\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
