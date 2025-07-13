#!/bin/bash

# Poseidon2 ZK Circuit 环境配置脚本
# 安装必要的工具和依赖

set -e

echo "🚀 开始配置 Poseidon2 ZK Circuit 开发环境..."

# 检查 Node.js 版本
check_nodejs() {
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装，请先安装 Node.js 16+"
        exit 1
    fi
    
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        echo "❌ Node.js 版本过低，需要 16+，当前版本: $(node -v)"
        exit 1
    fi
    
    echo "✅ Node.js 版本检查通过: $(node -v)"
}

# 安装 Circom
install_circom() {
    echo "📦 安装 Circom..."
    
    if command -v circom &> /dev/null; then
        echo "✅ Circom 已安装: $(circom --version)"
        return
    fi
    
    # 下载并安装 Circom
    if command -v cargo &> /dev/null; then
        echo "使用 Cargo 安装 Circom..."
        cargo install --git https://github.com/iden3/circom.git
    else
        echo "❌ 需要安装 Rust 和 Cargo 来编译 Circom"
        echo "请访问 https://rustup.rs/ 安装 Rust"
        exit 1
    fi
}

# 安装 SnarkJS
install_snarkjs() {
    echo "📦 安装 SnarkJS..."
    
    if command -v snarkjs &> /dev/null; then
        echo "✅ SnarkJS 已安装: $(snarkjs --version)"
        return
    fi
    
    npm install -g snarkjs
    echo "✅ SnarkJS 安装完成"
}

# 安装项目依赖
install_dependencies() {
    echo "📦 安装项目依赖..."
    
    if [ ! -f "package.json" ]; then
        echo "❌ 在项目根目录下运行此脚本"
        exit 1
    fi
    
    npm install
    echo "✅ 项目依赖安装完成"
}

# 创建必要的目录
create_directories() {
    echo "📁 创建项目目录结构..."
    
    mkdir -p build
    mkdir -p proofs
    mkdir -p tests/vectors
    mkdir -p docs/images
    
    echo "✅ 目录结构创建完成"
}

# 下载可信设置参数
download_ptau() {
    echo "🔐 下载可信设置参数..."
    
    PTAU_FILE="build/powersoftau_final.ptau"
    
    if [ -f "$PTAU_FILE" ]; then
        echo "✅ 可信设置参数已存在"
        return
    fi
    
    # 下载适当大小的 powers of tau 文件
    # 对于小电路，使用较小的文件
    echo "下载 Powers of Tau 文件 (约 50MB)..."
    
    if command -v wget &> /dev/null; then
        wget -O "$PTAU_FILE" "https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_12.ptau"
    elif command -v curl &> /dev/null; then
        curl -L -o "$PTAU_FILE" "https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_12.ptau"
    else
        echo "❌ 需要 wget 或 curl 来下载文件"
        exit 1
    fi
    
    echo "✅ 可信设置参数下载完成"
}

# 验证安装
verify_installation() {
    echo "🔍 验证安装..."
    
    # 验证 Circom
    if ! circom --version &> /dev/null; then
        echo "❌ Circom 安装验证失败"
        exit 1
    fi
    
    # 验证 SnarkJS
    if ! snarkjs --version &> /dev/null; then
        echo "❌ SnarkJS 安装验证失败"
        exit 1
    fi
    
    # 验证 Node.js 依赖
    if ! node -e "require('circomlib')" &> /dev/null; then
        echo "❌ Node.js 依赖验证失败"
        exit 1
    fi
    
    echo "✅ 所有组件验证通过"
}

# 创建配置文件
create_config() {
    echo "⚙️ 创建配置文件..."
    
    cat > .env << EOF
# Poseidon2 Circuit Configuration
CIRCUIT_NAME=poseidon2
CURVE=bn128
PROTOCOL=groth16

# Build configuration
BUILD_DIR=build
PROOF_DIR=proofs
WITNESS_DIR=witness

# Circuit parameters
FIELD_SIZE=256
STATE_SIZE_1=3
STATE_SIZE_2=2
SBOX_DEGREE=5
EOF

    echo "✅ 配置文件创建完成"
}

# 主函数
main() {
    echo "🎯 Poseidon2 ZK Circuit 环境配置"
    echo "================================="
    
    check_nodejs
    install_circom
    install_snarkjs
    install_dependencies
    create_directories
    download_ptau
    create_config
    verify_installation
    
    echo ""
    echo "🎉 环境配置完成！"
    echo ""
    echo "下一步操作:"
    echo "1. 编译电路: npm run compile"
    echo "2. 生成证明: npm run prove"
    echo "3. 验证证明: npm run verify"
    echo "4. 运行测试: npm test"
    echo ""
    echo "📖 查看 README.md 获取更多信息"
}

# 检查是否以正确方式运行
if [ "$0" = "${BASH_SOURCE[0]}" ]; then
    main "$@"
fi
