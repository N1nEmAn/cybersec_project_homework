const { Poseidon2 } = require('../js/poseidon2.js');
const { Poseidon2Constants } = require('../js/constants.js');

// 测试套件
class Poseidon2TestSuite {
    constructor() {
        this.poseidon2 = new Poseidon2();
        this.constants = new Poseidon2Constants();
        this.testResults = [];
    }

    // 运行所有测试
    async runAllTests() {
        console.log('🧪 开始 Poseidon2 单元测试...\n');

        await this.testBasicHashing();
        await this.testInputValidation();
        await this.testConstantsGeneration();
        await this.testSboxFunction();
        await this.testLinearLayer();
        await this.testPermutation();
        await this.testPerformance();
        
        this.printSummary();
        return this.testResults.every(result => result.passed);
    }

    // 测试基本哈希功能
    async testBasicHashing() {
        console.log('📝 测试基本哈希功能...');

        try {
            const input1 = 123n;
            const input2 = 456n;
            
            const hash1 = await this.poseidon2.hash([input1, input2]);
            const hash2 = await this.poseidon2.hash([input1, input2]);
            
            // 确定性测试
            if (hash1 === hash2) {
                this.addTestResult('基本哈希确定性', true, 'same hash for same input');
            } else {
                this.addTestResult('基本哈希确定性', false, `hash1: ${hash1}, hash2: ${hash2}`);
            }

            // 不同输入产生不同哈希
            const hash3 = await this.poseidon2.hash([789n, 101112n]);
            if (hash1 !== hash3) {
                this.addTestResult('不同输入产生不同哈希', true, 'hashes are different');
            } else {
                this.addTestResult('不同输入产生不同哈希', false, 'collision detected');
            }

            // 验证功能
            const isValid = await this.poseidon2.verify([input1, input2], hash1);
            this.addTestResult('哈希验证功能', isValid, isValid ? 'verification passed' : 'verification failed');

        } catch (error) {
            this.addTestResult('基本哈希功能', false, error.message);
        }
    }

    // 测试输入验证
    async testInputValidation() {
        console.log('🔍 测试输入验证...');

        try {
            // 测试输入数量验证
            try {
                await this.poseidon2.hash([123n]); // 只有一个输入
                this.addTestResult('输入数量验证', false, 'should reject single input');
            } catch (error) {
                this.addTestResult('输入数量验证', true, 'correctly rejected invalid input count');
            }

            // 测试输入范围验证
            const fieldSize = this.poseidon2.getFieldSize();
            try {
                await this.poseidon2.hash([fieldSize, 123n]); // 超出范围
                this.addTestResult('输入范围验证', false, 'should reject out-of-range input');
            } catch (error) {
                this.addTestResult('输入范围验证', true, 'correctly rejected out-of-range input');
            }

            // 测试字符串转换
            const stringInput = "test";
            const fieldElement = this.poseidon2.stringToField(stringInput);
            if (fieldElement >= 0n && fieldElement < fieldSize) {
                this.addTestResult('字符串转字段元素', true, `converted: ${fieldElement}`);
            } else {
                this.addTestResult('字符串转字段元素', false, 'conversion out of range');
            }

        } catch (error) {
            this.addTestResult('输入验证', false, error.message);
        }
    }

