#!/usr/bin/env python3
"""
SM4命令行工具
提供SM4加密解密的命令行接口
"""

import argparse
import sys
import os
import binascii
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.basic.sm4_basic import SM4Basic
from src.optimized.sm4_lookup_table import SM4LookupTable
from src.optimized.sm4_bitwise import SM4Bitwise
from src.optimized.sm4_parallel import SM4Parallel
from src.modes.sm4_modes import SM4Modes


def get_sm4_instance(impl_type, key):
    """根据实现类型获取SM4实例"""
    if impl_type == 'basic':
        return SM4Basic(key)
    elif impl_type == 'lookup':
        return SM4LookupTable(key)
    elif impl_type == 'bitwise':
        return SM4Bitwise(key)
    elif impl_type == 'parallel':
        return SM4Parallel(key)
    else:
        raise ValueError(f"不支持的实现类型: {impl_type}")


def encrypt_command(args):
    """加密命令"""
    try:
        # 读取密钥
        key = bytes.fromhex(args.key)
        if len(key) != 16:
            print("错误: 密钥必须是16字节（32位十六进制字符）")
            return 1
        
        # 读取输入数据
        if args.input == '-':
            if args.hex_input:
                input_hex = input().strip()
                data = bytes.fromhex(input_hex)
            else:
                data = input().encode('utf-8')
        else:
            with open(args.input, 'rb') as f:
                data = f.read()
        
        # 执行加密
        if args.mode == 'block':
            # 单块模式
            sm4 = get_sm4_instance(args.implementation, key)
            if len(data) != 16:
                print("错误: 单块模式要求输入数据为16字节")
                return 1
            result = sm4.encrypt_block(data)
        else:
            # 使用加密模式
            sm4_modes = SM4Modes(key)
            
            if args.mode == 'ecb':
                result = sm4_modes.encrypt_ecb(data)
            elif args.mode == 'cbc':
                iv = None
                if args.iv:
                    iv = bytes.fromhex(args.iv)
                result, iv = sm4_modes.encrypt_cbc(data, iv)
                if args.output_iv:
                    print(f"IV: {iv.hex().upper()}")
            elif args.mode == 'ctr':
                counter = None
                if args.iv:
                    counter = bytes.fromhex(args.iv)
                result, counter = sm4_modes.encrypt_ctr(data, counter)
                if args.output_iv:
                    print(f"Counter: {counter.hex().upper()}")
            elif args.mode == 'cfb':
                iv = None
                if args.iv:
                    iv = bytes.fromhex(args.iv)
                result, iv = sm4_modes.encrypt_cfb(data, iv)
                if args.output_iv:
                    print(f"IV: {iv.hex().upper()}")
            elif args.mode == 'ofb':
                iv = None
                if args.iv:
                    iv = bytes.fromhex(args.iv)
                result, iv = sm4_modes.encrypt_ofb(data, iv)
                if args.output_iv:
                    print(f"IV: {iv.hex().upper()}")
        
        # 输出结果
        if args.output == '-':
            if args.hex_output:
                print(result.hex().upper())
            else:
                sys.stdout.buffer.write(result)
        else:
            with open(args.output, 'wb') as f:
                f.write(result)
            
        return 0
        
    except Exception as e:
        print(f"加密失败: {e}", file=sys.stderr)
        return 1


def decrypt_command(args):
    """解密命令"""
    try:
        # 读取密钥
        key = bytes.fromhex(args.key)
        if len(key) != 16:
            print("错误: 密钥必须是16字节（32位十六进制字符）")
            return 1
        
        # 读取输入数据
        if args.input == '-':
            if args.hex_input:
                input_hex = input().strip()
                data = bytes.fromhex(input_hex)
            else:
                data = sys.stdin.buffer.read()
        else:
            with open(args.input, 'rb') as f:
                data = f.read()
        
        # 读取IV（如果需要）
        iv = None
        if args.iv:
            iv = bytes.fromhex(args.iv)
        
        # 执行解密
        if args.mode == 'block':
            # 单块模式
            sm4 = get_sm4_instance(args.implementation, key)
            if len(data) != 16:
                print("错误: 单块模式要求输入数据为16字节")
                return 1
            result = sm4.decrypt_block(data)
        else:
            # 使用加密模式
            sm4_modes = SM4Modes(key)
            
            if args.mode == 'ecb':
                result = sm4_modes.decrypt_ecb(data)
            elif args.mode == 'cbc':
                if not iv:
                    print("错误: CBC模式需要IV")
                    return 1
                result = sm4_modes.decrypt_cbc(data, iv)
            elif args.mode == 'ctr':
                if not iv:
                    print("错误: CTR模式需要计数器")
                    return 1
                result = sm4_modes.decrypt_ctr(data, iv)
            elif args.mode == 'cfb':
                if not iv:
                    print("错误: CFB模式需要IV")
                    return 1
                result = sm4_modes.decrypt_cfb(data, iv)
            elif args.mode == 'ofb':
                if not iv:
                    print("错误: OFB模式需要IV")
                    return 1
                result = sm4_modes.decrypt_ofb(data, iv)
        
        # 输出结果
        if args.output == '-':
            if args.hex_output:
                print(result.hex().upper())
            else:
                try:
                    print(result.decode('utf-8'))
                except UnicodeDecodeError:
                    sys.stdout.buffer.write(result)
        else:
            with open(args.output, 'wb') as f:
                f.write(result)
            
        return 0
        
    except Exception as e:
        print(f"解密失败: {e}", file=sys.stderr)
        return 1


