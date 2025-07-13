#!/bin/bash

# Groth16 零知识证明生成脚本

set -e

# 配置变量
CIRCUIT_NAME="poseidon2"
BUILD_DIR="build"
PROOF_DIR="proofs"
INPUT_FILE="input.json"

echo "🔐 生成 Poseidon2 零知识证明..."

# 检查必要文件
WASM_FILE="${BUILD_DIR}/${CIRCUIT_NAME}.wasm"
ZKEY_FILE="${BUILD_DIR}/${CIRCUIT_NAME}.zkey"

if [ ! -f "$WASM_FILE" ]; then
    echo "❌ WASM 文件不存在: $WASM_FILE"
    echo "请先运行: npm run compile"
    exit 1
fi

if [ ! -f "$ZKEY_FILE" ]; then
    echo "❌ 证明密钥不存在: $ZKEY_FILE"
    echo "请先运行: npm run compile"
    exit 1
fi

# 创建证明目录
mkdir -p "$PROOF_DIR"

# 创建测试输入 (如果不存在)
if [ ! -f "$INPUT_FILE" ]; then
    echo "📝 创建测试输入文件..."
    cat > "$INPUT_FILE" << EOF
{
    "preimage": ["123", "456"],
    "expectedHash": "0"
}
EOF
    echo "✅ 创建了示例输入文件: $INPUT_FILE"
fi

echo "📋 使用输入文件: $INPUT_FILE"

# 生成见证
WITNESS_FILE="${PROOF_DIR}/witness.wtns"
echo "🧮 计算见证..."

# 使用 snarkjs 计算见证
node -e "
const snarkjs = require('snarkjs');
const fs = require('fs');

async function generateWitness() {
    try {
        const input = JSON.parse(fs.readFileSync('$INPUT_FILE', 'utf8'));
        
        // 如果期望哈希值为0，需要计算实际哈希值
        if (input.expectedHash === '0') {
            const { Poseidon2 } = require('./js/poseidon2.js');
            const poseidon2 = new Poseidon2();
            const hash = await poseidon2.hash(input.preimage.map(x => BigInt(x)));
            input.expectedHash = hash.toString();
            console.log('计算的哈希值:', hash.toString());
        }
        
        // 生成见证
        const { witness } = await snarkjs.wtns.calculate(
            input,
            '$WASM_FILE',
            '$WITNESS_FILE'
        );
        
        console.log('✅ 见证生成成功');
    } catch (error) {
        console.error('❌ 见证生成失败:', error.message);
        process.exit(1);
    }
}

generateWitness();
"

# 生成证明
PROOF_FILE="${PROOF_DIR}/proof.json"
PUBLIC_FILE="${PROOF_DIR}/public.json"

echo "🔒 生成 Groth16 证明..."
snarkjs groth16 prove "$ZKEY_FILE" "$WITNESS_FILE" "$PROOF_FILE" "$PUBLIC_FILE"

if [ ! -f "$PROOF_FILE" ]; then
    echo "❌ 证明生成失败"
    exit 1
fi

echo "✅ 证明生成成功!"

# 显示证明信息
echo ""
echo "📄 证明文件:"
echo "  - 证明: $PROOF_FILE"
echo "  - 公开输入: $PUBLIC_FILE"
echo "  - 见证: $WITNESS_FILE"

# 显示证明大小
PROOF_SIZE=$(stat -c%s "$PROOF_FILE" 2>/dev/null || stat -f%z "$PROOF_FILE" 2>/dev/null || echo "unknown")
echo "  - 证明大小: $PROOF_SIZE bytes"

# 显示证明内容 (前几行)
echo ""
echo "🔍 证明内容预览:"
head -10 "$PROOF_FILE"

echo ""
echo "🎉 证明生成完成!"
echo ""
echo "下一步: 运行 'npm run verify' 验证证明"
