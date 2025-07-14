"""
SM2 Cryptographic Utilities Package

This module provides comprehensive utilities for SM2 elliptic curve cryptography,
including key management, signature verification, and cryptographic helpers.

Author: SM2 Research Team
License: MIT
"""

import hashlib
import secrets
import struct
import time
from typing import Tuple, Optional, List, Dict, Any
import json
from dataclasses import dataclass
from enum import Enum

# Import basic SM2 implementation
from .sm2_basic import SM2, Point, CurveParams

class KeyFormat(Enum):
    """Supported key formats"""
    PEM = "pem"
    DER = "der" 
    HEX = "hex"
    JSON = "json"

class HashAlgorithm(Enum):
    """Supported hash algorithms"""
    SM3 = "sm3"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"

@dataclass
class SM2KeyPair:
    """SM2 Key pair data structure"""
    private_key: int
    public_key: Point
    curve_params: CurveParams
    created_at: float
    key_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert key pair to dictionary"""
        return {
            'private_key': hex(self.private_key),
            'public_key': {
                'x': hex(self.public_key.x),
                'y': hex(self.public_key.y)
            },
            'curve_params': {
                'p': hex(self.curve_params.p),
                'a': hex(self.curve_params.a),
                'b': hex(self.curve_params.b),
                'n': hex(self.curve_params.n),
                'gx': hex(self.curve_params.gx),
                'gy': hex(self.curve_params.gy)
            },
            'created_at': self.created_at,
            'key_id': self.key_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SM2KeyPair':
        """Create key pair from dictionary"""
        curve_params = CurveParams(
            p=int(data['curve_params']['p'], 16),
            a=int(data['curve_params']['a'], 16),
            b=int(data['curve_params']['b'], 16),
            n=int(data['curve_params']['n'], 16),
            gx=int(data['curve_params']['gx'], 16),
            gy=int(data['curve_params']['gy'], 16)
        )
        
        return cls(
            private_key=int(data['private_key'], 16),
            public_key=Point(
                int(data['public_key']['x'], 16),
                int(data['public_key']['y'], 16)
            ),
            curve_params=curve_params,
            created_at=data['created_at'],
            key_id=data.get('key_id')
        )

class SM2KeyManager:
    """SM2 Key management utilities"""
    
    def __init__(self):
        self.sm2 = SM2()
    
    def generate_keypair(self, key_id: Optional[str] = None) -> SM2KeyPair:
        """Generate a new SM2 key pair"""
        private_key = secrets.randbelow(self.sm2.curve.n - 1) + 1
        public_key = self.sm2.point_multiply(private_key, self.sm2.G)
        
        return SM2KeyPair(
            private_key=private_key,
            public_key=public_key,
            curve_params=self.sm2.curve,
            created_at=time.time(),
            key_id=key_id or self._generate_key_id()
        )
    
    def _generate_key_id(self) -> str:
        """Generate a unique key ID"""
        return f"sm2-{int(time.time() * 1000000):016x}"
    
    def export_private_key(self, keypair: SM2KeyPair, format: KeyFormat, 
                          password: Optional[str] = None) -> str:
        """Export private key in specified format"""
        if format == KeyFormat.HEX:
            return f"{keypair.private_key:064x}"
        elif format == KeyFormat.JSON:
            data = keypair.to_dict()
            if password:
                data = self._encrypt_key_data(data, password)
            return json.dumps(data, indent=2)
        elif format == KeyFormat.PEM:
            return self._to_pem_format(keypair, password)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_public_key(self, keypair: SM2KeyPair, format: KeyFormat) -> str:
        """Export public key in specified format"""
        if format == KeyFormat.HEX:
            return f"04{keypair.public_key.x:064x}{keypair.public_key.y:064x}"
        elif format == KeyFormat.JSON:
            return json.dumps({
                'public_key': {
                    'x': hex(keypair.public_key.x),
                    'y': hex(keypair.public_key.y)
                },
                'curve_params': {
                    'p': hex(keypair.curve_params.p),
                    'a': hex(keypair.curve_params.a), 
                    'b': hex(keypair.curve_params.b),
                    'n': hex(keypair.curve_params.n),
                    'gx': hex(keypair.curve_params.gx),
                    'gy': hex(keypair.curve_params.gy)
                }
            }, indent=2)
        elif format == KeyFormat.PEM:
            return self._public_key_to_pem(keypair)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_private_key(self, key_data: str, format: KeyFormat,
                          password: Optional[str] = None) -> SM2KeyPair:
        """Import private key from specified format"""
        if format == KeyFormat.HEX:
            private_key = int(key_data, 16)
            public_key = self.sm2.point_multiply(private_key, self.sm2.G)
            return SM2KeyPair(
                private_key=private_key,
                public_key=public_key,
                curve_params=self.sm2.curve,
                created_at=time.time()
            )
        elif format == KeyFormat.JSON:
            data = json.loads(key_data)
            if password and 'encrypted' in data:
                data = self._decrypt_key_data(data, password)
            return SM2KeyPair.from_dict(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _encrypt_key_data(self, data: Dict[str, Any], password: str) -> Dict[str, Any]:
        """Encrypt key data with password (simplified AES)"""
        # This is a simplified implementation
        # In production, use proper key derivation and encryption
        import base64
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        f = Fernet(key)
        
        encrypted_data = f.encrypt(json.dumps(data).encode())
        
        return {
            'encrypted': True,
            'salt': base64.b64encode(salt).decode(),
            'data': base64.b64encode(encrypted_data).decode()
        }
    
    def _decrypt_key_data(self, data: Dict[str, Any], password: str) -> Dict[str, Any]:
        """Decrypt key data with password"""
        import base64
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        
        salt = base64.b64decode(data['salt'])
        encrypted_data = base64.b64decode(data['data'])
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        f = Fernet(key)
        
        decrypted_data = f.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    
    def _to_pem_format(self, keypair: SM2KeyPair, password: Optional[str] = None) -> str:
        """Convert to PEM format (simplified)"""
        # This is a simplified PEM format for demonstration
        header = "-----BEGIN SM2 PRIVATE KEY-----"
        footer = "-----END SM2 PRIVATE KEY-----"
        
        import base64
        key_data = f"{keypair.private_key:064x}"
        if password:
            # In practice, use proper PKCS#8 encryption
            key_data = f"ENCRYPTED:{key_data}"
        
        encoded = base64.b64encode(key_data.encode()).decode()
        # Break into 64-character lines
        lines = [encoded[i:i+64] for i in range(0, len(encoded), 64)]
        
        return f"{header}\n" + "\n".join(lines) + f"\n{footer}"
    
    def _public_key_to_pem(self, keypair: SM2KeyPair) -> str:
        """Convert public key to PEM format"""
        header = "-----BEGIN SM2 PUBLIC KEY-----"
        footer = "-----END SM2 PUBLIC KEY-----"
        
        import base64
        key_data = f"04{keypair.public_key.x:064x}{keypair.public_key.y:064x}"
        encoded = base64.b64encode(key_data.encode()).decode()
        lines = [encoded[i:i+64] for i in range(0, len(encoded), 64)]
        
        return f"{header}\n" + "\n".join(lines) + f"\n{footer}"

class SM2SignatureVerifier:
    """Advanced SM2 signature verification utilities"""
    
    def __init__(self):
        self.sm2 = SM2()
    
    def verify_signature(self, message: bytes, signature: Tuple[int, int], 
                        public_key: Point, user_id: bytes = b"1234567812345678") -> bool:
        """Verify SM2 signature with enhanced error checking"""
        try:
            return self.sm2.verify(message, signature, public_key, user_id)
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    def batch_verify_signatures(self, signatures_data: List[Dict[str, Any]]) -> List[bool]:
        """Batch verification of multiple signatures"""
        results = []
        for data in signatures_data:
            try:
                result = self.verify_signature(
                    data['message'],
                    data['signature'],
                    data['public_key'],
                    data.get('user_id', b"1234567812345678")
                )
                results.append(result)
            except Exception:
                results.append(False)
        return results
    
    def verify_signature_chain(self, signature_chain: List[Dict[str, Any]]) -> bool:
        """Verify a chain of linked signatures"""
        for i, sig_data in enumerate(signature_chain):
            if not self.verify_signature(
                sig_data['message'],
                sig_data['signature'],
                sig_data['public_key'],
                sig_data.get('user_id', b"1234567812345678")
            ):
                return False
            
            # Verify chain linking if specified
            if i > 0 and 'previous_hash' in sig_data:
                prev_hash = hashlib.sha256(signature_chain[i-1]['message']).hexdigest()
                if sig_data['previous_hash'] != prev_hash:
                    return False
        
        return True

class SM2Benchmarker:
    """Performance benchmarking utilities"""
    
    def __init__(self):
        self.sm2 = SM2()
        self.key_manager = SM2KeyManager()
    
    def benchmark_key_generation(self, num_keys: int = 1000) -> Dict[str, float]:
        """Benchmark key generation performance"""
        start_time = time.time()
        
        for _ in range(num_keys):
            self.key_manager.generate_keypair()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            'total_time': total_time,
            'keys_per_second': num_keys / total_time,
            'time_per_key': total_time / num_keys
        }
    
    def benchmark_signing(self, message_size: int = 1024, num_signatures: int = 1000) -> Dict[str, float]:
        """Benchmark signing performance"""
        keypair = self.key_manager.generate_keypair()
        message = secrets.token_bytes(message_size)
        
        start_time = time.time()
        
        for _ in range(num_signatures):
            self.sm2.sign(message, keypair.private_key)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            'total_time': total_time,
            'signatures_per_second': num_signatures / total_time,
            'time_per_signature': total_time / num_signatures,
            'message_size': message_size
        }
    
    def benchmark_verification(self, message_size: int = 1024, num_verifications: int = 1000) -> Dict[str, float]:
        """Benchmark verification performance"""
        keypair = self.key_manager.generate_keypair()
        message = secrets.token_bytes(message_size)
        signature = self.sm2.sign(message, keypair.private_key)
        
        start_time = time.time()
        
        for _ in range(num_verifications):
            self.sm2.verify(message, signature, keypair.public_key)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            'total_time': total_time,
            'verifications_per_second': num_verifications / total_time,
            'time_per_verification': total_time / num_verifications,
            'message_size': message_size
        }
    
    def comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmark"""
        print("Running comprehensive SM2 benchmark...")
        
        results = {
            'key_generation': self.benchmark_key_generation(100),
            'signing_1kb': self.benchmark_signing(1024, 100),
            'signing_64kb': self.benchmark_signing(65536, 100),
            'verification_1kb': self.benchmark_verification(1024, 100),
            'verification_64kb': self.benchmark_verification(65536, 100),
            'timestamp': time.time()
        }
        
        return results