    // 测试轮常数生成
    async testConstantsGeneration() {
        console.log('🔢 测试轮常数生成...');

        try {
            // 生成 (256,3,5) 配置的常数
            const constants_3_5 = this.constants.generateConstants_256_3_5();
            
            if (constants_3_5.length === 64) {
                this.addTestResult('轮常数数量 (3,5)', true, `generated ${constants_3_5.length} rounds`);
            } else {
                this.addTestResult('轮常数数量 (3,5)', false, `expected 64, got ${constants_3_5.length}`);
            }

            // 检查每轮有3个常数
            if (constants_3_5[0].length === 3) {
                this.addTestResult('每轮常数数量 (3,5)', true, 'each round has 3 constants');
            } else {
                this.addTestResult('每轮常数数量 (3,5)', false, `expected 3, got ${constants_3_5[0].length}`);
            }

            // 验证常数安全性
            const validation = this.constants.validateConstants(constants_3_5);
            this.addTestResult('常数非零性', validation.nonZero, 'all constants non-zero');
            this.addTestResult('常数唯一性', validation.distinct, 'all constants distinct');
            this.addTestResult('常数分布性', validation.distribution, 'good bit distribution');

            // 生成 (256,2,5) 配置的常数
            const constants_2_5 = this.constants.generateConstants_256_2_5();
            
            if (constants_2_5.length === 65) {
                this.addTestResult('轮常数数量 (2,5)', true, `generated ${constants_2_5.length} rounds`);
            } else {
                this.addTestResult('轮常数数量 (2,5)', false, `expected 65, got ${constants_2_5.length}`);
            }

        } catch (error) {
            this.addTestResult('轮常数生成', false, error.message);
        }
    }

    // 测试 S-box 函数
    async testSboxFunction() {
        console.log('📦 测试 S-box 函数...');

        try {
            // 测试基本 S-box 属性
            const zero = this.poseidon2.sbox(0n);
            if (zero === 0n) {
                this.addTestResult('S-box: 0^5 = 0', true, 'correct');
            } else {
                this.addTestResult('S-box: 0^5 = 0', false, `got ${zero}`);
            }

            const one = this.poseidon2.sbox(1n);
            if (one === 1n) {
                this.addTestResult('S-box: 1^5 = 1', true, 'correct');
            } else {
                this.addTestResult('S-box: 1^5 = 1', false, `got ${one}`);
            }

            // 测试一些已知值
            const two = this.poseidon2.sbox(2n);
            const expected_two = 32n; // 2^5 = 32
            if (two === expected_two) {
                this.addTestResult('S-box: 2^5 = 32', true, 'correct');
            } else {
                this.addTestResult('S-box: 2^5 = 32', false, `expected ${expected_two}, got ${two}`);
            }

            // 测试 S-box 在有限域上的正确性
            const fieldSize = this.poseidon2.getFieldSize();
            const largeInput = fieldSize - 1n;
            const result = this.poseidon2.sbox(largeInput);
            
            if (result >= 0n && result < fieldSize) {
                this.addTestResult('S-box 有限域范围', true, 'result in field');
            } else {
                this.addTestResult('S-box 有限域范围', false, 'result out of field');
            }

        } catch (error) {
            this.addTestResult('S-box 函数', false, error.message);
        }
    }

    // 测试线性层
    async testLinearLayer() {
        console.log('🔀 测试线性层...');

        try {
            // 测试基本线性变换
            const input = [1n, 2n, 3n];
            const output = this.poseidon2.linearLayer(input);
            
            if (output.length === 3) {
                this.addTestResult('线性层输出长度', true, 'correct length');
            } else {
                this.addTestResult('线性层输出长度', false, `expected 3, got ${output.length}`);
            }

            // 测试线性性质: f(a + b) = f(a) + f(b)
            const a = [1n, 0n, 0n];
            const b = [0n, 1n, 0n];
            const sum = [1n, 1n, 0n];
            
            const fa = this.poseidon2.linearLayer(a);
            const fb = this.poseidon2.linearLayer(b);
            const fsum = this.poseidon2.linearLayer(sum);
            
            const fieldSize = this.poseidon2.getFieldSize();
            const expected = [
                (fa[0] + fb[0]) % fieldSize,
                (fa[1] + fb[1]) % fieldSize,
                (fa[2] + fb[2]) % fieldSize
            ];
            
            if (JSON.stringify(fsum) === JSON.stringify(expected)) {
                this.addTestResult('线性层线性性', true, 'f(a+b) = f(a)+f(b)');
            } else {
                this.addTestResult('线性层线性性', false, 'linearity test failed');
            }

            // 测试零向量
            const zeroInput = [0n, 0n, 0n];
            const zeroOutput = this.poseidon2.linearLayer(zeroInput);
            const allZero = zeroOutput.every(x => x === 0n);
            
            this.addTestResult('线性层零向量', allZero, allZero ? 'f(0) = 0' : 'f(0) ≠ 0');

        } catch (error) {
            this.addTestResult('线性层', false, error.message);
        }
    }

