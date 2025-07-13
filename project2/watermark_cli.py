"""
数字水印系统命令行界面
提供水印嵌入、提取、攻击测试和评估功能
"""

import argparse
import sys
import os
import logging
from pathlib import Path
import numpy as np
import cv2

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.algorithms import AlgorithmRegistry
from src.attacks import AttackEngine
from src.evaluation import EvaluationEngine
from src.utils.image_loader import ImageLoader
from src.utils.logger import setup_logger


def setup_arguments():
    """设置命令行参数"""
    parser = argparse.ArgumentParser(
        description='数字水印系统 - 水印嵌入、提取、攻击测试和评估',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 嵌入水印
  python watermark_cli.py embed -i input.jpg -w watermark.png -o output.jpg -a lsb
  
  # 提取水印
  python watermark_cli.py extract -i watermarked.jpg -o extracted_wm.png -a lsb
  
  # 攻击测试
  python watermark_cli.py attack -i watermarked.jpg -o attacked.jpg -t gaussian_noise --std 25
  
  # 综合评估
  python watermark_cli.py evaluate -o original.jpg -w watermarked.jpg -ow original_wm.png -ew extracted_wm.png
        """
    )
    
    # 主命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 嵌入水印命令
    embed_parser = subparsers.add_parser('embed', help='嵌入水印')
    embed_parser.add_argument('-i', '--input', required=True, 
                             help='输入图像路径')
    embed_parser.add_argument('-w', '--watermark', required=True,
                             help='水印图像路径')
    embed_parser.add_argument('-o', '--output', required=True,
                             help='输出图像路径')
    embed_parser.add_argument('-a', '--algorithm', required=True,
                             choices=['lsb', 'dct'], 
                             help='水印算法')
    embed_parser.add_argument('--strength', type=float, default=0.1,
                             help='水印强度 (默认: 0.1)')
    embed_parser.add_argument('--key', type=str, default='secret_key',
                             help='密钥 (默认: secret_key)')
    
    # 提取水印命令
    extract_parser = subparsers.add_parser('extract', help='提取水印')
    extract_parser.add_argument('-i', '--input', required=True,
                               help='含水印图像路径')
    extract_parser.add_argument('-o', '--output', required=True,
                               help='提取水印保存路径')
    extract_parser.add_argument('-a', '--algorithm', required=True,
                               choices=['lsb', 'dct'],
                               help='水印算法')
    extract_parser.add_argument('--original', type=str,
                               help='原始图像路径 (DCT算法非盲提取需要)')
    extract_parser.add_argument('--size', type=int, nargs=2, default=[64, 64],
                               help='水印尺寸 (默认: 64 64)')
    extract_parser.add_argument('--key', type=str, default='secret_key',
                               help='密钥 (默认: secret_key)')
    
    # 攻击测试命令
    attack_parser = subparsers.add_parser('attack', help='攻击测试')
    attack_parser.add_argument('-i', '--input', required=True,
                              help='输入图像路径')
    attack_parser.add_argument('-o', '--output', required=True,
                              help='攻击后图像保存路径')
    attack_parser.add_argument('-t', '--type', required=True,
                              help='攻击类型')
    attack_parser.add_argument('--list-attacks', action='store_true',
                              help='列出所有可用的攻击类型')
    # 攻击参数
    attack_parser.add_argument('--angle', type=float, help='旋转角度')
    attack_parser.add_argument('--scale', type=float, help='缩放因子')
    attack_parser.add_argument('--tx', type=int, help='x方向平移')
    attack_parser.add_argument('--ty', type=int, help='y方向平移')
    attack_parser.add_argument('--crop-ratio', type=float, help='裁剪比例')
    attack_parser.add_argument('--std', type=float, help='高斯噪声标准差')
    attack_parser.add_argument('--sigma', type=float, help='高斯模糊标准差')
    attack_parser.add_argument('--quality', type=int, help='JPEG压缩质量')
    attack_parser.add_argument('--brightness', type=float, help='亮度调整')
    attack_parser.add_argument('--contrast', type=float, help='对比度调整')
    
    # 评估命令
    eval_parser = subparsers.add_parser('evaluate', help='综合评估')
    eval_parser.add_argument('-o', '--original', required=True,
                            help='原始图像路径')
    eval_parser.add_argument('-w', '--watermarked', required=True,
                            help='含水印图像路径')
    eval_parser.add_argument('-ow', '--original-watermark', required=True,
                            help='原始水印路径')
    eval_parser.add_argument('-ew', '--extracted-watermark', required=True,
                            help='提取水印路径')
    eval_parser.add_argument('--report', type=str,
                            help='评估报告保存路径')
    
    # 批量测试命令
    batch_parser = subparsers.add_parser('batch', help='批量测试')
    batch_parser.add_argument('-c', '--config', required=True,
                             help='批量测试配置文件')
    batch_parser.add_argument('-o', '--output-dir', required=True,
                             help='结果输出目录')
    
    # 通用参数
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出')
    parser.add_argument('--log-file', type=str,
                       help='日志文件路径')
    
    return parser


def load_image(image_path: str) -> np.ndarray:
    """加载图像"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像文件不存在: {image_path}")
    
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"无法加载图像: {image_path}")
    
    return image


