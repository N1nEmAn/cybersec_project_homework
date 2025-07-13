#!/usr/bin/env python3
"""
SM4加密算法GUI演示程序
提供图形用户界面来测试SM4的各种实现和加密模式
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import binascii
import traceback
from src.basic.sm4_basic import SM4Basic
from src.optimized.sm4_lookup_table import SM4LookupTable
from src.optimized.sm4_bitwise import SM4Bitwise
from src.optimized.sm4_parallel import SM4Parallel
from src.modes.sm4_modes import SM4Modes


class SM4GUI:
    """SM4加密算法GUI演示程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SM4加密算法演示程序")
        self.root.geometry("800x700")
        
        # 创建笔记本控件
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建各个标签页
        self.create_basic_tab()
        self.create_optimization_tab()
        self.create_modes_tab()
        self.create_benchmark_tab()
        
    def create_basic_tab(self):
        """创建基础功能标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="基础加密")
        
        # 密钥输入
        ttk.Label(frame, text="密钥 (32位十六进制):").pack(pady=5)
        self.key_entry = tk.Entry(frame, width=50)
        self.key_entry.pack(pady=5)
        self.key_entry.insert(0, "0123456789ABCDEFFEDCBA9876543210")
        
        # 明文输入
        ttk.Label(frame, text="明文:").pack(pady=5)
        self.plaintext_text = scrolledtext.ScrolledText(frame, height=5)
        self.plaintext_text.pack(fill='x', padx=20, pady=5)
        self.plaintext_text.insert('1.0', "Hello, SM4!")
        
        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="加密", command=self.encrypt_basic).pack(side='left', padx=5)
        ttk.Button(button_frame, text="解密", command=self.decrypt_basic).pack(side='left', padx=5)
        ttk.Button(button_frame, text="清除", command=self.clear_basic).pack(side='left', padx=5)
        
        # 密文输出
        ttk.Label(frame, text="密文 (十六进制):").pack(pady=5)
        self.ciphertext_text = scrolledtext.ScrolledText(frame, height=5)
        self.ciphertext_text.pack(fill='x', padx=20, pady=5)
    
    def create_optimization_tab(self):
        """创建优化实现标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="优化实现")
        
        # 实现选择
        ttk.Label(frame, text="选择实现:").pack(pady=5)
        self.impl_var = tk.StringVar(value="basic")
        impl_frame = ttk.Frame(frame)
        impl_frame.pack(pady=5)
        
        ttk.Radiobutton(impl_frame, text="基础实现", variable=self.impl_var, 
                       value="basic").pack(side='left', padx=10)
        ttk.Radiobutton(impl_frame, text="查找表优化", variable=self.impl_var, 
                       value="lookup").pack(side='left', padx=10)
        ttk.Radiobutton(impl_frame, text="位运算优化", variable=self.impl_var, 
                       value="bitwise").pack(side='left', padx=10)
        ttk.Radiobutton(impl_frame, text="并行优化", variable=self.impl_var, 
                       value="parallel").pack(side='left', padx=10)
        
        # 密钥输入
        ttk.Label(frame, text="密钥 (32位十六进制):").pack(pady=5)
        self.opt_key_entry = tk.Entry(frame, width=50)
        self.opt_key_entry.pack(pady=5)
        self.opt_key_entry.insert(0, "0123456789ABCDEFFEDCBA9876543210")
        
        # 数据输入
        ttk.Label(frame, text="数据:").pack(pady=5)
        self.opt_data_text = scrolledtext.ScrolledText(frame, height=4)
        self.opt_data_text.pack(fill='x', padx=20, pady=5)
        self.opt_data_text.insert('1.0', "Performance test data for SM4 optimization")
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="测试加密", command=self.test_optimization).pack(side='left', padx=5)
        ttk.Button(button_frame, text="性能测试", command=self.benchmark_optimization).pack(side='left', padx=5)
        
        # 结果输出
        ttk.Label(frame, text="测试结果:").pack(pady=5)
        self.opt_result_text = scrolledtext.ScrolledText(frame, height=8)
        self.opt_result_text.pack(fill='x', padx=20, pady=5)
    
    def create_modes_tab(self):
        """创建加密模式标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="加密模式")
        
        # 模式选择
        ttk.Label(frame, text="加密模式:").pack(pady=5)
        self.mode_var = tk.StringVar(value="ecb")
        mode_frame = ttk.Frame(frame)
        mode_frame.pack(pady=5)
        
        ttk.Radiobutton(mode_frame, text="ECB", variable=self.mode_var, 
                       value="ecb").pack(side='left', padx=10)
        ttk.Radiobutton(mode_frame, text="CBC", variable=self.mode_var, 
                       value="cbc").pack(side='left', padx=10)
        ttk.Radiobutton(mode_frame, text="CTR", variable=self.mode_var, 
                       value="ctr").pack(side='left', padx=10)
        ttk.Radiobutton(mode_frame, text="CFB", variable=self.mode_var, 
                       value="cfb").pack(side='left', padx=10)
        ttk.Radiobutton(mode_frame, text="OFB", variable=self.mode_var, 
                       value="ofb").pack(side='left', padx=10)
        
        # 密钥和IV
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(input_frame, text="密钥:").pack(anchor='w')
        self.mode_key_entry = tk.Entry(input_frame, width=60)
        self.mode_key_entry.pack(fill='x', pady=2)
        self.mode_key_entry.insert(0, "0123456789ABCDEFFEDCBA9876543210")
        
        ttk.Label(input_frame, text="IV/计数器 (可选):").pack(anchor='w')
        self.iv_entry = tk.Entry(input_frame, width=60)
        self.iv_entry.pack(fill='x', pady=2)
        
        # 数据输入
        ttk.Label(frame, text="明文:").pack(pady=5)
        self.mode_data_text = scrolledtext.ScrolledText(frame, height=4)
        self.mode_data_text.pack(fill='x', padx=20, pady=5)
        self.mode_data_text.insert('1.0', "Test message for different SM4 modes")
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="加密", command=self.encrypt_mode).pack(side='left', padx=5)
        ttk.Button(button_frame, text="解密", command=self.decrypt_mode).pack(side='left', padx=5)
        ttk.Button(button_frame, text="比较模式", command=self.compare_modes).pack(side='left', padx=5)
        
        # 结果输出
        ttk.Label(frame, text="结果:").pack(pady=5)
        self.mode_result_text = scrolledtext.ScrolledText(frame, height=8)
        self.mode_result_text.pack(fill='x', padx=20, pady=5)
    
    def create_benchmark_tab(self):
        """创建性能测试标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="性能测试")
        
        # 测试配置
        config_frame = ttk.Frame(frame)
        config_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(config_frame, text="数据大小 (字节):").pack(anchor='w')
        self.size_entry = tk.Entry(config_frame, width=20)
        self.size_entry.pack(anchor='w', pady=2)
        self.size_entry.insert(0, "65536")
        
        ttk.Label(config_frame, text="测试轮数:").pack(anchor='w')
        self.rounds_entry = tk.Entry(config_frame, width=20)
        self.rounds_entry.pack(anchor='w', pady=2)
        self.rounds_entry.insert(0, "100")
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="运行性能测试", command=self.run_benchmark).pack(side='left', padx=5)
        ttk.Button(button_frame, text="比较所有实现", command=self.compare_all).pack(side='left', padx=5)
        
        # 结果输出
        ttk.Label(frame, text="性能测试结果:").pack(pady=5)
        self.benchmark_result_text = scrolledtext.ScrolledText(frame, height=15)
        self.benchmark_result_text.pack(fill='both', expand=True, padx=20, pady=5)
    
    def get_key_bytes(self, entry):
        """从输入框获取密钥字节"""
        try:
            key_hex = entry.get().replace(' ', '')
            if len(key_hex) != 32:
                raise ValueError("密钥必须是32位十六进制字符")
            return bytes.fromhex(key_hex)
        except ValueError as e:
            messagebox.showerror("错误", f"密钥格式错误: {e}")
            return None
    
    def encrypt_basic(self):
        """基础加密"""
        try:
            key = self.get_key_bytes(self.key_entry)
            if not key:
                return
            
            plaintext = self.plaintext_text.get('1.0', 'end-1c').encode('utf-8')
            sm4 = SM4Basic(key)
            ciphertext = sm4.encrypt_ecb(plaintext)
            
            self.ciphertext_text.delete('1.0', 'end')
            self.ciphertext_text.insert('1.0', ciphertext.hex().upper())
            
        except Exception as e:
            messagebox.showerror("错误", f"加密失败: {e}")
    
    def decrypt_basic(self):
        """基础解密"""
        try:
            key = self.get_key_bytes(self.key_entry)
            if not key:
                return
            
            ciphertext_hex = self.ciphertext_text.get('1.0', 'end-1c').replace(' ', '')
            ciphertext = bytes.fromhex(ciphertext_hex)
            
            sm4 = SM4Basic(key)
            plaintext = sm4.decrypt_ecb(ciphertext)
            
            self.plaintext_text.delete('1.0', 'end')
            self.plaintext_text.insert('1.0', plaintext.decode('utf-8'))
            
        except Exception as e:
            messagebox.showerror("错误", f"解密失败: {e}")
    
    def clear_basic(self):
        """清除基础页面内容"""
        self.plaintext_text.delete('1.0', 'end')
        self.ciphertext_text.delete('1.0', 'end')
    
    def test_optimization(self):
        """测试优化实现"""
        try:
            key = self.get_key_bytes(self.opt_key_entry)
            if not key:
                return
            
            data = self.opt_data_text.get('1.0', 'end-1c').encode('utf-8')
            impl_type = self.impl_var.get()
            
            # 选择实现
            if impl_type == "basic":
                sm4 = SM4Basic(key)
            elif impl_type == "lookup":
                sm4 = SM4LookupTable(key)
            elif impl_type == "bitwise":
                sm4 = SM4Bitwise(key)
            elif impl_type == "parallel":
                sm4 = SM4Parallel(key)
            
            # 测试加密解密
            ciphertext = sm4.encrypt_ecb(data)
            decrypted = sm4.decrypt_ecb(ciphertext)
            
            result = f"实现类型: {impl_type}\n"
            result += f"原始数据: {data.decode('utf-8')}\n"
            result += f"密文 (hex): {ciphertext.hex().upper()}\n"
            result += f"解密结果: {decrypted.decode('utf-8')}\n"
            result += f"正确性: {'✓ 通过' if decrypted == data else '✗ 失败'}\n"
            
            self.opt_result_text.delete('1.0', 'end')
            self.opt_result_text.insert('1.0', result)
            
        except Exception as e:
            self.opt_result_text.delete('1.0', 'end')
            self.opt_result_text.insert('1.0', f"测试失败: {e}\n{traceback.format_exc()}")
    
    def benchmark_optimization(self):
        """性能测试优化实现"""
        try:
            key = self.get_key_bytes(self.opt_key_entry)
            if not key:
                return
            
            impl_type = self.impl_var.get()
            
            # 选择实现并运行基准测试
            if impl_type == "basic":
                sm4 = SM4Basic(key)
                result = "基础实现性能测试\n"
            elif impl_type == "lookup":
                sm4 = SM4LookupTable(key)
                result = "查找表优化性能测试\n"
                benchmark_result = sm4.benchmark_lookup_table()
                result += f"查找表时间: {benchmark_result['lookup_time']:.4f}s\n"
                result += f"基础实现时间: {benchmark_result['basic_time']:.4f}s\n"
                result += f"加速比: {benchmark_result['speedup']:.2f}x\n"
            elif impl_type == "parallel":
                sm4 = SM4Parallel(key)
                result = "并行优化性能测试\n"
                benchmark_result = sm4.benchmark_parallel()
                result += f"并行时间: {benchmark_result['parallel_time']:.4f}s\n"
                result += f"基础实现时间: {benchmark_result['basic_time']:.4f}s\n"
                result += f"加速比: {benchmark_result['speedup']:.2f}x\n"
            else:
                result = f"{impl_type} 实现暂无性能测试"
            
            self.opt_result_text.delete('1.0', 'end')
            self.opt_result_text.insert('1.0', result)
            
        except Exception as e:
            self.opt_result_text.delete('1.0', 'end')
            self.opt_result_text.insert('1.0', f"性能测试失败: {e}")
    
    def encrypt_mode(self):
        """加密模式测试"""
        try:
            key = self.get_key_bytes(self.mode_key_entry)
            if not key:
                return
            
            data = self.mode_data_text.get('1.0', 'end-1c').encode('utf-8')
            mode = self.mode_var.get()
            
            sm4_modes = SM4Modes(key)
            
            # 获取IV（如果需要）
            iv_hex = self.iv_entry.get().replace(' ', '')
            iv = None
            if iv_hex:
                if len(iv_hex) == 32:
                    iv = bytes.fromhex(iv_hex)
                else:
                    messagebox.showerror("错误", "IV必须是32位十六进制字符")
                    return
            
            # 根据模式加密
            if mode == "ecb":
                ciphertext = sm4_modes.encrypt_ecb(data)
                result = f"ECB模式加密\n密文: {ciphertext.hex().upper()}\n"
            elif mode == "cbc":
                ciphertext, used_iv = sm4_modes.encrypt_cbc(data, iv)
                result = f"CBC模式加密\nIV: {used_iv.hex().upper()}\n密文: {ciphertext.hex().upper()}\n"
                self.iv_entry.delete(0, 'end')
                self.iv_entry.insert(0, used_iv.hex().upper())
            elif mode == "ctr":
                ciphertext, counter = sm4_modes.encrypt_ctr(data, iv)
                result = f"CTR模式加密\n计数器: {counter.hex().upper()}\n密文: {ciphertext.hex().upper()}\n"
                self.iv_entry.delete(0, 'end')
                self.iv_entry.insert(0, counter.hex().upper())
            elif mode == "cfb":
                ciphertext, used_iv = sm4_modes.encrypt_cfb(data, iv)
                result = f"CFB模式加密\nIV: {used_iv.hex().upper()}\n密文: {ciphertext.hex().upper()}\n"
                self.iv_entry.delete(0, 'end')
                self.iv_entry.insert(0, used_iv.hex().upper())
            elif mode == "ofb":
                ciphertext, used_iv = sm4_modes.encrypt_ofb(data, iv)
                result = f"OFB模式加密\nIV: {used_iv.hex().upper()}\n密文: {ciphertext.hex().upper()}\n"
                self.iv_entry.delete(0, 'end')
                self.iv_entry.insert(0, used_iv.hex().upper())
            
            self.mode_result_text.delete('1.0', 'end')
            self.mode_result_text.insert('1.0', result)
            
        except Exception as e:
            messagebox.showerror("错误", f"加密失败: {e}")
    
    def decrypt_mode(self):
        """解密模式测试"""
        try:
            # 这里可以实现解密功能
            messagebox.showinfo("提示", "解密功能待实现")
        except Exception as e:
            messagebox.showerror("错误", f"解密失败: {e}")
    
    def compare_modes(self):
        """比较不同加密模式"""
        try:
            key = self.get_key_bytes(self.mode_key_entry)
            if not key:
                return
            
            data = self.mode_data_text.get('1.0', 'end-1c').encode('utf-8')
            sm4_modes = SM4Modes(key)
            
            result = f"加密模式比较\n原始数据: {data.decode('utf-8')}\n\n"
            
            # 测试所有模式
            ecb_cipher = sm4_modes.encrypt_ecb(data)
            result += f"ECB: {ecb_cipher.hex().upper()}\n"
            
            cbc_cipher, cbc_iv = sm4_modes.encrypt_cbc(data)
            result += f"CBC: {cbc_cipher.hex().upper()}\n"
            
            ctr_cipher, ctr_counter = sm4_modes.encrypt_ctr(data)
            result += f"CTR: {ctr_cipher.hex().upper()}\n"
            
            cfb_cipher, cfb_iv = sm4_modes.encrypt_cfb(data)
            result += f"CFB: {cfb_cipher.hex().upper()}\n"
            
            ofb_cipher, ofb_iv = sm4_modes.encrypt_ofb(data)
            result += f"OFB: {ofb_cipher.hex().upper()}\n"
            
            self.mode_result_text.delete('1.0', 'end')
            self.mode_result_text.insert('1.0', result)
            
        except Exception as e:
            messagebox.showerror("错误", f"模式比较失败: {e}")
    
    def run_benchmark(self):
        """运行性能测试"""
        try:
            data_size = int(self.size_entry.get())
            rounds = int(self.rounds_entry.get())
            
            result = f"性能测试结果 (数据大小: {data_size} 字节, 测试轮数: {rounds})\n"
            result += "=" * 50 + "\n"
            
            # 这里可以添加具体的性能测试代码
            result += "测试功能开发中...\n"
            
            self.benchmark_result_text.delete('1.0', 'end')
            self.benchmark_result_text.insert('1.0', result)
            
        except Exception as e:
            messagebox.showerror("错误", f"性能测试失败: {e}")
    
    def compare_all(self):
        """比较所有实现"""
        try:
            result = "SM4实现性能比较\n"
            result += "=" * 30 + "\n"
            result += "比较功能开发中...\n"
            
            self.benchmark_result_text.delete('1.0', 'end')
            self.benchmark_result_text.insert('1.0', result)
            
        except Exception as e:
            messagebox.showerror("错误", f"比较测试失败: {e}")


def main():
    """启动GUI程序"""
    root = tk.Tk()
    app = SM4GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
