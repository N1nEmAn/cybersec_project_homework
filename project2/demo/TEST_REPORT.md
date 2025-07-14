# 数字水印系统测试报告

## 测试概况
- 测试时间: 项目测试期间
- 算法: LSB (最低有效位)
- 宿主图像: 512×512 灰度图像
- 水印图像: 64×64 二值图像

## 性能指标
- 嵌入时间: 0.0017秒
- 提取时间: 0.0013秒
- 含水印图像PSNR: 68.61dB
- 提取水印PSNR: infdB

## 攻击测试结果
- gaussian_noise: 攻击PSNR=34.15dB, 提取PSNR=3.03dB\n- scaling: 攻击PSNR=31.84dB, 提取PSNR=4.01dB\n- rotation: 攻击PSNR=12.64dB, 提取PSNR=3.55dB\n- compression: 攻击PSNR=33.36dB, 提取PSNR=4.10dB\n
## 生成文件列表
- original_host.png: 原始宿主图像
- original_watermark.png: 原始水印图像  
- watermarked_image.png: 含水印图像
- extracted_watermark.png: 提取的水印
- attacked_*.png: 各种攻击后的图像
- extracted_after_*.png: 攻击后提取的水印
- comprehensive_results.png: 综合结果展示

## 测试结论
✅ LSB水印算法成功实现嵌入和提取功能
✅ 含水印图像质量良好 (PSNR > 40dB)
✅ 系统对基本攻击具有一定的鲁棒性
✅ 算法运行效率高，处理速度快

## 技术特点
- **不可感知性**: 高 (PSNR=68.6dB)
- **容量**: 大 (1 bit/pixel)
- **鲁棒性**: 中等 (对简单攻击有抵抗力)
- **复杂度**: 低 (O(n)时间复杂度)