def save_image(image: np.ndarray, output_path: str):
    """保存图像"""
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    success = cv2.imwrite(output_path, image)
    if not success:
        raise ValueError(f"无法保存图像: {output_path}")


def embed_watermark(args):
    """嵌入水印"""
    logger = logging.getLogger(__name__)
    
    try:
        # 加载图像和水印
        logger.info(f"加载原始图像: {args.input}")
        host_image = load_image(args.input)
        
        logger.info(f"加载水印图像: {args.watermark}")
        watermark = load_image(args.watermark)
        
        # 获取算法
        algorithm_registry = AlgorithmRegistry()
        algorithm = algorithm_registry.get_algorithm(args.algorithm)
        
        # 嵌入水印
        logger.info(f"使用 {args.algorithm} 算法嵌入水印")
        watermarked_image = algorithm.embed(
            host_image, watermark, 
            strength=args.strength,
            key=args.key
        )
        
        # 保存结果
        logger.info(f"保存含水印图像: {args.output}")
        save_image(watermarked_image, args.output)
        
        print(f"水印嵌入完成: {args.output}")
        
    except Exception as e:
        logger.error(f"水印嵌入失败: {e}")
        print(f"错误: {e}")
        return False
    
    return True


def extract_watermark(args):
    """提取水印"""
    logger = logging.getLogger(__name__)
    
    try:
        # 加载含水印图像
        logger.info(f"加载含水印图像: {args.input}")
        watermarked_image = load_image(args.input)
        
        # 获取算法
        algorithm_registry = AlgorithmRegistry()
        algorithm = algorithm_registry.get_algorithm(args.algorithm)
        
        # 根据算法类型选择提取方式
        if args.algorithm == 'dct' and args.original:
            # DCT算法非盲提取
            logger.info(f"加载原始图像: {args.original}")
            original_image = load_image(args.original)
            extracted_watermark = algorithm.extract_non_blind(
                watermarked_image, original_image,
                watermark_size=tuple(args.size),
                key=args.key
            )
        else:
            # 盲提取
            extracted_watermark = algorithm.extract(
                watermarked_image,
                watermark_size=tuple(args.size),
                key=args.key
            )
        
        # 保存提取的水印
        logger.info(f"保存提取的水印: {args.output}")
        save_image(extracted_watermark, args.output)
        
        print(f"水印提取完成: {args.output}")
        
    except Exception as e:
        logger.error(f"水印提取失败: {e}")
        print(f"错误: {e}")
        return False
    
    return True


