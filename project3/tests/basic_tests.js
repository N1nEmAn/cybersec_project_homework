const { Poseidon2 } = require('../js/poseidon2.js');

async function testPoseidon2() {
    console.log('🧪 Poseidon2 基础功能测试');
    console.log('============================');

    const poseidon2 = new Poseidon2();

    // 测试用例 1: (256,3,5) 配置 - 3个输入元素
    console.log('\n📋 测试配置 (256,3,5):');
    const input3 = [123n, 456n, 789n];
    try {
        const hash3 = await poseidon2.hash(input3);
        console.log(`输入: [${input3.join(', ')}]`);
        console.log(`哈希: ${hash3}`);
        console.log('✅ 3输入测试通过');
    } catch (error) {
        console.log('❌ 3输入测试失败:', error.message);
    }

    // 测试用例 2: (256,2,5) 配置 - 2个输入元素
    console.log('\n📋 测试配置 (256,2,5):');
    const input2 = [123n, 456n];
    try {
        const hash2 = await poseidon2.hash(input2);
        console.log(`输入: [${input2.join(', ')}]`);
        console.log(`哈希: ${hash2}`);
        console.log('✅ 2输入测试通过');

        // 验证测试
        const isValid = await poseidon2.verify(input2, hash2);
        console.log(`验证结果: ${isValid ? '✅ 通过' : '❌ 失败'}`);
    } catch (error) {
        console.log('❌ 2输入测试失败:', error.message);
    }

    // 测试用例 3: 字符串转换
    console.log('\n📋 测试字符串输入:');
    const str1 = poseidon2.stringToField('hello');
    const str2 = poseidon2.stringToField('world');
    try {
        const hashStr = await poseidon2.hash([str1, str2]);
        console.log(`输入: ["hello", "world"]`);
        console.log(`字段值: [${str1}, ${str2}]`);
        console.log(`哈希: ${hashStr}`);
        console.log('✅ 字符串测试通过');
    } catch (error) {
        console.log('❌ 字符串测试失败:', error.message);
    }

    // 测试用例 4: 边界值测试
    console.log('\n📋 测试边界值:');
    const boundary = [0n, 1n];
    try {
        const hashBoundary = await poseidon2.hash(boundary);
        console.log(`输入: [${boundary.join(', ')}]`);
        console.log(`哈希: ${hashBoundary}`);
        console.log('✅ 边界值测试通过');
    } catch (error) {
        console.log('❌ 边界值测试失败:', error.message);
    }

    console.log('\n🎉 基础测试完成！');
}

// 运行测试
if (require.main === module) {
    testPoseidon2().catch(console.error);
}

module.exports = { testPoseidon2 };
