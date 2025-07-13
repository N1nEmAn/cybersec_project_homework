# 数字水印系统使用指南

## 快速开始

### 安装和配置

1. **克隆项目**
   ```bash
   git clone https://github.com/N1nEmAn/cybersec_project_homework.git
   cd cybersec_project_homework/project2
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **验证安装**
   ```bash
   python basic_demo.py
   ```

## 命令行工具详细使用

### watermark_cli.py 完整参数说明

#### 基本语法
```bash
python watermark_cli.py <command> [options]
```

#### 可用命令

##### 1. embed - 水印嵌入
```bash
python watermark_cli.py embed \\
    --input <输入图像路径> \\
    --watermark <水印图像路径> \\
    --output <输出图像路径> \\
    --algorithm <算法类型> \\
    [可选参数]
```

**参数说明:**
- `--input, -i`: 输入的宿主图像路径
- `--watermark, -w`: 水印图像路径
- `--output, -o`: 输出的含水印图像路径
- `--algorithm, -a`: 算法类型 (`lsb` | `dct`)
- `--strength, -s`: 嵌入强度 (0.1-1.0, 默认0.5)
- `--bit-plane`: LSB算法的位平面 (0-7, 默认0)
- `--alpha`: DCT算法的alpha参数 (0.01-0.5, 默认0.1)
- `--quality, -q`: 输出图像质量 (1-100, 默认95)

**示例:**
```bash
# LSB算法嵌入
python watermark_cli.py embed \\
    -i data/input/host.png \\
    -w data/watermarks/watermark.png \\
    -o demo/watermarked_lsb.png \\
    -a lsb -s 0.8

# DCT算法嵌入
python watermark_cli.py embed \\
    -i data/input/host.png \\
    -w data/watermarks/watermark.png \\
    -o demo/watermarked_dct.png \\
    -a dct --alpha 0.1
```

##### 2. extract - 水印提取
```bash
python watermark_cli.py extract \\
    --input <含水印图像路径> \\
    --output <提取的水印保存路径> \\
    --algorithm <算法类型> \\
    [可选参数]
```

**参数说明:**
- `--input, -i`: 含水印的图像路径
- `--output, -o`: 提取水印的保存路径
- `--algorithm, -a`: 提取算法类型
- `--size`: 水印尺寸 (格式: 宽 高)
- `--original`: 原始图像路径 (DCT非盲提取需要)

**示例:**
```bash
# LSB提取 (盲提取)
python watermark_cli.py extract \\
    -i demo/watermarked_lsb.png \\
    -o demo/extracted_watermark.png \\
    -a lsb --size 64 64

# DCT提取 (非盲提取)
python watermark_cli.py extract \\
    -i demo/watermarked_dct.png \\
    -o demo/extracted_watermark_dct.png \\
    -a dct --original data/input/host.png
```

##### 3. attack - 攻击测试
```bash
python watermark_cli.py attack \\
    --input <图像路径> \\
    --output <攻击后图像路径> \\
    --attack <攻击类型> \\
    [攻击参数]
```

**攻击类型:**

| 攻击类型 | 参数 | 示例 |
|----------|------|------|
| `gaussian_noise` | 噪声方差 | `--params 0.01` |
| `rotation` | 角度(度) | `--params 15` |
| `scaling` | 缩放因子 | `--params 0.8` |
| `compression` | JPEG质量 | `--params 70` |
| `cropping` | 裁剪比例 | `--params 0.1` |
| `blur` | 模糊半径 | `--params 2.0` |

**示例:**
```bash
# 高斯噪声攻击
python watermark_cli.py attack \\
    -i demo/watermarked_lsb.png \\
    -o demo/attacked_noise.png \\
    --attack gaussian_noise --params 0.01

# 旋转攻击
python watermark_cli.py attack \\
    -i demo/watermarked_lsb.png \\
    -o demo/attacked_rotation.png \\
    --attack rotation --params 15

# JPEG压缩攻击
python watermark_cli.py attack \\
    -i demo/watermarked_lsb.png \\
    -o demo/attacked_compression.png \\
    --attack compression --params 70
```

##### 4. evaluate - 质量评估
```bash
python watermark_cli.py evaluate \\
    --original <原始图像> \\
    --watermarked <含水印图像> \\
    [可选参数]