    // 测试置换函数
    async testPermutation() {
        console.log('🔄 测试置换函数...');

        try {
            // 测试基本置换
            const input = [123n, 456n, 789n];
            const output = this.poseidon2.permutation(input);
            
            if (output.length === 3) {
                this.addTestResult('置换输出长度', true, 'correct length');
            } else {
                this.addTestResult('置换输出长度', false, `expected 3, got ${output.length}`);
            }

            // 测试确定性
            const output2 = this.poseidon2.permutation(input);
            if (JSON.stringify(output) === JSON.stringify(output2)) {
                this.addTestResult('置换确定性', true, 'same output for same input');
            } else {
                this.addTestResult('置换确定性', false, 'non-deterministic output');
            }

            // 测试不同输入产生不同输出
            const differentInput = [789n, 456n, 123n];
            const differentOutput = this.poseidon2.permutation(differentInput);
            
            if (JSON.stringify(output) !== JSON.stringify(differentOutput)) {
                this.addTestResult('置换区分性', true, 'different inputs give different outputs');
            } else {
                this.addTestResult('置换区分性', false, 'collision in permutation');
            }

        } catch (error) {
            this.addTestResult('置换函数', false, error.message);
        }
    }

    // 性能测试
    async testPerformance() {
        console.log('⚡ 测试性能...');

        try {
            const iterations = 100;
            const testInputs = Array.from({length: iterations}, (_, i) => [BigInt(i), BigInt(i + 1000)]);

            // 哈希性能测试
            const hashStart = Date.now();
            for (const inputs of testInputs) {
                await this.poseidon2.hash(inputs);
            }
            const hashEnd = Date.now();
            const hashTime = hashEnd - hashStart;
            const hashRate = (iterations * 1000) / hashTime;

            this.addTestResult('哈希性能', true, `${hashRate.toFixed(2)} hashes/sec`);

            // 批量哈希测试
            const batchStart = Date.now();
            await this.poseidon2.batchHash(testInputs);
            const batchEnd = Date.now();
            const batchTime = batchEnd - batchStart;
            const batchRate = (iterations * 1000) / batchTime;

            this.addTestResult('批量哈希性能', true, `${batchRate.toFixed(2)} hashes/sec`);

            // 性能比较
            if (batchRate >= hashRate * 0.8) {
                this.addTestResult('批量处理效率', true, 'batch processing efficient');
            } else {
                this.addTestResult('批量处理效率', false, 'batch processing inefficient');
            }

        } catch (error) {
            this.addTestResult('性能测试', false, error.message);
        }
    }

    // 添加测试结果
    addTestResult(testName, passed, details) {
        const result = { testName, passed, details };
        this.testResults.push(result);
        
        const status = passed ? '✅' : '❌';
        console.log(`  ${status} ${testName}: ${details}`);
    }

    // 打印测试摘要
    printSummary() {
        const totalTests = this.testResults.length;
        const passedTests = this.testResults.filter(r => r.passed).length;
        const failedTests = totalTests - passedTests;

        console.log('\n📊 测试摘要');
        console.log('=================');
        console.log(`总测试数: ${totalTests}`);
        console.log(`通过: ${passedTests} ✅`);
        console.log(`失败: ${failedTests} ❌`);
        console.log(`成功率: ${((passedTests / totalTests) * 100).toFixed(2)}%`);

        if (failedTests > 0) {
            console.log('\n❌ 失败的测试:');
            this.testResults
                .filter(r => !r.passed)
                .forEach(r => console.log(`  - ${r.testName}: ${r.details}`));
        }

        console.log('\n🎯 测试完成!');
    }
}

// 主函数
async function main() {
    const testSuite = new Poseidon2TestSuite();
    const allPassed = await testSuite.runAllTests();
    
    process.exit(allPassed ? 0 : 1);
}

// 如果直接运行此文件，执行测试
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { Poseidon2TestSuite };