def benchmark_command(args):
    """性能测试命令"""
    try:
        key = bytes.fromhex(args.key)
        
        print("SM4性能测试")
        print("=" * 40)
        
        # 测试数据
        test_data = os.urandom(args.size)
        
        implementations = ['basic', 'lookup', 'bitwise', 'parallel']
        results = {}
        
        for impl in implementations:
            try:
                sm4 = get_sm4_instance(impl, key)
                
                import time
                start_time = time.time()
                
                for _ in range(args.rounds):
                    sm4.encrypt_ecb(test_data)
                
                end_time = time.time()
                elapsed = end_time - start_time
                
                results[impl] = {
                    'time': elapsed,
                    'throughput': (args.size * args.rounds) / elapsed / 1024 / 1024
                }
                
                print(f"{impl:10s}: {elapsed:.4f}s, {results[impl]['throughput']:.2f} MB/s")
                
            except Exception as e:
                print(f"{impl:10s}: 错误 - {e}")
        
        # 计算加速比
        if 'basic' in results:
            base_time = results['basic']['time']
            print("\n加速比 (相对于基础实现):")
            for impl, result in results.items():
                if impl != 'basic':
                    speedup = base_time / result['time']
                    print(f"{impl:10s}: {speedup:.2f}x")
        
        return 0
        
    except Exception as e:
        print(f"性能测试失败: {e}", file=sys.stderr)
        return 1


def test_command(args):
    """测试命令"""
    try:
        print("SM4实现正确性测试")
        print("=" * 30)
        
        # 标准测试向量
        key = bytes.fromhex('0123456789abcdeffedcba9876543210')
        plaintext = bytes.fromhex('0123456789abcdeffedcba9876543210')
        expected = bytes.fromhex('681edf34d206965e86b3e94f536e4246')
        
        implementations = ['basic', 'lookup', 'bitwise', 'parallel']
        
        all_passed = True
        
        for impl in implementations:
            try:
                sm4 = get_sm4_instance(impl, key)
                result = sm4.encrypt_block(plaintext)
                
                if result == expected:
                    print(f"{impl:10s}: ✓ 通过")
                else:
                    print(f"{impl:10s}: ✗ 失败")
                    print(f"          期望: {expected.hex().upper()}")
                    print(f"          实际: {result.hex().upper()}")
                    all_passed = False
                    
            except Exception as e:
                print(f"{impl:10s}: ✗ 错误 - {e}")
                all_passed = False
        
        # 测试加密模式
        print("\n加密模式测试:")
        sm4_modes = SM4Modes(key)
        test_data = b"Hello, SM4 modes!"
        
        modes = ['ecb', 'cbc', 'ctr', 'cfb', 'ofb']
        
        for mode in modes:
            try:
                if mode == 'ecb':
                    encrypted = sm4_modes.encrypt_ecb(test_data)
                    decrypted = sm4_modes.decrypt_ecb(encrypted)
                elif mode == 'cbc':
                    encrypted, iv = sm4_modes.encrypt_cbc(test_data)
                    decrypted = sm4_modes.decrypt_cbc(encrypted, iv)
                elif mode == 'ctr':
                    encrypted, counter = sm4_modes.encrypt_ctr(test_data)
                    decrypted = sm4_modes.decrypt_ctr(encrypted, counter)
                elif mode == 'cfb':
                    encrypted, iv = sm4_modes.encrypt_cfb(test_data)
                    decrypted = sm4_modes.decrypt_cfb(encrypted, iv)
                elif mode == 'ofb':
                    encrypted, iv = sm4_modes.encrypt_ofb(test_data)
                    decrypted = sm4_modes.decrypt_ofb(encrypted, iv)
                
                if decrypted == test_data:
                    print(f"{mode.upper():10s}: ✓ 通过")
                else:
                    print(f"{mode.upper():10s}: ✗ 失败")
                    all_passed = False
                    
            except Exception as e:
                print(f"{mode.upper():10s}: ✗ 错误 - {e}")
                all_passed = False
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"测试失败: {e}", file=sys.stderr)
        return 1