```

**参数说明:**
- `--original`: 原始宿主图像
- `--watermarked`: 含水印图像
- `--original-watermark`: 原始水印图像
- `--extracted-watermark`: 提取的水印图像
- `--metrics`: 评估指标 (`psnr,ssim,mse,ber,nc`)
- `--output`: 评估报告保存路径

**示例:**
```bash
python watermark_cli.py evaluate \\
    --original data/input/host.png \\
    --watermarked demo/watermarked_lsb.png \\
    --original-watermark data/watermarks/watermark.png \\
    --extracted-watermark demo/extracted_watermark.png \\
    --metrics psnr,ssim,ber,nc \\
    --output demo/evaluation_report.json
```

##### 5. batch - 批量处理
```bash
python watermark_cli.py batch \\
    --input-dir <输入目录> \\
    --watermark <水印图像> \\
    --output-dir <输出目录> \\
    --algorithm <算法类型>
```

**示例:**
```bash
# 批量嵌入水印
python watermark_cli.py batch \\
    --input-dir data/input/ \\
    --watermark data/watermarks/watermark.png \\
    --output-dir results/batch_watermarked/ \\
    --algorithm lsb
```

## Python API 详细使用

### LSB算法API

#### 基本使用
```python
from src.algorithms.lsb_watermark import LSBWatermark
import cv2

# 初始化算法
lsb = LSBWatermark(bit_plane=0)

# 加载图像
host = cv2.imread('data/input/host.png', cv2.IMREAD_GRAYSCALE)
watermark = cv2.imread('data/watermarks/watermark.png', cv2.IMREAD_GRAYSCALE)

# 嵌入水印
watermarked = lsb.embed(host, watermark, strength=0.8)

# 提取水印
extracted = lsb.extract(watermarked, watermark.shape)

# 保存结果
cv2.imwrite('demo/watermarked_api.png', watermarked)
cv2.imwrite('demo/extracted_api.png', extracted * 255)
```

#### 高级配置
```python
# 自定义配置
lsb_config = {
    'bit_plane': 0,        # 位平面选择
    'scramble': True,      # 水印置乱
    'error_correction': True,  # 错误纠正
    'adaptive': True       # 自适应嵌入
}

lsb = LSBWatermark(**lsb_config)

# 设置嵌入区域
embed_region = (100, 100, 400, 400)  # (x, y, width, height)
watermarked = lsb.embed(host, watermark, region=embed_region)
```

#### 质量控制
```python
# 质量驱动的嵌入
target_psnr = 40  # 目标PSNR值
strength = lsb.find_optimal_strength(host, watermark, target_psnr)
watermarked = lsb.embed(host, watermark, strength=strength)
```

### DCT算法API

#### 基本使用
```python
from src.algorithms.dct_watermark import DCTWatermark

# 初始化算法
dct = DCTWatermark(block_size=8, alpha=0.1)

# 嵌入水印
watermarked = dct.embed(host, watermark)

# 提取水印 (非盲)
extracted = dct.extract(watermarked, host)

# 盲提取 (需要训练)
blind_extracted = dct.blind_extract(watermarked, watermark.shape)
```

#### 高级配置
```python
# DCT高级配置
dct_config = {
    'block_size': 8,           # DCT块大小
    'alpha': 0.1,              # 嵌入强度
    'coefficient_select': 'middle_freq',  # 系数选择策略
    'quantization_aware': True,   # 量化感知
    'perceptual_model': 'watson'  # 感知模型
}

dct = DCTWatermark(**dct_config)
```

#### 鲁棒性增强
```python
# 错误纠正编码
dct.enable_error_correction(method='bch', t=2)

# 扩频技术
dct.enable_spread_spectrum(pn_length=127)

# 多尺度嵌入
dct.enable_multiscale(scales=[1.0, 0.5, 0.25])
```

### 攻击测试API

#### 几何攻击
```python
from src.attacks.geometric_attacks import GeometricAttacks

geo_attacks = GeometricAttacks()

# 旋转攻击
rotated = geo_attacks.rotation(watermarked, angle=15)

# 缩放攻击
scaled = geo_attacks.scaling(watermarked, factor=0.8)

# 裁剪攻击
cropped = geo_attacks.cropping(watermarked, ratio=0.1)

# 组合攻击
combined = geo_attacks.combined_attack(
    watermarked, 
    operations=['rotation', 'scaling'],
    params=[10, 0.9]
)
```

#### 信号处理攻击
```python
from src.attacks.signal_processing_attacks import SignalProcessingAttacks

sig_attacks = SignalProcessingAttacks()

# 噪声攻击
noisy = sig_attacks.gaussian_noise(watermarked, variance=0.01)