class SM2Validator:
    """SM2 cryptographic validation utilities"""
    
    def __init__(self):
        self.sm2 = SM2()
    
    def validate_private_key(self, private_key: int) -> bool:
        """Validate private key is in valid range"""
        return 1 <= private_key <= self.sm2.curve.n - 1
    
    def validate_public_key(self, public_key: Point) -> bool:
        """Validate public key is on the curve"""
        try:
            return self.sm2.is_on_curve(public_key)
        except:
            return False
    
    def validate_signature(self, signature: Tuple[int, int]) -> bool:
        """Validate signature components are in valid range"""
        r, s = signature
        return (1 <= r <= self.sm2.curve.n - 1) and (1 <= s <= self.sm2.curve.n - 1)
    
    def validate_curve_parameters(self, curve: CurveParams) -> bool:
        """Validate curve parameters"""
        # Check that curve equation is satisfied by generator point
        try:
            left = pow(curve.gy, 2, curve.p)
            right = (pow(curve.gx, 3, curve.p) + curve.a * curve.gx + curve.b) % curve.p
            return left == right
        except:
            return False

class SM2Utils:
    """General SM2 utility functions"""
    
    @staticmethod
    def bytes_to_int(data: bytes) -> int:
        """Convert bytes to integer"""
        return int.from_bytes(data, byteorder='big')
    
    @staticmethod
    def int_to_bytes(value: int, length: int = 32) -> bytes:
        """Convert integer to bytes with specified length"""
        return value.to_bytes(length, byteorder='big')
    
    @staticmethod
    def point_to_bytes(point: Point, compressed: bool = False) -> bytes:
        """Convert point to byte representation"""
        if compressed:
            prefix = 0x02 if point.y % 2 == 0 else 0x03
            return bytes([prefix]) + SM2Utils.int_to_bytes(point.x, 32)
        else:
            return bytes([0x04]) + SM2Utils.int_to_bytes(point.x, 32) + SM2Utils.int_to_bytes(point.y, 32)
    
    @staticmethod
    def bytes_to_point(data: bytes) -> Point:
        """Convert byte representation to point"""
        if len(data) == 33:  # Compressed
            prefix = data[0]
            x = SM2Utils.bytes_to_int(data[1:33])
            # Decompress point (simplified - would need curve parameters)
            raise NotImplementedError("Point decompression not implemented")
        elif len(data) == 65:  # Uncompressed
            if data[0] != 0x04:
                raise ValueError("Invalid uncompressed point prefix")
            x = SM2Utils.bytes_to_int(data[1:33])
            y = SM2Utils.bytes_to_int(data[33:65])
            return Point(x, y)
        else:
            raise ValueError("Invalid point data length")
    
    @staticmethod
    def generate_random_message(length: int = 32) -> bytes:
        """Generate random message for testing"""
        return secrets.token_bytes(length)
    
    @staticmethod
    def hash_message(message: bytes, algorithm: HashAlgorithm = HashAlgorithm.SM3) -> bytes:
        """Hash message with specified algorithm"""
        if algorithm == HashAlgorithm.SM3:
            # Would use actual SM3 implementation
            return hashlib.sha256(message).digest()  # Placeholder
        elif algorithm == HashAlgorithm.SHA256:
            return hashlib.sha256(message).digest()
        elif algorithm == HashAlgorithm.SHA384:
            return hashlib.sha384(message).digest()
        elif algorithm == HashAlgorithm.SHA512:
            return hashlib.sha512(message).digest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

