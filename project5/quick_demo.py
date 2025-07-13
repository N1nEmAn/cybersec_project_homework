#!/usr/bin/env python3
"""
SM2 Quick Demo Script
Quick demonstration of SM2 implementations
"""

import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sm2_basic import SM2Basic
from sm2_optimized import SM2Optimized
from sm2_simd import SM2SIMD


def quick_demo():
    """Quick demonstration of all three implementations"""
    print("=== SM2 Quick Demo ===\n")
    
    implementations = {
        'Basic': SM2Basic(),
        'Optimized': SM2Optimized(),
        'SIMD': SM2SIMD()
    }
    
    message = b"Quick demo message"
    
    for name, impl in implementations.items():
        print(f"--- {name} Implementation ---")
        
        # Generate keys
        start = time.time()
        private_key, public_key = impl.generate_keypair()
        keygen_time = time.time() - start
        
        # Sign message
        start = time.time()
        signature = impl.sign(message, private_key)
        sign_time = time.time() - start
        
        # Verify signature
        start = time.time()
        is_valid = impl.verify(message, signature, public_key)
        verify_time = time.time() - start
        
        print(f"Key Generation: {keygen_time:.4f}s")
        print(f"Signing: {sign_time:.4f}s")
        print(f"Verification: {verify_time:.4f}s")
        print(f"Result: {'✓ VALID' if is_valid else '✗ INVALID'}\n")


if __name__ == "__main__":
    quick_demo()
