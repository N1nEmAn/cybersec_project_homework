"""
简单的日志工具
记录操作过程和错误信息
"""

import os
import datetime
from pathlib import Path


class SimpleLogger:
    def __init__(self, log_file="sm4.log"):
        """初始化日志记录器"""
        self.log_file = Path(__file__).parent / log_file
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log(self, level, message):
        """记录日志"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        # 写入文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # 同时输出到控制台
        print(log_entry.strip())
    
    def info(self, message):
        """记录信息"""
        self.log("INFO", message)
    
    def error(self, message):
        """记录错误"""
        self.log("ERROR", message)
    
    def warning(self, message):
        """记录警告"""
        self.log("WARNING", message)
    
    def debug(self, message):
        """记录调试信息"""
        self.log("DEBUG", message)


# 全局日志实例
logger = SimpleLogger()


def test_logger():
    """测试日志功能"""
    logger.info("这是一条信息")
    logger.warning("这是一条警告")
    logger.error("这是一条错误")
    logger.debug("这是调试信息")


if __name__ == "__main__":
    test_logger()
