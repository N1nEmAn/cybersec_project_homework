// Poseidon2 轮常数生成
// 基于 Grain LFSR 的确定性生成算法

class GrainLFSR {
    constructor() {
        // Grain LFSR 的初始状态
        this.state = new Array(80).fill(0);
        this.initialized = false;
    }

    // 初始化 LFSR 状态
    init(initSequence) {
        if (typeof initSequence === 'string') {
            // 从字符串生成初始状态
            for (let i = 0; i < Math.min(initSequence.length, 80); i++) {
                this.state[i] = initSequence.charCodeAt(i) % 2;
            }
        } else if (Array.isArray(initSequence)) {
            // 从数组生成初始状态
            for (let i = 0; i < Math.min(initSequence.length, 80); i++) {
                this.state[i] = initSequence[i] % 2;
            }
        } else {
            // 默认初始状态
            this.state.fill(1);
        }
        this.initialized = true;
    }

    // LFSR 反馈函数
    feedback() {
        // Grain LFSR 的反馈多项式
        // f(x) = x^80 + x^78 + x^72 + x^62 + x^57 + x^40 + x^36 + x^24 + x^21 + x^13 + x^9 + x^1 + 1
        const tapPositions = [80, 78, 72, 62, 57, 40, 36, 24, 21, 13, 9, 1, 0];
        
        let feedbackBit = 0;
        for (let pos of tapPositions) {
            if (pos < 80) {
                feedbackBit ^= this.state[pos];
            }
        }
        
        return feedbackBit;
    }

    // 生成下一个位
    nextBit() {
        if (!this.initialized) {
            this.init();
        }

        const outputBit = this.state[0];
        const feedback = this.feedback();
        
        // 移位寄存器
        for (let i = 0; i < 79; i++) {
            this.state[i] = this.state[i + 1];
        }
        this.state[79] = feedback;
        
        return outputBit;
    }

    // 生成指定长度的位序列
    generateBits(length) {
        const bits = [];
        for (let i = 0; i < length; i++) {
            bits.push(this.nextBit());
        }
        return bits;
    }

    // 生成字段元素
    generateFieldElement(bitLength = 254) {
        const bits = this.generateBits(bitLength);
        let element = 0n;
        
        for (let i = 0; i < bits.length; i++) {
            if (bits[i] === 1) {
                element |= (1n << BigInt(i));
            }
        }
        
        // 确保在字段范围内
        const fieldSize = BigInt("21888242871839275222246405745257275088548364400416034343698204186575808495617");
        return element % fieldSize;
    }
}

// Poseidon2 轮常数生成器
class Poseidon2Constants {
    constructor() {
        this.lfsr = new GrainLFSR();
    }

    // 生成所有轮常数
    generateRoundConstants(t, totalRounds) {
        // 初始化 LFSR
        const initSequence = "Poseidon2_constants_" + t + "_" + totalRounds;
        this.lfsr.init(initSequence);
        
        const constants = [];
        
        for (let round = 0; round < totalRounds; round++) {
            const roundConstants = [];
            for (let state = 0; state < t; state++) {
                roundConstants.push(this.lfsr.generateFieldElement());
            }
            constants.push(roundConstants);
        }
        
        return constants;
    }

    // 生成 (256,3,5) 配置的常数
    generateConstants_256_3_5() {
        const R_F = 8;
        const R_P = 56;
        const totalRounds = R_F + R_P;
        
        return this.generateRoundConstants(3, totalRounds);
    }

    // 生成 (256,2,5) 配置的常数
    generateConstants_256_2_5() {
        const R_F = 8;
        const R_P = 57;
        const totalRounds = R_F + R_P;
        
        return this.generateRoundConstants(2, totalRounds);
    }

    // 验证常数的安全性
    validateConstants(constants) {
        const validationResults = {
            nonZero: true,
            distinct: true,
            distribution: true
        };

        // 检查非零
        for (let round of constants) {
            for (let constant of round) {
                if (constant === 0n) {
                    validationResults.nonZero = false;
                    break;
                }
            }
            if (!validationResults.nonZero) break;
        }

        // 检查唯一性
        const allConstants = [];
        for (let round of constants) {
            allConstants.push(...round);
        }
        
        const uniqueConstants = new Set(allConstants);
        validationResults.distinct = uniqueConstants.size === allConstants.length;

        // 检查分布均匀性 (简化检查)
        const bitCounts = new Array(254).fill(0);
        for (let constant of allConstants) {
            for (let bit = 0; bit < 254; bit++) {
                if ((constant >> BigInt(bit)) & 1n) {
                    bitCounts[bit]++;
                }
            }
        }
        
        // 检查每个位置的 0/1 分布是否相对均匀
        const expectedCount = allConstants.length / 2;
        const tolerance = expectedCount * 0.2; // 20% 容差
        
        for (let count of bitCounts) {
            if (Math.abs(count - expectedCount) > tolerance) {
                validationResults.distribution = false;
                break;
            }
        }

        return validationResults;
    }

    // 导出常数到 JSON 格式
    exportToJSON(constants, config) {
        return {
            config: config,
            generated_at: new Date().toISOString(),
            constants: constants.map(round => 
                round.map(c => "0x" + c.toString(16))
            )
        };
    }

    // 从 JSON 导入常数
    importFromJSON(jsonData) {
        return jsonData.constants.map(round =>
            round.map(c => BigInt(c))
        );
    }
}

// 预计算的常数缓存
class ConstantsCache {
    constructor() {
        this.cache = new Map();
        this.generator = new Poseidon2Constants();
    }

    // 获取常数 (带缓存)
    getConstants(t, totalRounds) {
        const key = `${t}_${totalRounds}`;
        
        if (!this.cache.has(key)) {
            const constants = this.generator.generateRoundConstants(t, totalRounds);
            this.cache.set(key, constants);
        }
        
        return this.cache.get(key);
    }

    // 预生成常用配置的常数
    precomputeCommonConstants() {
        // (256,3,5) 配置
        this.getConstants(3, 64);
        
        // (256,2,5) 配置  
        this.getConstants(2, 65);
        
        console.log("预计算完成，缓存了常用配置的轮常数");
    }

    // 清除缓存
    clearCache() {
        this.cache.clear();
    }

    // 获取缓存统计
    getCacheStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    }
}

// 导出模块
module.exports = {
    GrainLFSR,
    Poseidon2Constants,
    ConstantsCache
};

// 测试和示例
if (require.main === module) {
    console.log("Poseidon2 轮常数生成测试");
    
    const generator = new Poseidon2Constants();
    
    // 生成 (256,3,5) 配置的常数
    const constants_3_5 = generator.generateConstants_256_3_5();
    console.log(`生成了 ${constants_3_5.length} 轮常数，每轮 3 个状态元素`);
    
    // 验证常数
    const validation = generator.validateConstants(constants_3_5);
    console.log("常数验证结果:", validation);
    
    // 显示前几个常数
    console.log("前 3 轮常数:");
    for (let i = 0; i < Math.min(3, constants_3_5.length); i++) {
        console.log(`Round ${i}:`, constants_3_5[i].map(c => "0x" + c.toString(16)));
    }
    
    // 测试缓存
    console.log("\n测试缓存系统:");
    const cache = new ConstantsCache();
    cache.precomputeCommonConstants();
    console.log("缓存统计:", cache.getCacheStats());
}