def demo_utilities():
    """Demonstrate SM2 utilities functionality"""
    print("=== SM2 Utilities Demo ===\n")
    
    # Key management demo
    print("1. Key Management:")
    key_manager = SM2KeyManager()
    keypair = key_manager.generate_keypair("demo-key")
    print(f"   Generated key ID: {keypair.key_id}")
    
    # Export keys in different formats
    hex_private = key_manager.export_private_key(keypair, KeyFormat.HEX)
    hex_public = key_manager.export_public_key(keypair, KeyFormat.HEX)
    print(f"   Private key (hex): {hex_private[:32]}...")
    print(f"   Public key (hex): {hex_public[:32]}...")
    
    # Signature verification demo
    print("\n2. Signature Verification:")
    verifier = SM2SignatureVerifier()
    message = b"Hello, SM2 World!"
    sm2 = SM2()
    signature = sm2.sign(message, keypair.private_key)
    is_valid = verifier.verify_signature(message, signature, keypair.public_key)
    print(f"   Message: {message.decode()}")
    print(f"   Signature valid: {is_valid}")
    
    # Benchmarking demo
    print("\n3. Performance Benchmarking:")
    benchmarker = SM2Benchmarker()
    key_gen_results = benchmarker.benchmark_key_generation(10)
    print(f"   Key generation: {key_gen_results['keys_per_second']:.2f} keys/sec")
    
    sign_results = benchmarker.benchmark_signing(1024, 10)
    print(f"   Signing (1KB): {sign_results['signatures_per_second']:.2f} sigs/sec")
    
    # Validation demo
    print("\n4. Cryptographic Validation:")
    validator = SM2Validator()
    key_valid = validator.validate_private_key(keypair.private_key)
    point_valid = validator.validate_public_key(keypair.public_key)
    sig_valid = validator.validate_signature(signature)
    print(f"   Private key valid: {key_valid}")
    print(f"   Public key valid: {point_valid}")
    print(f"   Signature valid: {sig_valid}")
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    demo_utilities()
