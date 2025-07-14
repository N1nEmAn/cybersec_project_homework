#ifndef MERKLE_TREE_H
#define MERKLE_TREE_H

#include <stdint.h>

typedef struct {
    uint8_t root_hash[32];
} merkle_tree_t;

void merkle_tree_build(merkle_tree_t *tree, uint8_t leaves[][32], int num_leaves);

#endif // MERKLE_TREE_H
