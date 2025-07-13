"""
广告转化归因示例

演示DDH-PSI协议在广告行业中的实际应用场景
"""

import sys
import os
import random
from typing import List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ddh_psi import DDHPSIProtocol


class AdvertisingAttributionDemo:
    """广告转化归因演示"""
    
    def __init__(self):
        self.ad_platform_data = []  # 广告平台数据（看过广告的用户）
        self.ecommerce_data = []    # 电商平台数据（购买用户及金额）
    
    def generate_sample_data(self, num_ad_viewers: int = 1000, 
                           num_purchasers: int = 200,
                           overlap_rate: float = 0.3) -> Tuple[List[str], List[Tuple[str, int]]]:
        """
        生成示例数据模拟真实场景
        
        Args:
            num_ad_viewers: 看过广告的用户数量
            num_purchasers: 购买用户数量  
            overlap_rate: 交集比例（归因率）
            
        Returns:
            (广告平台数据, 电商平台数据)
        """
        print(f"生成示例数据:")
        print(f"  - 广告观看用户: {num_ad_viewers:,}")
        print(f"  - 购买用户: {num_purchasers:,}")
        print(f"  - 预期归因率: {overlap_rate:.1%}")
        
        # 生成基础用户ID池
        all_users = [f"user_{i:06d}" for i in range(num_ad_viewers + num_purchasers)]
        random.shuffle(all_users)
        
        # 广告平台数据：看过广告的用户ID
        self.ad_platform_data = all_users[:num_ad_viewers]
        
        # 计算交集大小
        overlap_size = int(num_purchasers * overlap_rate)
        
        # 电商平台数据：购买用户及消费金额
        # 一部分用户来自广告观看者（归因用户）
        attributed_users = random.sample(self.ad_platform_data, overlap_size)
        
        # 其余用户是非归因用户
        non_attributed_users = random.sample(
            all_users[num_ad_viewers:], num_purchasers - overlap_size
        )
        
        # 生成购买数据（用户ID + 消费金额）
        self.ecommerce_data = []
        
        # 归因用户（可能消费更高）
        for user in attributed_users:
            amount = random.randint(100, 1000)  # 100-1000元
            self.ecommerce_data.append((user, amount))
        
        # 非归因用户
        for user in non_attributed_users:
            amount = random.randint(50, 500)   # 50-500元
            self.ecommerce_data.append((user, amount))
        
        # 打乱顺序
        random.shuffle(self.ecommerce_data)
        
        return self.ad_platform_data.copy(), self.ecommerce_data.copy()
    
    def run_attribution_analysis(self, verbose: bool = True) -> dict:
        """
        运行广告归因分析
        
        Args:
            verbose: 是否显示详细信息
            
        Returns:
            归因分析结果
        """
        if verbose:
            print(f"\\n=== 开始广告归因分析 ===")
        
        # 执行DDH-PSI协议
        attributed_users, total_attributed_revenue = DDHPSIProtocol.run_protocol(
            self.ad_platform_data, 
            self.ecommerce_data,
            verbose=verbose
        )
        
        # 计算分析指标
        total_ad_viewers = len(self.ad_platform_data)
        total_purchasers = len(self.ecommerce_data)
        total_revenue = sum(amount for _, amount in self.ecommerce_data)
        
        attribution_rate = attributed_users / total_ad_viewers if total_ad_viewers > 0 else 0
        conversion_rate = attributed_users / total_purchasers if total_purchasers > 0 else 0
        avg_attributed_revenue = total_attributed_revenue / attributed_users if attributed_users > 0 else 0
        avg_total_revenue = total_revenue / total_purchasers if total_purchasers > 0 else 0
        revenue_lift = (avg_attributed_revenue / avg_total_revenue - 1) if avg_total_revenue > 0 else 0
        
        results = {
            'total_ad_viewers': total_ad_viewers,
            'total_purchasers': total_purchasers,
            'attributed_users': attributed_users,
            'attribution_rate': attribution_rate,
            'conversion_rate': conversion_rate,
            'total_revenue': total_revenue,
            'attributed_revenue': total_attributed_revenue,
            'avg_attributed_revenue': avg_attributed_revenue,
            'avg_total_revenue': avg_total_revenue,
            'revenue_lift': revenue_lift
        }
        
        if verbose:
            self.print_attribution_report(results)
        
        return results
    
    def print_attribution_report(self, results: dict):
        """打印归因分析报告"""
        print(f"\\n=== 广告归因分析报告 ===")
        print(f"📊 基础数据:")
        print(f"   - 广告观看用户: {results['total_ad_viewers']:,}")
        print(f"   - 购买用户总数: {results['total_purchasers']:,}")
        print(f"   - 总收入: ¥{results['total_revenue']:,}")
        
        print(f"\\n🎯 归因结果:")
        print(f"   - 归因用户数: {results['attributed_users']:,}")
        print(f"   - 归因率: {results['attribution_rate']:.1%}")
        print(f"   - 转化率: {results['conversion_rate']:.1%}")
        
        print(f"\\n💰 收入分析:")
        print(f"   - 归因收入: ¥{results['attributed_revenue']:,}")
        print(f"   - 归因用户平均消费: ¥{results['avg_attributed_revenue']:.0f}")
        print(f"   - 全体用户平均消费: ¥{results['avg_total_revenue']:.0f}")
        print(f"   - 收入提升: {results['revenue_lift']:+.1%}")
        
        print(f"\\n📈 广告效果评估:")
        if results['attribution_rate'] > 0.2:
            print(f"   ✅ 归因率较高，广告投放效果良好")
        elif results['attribution_rate'] > 0.1:
            print(f"   ⚠️ 归因率中等，建议优化广告定向")
        else:
            print(f"   ❌ 归因率较低，需要重新评估广告策略")
        
        if results['revenue_lift'] > 0.2:
            print(f"   ✅ 显著的收入提升，ROI良好")
        elif results['revenue_lift'] > 0:
            print(f"   ⚠️ 有一定收入提升，可继续优化")
        else:
            print(f"   ❌ 无明显收入提升，需要重新评估")
    
    def run_comparative_analysis(self):
        """运行对比分析：不同参数下的归因效果"""
        print(f"\\n=== 对比分析：不同场景下的归因效果 ===")
        
        scenarios = [
            {"name": "高效广告", "viewers": 500, "purchasers": 100, "overlap": 0.4},
            {"name": "中效广告", "viewers": 1000, "purchasers": 150, "overlap": 0.25},
            {"name": "低效广告", "viewers": 2000, "purchasers": 200, "overlap": 0.1},
            {"name": "精准投放", "viewers": 300, "purchasers": 80, "overlap": 0.6},
        ]
        
        comparison_results = []
        
        for scenario in scenarios:
            print(f"\\n--- {scenario['name']} ---")
            
            # 生成数据并运行分析
            self.generate_sample_data(
                scenario['viewers'], 
                scenario['purchasers'], 
                scenario['overlap']
            )
            
            result = self.run_attribution_analysis(verbose=False)
            result['scenario_name'] = scenario['name']
            comparison_results.append(result)
            
            print(f"归因率: {result['attribution_rate']:.1%}, "
                  f"收入提升: {result['revenue_lift']:+.1%}")
        
        # 输出对比总结
        print(f"\\n=== 场景对比总结 ===")
        print(f"{'场景':<10} {'归因率':<8} {'转化率':<8} {'收入提升':<10} {'ROI评级'}")
        print(f"{'-'*50}")
        
        for result in comparison_results:
            roi_rating = "优秀" if result['revenue_lift'] > 0.2 else \
                        "良好" if result['revenue_lift'] > 0.1 else \
                        "一般" if result['revenue_lift'] > 0 else "较差"
            
            print(f"{result['scenario_name']:<10} "
                  f"{result['attribution_rate']:>6.1%} "
                  f"{result['conversion_rate']:>6.1%} "
                  f"{result['revenue_lift']:>+8.1%} "
                  f"{roi_rating}")
        
        return comparison_results


def main():
    """主函数：运行广告归因演示"""
    print("=== DDH-PSI协议广告转化归因演示 ===")
    print("本演示模拟广告平台和电商平台的隐私数据协作场景")
    print("协议能够在保护双方用户隐私的前提下计算广告转化效果\\n")
    
    demo = AdvertisingAttributionDemo()
    
    # 1. 基础归因分析
    print("1️⃣ 基础归因分析")
    demo.generate_sample_data(num_ad_viewers=1000, num_purchasers=200, overlap_rate=0.25)
    demo.run_attribution_analysis()
    
    # 2. 对比分析
    print("\\n\\n2️⃣ 多场景对比分析")
    demo.run_comparative_analysis()
    
    # 3. 隐私保护说明
    print(f"\\n\\n=== 隐私保护特性 ===")
    print(f"✅ 广告平台无法获知具体购买用户和金额")
    print(f"✅ 电商平台无法获知具体广告观看用户")
    print(f"✅ 双方仅获得聚合统计结果")
    print(f"✅ 基于DDH假设和同态加密的强安全保证")
    print(f"✅ 适用于跨企业的数据协作场景")
    
    print(f"\\n演示完成！协议成功实现了隐私保护下的广告归因分析。")


if __name__ == '__main__':
    main()
