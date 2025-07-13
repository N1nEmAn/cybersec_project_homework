"""
数字水印系统图形用户界面
基于tkinter的GUI应用程序
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import os
import sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageTk
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.algorithms import AlgorithmRegistry
from src.attacks import AttackEngine
from src.evaluation import EvaluationEngine
from src.utils.logger import setup_logger

class WatermarkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("数字水印系统 GUI")
        self.root.geometry("1200x800")
        
        # 初始化组件
        self.algorithm_registry = AlgorithmRegistry()
        self.attack_engine = AttackEngine()
        self.evaluation_engine = EvaluationEngine()
        
        # 图像变量
        self.host_image = None
        self.watermark_image = None
        self.watermarked_image = None
        self.attacked_image = None
        self.extracted_watermark = None
        
        # 文件路径
        self.host_path = tk.StringVar()
        self.watermark_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        # 算法参数
        self.algorithm_var = tk.StringVar(value="lsb")
        self.strength_var = tk.DoubleVar(value=0.1)
        self.key_var = tk.StringVar(value="secret_key")
        
        # 攻击参数
        self.attack_type_var = tk.StringVar()
        self.attack_param_var = tk.DoubleVar(value=10.0)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建笔记本控件（选项卡）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 水印嵌入选项卡
        self.embed_frame = ttk.Frame(notebook)
        notebook.add(self.embed_frame, text="水印嵌入")
        self.setup_embed_tab()
        
        # 水印提取选项卡
        self.extract_frame = ttk.Frame(notebook)
        notebook.add(self.extract_frame, text="水印提取")
        self.setup_extract_tab()
        
        # 攻击测试选项卡
        self.attack_frame = ttk.Frame(notebook)
        notebook.add(self.attack_frame, text="攻击测试")
        self.setup_attack_tab()
        
        # 评估分析选项卡
        self.eval_frame = ttk.Frame(notebook)
        notebook.add(self.eval_frame, text="评估分析")
        self.setup_evaluation_tab()
        
        # 批量测试选项卡
        self.batch_frame = ttk.Frame(notebook)
        notebook.add(self.batch_frame, text="批量测试")
        self.setup_batch_tab()
        
    def setup_embed_tab(self):
        """设置水印嵌入选项卡"""
        # 左侧控制面板
        control_frame = ttk.LabelFrame(self.embed_frame, text="控制面板")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 文件选择
        ttk.Label(control_frame, text="载体图像:").pack(anchor=tk.W, pady=2)
        ttk.Entry(control_frame, textvariable=self.host_path, width=40).pack(pady=2)
        ttk.Button(control_frame, text="选择文件", 
                  command=self.select_host_image).pack(pady=2)
        
        ttk.Label(control_frame, text="水印图像:").pack(anchor=tk.W, pady=2)
        ttk.Entry(control_frame, textvariable=self.watermark_path, width=40).pack(pady=2)
        ttk.Button(control_frame, text="选择文件", 
                  command=self.select_watermark_image).pack(pady=2)
        
        # 算法选择
        ttk.Label(control_frame, text="水印算法:").pack(anchor=tk.W, pady=2)
        algorithm_combo = ttk.Combobox(control_frame, textvariable=self.algorithm_var,
                                     values=["lsb", "dct"], state="readonly")
        algorithm_combo.pack(pady=2)
        
        # 参数设置
        ttk.Label(control_frame, text="水印强度:").pack(anchor=tk.W, pady=2)
        ttk.Scale(control_frame, from_=0.01, to=1.0, variable=self.strength_var,
                 orient=tk.HORIZONTAL).pack(fill=tk.X, pady=2)
        ttk.Label(control_frame, textvariable=self.strength_var).pack(pady=2)
        
        ttk.Label(control_frame, text="密钥:").pack(anchor=tk.W, pady=2)
        ttk.Entry(control_frame, textvariable=self.key_var, width=40).pack(pady=2)
        
        # 操作按钮
        ttk.Button(control_frame, text="嵌入水印", 
                  command=self.embed_watermark).pack(pady=10)
        ttk.Button(control_frame, text="保存结果", 
                  command=self.save_watermarked_image).pack(pady=2)
        
        # 右侧图像显示
        image_frame = ttk.Frame(self.embed_frame)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建图像显示区域
        self.embed_canvas = tk.Canvas(image_frame, bg='white')
        self.embed_canvas.pack(fill=tk.BOTH, expand=True)
        
    def setup_extract_tab(self):
        """设置水印提取选项卡"""
        # 左侧控制面板
        control_frame = ttk.LabelFrame(self.extract_frame, text="控制面板")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 文件选择
        ttk.Label(control_frame, text="含水印图像:").pack(anchor=tk.W, pady=2)
        self.watermarked_path = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.watermarked_path, width=40).pack(pady=2)
        ttk.Button(control_frame, text="选择文件", 
                  command=self.select_watermarked_image).pack(pady=2)
        
        # 水印尺寸
        ttk.Label(control_frame, text="水印尺寸:").pack(anchor=tk.W, pady=2)
        size_frame = ttk.Frame(control_frame)
        size_frame.pack(pady=2)
        self.wm_width = tk.IntVar(value=64)
        self.wm_height = tk.IntVar(value=64)
        ttk.Entry(size_frame, textvariable=self.wm_width, width=10).pack(side=tk.LEFT)
        ttk.Label(size_frame, text=" × ").pack(side=tk.LEFT)
        ttk.Entry(size_frame, textvariable=self.wm_height, width=10).pack(side=tk.LEFT)
        
        # 操作按钮
        ttk.Button(control_frame, text="提取水印", 
                  command=self.extract_watermark).pack(pady=10)
        ttk.Button(control_frame, text="保存水印", 
                  command=self.save_extracted_watermark).pack(pady=2)
        
        # 右侧图像显示
        image_frame = ttk.Frame(self.extract_frame)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.extract_canvas = tk.Canvas(image_frame, bg='white')
        self.extract_canvas.pack(fill=tk.BOTH, expand=True)
        
    def setup_attack_tab(self):
        """设置攻击测试选项卡"""
        # 左侧控制面板
        control_frame = ttk.LabelFrame(self.attack_frame, text="攻击控制")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 攻击类型选择
        ttk.Label(control_frame, text="攻击类型:").pack(anchor=tk.W, pady=2)
        attack_types = [
            "gaussian_noise", "salt_pepper_noise", "uniform_noise",
            "gaussian_blur", "median_blur", "motion_blur",
            "jpeg_compression", "brightness_adjust", "contrast_adjust",
            "rotate", "scale", "translate", "crop",
            "flip_horizontal", "flip_vertical", "shear"
        ]
        attack_combo = ttk.Combobox(control_frame, textvariable=self.attack_type_var,
                                   values=attack_types, state="readonly")
        attack_combo.pack(pady=2, fill=tk.X)
        
        # 攻击参数
        ttk.Label(control_frame, text="攻击参数:").pack(anchor=tk.W, pady=2)
        ttk.Scale(control_frame, from_=0.1, to=50.0, variable=self.attack_param_var,
                 orient=tk.HORIZONTAL).pack(fill=tk.X, pady=2)
        ttk.Label(control_frame, textvariable=self.attack_param_var).pack(pady=2)
        
        # 操作按钮
        ttk.Button(control_frame, text="执行攻击", 
                  command=self.apply_attack).pack(pady=10)
        ttk.Button(control_frame, text="保存结果", 
                  command=self.save_attacked_image).pack(pady=2)
        
        # 右侧图像显示
        image_frame = ttk.Frame(self.attack_frame)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.attack_canvas = tk.Canvas(image_frame, bg='white')
        self.attack_canvas.pack(fill=tk.BOTH, expand=True)
        
    def setup_evaluation_tab(self):
        """设置评估分析选项卡"""
        # 左侧控制面板
        control_frame = ttk.LabelFrame(self.eval_frame, text="评估控制")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Button(control_frame, text="综合评估", 
                  command=self.comprehensive_evaluation).pack(pady=10)
        ttk.Button(control_frame, text="导出报告", 
                  command=self.export_evaluation_report).pack(pady=2)
        
        # 右侧结果显示
        result_frame = ttk.Frame(self.eval_frame)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.eval_text = ScrolledText(result_frame, height=30, width=60)
        self.eval_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_batch_tab(self):
        """设置批量测试选项卡"""
        # 控制面板
        control_frame = ttk.LabelFrame(self.batch_frame, text="批量测试控制")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 测试配置
        ttk.Label(control_frame, text="测试算法:").pack(anchor=tk.W, pady=2)
        self.batch_algorithms = tk.StringVar(value="lsb,dct")
        ttk.Entry(control_frame, textvariable=self.batch_algorithms, width=40).pack(pady=2)
        
        ttk.Label(control_frame, text="测试图像目录:").pack(anchor=tk.W, pady=2)
        self.test_image_dir = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.test_image_dir, width=40).pack(pady=2)
        ttk.Button(control_frame, text="选择目录", 
                  command=self.select_test_directory).pack(pady=2)
        
        ttk.Button(control_frame, text="开始批量测试", 
                  command=self.start_batch_test).pack(pady=10)
        
        # 进度显示
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(control_frame, variable=self.progress_var, 
                       maximum=100).pack(fill=tk.X, pady=5)
        
        # 结果显示
        result_frame = ttk.Frame(self.batch_frame)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.batch_text = ScrolledText(result_frame, height=30, width=60)
        self.batch_text.pack(fill=tk.BOTH, expand=True)
        
    def select_host_image(self):
        """选择载体图像"""
        filename = filedialog.askopenfilename(
            title="选择载体图像",
            filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("所有文件", "*.*")]
        )
        if filename:
            self.host_path.set(filename)
            self.load_host_image(filename)
            
    def select_watermark_image(self):
        """选择水印图像"""
        filename = filedialog.askopenfilename(
            title="选择水印图像",
            filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("所有文件", "*.*")]
        )
        if filename:
            self.watermark_path.set(filename)
            self.load_watermark_image(filename)
            
    def select_watermarked_image(self):
        """选择含水印图像"""
        filename = filedialog.askopenfilename(
            title="选择含水印图像",
            filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("所有文件", "*.*")]
        )
        if filename:
            self.watermarked_path.set(filename)
            self.load_watermarked_image(filename)
            
    def select_test_directory(self):
        """选择测试图像目录"""
        dirname = filedialog.askdirectory(title="选择测试图像目录")
        if dirname:
            self.test_image_dir.set(dirname)
            
    def load_host_image(self, filename):
        """加载载体图像"""
        try:
            self.host_image = cv2.imread(filename)
            if self.host_image is None:
                raise ValueError("无法加载图像")
            self.display_image(self.host_image, self.embed_canvas, "载体图像")
        except Exception as e:
            messagebox.showerror("错误", f"加载载体图像失败: {e}")
            
    def load_watermark_image(self, filename):
        """加载水印图像"""
        try:
            self.watermark_image = cv2.imread(filename)
            if self.watermark_image is None:
                raise ValueError("无法加载图像")
            self.display_image(self.watermark_image, self.embed_canvas, "水印图像", offset=(300, 0))
        except Exception as e:
            messagebox.showerror("错误", f"加载水印图像失败: {e}")
            
    def load_watermarked_image(self, filename):
        """加载含水印图像"""
        try:
            self.watermarked_image = cv2.imread(filename)
            if self.watermarked_image is None:
                raise ValueError("无法加载图像")
            self.display_image(self.watermarked_image, self.extract_canvas, "含水印图像")
        except Exception as e:
            messagebox.showerror("错误", f"加载含水印图像失败: {e}")
            
    def display_image(self, image, canvas, title, offset=(0, 0)):
        """在画布上显示图像"""
        try:
            # 转换颜色空间
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
                
            # 调整图像尺寸
            height, width = image_rgb.shape[:2]
            max_size = 250
            if height > max_size or width > max_size:
                scale = min(max_size/height, max_size/width)
                new_height, new_width = int(height*scale), int(width*scale)
                image_rgb = cv2.resize(image_rgb, (new_width, new_height))
                
            # 转换为PIL图像
            pil_image = Image.fromarray(image_rgb)
            photo = ImageTk.PhotoImage(pil_image)
            
            # 在画布上显示
            canvas.delete("all")
            x, y = offset
            canvas.create_image(10 + x, 10 + y, anchor=tk.NW, image=photo)
            canvas.create_text(10 + x, pil_image.height + 20 + y, anchor=tk.NW, text=title)
            
            # 保持引用
            canvas.image = photo
            
        except Exception as e:
            messagebox.showerror("错误", f"显示图像失败: {e}")
            
    def embed_watermark(self):
        """嵌入水印"""
        if self.host_image is None or self.watermark_image is None:
            messagebox.showerror("错误", "请先选择载体图像和水印图像")
            return
            
        try:
            # 获取算法
            algorithm = self.algorithm_registry.get_algorithm(self.algorithm_var.get())
            
            # 嵌入水印
            if self.algorithm_var.get() == 'lsb':
                self.watermarked_image = algorithm.embed(
                    self.host_image, self.watermark_image, 
                    strength=self.strength_var.get()
                )
            else:
                self.watermarked_image = algorithm.embed(
                    self.host_image, self.watermark_image, 
                    strength=self.strength_var.get(),
                    key=self.key_var.get()
                )
                
            # 显示结果
            self.display_image(self.watermarked_image, self.embed_canvas, "含水印图像", offset=(600, 0))
            messagebox.showinfo("成功", "水印嵌入完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"水印嵌入失败: {e}")
            
    def extract_watermark(self):
        """提取水印"""
        if self.watermarked_image is None:
            messagebox.showerror("错误", "请先选择含水印图像")
            return
            
        try:
            # 获取算法
            algorithm = self.algorithm_registry.get_algorithm(self.algorithm_var.get())
            
            # 提取水印
            watermark_size = (self.wm_width.get(), self.wm_height.get())
            if self.algorithm_var.get() == 'lsb':
                self.extracted_watermark = algorithm.extract(
                    self.watermarked_image, watermark_size=watermark_size
                )
            else:
                self.extracted_watermark = algorithm.extract(
                    self.watermarked_image, watermark_size=watermark_size,
                    key=self.key_var.get()
                )
                
            # 显示结果
            self.display_image(self.extracted_watermark, self.extract_canvas, "提取水印", offset=(300, 0))
            messagebox.showinfo("成功", "水印提取完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"水印提取失败: {e}")
            
    def apply_attack(self):
        """执行攻击"""
        if self.watermarked_image is None:
            messagebox.showerror("错误", "请先嵌入水印")
            return
            
        try:
            attack_type = self.attack_type_var.get()
            param_value = self.attack_param_var.get()
            
            # 根据攻击类型设置参数
            if attack_type in ["gaussian_noise", "salt_pepper_noise", "uniform_noise"]:
                params = {"std": param_value}
            elif attack_type in ["gaussian_blur", "motion_blur"]:
                params = {"sigma": param_value}
            elif attack_type == "median_blur":
                params = {"kernel_size": int(param_value)}
            elif attack_type == "jpeg_compression":
                params = {"quality": int(param_value)}
            elif attack_type in ["brightness_adjust", "contrast_adjust"]:
                params = {"factor": param_value}
            elif attack_type == "rotate":
                params = {"angle": param_value}
            elif attack_type == "scale":
                params = {"scale_factor": param_value}
            elif attack_type == "crop":
                params = {"crop_ratio": param_value / 100.0}
            else:
                params = {}
                
            # 执行攻击
            self.attacked_image = self.attack_engine.apply_attack_by_name(
                self.watermarked_image, attack_type, **params
            )
            
            # 显示结果
            self.display_image(self.attacked_image, self.attack_canvas, f"攻击后图像 ({attack_type})")
            messagebox.showinfo("成功", f"{attack_type} 攻击执行完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"攻击执行失败: {e}")
            
    def comprehensive_evaluation(self):
        """综合评估"""
        if not all([self.host_image is not None, self.watermarked_image is not None,
                   self.watermark_image is not None, self.extracted_watermark is not None]):
            messagebox.showerror("错误", "请先完成水印嵌入和提取")
            return
            
        try:
            # 准备评估数据
            original_wm = cv2.cvtColor(self.watermark_image, cv2.COLOR_BGR2GRAY)
            extracted_wm = cv2.cvtColor(self.extracted_watermark, cv2.COLOR_BGR2GRAY) if len(self.extracted_watermark.shape) == 3 else self.extracted_watermark
            
            # 执行评估
            results = self.evaluation_engine.comprehensive_evaluation(
                self.host_image, self.watermarked_image,
                original_wm, extracted_wm
            )
            
            # 显示结果
            self.display_evaluation_results(results)
            
        except Exception as e:
            messagebox.showerror("错误", f"评估失败: {e}")
            
    def display_evaluation_results(self, results):
        """显示评估结果"""
        self.eval_text.delete(1.0, tk.END)
        
        text = "=== 综合评估结果 ===\n\n"
        
        text += "图像质量指标:\n"
        for metric, value in results['image_quality'].items():
            text += f"  {metric.upper()}: {value:.4f}\n"
        text += f"  整体评估: {results['overall_assessment']['image_quality']}\n\n"
        
        text += "水印鲁棒性指标:\n"
        for metric, value in results['watermark_robustness'].items():
            text += f"  {metric.upper()}: {value:.4f}\n"
        text += f"  整体评估: {results['overall_assessment']['watermark_quality']}\n\n"
        
        self.eval_text.insert(tk.END, text)
        
    def export_evaluation_report(self):
        """导出评估报告"""
        filename = filedialog.asksaveasfilename(
            title="保存评估报告",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                content = self.eval_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"报告已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存报告失败: {e}")
                
    def save_watermarked_image(self):
        """保存含水印图像"""
        if self.watermarked_image is None:
            messagebox.showerror("错误", "没有可保存的含水印图像")
            return
            
        filename = filedialog.asksaveasfilename(
            title="保存含水印图像",
            defaultextension=".png",
            filetypes=[("PNG文件", "*.png"), ("JPEG文件", "*.jpg"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                cv2.imwrite(filename, self.watermarked_image)
                messagebox.showinfo("成功", f"图像已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存图像失败: {e}")
                
    def save_extracted_watermark(self):
        """保存提取的水印"""
        if self.extracted_watermark is None:
            messagebox.showerror("错误", "没有可保存的提取水印")
            return
            
        filename = filedialog.asksaveasfilename(
            title="保存提取水印",
            defaultextension=".png",
            filetypes=[("PNG文件", "*.png"), ("JPEG文件", "*.jpg"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                cv2.imwrite(filename, self.extracted_watermark)
                messagebox.showinfo("成功", f"水印已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存水印失败: {e}")
                
    def save_attacked_image(self):
        """保存攻击后图像"""
        if self.attacked_image is None:
            messagebox.showerror("错误", "没有可保存的攻击后图像")
            return
            
        filename = filedialog.asksaveasfilename(
            title="保存攻击后图像",
            defaultextension=".png",
            filetypes=[("PNG文件", "*.png"), ("JPEG文件", "*.jpg"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                cv2.imwrite(filename, self.attacked_image)
                messagebox.showinfo("成功", f"图像已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存图像失败: {e}")
                
    def start_batch_test(self):
        """开始批量测试"""
        if not self.test_image_dir.get():
            messagebox.showerror("错误", "请选择测试图像目录")
            return
            
        # 在新线程中执行批量测试
        thread = threading.Thread(target=self.run_batch_test)
        thread.daemon = True
        thread.start()
        
    def run_batch_test(self):
        """运行批量测试"""
        try:
            self.batch_text.delete(1.0, tk.END)
            self.batch_text.insert(tk.END, "开始批量测试...\n")
            
            # 这里可以调用robustness_test.py的功能
            # 为简化，这里只做基本的示例
            algorithms = self.batch_algorithms.get().split(',')
            test_dir = self.test_image_dir.get()
            
            for i, algorithm in enumerate(algorithms):
                progress = (i + 1) / len(algorithms) * 100
                self.progress_var.set(progress)
                
                self.batch_text.insert(tk.END, f"测试算法: {algorithm}\n")
                self.batch_text.see(tk.END)
                self.root.update()
                
            self.batch_text.insert(tk.END, "批量测试完成!\n")
            
        except Exception as e:
            self.batch_text.insert(tk.END, f"批量测试失败: {e}\n")

def main():
    """主函数"""
    root = tk.Tk()
    app = WatermarkGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