# 压缩攻击
compressed = sig_attacks.jpeg_compression(watermarked, quality=70)

# 滤波攻击
filtered = sig_attacks.gaussian_filter(watermarked, sigma=1.0)
```

### 评估API

#### 图像质量评估
```python
from src.evaluation.image_quality import ImageQuality

evaluator = ImageQuality()

# 基本指标
metrics = evaluator.calculate_metrics(original, watermarked)
print(f"PSNR: {metrics['psnr']:.2f}dB")
print(f"SSIM: {metrics['ssim']:.4f}")
print(f"MSE: {metrics['mse']:.2f}")

# 感知质量评估
perceptual_score = evaluator.perceptual_quality(original, watermarked)
```

#### 鲁棒性评估
```python
from src.evaluation.watermark_robustness import WatermarkRobustness

robustness = WatermarkRobustness()

# 单攻击鲁棒性
ber = robustness.bit_error_rate(original_watermark, extracted_watermark)
nc = robustness.normalized_correlation(original_watermark, extracted_watermark)

# 多攻击鲁棒性测试
robustness_report = robustness.comprehensive_test(
    watermarked_image, 
    original_watermark,
    attack_list=['rotation', 'compression', 'noise']
)
```

## GUI使用指南

### 启动图形界面
```bash
python src/gui/watermark_gui.py
```

### 界面功能说明

#### 1. 嵌入标签页
- **选择宿主图像**: 点击"浏览"选择输入图像
- **选择水印图像**: 点击"浏览"选择水印图像
- **算法选择**: 从下拉菜单选择LSB或DCT
- **参数设置**: 调整嵌入强度等参数
- **执行嵌入**: 点击"嵌入水印"按钮
- **预览结果**: 在右侧查看嵌入效果

#### 2. 提取标签页
- **选择含水印图像**: 选择要提取水印的图像
- **设置提取参数**: 水印尺寸、算法类型等
- **执行提取**: 点击"提取水印"按钮
- **查看结果**: 显示提取的水印图像

#### 3. 攻击测试标签页
- **选择测试图像**: 选择要测试的含水印图像
- **选择攻击类型**: 从列表选择攻击方法
- **设置攻击参数**: 调整攻击强度
- **执行攻击**: 应用选择的攻击
- **查看效果**: 显示攻击后的图像

#### 4. 评估标签页
- **图像质量评估**: 计算PSNR、SSIM等指标
- **鲁棒性分析**: 显示攻击测试结果
- **生成报告**: 导出详细的评估报告

#### 5. 批处理标签页
- **选择输入目录**: 批量处理的图像文件夹
- **设置输出目录**: 结果保存位置
- **配置处理参数**: 批量处理的参数设置
- **开始批处理**: 执行批量水印操作

## 配置文件使用

### config.py 配置说明

```python
# 默认算法参数
DEFAULT_LSB_CONFIG = {
    'bit_plane': 0,
    'strength': 0.5,
    'scramble_key': 12345
}

DEFAULT_DCT_CONFIG = {
    'block_size': 8,
    'alpha': 0.1,
    'coefficient_positions': [(2,1), (1,2), (3,0), (0,3)]
}

# 路径配置
PATHS = {
    'input_dir': 'data/input/',
    'output_dir': 'data/output/',
    'watermark_dir': 'data/watermarks/',
    'temp_dir': 'temp/',
    'log_dir': 'logs/'
}

# 质量阈值
QUALITY_THRESHOLDS = {
    'psnr_min': 30.0,
    'ssim_min': 0.95,
    'ber_max': 0.1
}
```

### 自定义配置

```python
# 创建自定义配置文件 my_config.py
MY_LSB_CONFIG = {
    'bit_plane': 1,           # 使用第二低位
    'strength': 0.3,          # 较小的嵌入强度
    'adaptive': True,         # 启用自适应嵌入
    'error_correction': True  # 启用错误纠正
}

# 在代码中使用
from my_config import MY_LSB_CONFIG
lsb = LSBWatermark(**MY_LSB_CONFIG)
```

## 常见问题解答

### Q1: 图像格式支持
**A**: 支持常见格式：PNG、JPEG、BMP、TIFF。推荐使用PNG格式以获得最佳质量。

### Q2: 水印尺寸要求
**A**: 
- LSB算法: 水印可以是任意尺寸，会自动调整
- DCT算法: 建议水印尺寸为原图的1/4到1/8

### Q3: 处理大图像的建议
**A**: 
- 使用流式处理: `enable_streaming=True`
- 增加内存限制: `memory_limit='4GB'`
- 启用并行处理: `num_threads=4`

### Q4: 提高鲁棒性的方法
**A**:
- 使用DCT算法而不是LSB
- 启用错误纠正编码
- 使用扩频技术
- 调整嵌入强度

### Q5: 优化处理速度
**A**:
- 启用多线程处理
- 使用向量化操作
- 减少图像尺寸
- 选择合适的参数

## 脚本示例

### 批量处理脚本
```python
#!/usr/bin/env python3
"""
批量水印处理脚本
"""

