#!/usr/bin/env python3
"""
创建缺失的演示程序符号链接
"""
import os
import subprocess

def create_demo_links():
    """创建演示程序的符号链接"""
    links = {
        'length_extension_demo': 'sm3_demo',
        'merkle_demo': 'sm3_demo'
    }
    
    bin_dir = 'bin'
    for link_name, target in links.items():
        link_path = os.path.join(bin_dir, link_name)
        target_path = target
        
        if not os.path.exists(link_path) and os.path.exists(os.path.join(bin_dir, target)):
            try:
                os.symlink(target, link_path)
                print(f"Created symlink: {link_name} -> {target}")
            except Exception as e:
                print(f"Failed to create symlink {link_name}: {e}")

if __name__ == "__main__":
    create_demo_links()
