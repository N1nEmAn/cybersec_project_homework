import numpy as np
from PIL import Image
import cv2
import os

def create_test_images():
    """创建测试图像"""
    # 创建目录
    os.makedirs('/home/S3vn/Public/cybersec_project_homework/project2/data/input', exist_ok=True)
    os.makedirs('/home/S3vn/Public/cybersec_project_homework/project2/data/output', exist_ok=True)
    os.makedirs('/home/S3vn/Public/cybersec_project_homework/project2/data/watermarks', exist_ok=True)
    
    # 创建宿主图像 - 512x512彩色图像
    host_data = np.zeros((512, 512, 3), dtype=np.uint8)
    
    # 创建渐变背景
    for i in range(512):
        for j in range(512):
            host_data[i, j] = [
                int(255 * (i / 512)),  # R channel gradient
                int(255 * (j / 512)),  # G channel gradient  
                int(255 * ((i + j) / 1024))  # B channel gradient
            ]
    
    # 添加几何图案
    center = (256, 256)
    cv2.circle(host_data, center, 100, (255, 255, 255), 3)
    cv2.rectangle(host_data, (150, 150), (350, 350), (0, 255, 0), 2)
    
    # 添加文字
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(host_data, 'HOST IMAGE', (180, 280), font, 1, (255, 255, 255), 2)
    
    host_img = Image.fromarray(host_data)
    host_img.save('/home/S3vn/Public/cybersec_project_homework/project2/data/input/host.png')
    
    # 创建水印图像 - 64x64黑白图像
    watermark_data = np.zeros((64, 64), dtype=np.uint8)
    
    # 创建"WM"图案
    # W
    for i in range(10, 54):
        watermark_data[i, 8] = 255
        watermark_data[i, 20] = 255
    for i in range(44, 54):
        watermark_data[i, 14] = 255
    for i in range(8, 21):
        watermark_data[52, i] = 255
    
    # M  
    for i in range(10, 54):
        watermark_data[i, 28] = 255
        watermark_data[i, 52] = 255
    for i in range(28, 53):
        watermark_data[12, i] = 255
    for i in range(12, 35):
        watermark_data[i, 40] = 255
    
    watermark_img = Image.fromarray(watermark_data, mode='L')
    watermark_img.save('/home/S3vn/Public/cybersec_project_homework/project2/data/watermarks/watermark.png')
    
    # 创建更多测试图像
    # Lena图像模拟
    lena_data = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)
    # 添加结构化模式
    for i in range(0, 512, 32):
        for j in range(0, 512, 32):
            cv2.rectangle(lena_data, (j, i), (j+16, i+16), (128, 128, 128), -1)
    
    lena_img = Image.fromarray(lena_data)
    lena_img.save('/home/S3vn/Public/cybersec_project_homework/project2/data/input/lena.png')
    
    # Baboon图像模拟
    baboon_data = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)
    # 添加高频纹理
    for i in range(512):
        for j in range(512):
            if (i + j) % 4 == 0:
                baboon_data[i, j] = np.minimum(baboon_data[i, j] + 50, 255)
    
    baboon_img = Image.fromarray(baboon_data)
    baboon_img.save('/home/S3vn/Public/cybersec_project_homework/project2/data/input/baboon.png')
    
    print("测试图像创建完成:")
    print("- 宿主图像: host.png (512x512)")
    print("- 水印图像: watermark.png (64x64)")
    print("- 测试图像: lena.png, baboon.png")

if __name__ == "__main__":
    create_test_images()