import os
import glob
from src.algorithms.lsb_watermark import LSBWatermark
import cv2

def batch_watermark(input_dir, watermark_path, output_dir):
    # 初始化算法
    lsb = LSBWatermark()
    
    # 加载水印
    watermark = cv2.imread(watermark_path, cv2.IMREAD_GRAYSCALE)
    
    # 处理所有图像
    image_files = glob.glob(os.path.join(input_dir, '*.png'))
    
    for img_path in image_files:
        # 加载图像
        host = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        
        # 嵌入水印
        watermarked = lsb.embed(host, watermark)
        
        # 保存结果
        filename = os.path.basename(img_path)
        output_path = os.path.join(output_dir, f'watermarked_{filename}')
        cv2.imwrite(output_path, watermarked)
        
        print(f'处理完成: {filename}')

if __name__ == '__main__':
    batch_watermark('data/input/', 'data/watermarks/logo.png', 'results/')
```

### 鲁棒性测试脚本
```python
#!/usr/bin/env python3
"""
自动鲁棒性测试脚本
"""

from src.algorithms.lsb_watermark import LSBWatermark
from src.attacks.geometric_attacks import GeometricAttacks
from src.evaluation.watermark_robustness import WatermarkRobustness
import cv2
import json

def robustness_test(watermarked_path, original_watermark_path):
    # 初始化
    lsb = LSBWatermark()
    attacks = GeometricAttacks()
    evaluator = WatermarkRobustness()
    
    # 加载图像
    watermarked = cv2.imread(watermarked_path, cv2.IMREAD_GRAYSCALE)
    original_wm = cv2.imread(original_watermark_path, cv2.IMREAD_GRAYSCALE)
    
    results = {}
    
    # 测试不同攻击
    attack_configs = [
        ('rotation', [5, 10, 15, 30]),
        ('scaling', [0.8, 0.9, 1.1, 1.2]),
        ('compression', [90, 80, 70, 60])
    ]
    
    for attack_type, params in attack_configs:
        results[attack_type] = {}
        
        for param in params:
            # 应用攻击
            if attack_type == 'rotation':
                attacked = attacks.rotation(watermarked, param)
            elif attack_type == 'scaling':
                attacked = attacks.scaling(watermarked, param)
            elif attack_type == 'compression':
                attacked = attacks.jpeg_compression(watermarked, param)
            
            # 提取水印
            extracted_wm = lsb.extract(attacked, original_wm.shape)
            
            # 计算鲁棒性指标
            ber = evaluator.bit_error_rate(original_wm, extracted_wm)
            nc = evaluator.normalized_correlation(original_wm, extracted_wm)
            
            results[attack_type][param] = {
                'ber': float(ber),
                'nc': float(nc),
                'success': ber < 0.2  # 成功阈值
            }
    
    # 保存结果
    with open('robustness_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == '__main__':
    results = robustness_test(
        'demo/watermarked_lsb.png',
        'data/watermarks/watermark.png'
    )
    print("鲁棒性测试完成，结果已保存到 robustness_report.json")
```

## 技术支持

### 日志系统
系统提供详细的日志记录功能：

```python
from src.utils.logger import setup_logger

# 设置日志
logger = setup_logger('watermark_system', 'logs/watermark.log')

# 使用日志
logger.info('开始处理图像')
logger.warning('图像质量较低')
logger.error('处理失败')
```

### 错误处理
```python
try:
    watermarked = lsb.embed(host, watermark)
except WatermarkError as e:
    print(f"水印处理错误: {e}")
except ImageError as e:
    print(f"图像处理错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

### 性能监控
```python
from src.utils.profiler import profile_function

@profile_function
def my_watermark_function():
    # 水印处理代码
    pass

# 查看性能报告
my_watermark_function()
```

本使用指南提供了数字水印系统的全面使用方法，涵盖了从基础操作到高级配置的各个方面。如有其他问题，请参考项目文档或提交Issue。
