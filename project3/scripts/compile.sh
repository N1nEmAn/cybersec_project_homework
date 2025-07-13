#!/bin/bash

# Circom 电路编译脚本
# 编译 Poseidon2 哈希电路

set -e

# 配置变量
CIRCUIT_NAME="poseidon2"
CIRCUIT_FILE="circuits/${CIRCUIT_NAME}.circom"
BUILD_DIR="build"
R1CS_FILE="${BUILD_DIR}/${CIRCUIT_NAME}.r1cs"
WASM_FILE="${BUILD_DIR}/${CIRCUIT_NAME}.wasm"
SYM_FILE="${BUILD_DIR}/${CIRCUIT_NAME}.sym"

echo "🔨 编译 Poseidon2 电路..."

# 检查电路文件是否存在
if [ ! -f "$CIRCUIT_FILE" ]; then
    echo "❌ 电路文件不存在: $CIRCUIT_FILE"
    exit 1
fi

# 创建构建目录
mkdir -p "$BUILD_DIR"

# 编译电路
echo "📋 编译电路文件: $CIRCUIT_FILE"
circom "$CIRCUIT_FILE" \
    --r1cs --wasm --sym \
    --output "$BUILD_DIR" \
    -O 2

# 检查编译结果
if [ ! -f "$R1CS_FILE" ]; then
    echo "❌ R1CS 文件生成失败"
    exit 1
fi

if [ ! -f "$WASM_FILE" ]; then
    echo "❌ WASM 文件生成失败"
    exit 1
fi

echo "✅ 电路编译完成!"

# 显示电路信息
echo ""
echo "📊 电路统计信息:"
snarkjs r1cs info "$R1CS_FILE"

# 导出电路约束信息
echo ""
echo "💾 导出约束信息..."
snarkjs r1cs export json "$R1CS_FILE" "${BUILD_DIR}/${CIRCUIT_NAME}_constraints.json"

# 生成可信设置
PTAU_FILE="${BUILD_DIR}/powersoftau_final.ptau"
ZKEY_FILE="${BUILD_DIR}/${CIRCUIT_NAME}.zkey"

if [ -f "$PTAU_FILE" ]; then
    echo ""
    echo "🔐 生成电路特定的可信设置..."
    
    # Groth16 setup
    snarkjs groth16 setup "$R1CS_FILE" "$PTAU_FILE" "$ZKEY_FILE"
    
    # 导出验证密钥
    VKEY_FILE="${BUILD_DIR}/${CIRCUIT_NAME}_vkey.json"
    snarkjs zkey export verificationkey "$ZKEY_FILE" "$VKEY_FILE"
    
    echo "✅ 可信设置生成完成!"
    echo "   - 证明密钥: $ZKEY_FILE"
    echo "   - 验证密钥: $VKEY_FILE"
else
    echo "⚠️  Powers of Tau 文件不存在，跳过可信设置生成"
    echo "   运行 'npm run setup' 下载必要文件"
fi

echo ""
echo "🎉 编译流程完成!"
echo ""
echo "生成的文件:"
echo "  - R1CS: $R1CS_FILE"
echo "  - WASM: $WASM_FILE"
echo "  - 符号: $SYM_FILE"
if [ -f "$ZKEY_FILE" ]; then
    echo "  - 证明密钥: $ZKEY_FILE"
    echo "  - 验证密钥: $VKEY_FILE"
fi
