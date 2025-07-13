from setuptools import setup, find_packages

setup(
    name="ddh-psi-protocol",
    version="1.0.0",
    description="DDH-based Private Set Intersection with Sum Protocol",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=3.4.8",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.2",
        "sympy>=1.9",
        "pytest>=6.2.0",
        "tqdm>=4.62.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Security :: Cryptography",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
