#!/bin/bash

# Groth16 证明验证脚本

set -e

# 配置变量
CIRCUIT_NAME="poseidon2"
BUILD_DIR="build"
PROOF_DIR="proofs"

echo "✅ 验证 Poseidon2 零知识证明..."

# 检查必要文件
VKEY_FILE="${BUILD_DIR}/${CIRCUIT_NAME}_vkey.json"
PROOF_FILE="${PROOF_DIR}/proof.json"
PUBLIC_FILE="${PROOF_DIR}/public.json"

if [ ! -f "$VKEY_FILE" ]; then
    echo "❌ 验证密钥不存在: $VKEY_FILE"
    echo "请先运行: npm run compile"
    exit 1
fi

if [ ! -f "$PROOF_FILE" ]; then
    echo "❌ 证明文件不存在: $PROOF_FILE"
    echo "请先运行: npm run prove"
    exit 1
fi

if [ ! -f "$PUBLIC_FILE" ]; then
    echo "❌ 公开输入文件不存在: $PUBLIC_FILE"
    echo "请先运行: npm run prove"
    exit 1
fi

echo "🔍 验证文件检查通过"

# 执行验证
echo "🔒 执行 Groth16 证明验证..."

if snarkjs groth16 verify "$VKEY_FILE" "$PUBLIC_FILE" "$PROOF_FILE"; then
    echo "✅ 证明验证成功!"
    echo ""
    echo "🎉 零知识证明有效："
    echo "   - 证明者知道哈希原象"
    echo "   - 原象确实产生了公开的哈希值"
    echo "   - 验证过程中未泄露原象信息"
    
    # 显示公开输入
    echo ""
    echo "📊 公开输入 (哈希值):"
    cat "$PUBLIC_FILE"
    
    # 性能统计
    echo ""
    echo "📈 性能统计:"
    PROOF_SIZE=$(stat -c%s "$PROOF_FILE" 2>/dev/null || stat -f%z "$PROOF_FILE" 2>/dev/null || echo "unknown")
    VKEY_SIZE=$(stat -c%s "$VKEY_FILE" 2>/dev/null || stat -f%z "$VKEY_FILE" 2>/dev/null || echo "unknown")
    
    echo "  - 证明大小: $PROOF_SIZE bytes"
    echo "  - 验证密钥大小: $VKEY_SIZE bytes"
    
    # 验证时间基准测试
    echo ""
    echo "⏱️  验证性能基准测试 (10次验证)..."
    
    start_time=$(date +%s%N)
    for i in {1..10}; do
        snarkjs groth16 verify "$VKEY_FILE" "$PUBLIC_FILE" "$PROOF_FILE" > /dev/null
    done
    end_time=$(date +%s%N)
    
    duration=$((($end_time - $start_time) / 1000000)) # 转换为毫秒
    avg_time=$(($duration / 10))
    
    echo "  - 平均验证时间: ${avg_time}ms"
    echo "  - 验证频率: $((1000 / $avg_time)) 次/秒"
    
else
    echo "❌ 证明验证失败!"
    echo ""
    echo "可能的原因:"
    echo "  - 证明文件损坏"
    echo "  - 公开输入不匹配"
    echo "  - 验证密钥不正确"
    echo "  - 电路实现有误"
    exit 1
fi

echo ""
echo "🎯 验证完成!"
