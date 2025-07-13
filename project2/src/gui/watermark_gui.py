#!/usr/bin/env python3
"""
水印GUI界面
提供用户友好的图形界面进行水印操作
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
import sys

# 添加项目路径
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

try:
    from src.algorithms.lsb_watermark import LSBWatermark
    from src.algorithms.dct_watermark import DCTWatermark
    from src.evaluation.image_quality import ImageQuality
except ImportError:
    print("警告: 部分模块导入失败，功能可能受限")

class WatermarkGUI:
    """水印系统GUI主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("数字水印系统")
        self.root.geometry("800x600")
        
        # 初始化变量
        self.host_image = None
        self.watermark_image = None
        self.watermarked_image = None
        self.extracted_watermark = None
        
        # 初始化算法
        try:
            self.lsb = LSBWatermark(bit_plane=2)
            self.dct = DCTWatermark(block_size=8, alpha=0.1)
            self.quality_eval = ImageQuality()
        except:
            self.lsb = None
            self.dct = None
            self.quality_eval = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建标签页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # 嵌入标签页
        embed_frame = ttk.Frame(notebook)
        notebook.add(embed_frame, text="水印嵌入")
        self.setup_embed_tab(embed_frame)
        
        # 提取标签页
        extract_frame = ttk.Frame(notebook)
        notebook.add(extract_frame, text="水印提取")
        self.setup_extract_tab(extract_frame)
        
        # 攻击测试标签页
        attack_frame = ttk.Frame(notebook)
        notebook.add(attack_frame, text="攻击测试")
        self.setup_attack_tab(attack_frame)
        
        # 评估标签页
        eval_frame = ttk.Frame(notebook)
        notebook.add(eval_frame, text="质量评估")
        self.setup_eval_tab(eval_frame)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief='sunken')
        status_bar.pack(side='bottom', fill='x')
    
    def setup_embed_tab(self, parent):
        """设置嵌入标签页"""
        # 文件选择框架
        file_frame = ttk.LabelFrame(parent, text="文件选择")
        file_frame.pack(fill='x', padx=5, pady=5)
        
        # 宿主图像选择
        ttk.Label(file_frame, text="宿主图像:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.host_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.host_path_var, width=50).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(file_frame, text="浏览", command=self.select_host_image).grid(row=0, column=2, padx=5, pady=2)
        
        # 水印图像选择
        ttk.Label(file_frame, text="水印图像:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.watermark_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.watermark_path_var, width=50).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(file_frame, text="浏览", command=self.select_watermark_image).grid(row=1, column=2, padx=5, pady=2)
        
        # 参数设置框架
        param_frame = ttk.LabelFrame(parent, text="参数设置")
        param_frame.pack(fill='x', padx=5, pady=5)
        
        # 算法选择
        ttk.Label(param_frame, text="算法:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.algorithm_var = tk.StringVar(value="lsb")
        algorithm_combo = ttk.Combobox(param_frame, textvariable=self.algorithm_var, values=["lsb", "dct"], state="readonly")
        algorithm_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # 强度设置
        ttk.Label(param_frame, text="强度:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.strength_var = tk.DoubleVar(value=0.8)
        strength_scale = ttk.Scale(param_frame, from_=0.1, to=1.0, variable=self.strength_var, orient='horizontal')
        strength_scale.grid(row=0, column=3, padx=5, pady=2)
        ttk.Label(param_frame, textvariable=self.strength_var).grid(row=0, column=4, padx=5, pady=2)
        
        # 嵌入按钮
        embed_btn = ttk.Button(param_frame, text="嵌入水印", command=self.embed_watermark)
        embed_btn.grid(row=1, column=0, columnspan=5, pady=10)
        
        # 图像显示框架
        display_frame = ttk.LabelFrame(parent, text="图像预览")
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建图像显示区域
        self.embed_canvas = tk.Canvas(display_frame, bg='white')
        self.embed_canvas.pack(fill='both', expand=True)
    
    def setup_extract_tab(self, parent):
        """设置提取标签页"""
        # 文件选择
        file_frame = ttk.LabelFrame(parent, text="含水印图像")
        file_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(file_frame, text="图像路径:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.watermarked_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.watermarked_path_var, width=50).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(file_frame, text="浏览", command=self.select_watermarked_image).grid(row=0, column=2, padx=5, pady=2)
        
        # 参数设置
        param_frame = ttk.LabelFrame(parent, text="提取参数")
        param_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(param_frame, text="算法:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.extract_algorithm_var = tk.StringVar(value="lsb")
        extract_algo_combo = ttk.Combobox(param_frame, textvariable=self.extract_algorithm_var, values=["lsb", "dct"], state="readonly")
        extract_algo_combo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(param_frame, text="水印尺寸:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.wm_width_var = tk.IntVar(value=64)
        self.wm_height_var = tk.IntVar(value=64)
        ttk.Entry(param_frame, textvariable=self.wm_width_var, width=8).grid(row=0, column=3, padx=2, pady=2)
        ttk.Label(param_frame, text="×").grid(row=0, column=4, padx=2, pady=2)
        ttk.Entry(param_frame, textvariable=self.wm_height_var, width=8).grid(row=0, column=5, padx=2, pady=2)
        
        # 提取按钮
        extract_btn = ttk.Button(param_frame, text="提取水印", command=self.extract_watermark)
        extract_btn.grid(row=1, column=0, columnspan=6, pady=10)
        
        # 图像显示
        display_frame = ttk.LabelFrame(parent, text="提取结果")
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.extract_canvas = tk.Canvas(display_frame, bg='white')
        self.extract_canvas.pack(fill='both', expand=True)
    
    def setup_attack_tab(self, parent):
        """设置攻击测试标签页"""
        attack_frame = ttk.LabelFrame(parent, text="攻击类型")
        attack_frame.pack(fill='x', padx=5, pady=5)
        
        self.attack_var = tk.StringVar(value="gaussian_noise")
        attacks = [
            "gaussian_noise", "rotation", "scaling", "compression",
            "crop", "flip_horizontal", "blur"
        ]
        
        for i, attack in enumerate(attacks):
            ttk.Radiobutton(attack_frame, text=attack, variable=self.attack_var, value=attack).grid(
                row=i//3, column=i%3, sticky='w', padx=5, pady=2)
        
        # 攻击参数
        param_frame = ttk.LabelFrame(parent, text="攻击参数")
        param_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(param_frame, text="参数值:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.attack_param_var = tk.DoubleVar(value=0.01)
        ttk.Entry(param_frame, textvariable=self.attack_param_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        # 攻击按钮
        attack_btn = ttk.Button(param_frame, text="执行攻击", command=self.apply_attack)
        attack_btn.grid(row=0, column=2, padx=10, pady=2)
        
        # 结果显示
        result_frame = ttk.LabelFrame(parent, text="攻击结果")
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.attack_canvas = tk.Canvas(result_frame, bg='white')
        self.attack_canvas.pack(fill='both', expand=True)
    
    def setup_eval_tab(self, parent):
        """设置评估标签页"""
        eval_frame = ttk.LabelFrame(parent, text="质量评估")
        eval_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 评估按钮
        eval_btn = ttk.Button(eval_frame, text="计算质量指标", command=self.calculate_metrics)
        eval_btn.pack(pady=10)
        
        # 结果显示
        self.eval_text = tk.Text(eval_frame, height=20, width=60)
        self.eval_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(eval_frame, orient="vertical", command=self.eval_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.eval_text.configure(yscrollcommand=scrollbar.set)
    
    def select_host_image(self):
        """选择宿主图像"""
        filename = filedialog.askopenfilename(
            title="选择宿主图像",
            filetypes=[("图像文件", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if filename:
            self.host_path_var.set(filename)
            self.load_host_image(filename)
    
    def select_watermark_image(self):
        """选择水印图像"""
        filename = filedialog.askopenfilename(
            title="选择水印图像",
            filetypes=[("图像文件", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if filename:
            self.watermark_path_var.set(filename)
            self.load_watermark_image(filename)
    
    def select_watermarked_image(self):
        """选择含水印图像"""
        filename = filedialog.askopenfilename(
            title="选择含水印图像",
            filetypes=[("图像文件", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if filename:
            self.watermarked_path_var.set(filename)
            self.load_watermarked_image(filename)
    
    def load_host_image(self, filename):
        """加载宿主图像"""
        try:
            self.host_image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
            self.status_var.set(f"已加载宿主图像: {filename}")
            self.update_embed_display()
        except Exception as e:
            messagebox.showerror("错误", f"加载宿主图像失败: {e}")
    
    def load_watermark_image(self, filename):
        """加载水印图像"""
        try:
            self.watermark_image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
            self.status_var.set(f"已加载水印图像: {filename}")
            self.update_embed_display()
        except Exception as e:
            messagebox.showerror("错误", f"加载水印图像失败: {e}")
    
    def load_watermarked_image(self, filename):
        """加载含水印图像"""
        try:
            self.watermarked_image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
            self.status_var.set(f"已加载含水印图像: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"加载含水印图像失败: {e}")
    
    def update_embed_display(self):
        """更新嵌入标签页的图像显示"""
        self.embed_canvas.delete("all")
        
        if self.host_image is not None:
            # 显示宿主图像
            host_display = cv2.resize(self.host_image, (200, 200))
            host_pil = Image.fromarray(host_display)
            host_tk = ImageTk.PhotoImage(host_pil)
            self.embed_canvas.create_image(50, 50, anchor='nw', image=host_tk)
            self.embed_canvas.create_text(150, 260, text="宿主图像")
            self.embed_canvas.host_tk = host_tk  # 保持引用
        
        if self.watermark_image is not None:
            # 显示水印图像
            wm_display = cv2.resize(self.watermark_image, (100, 100))
            wm_pil = Image.fromarray(wm_display)
            wm_tk = ImageTk.PhotoImage(wm_pil)
            self.embed_canvas.create_image(300, 75, anchor='nw', image=wm_tk)
            self.embed_canvas.create_text(350, 180, text="水印图像")
            self.embed_canvas.wm_tk = wm_tk  # 保持引用
    
    def embed_watermark(self):
        """嵌入水印"""
        if self.host_image is None or self.watermark_image is None:
            messagebox.showerror("错误", "请先选择宿主图像和水印图像")
            return
        
        if self.lsb is None:
            messagebox.showerror("错误", "水印算法模块未加载")
            return
        
        try:
            algorithm = self.algorithm_var.get()
            strength = self.strength_var.get()
            
            self.status_var.set("正在嵌入水印...")
            
            if algorithm == "lsb":
                self.watermarked_image = self.lsb.embed(self.host_image, self.watermark_image, strength)
            elif algorithm == "dct" and self.dct is not None:
                self.watermarked_image = self.dct.embed(self.host_image, self.watermark_image, strength)
                self.watermarked_image = self.watermarked_image.astype(np.uint8)
            else:
                messagebox.showerror("错误", "不支持的算法")
                return
            
            # 保存结果
            output_path = filedialog.asksaveasfilename(
                title="保存含水印图像",
                defaultextension=".png",
                filetypes=[("PNG文件", "*.png"), ("JPEG文件", "*.jpg")]
            )
            
            if output_path:
                cv2.imwrite(output_path, self.watermarked_image)
                self.status_var.set(f"水印嵌入完成，已保存至: {output_path}")
                messagebox.showinfo("成功", "水印嵌入完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"水印嵌入失败: {e}")
            self.status_var.set("就绪")
    
    def extract_watermark(self):
        """提取水印"""
        if self.watermarked_image is None:
            messagebox.showerror("错误", "请先选择含水印图像")
            return
        
        if self.lsb is None:
            messagebox.showerror("错误", "水印算法模块未加载")
            return
        
        try:
            algorithm = self.extract_algorithm_var.get()
            wm_size = (self.wm_height_var.get(), self.wm_width_var.get())
            
            self.status_var.set("正在提取水印...")
            
            if algorithm == "lsb":
                self.extracted_watermark = self.lsb.extract(self.watermarked_image, wm_size)
            elif algorithm == "dct" and self.dct is not None:
                self.extracted_watermark = self.dct.extract(self.watermarked_image)
            else:
                messagebox.showerror("错误", "不支持的算法")
                return
            
            # 显示提取结果
            self.update_extract_display()
            
            # 保存结果
            output_path = filedialog.asksaveasfilename(
                title="保存提取的水印",
                defaultextension=".png",
                filetypes=[("PNG文件", "*.png")]
            )
            
            if output_path:
                cv2.imwrite(output_path, self.extracted_watermark)
                self.status_var.set(f"水印提取完成，已保存至: {output_path}")
                messagebox.showinfo("成功", "水印提取完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"水印提取失败: {e}")
            self.status_var.set("就绪")
    
    def update_extract_display(self):
        """更新提取结果显示"""
        self.extract_canvas.delete("all")
        
        if self.extracted_watermark is not None:
            # 显示提取的水印
            extracted_display = cv2.resize(self.extracted_watermark, (200, 200))
            extracted_pil = Image.fromarray(extracted_display)
            extracted_tk = ImageTk.PhotoImage(extracted_pil)
            self.extract_canvas.create_image(50, 50, anchor='nw', image=extracted_tk)
            self.extract_canvas.create_text(150, 260, text="提取的水印")
            self.extract_canvas.extracted_tk = extracted_tk  # 保持引用
    
    def apply_attack(self):
        """应用攻击"""
        if self.watermarked_image is None:
            messagebox.showerror("错误", "请先生成含水印图像")
            return
        
        try:
            attack_type = self.attack_var.get()
            param = self.attack_param_var.get()
            
            self.status_var.set(f"正在应用{attack_type}攻击...")
            
            # 简单攻击实现
            attacked_image = self.watermarked_image.copy()
            
            if attack_type == "gaussian_noise":
                noise = np.random.normal(0, param * 255, attacked_image.shape)
                attacked_image = np.clip(attacked_image.astype(float) + noise, 0, 255).astype(np.uint8)
            elif attack_type == "rotation":
                h, w = attacked_image.shape
                center = (w//2, h//2)
                matrix = cv2.getRotationMatrix2D(center, param, 1.0)
                attacked_image = cv2.warpAffine(attacked_image, matrix, (w, h))
            elif attack_type == "scaling":
                h, w = attacked_image.shape
                new_size = (int(w * param), int(h * param))
                attacked_image = cv2.resize(attacked_image, new_size)
                attacked_image = cv2.resize(attacked_image, (w, h))
            
            # 保存攻击结果
            output_path = filedialog.asksaveasfilename(
                title="保存攻击后图像",
                defaultextension=".png",
                filetypes=[("PNG文件", "*.png")]
            )
            
            if output_path:
                cv2.imwrite(output_path, attacked_image)
                self.status_var.set(f"{attack_type}攻击完成，已保存至: {output_path}")
                messagebox.showinfo("成功", "攻击测试完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"攻击测试失败: {e}")
            self.status_var.set("就绪")
    
    def calculate_metrics(self):
        """计算质量指标"""
        if self.host_image is None or self.watermarked_image is None:
            messagebox.showerror("错误", "请先加载原始图像和含水印图像")
            return
        
        try:
            self.status_var.set("正在计算质量指标...")
            
            # 计算基本指标
            mse = np.mean((self.host_image.astype(float) - self.watermarked_image.astype(float)) ** 2)
            psnr = 10 * np.log10(255**2 / mse) if mse > 0 else float('inf')
            
            # 显示结果
            self.eval_text.delete(1.0, tk.END)
            self.eval_text.insert(tk.END, "=== 图像质量评估结果 ===\\n\\n")
            self.eval_text.insert(tk.END, f"均方误差 (MSE): {mse:.4f}\\n")
            self.eval_text.insert(tk.END, f"峰值信噪比 (PSNR): {psnr:.2f} dB\\n")
            
            if self.quality_eval:
                metrics = self.quality_eval.calculate_metrics(self.host_image, self.watermarked_image)
                self.eval_text.insert(tk.END, f"结构相似性 (SSIM): {metrics.get('ssim', 'N/A'):.4f}\\n")
            
            self.eval_text.insert(tk.END, "\\n=== 评估标准 ===\\n")
            self.eval_text.insert(tk.END, "PSNR > 40dB: 优秀\\n")
            self.eval_text.insert(tk.END, "PSNR 30-40dB: 良好\\n")
            self.eval_text.insert(tk.END, "PSNR < 30dB: 可察觉失真\\n")
            
            self.status_var.set("质量指标计算完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"计算质量指标失败: {e}")
            self.status_var.set("就绪")

def main():
    """主函数"""
    root = tk.Tk()
    app = WatermarkGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