def attack_image(args):
    """攻击测试"""
    logger = logging.getLogger(__name__)
    
    # 列出所有攻击类型
    if args.list_attacks:
        attack_engine = AttackEngine()
        configs = attack_engine.get_all_attack_configs()
        print("可用的攻击类型:")
        for attack_name in sorted(configs.keys()):
            print(f"  {attack_name}")
        return True
    
    try:
        # 加载图像
        logger.info(f"加载图像: {args.input}")
        image = load_image(args.input)
        
        # 创建攻击引擎
        attack_engine = AttackEngine()
        
        # 构建攻击参数
        attack_params = {}
        if args.angle is not None:
            attack_params['angle'] = args.angle
        if args.scale is not None:
            attack_params['scale_factor'] = args.scale
        if args.tx is not None:
            attack_params['tx'] = args.tx
        if args.ty is not None:
            attack_params['ty'] = args.ty
        if args.crop_ratio is not None:
            attack_params['crop_ratio'] = args.crop_ratio
        if args.std is not None:
            attack_params['std'] = args.std
        if args.sigma is not None:
            attack_params['sigma'] = args.sigma
        if args.quality is not None:
            attack_params['quality'] = args.quality
        if args.brightness is not None:
            attack_params['brightness'] = args.brightness
        if args.contrast is not None:
            attack_params['contrast'] = args.contrast
        
        # 执行攻击
        logger.info(f"执行 {args.type} 攻击")
        attacked_image = attack_engine.apply_attack_by_name(
            image, args.type, **attack_params)
        
        # 保存结果
        logger.info(f"保存攻击后图像: {args.output}")
        save_image(attacked_image, args.output)
        
        print(f"攻击测试完成: {args.output}")
        
    except Exception as e:
        logger.error(f"攻击测试失败: {e}")
        print(f"错误: {e}")
        return False
    
    return True


def evaluate_watermark(args):
    """综合评估"""
    logger = logging.getLogger(__name__)
    
    try:
        # 加载所有图像
        logger.info("加载图像进行评估")
        original_image = load_image(args.original)
        watermarked_image = load_image(args.watermarked)
        original_watermark = load_image(args.original_watermark)
        extracted_watermark = load_image(args.extracted_watermark)
        
        # 转换为灰度图像（如果需要）
        if len(original_watermark.shape) == 3:
            original_watermark = cv2.cvtColor(original_watermark, cv2.COLOR_BGR2GRAY)
        if len(extracted_watermark.shape) == 3:
            extracted_watermark = cv2.cvtColor(extracted_watermark, cv2.COLOR_BGR2GRAY)
        
        # 创建评估引擎
        evaluation_engine = EvaluationEngine()
        
        # 执行综合评估
        logger.info("执行综合评估")
        results = evaluation_engine.comprehensive_evaluation(
            original_image, watermarked_image,
            original_watermark, extracted_watermark
        )
        
        # 显示结果
        print("\n=== 综合评估结果 ===")
        
        print("\n图像质量指标:")
        for metric, value in results['image_quality'].items():
            print(f"  {metric.upper()}: {value:.4f}")
        print(f"  整体评估: {results['overall_assessment']['image_quality']}")
        
        print("\n水印鲁棒性指标:")
        for metric, value in results['watermark_robustness'].items():
            print(f"  {metric.upper()}: {value:.4f}")
        print(f"  整体评估: {results['overall_assessment']['watermark_quality']}")
        
        # 保存报告
        if args.report:
            logger.info(f"保存评估报告: {args.report}")
            save_evaluation_report(results, args.report)
            print(f"\n评估报告已保存: {args.report}")
        
    except Exception as e:
        logger.error(f"评估失败: {e}")
        print(f"错误: {e}")
        return False
    
    return True


def save_evaluation_report(results: dict, report_path: str):
    """保存评估报告"""
    import json
    
    # 确保输出目录存在
    output_dir = os.path.dirname(report_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 保存为JSON格式
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def batch_test(args):
    """批量测试"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"加载批量测试配置: {args.config}")
        # 这里可以实现批量测试的配置文件解析和执行
        print("批量测试功能待实现")
        
    except Exception as e:
        logger.error(f"批量测试失败: {e}")
        print(f"错误: {e}")
        return False
    
    return True


def main():
    """主函数"""
    parser = setup_arguments()
    args = parser.parse_args()
    
    # 如果没有提供命令，显示帮助
    if not args.command:
        parser.print_help()
        return
    
    # 设置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(
        name='watermark_cli',
        level=log_level,
        log_file=args.log_file
    )
    
    logger.info(f"开始执行命令: {args.command}")
    
    # 执行对应的命令
    success = False
    if args.command == 'embed':
        success = embed_watermark(args)
    elif args.command == 'extract':
        success = extract_watermark(args)
    elif args.command == 'attack':
        success = attack_image(args)
    elif args.command == 'evaluate':
        success = evaluate_watermark(args)
    elif args.command == 'batch':
        success = batch_test(args)
    else:
        logger.error(f"未知命令: {args.command}")
        parser.print_help()
    
    if success:
        logger.info("命令执行成功")
    else:
        logger.error("命令执行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