def report_bug(args):
    """生成错误报告"""
    try:
        print("生成错误报告...")
        
        import platform
        import sys
        from pathlib import Path
        
        report_data = {
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "系统": platform.system(),
            "架构": platform.machine(),
            "Python版本": sys.version,
            "项目路径": str(Path(__file__).parent),
            "描述": args.description if hasattr(args, 'description') else "用户未提供描述"
        }
        
        report_file = f"bug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("SM4项目错误报告\n")
            f.write("=" * 30 + "\n\n")
            
            for key, value in report_data.items():
                f.write(f"{key}: {value}\n")
            
            f.write(f"\n详细描述:\n{args.description if hasattr(args, 'description') else '无'}\n")
        
        print(f"错误报告已生成: {report_file}")
        
    except Exception as e:
        print(f"生成报告失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='SM4加密算法命令行工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 加密命令
    encrypt_parser = subparsers.add_parser('encrypt', help='加密数据')
    encrypt_parser.add_argument('-k', '--key', required=True, help='32位十六进制密钥')
    encrypt_parser.add_argument('-i', '--input', default='-', help='输入文件 (默认: 标准输入)')
    encrypt_parser.add_argument('-o', '--output', default='-', help='输出文件 (默认: 标准输出)')
    encrypt_parser.add_argument('-m', '--mode', default='ecb', 
                               choices=['block', 'ecb', 'cbc', 'ctr', 'cfb', 'ofb'],
                               help='加密模式 (默认: ecb)')
    encrypt_parser.add_argument('--iv', help='初始化向量或计数器 (32位十六进制)')
    encrypt_parser.add_argument('--implementation', default='basic',
                               choices=['basic', 'lookup', 'bitwise', 'parallel'],
                               help='SM4实现类型 (默认: basic)')
    encrypt_parser.add_argument('--hex-input', action='store_true', help='输入为十六进制')
    encrypt_parser.add_argument('--hex-output', action='store_true', help='输出为十六进制')
    encrypt_parser.add_argument('--output-iv', action='store_true', help='输出生成的IV')
    
    # 解密命令
    decrypt_parser = subparsers.add_parser('decrypt', help='解密数据')
    decrypt_parser.add_argument('-k', '--key', required=True, help='32位十六进制密钥')
    decrypt_parser.add_argument('-i', '--input', default='-', help='输入文件 (默认: 标准输入)')
    decrypt_parser.add_argument('-o', '--output', default='-', help='输出文件 (默认: 标准输出)')
    decrypt_parser.add_argument('-m', '--mode', default='ecb',
                               choices=['block', 'ecb', 'cbc', 'ctr', 'cfb', 'ofb'],
                               help='加密模式 (默认: ecb)')
    decrypt_parser.add_argument('--iv', help='初始化向量或计数器 (32位十六进制)')
    decrypt_parser.add_argument('--implementation', default='basic',
                               choices=['basic', 'lookup', 'bitwise', 'parallel'],
                               help='SM4实现类型 (默认: basic)')
    decrypt_parser.add_argument('--hex-input', action='store_true', help='输入为十六进制')
    decrypt_parser.add_argument('--hex-output', action='store_true', help='输出为十六进制')
    
    # 性能测试命令
    benchmark_parser = subparsers.add_parser('benchmark', help='性能测试')
    benchmark_parser.add_argument('-k', '--key', default='0123456789ABCDEFFEDCBA9876543210',
                                 help='32位十六进制密钥')
    benchmark_parser.add_argument('-s', '--size', type=int, default=65536,
                                 help='测试数据大小 (字节, 默认: 65536)')
    benchmark_parser.add_argument('-r', '--rounds', type=int, default=100,
                                 help='测试轮数 (默认: 100)')
    
    # 测试命令
    test_parser = subparsers.add_parser('test', help='正确性测试')
    
    # 错误报告命令
    report_parser = subparsers.add_parser('report', help='生成错误报告')
    report_parser.add_argument('-d', '--description', help='错误描述')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'encrypt':
        return encrypt_command(args)
    elif args.command == 'decrypt':
        return decrypt_command(args)
    elif args.command == 'benchmark':
        return benchmark_command(args)
    elif args.command == 'test':
        return test_command(args)
    elif args.command == 'report':
        return report_bug(args)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
