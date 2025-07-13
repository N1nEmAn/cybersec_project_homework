pragma circom 2.1.4;

include "./permutation.circom";

// Poseidon2 哈希主电路 - 支持 (256,2,5) 配置
// 公开输入: 哈希值 (用于验证)
// 私有输入: 原象 (2个字段元素)
template Poseidon2Hash() {
    // 私有输入: 2个预象元素
    signal private input preimage[2];
    
    // 公开输入: 期望的哈希值
    signal input hash;
    
    // 实例化 Poseidon2 置换 (状态大小 = 3)
    // 将2个输入扩展为3个状态元素: [preimage[0], preimage[1], 0]
    component perm = Poseidon2Permutation(3);
    
    // 初始化状态
    perm.inputs[0] <== preimage[0];
    perm.inputs[1] <== preimage[1]; 
    perm.inputs[2] <== 0;  // 填充零
    
    // 计算的哈希值是置换结果的第一个元素
    signal computedHash <== perm.out[0];
    
    // 约束: 计算的哈希必须等于提供的哈希
    hash === computedHash;
}

// 主组件 - 用于 Groth16 证明
component main{public [hash]} = Poseidon2Hash();
