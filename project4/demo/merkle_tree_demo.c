#include "merkle_tree.h"
#include <stdio.h>

int main() {
    merkle_tree_t tree;
    uint8_t leaves[4][32] = {{0}};
    int num_leaves = 4;

    // 修复函数调用
    merkle_tree_build(&tree, leaves, num_leaves);

    printf("Merkle tree built successfully\n");
    return 0;
}
