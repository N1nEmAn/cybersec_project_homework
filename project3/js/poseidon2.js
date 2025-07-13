const { buildPoseidon } = require("circomlibjs");

class Poseidon2 {
    constructor() {
        this.poseidon = null;
        this.initialized = false;
    }

    async init() {
        if (!this.initialized) {
            this.poseidon = await buildPoseidon();
            this.initialized = true;
        }
    }

    // Poseidon2 哈希函数实现
    // 基于论文 https://eprint.iacr.org/2023/323.pdf
    async hash(inputs) {
        await this.init();
        
        if (inputs.length !== 2) {
            throw new Error("Poseidon2 currently supports 2 inputs only");
        }

        // 验证输入是否在有效范围内
        for (let input of inputs) {
            if (typeof input === 'string') {
                input = BigInt(input);
            }
            if (input < 0 || input >= this.getFieldSize()) {
                throw new Error("Input out of field range");
            }
        }

        // 使用 Poseidon 作为基础 (临时实现)
        // 实际的 Poseidon2 需要实现优化的置换函数
        return this.poseidon(inputs);
    }

    // 获取有限域大小
    getFieldSize() {
        return BigInt("21888242871839275222246405745257275088548364400416034343698204186575808495617");
    }

    // Poseidon2 置换函数
    permutation(state) {
        // 参数: (n,t,d) = (256,3,5)
        const t = 3;          // 状态大小
        const d = 5;          // S-box 幂次
        const R_F = 8;        // 完整轮数
        const R_P = 56;       // 部分轮数
        
        let currentState = [...state];
        
        // 执行所有轮次
        for (let round = 0; round < R_F + R_P; round++) {
            // 添加轮常数
            currentState = this.addRoundConstants(currentState, round);
            
            // S-box 层
            if (round < R_F / 2 || round >= R_F / 2 + R_P) {
                // 完整轮: 对所有元素应用 S-box
                currentState = currentState.map(x => this.sbox(x));
            } else {
                // 部分轮: 只对第一个元素应用 S-box
                currentState[0] = this.sbox(currentState[0]);
            }
            
            // 线性层 (MDS 矩阵乘法)
            currentState = this.linearLayer(currentState);
        }
        
        return currentState;
    }

    // S-box: x^5 在有限域上
    sbox(x) {
        const fieldSize = this.getFieldSize();
        const bigX = BigInt(x);
        
        // 计算 x^5 mod p
        let result = bigX;
        for (let i = 1; i < 5; i++) {
            result = (result * bigX) % fieldSize;
        }
        
        return result;
    }

    // 添加轮常数
    addRoundConstants(state, round) {
        const constants = this.getRoundConstants(round);
        return state.map((x, i) => {
            const fieldSize = this.getFieldSize();
            return (BigInt(x) + BigInt(constants[i])) % fieldSize;
        });
    }

    // 线性层: MDS 矩阵乘法
    linearLayer(state) {
        // 3x3 MDS 矩阵
        const matrix = [
            [2n, 1n, 1n],
            [1n, 2n, 1n],
            [1n, 1n, 3n]
        ];
        
        const fieldSize = this.getFieldSize();
        const result = [];
        
        for (let i = 0; i < 3; i++) {
            let sum = 0n;
            for (let j = 0; j < 3; j++) {
                sum += matrix[i][j] * BigInt(state[j]);
            }
            result[i] = sum % fieldSize;
        }
        
        return result;
    }

    // 获取轮常数
    getRoundConstants(round) {
        // 简化的轮常数生成
        // 实际实现应该使用 Grain LFSR
        const baseConstants = [
            0x10d7ac06a4fd97f5n,
            0x0abcd5c3f9e8d2e5n,
            0x1a2b3c4d5e6f7a8bn
        ];
        
        return baseConstants.map(c => c + BigInt(round) * 0x1000n);
    }

    // 将字符串转换为字段元素
    stringToField(str) {
        const encoder = new TextEncoder();
        const bytes = encoder.encode(str);
        let result = 0n;
        
        for (let i = 0; i < bytes.length && i < 31; i++) {
            result = result * 256n + BigInt(bytes[i]);
        }
        
        return result % this.getFieldSize();
    }

    // 将数字转换为字段元素
    numberToField(num) {
        return BigInt(num) % this.getFieldSize();
    }

    // 批量哈希
    async batchHash(inputsList) {
        const results = [];
        for (const inputs of inputsList) {
            results.push(await this.hash(inputs));
        }
        return results;
    }

    // 验证哈希
    async verify(inputs, expectedHash) {
        const computedHash = await this.hash(inputs);
        return computedHash === expectedHash;
    }
}

// 导出模块
module.exports = { Poseidon2 };

// 使用示例
async function example() {
    const poseidon2 = new Poseidon2();
    
    // 测试输入
    const input1 = 123n;
    const input2 = 456n;
    
    try {
        const hash = await poseidon2.hash([input1, input2]);
        console.log(`Poseidon2 Hash: ${hash}`);
        
        // 验证
        const isValid = await poseidon2.verify([input1, input2], hash);
        console.log(`Verification: ${isValid}`);
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// 如果直接运行此文件，执行示例
if (require.main === module) {
    example();
}
