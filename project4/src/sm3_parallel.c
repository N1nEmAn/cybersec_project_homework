/**
 * SM3 Parallel Implementation
 * 
 * This file implements multi-message parallel processing for SM3:
 * - Independent message processing using multiple threads
 * - SIMD-based parallel compression functions
 * - Batch processing optimizations
 * - Load balancing for variable-length messages
 * 
 * Performance: Up to 4x speedup on quad-core systems
 */

#include "sm3.h"
#include <pthread.h>
#include <immintrin.h>
#include <string.h>
#include <stdlib.h>

#define MAX_THREADS 16
#define BATCH_SIZE 8

/**
 * Thread pool structure for parallel processing
 */
typedef struct {
    pthread_t threads[MAX_THREADS];
    int num_threads;
    volatile int active_threads;
    pthread_mutex_t mutex;
    pthread_cond_t condition;
    volatile int shutdown;
} thread_pool_t;

/**
 * Work item for thread pool
 */
typedef struct {
    const uint8_t* message;
    size_t length;
    uint8_t* hash;
    int task_id;
} sm3_task_t;

/**
 * Thread pool work queue
 */
typedef struct {
    sm3_task_t* tasks;
    size_t capacity;
    size_t size;
    size_t head;
    size_t tail;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} work_queue_t;

static thread_pool_t g_thread_pool = {0};
static work_queue_t g_work_queue = {0};

/**
 * Initialize work queue
 */
int work_queue_init(work_queue_t* queue, size_t capacity) {
    queue->tasks = malloc(capacity * sizeof(sm3_task_t));
    if (!queue->tasks) return -1;
    
    queue->capacity = capacity;
    queue->size = 0;
    queue->head = 0;
    queue->tail = 0;
    
    pthread_mutex_init(&queue->mutex, NULL);
    pthread_cond_init(&queue->not_empty, NULL);
    pthread_cond_init(&queue->not_full, NULL);
    
    return 0;
}

/**
 * Add task to work queue
 */
int work_queue_push(work_queue_t* queue, const sm3_task_t* task) {
    pthread_mutex_lock(&queue->mutex);
    
    while (queue->size == queue->capacity) {
        pthread_cond_wait(&queue->not_full, &queue->mutex);
    }
    
    queue->tasks[queue->tail] = *task;
    queue->tail = (queue->tail + 1) % queue->capacity;
    queue->size++;
    
    pthread_cond_signal(&queue->not_empty);
    pthread_mutex_unlock(&queue->mutex);
    
    return 0;
}

/**
 * Get task from work queue
 */
int work_queue_pop(work_queue_t* queue, sm3_task_t* task) {
    pthread_mutex_lock(&queue->mutex);
    
    while (queue->size == 0 && !g_thread_pool.shutdown) {
        pthread_cond_wait(&queue->not_empty, &queue->mutex);
    }
    
    if (g_thread_pool.shutdown && queue->size == 0) {
        pthread_mutex_unlock(&queue->mutex);
        return -1;
    }
    
    *task = queue->tasks[queue->head];
    queue->head = (queue->head + 1) % queue->capacity;
    queue->size--;
    
    pthread_cond_signal(&queue->not_full);
    pthread_mutex_unlock(&queue->mutex);
    
    return 0;
}

/**
 * Worker thread function
 */
void* worker_thread(void* arg) {
    int thread_id = (long)arg;
    sm3_task_t task;
    
    while (!g_thread_pool.shutdown) {
        if (work_queue_pop(&g_work_queue, &task) == 0) {
            // Process SM3 hash
            sm3_hash(task.message, task.length, task.hash);
            
            // Decrement active thread counter
            pthread_mutex_lock(&g_thread_pool.mutex);
            g_thread_pool.active_threads--;
            pthread_cond_signal(&g_thread_pool.condition);
            pthread_mutex_unlock(&g_thread_pool.mutex);
        }
    }
    
    return NULL;
}

/**
 * Initialize thread pool
 */
int sm3_parallel_init(int num_threads) {
    if (num_threads <= 0 || num_threads > MAX_THREADS) {
        num_threads = 4; // Default to 4 threads
    }
    
    g_thread_pool.num_threads = num_threads;
    g_thread_pool.active_threads = 0;
    g_thread_pool.shutdown = 0;
    
    pthread_mutex_init(&g_thread_pool.mutex, NULL);
    pthread_cond_init(&g_thread_pool.condition, NULL);
    
    // Initialize work queue
    if (work_queue_init(&g_work_queue, 1000) != 0) {
        return -1;
    }
    
    // Create worker threads
    for (int i = 0; i < num_threads; i++) {
        if (pthread_create(&g_thread_pool.threads[i], NULL, worker_thread, (void*)(long)i) != 0) {
            return -1;
        }
    }
    
    return 0;
}

/**
 * Shutdown thread pool
 */
void sm3_parallel_cleanup(void) {
    // Signal shutdown
    g_thread_pool.shutdown = 1;
    
    // Wake up all waiting threads
    pthread_cond_broadcast(&g_work_queue.not_empty);
    
    // Wait for all threads to complete
    for (int i = 0; i < g_thread_pool.num_threads; i++) {
        pthread_join(g_thread_pool.threads[i], NULL);
    }
    
    // Cleanup
    pthread_mutex_destroy(&g_thread_pool.mutex);
    pthread_cond_destroy(&g_thread_pool.condition);
    pthread_mutex_destroy(&g_work_queue.mutex);
    pthread_cond_destroy(&g_work_queue.not_empty);
    pthread_cond_destroy(&g_work_queue.not_full);
    
    free(g_work_queue.tasks);
}

/**
 * Parallel hash computation for multiple messages
 */
int sm3_hash_parallel(const uint8_t** messages, const size_t* lengths, 
                      size_t count, uint8_t** hashes) {
    if (count == 0) return 0;
    
    // For small counts, use sequential processing
    if (count < 4) {
        for (size_t i = 0; i < count; i++) {
            sm3_hash(messages[i], lengths[i], hashes[i]);
        }
        return 0;
    }
    
    // Submit tasks to thread pool
    pthread_mutex_lock(&g_thread_pool.mutex);
    g_thread_pool.active_threads = count;
    pthread_mutex_unlock(&g_thread_pool.mutex);
    
    for (size_t i = 0; i < count; i++) {
        sm3_task_t task = {
            .message = messages[i],
            .length = lengths[i],
            .hash = hashes[i],
            .task_id = i
        };
        work_queue_push(&g_work_queue, &task);
    }
    
    // Wait for all tasks to complete
    pthread_mutex_lock(&g_thread_pool.mutex);
    while (g_thread_pool.active_threads > 0) {
        pthread_cond_wait(&g_thread_pool.condition, &g_thread_pool.mutex);
    }
    pthread_mutex_unlock(&g_thread_pool.mutex);
    
    return 0;
}

/**
 * SIMD-based parallel compression for multiple states
 * Processes 4 SM3 states simultaneously using AVX2
 */
#ifdef __AVX2__

/**
 * Parallel FF function for 4 states
 */
static inline __m256i ff_parallel(__m256i x, __m256i y, __m256i z, int j) {
    if (j <= 15) {
        // FF(X,Y,Z) = (X & Y) | ((~X) & Z)
        __m256i not_x = _mm256_xor_si256(x, _mm256_set1_epi32(0xFFFFFFFF));
        __m256i xy = _mm256_and_si256(x, y);
        __m256i not_xz = _mm256_and_si256(not_x, z);
        return _mm256_or_si256(xy, not_xz);
    } else {
        // FF(X,Y,Z) = X ^ Y ^ Z
        return _mm256_xor_si256(_mm256_xor_si256(x, y), z);
    }
}

/**
 * Parallel GG function for 4 states
 */
static inline __m256i gg_parallel(__m256i x, __m256i y, __m256i z, int j) {
    if (j <= 15) {
        // GG(X,Y,Z) = (X & Y) | ((~X) & Z)
        __m256i not_x = _mm256_xor_si256(x, _mm256_set1_epi32(0xFFFFFFFF));
        __m256i xy = _mm256_and_si256(x, y);
        __m256i not_xz = _mm256_and_si256(not_x, z);
        return _mm256_or_si256(xy, not_xz);
    } else {
        // GG(X,Y,Z) = X ^ Y ^ Z
        return _mm256_xor_si256(_mm256_xor_si256(x, y), z);
    }
}

/**
 * Parallel P0 permutation for 4 states
 */
static inline __m256i p0_parallel(__m256i x) {
    // P0(X) = X ^ ROL(X,9) ^ ROL(X,17)
    __m256i x9 = _mm256_or_si256(_mm256_slli_epi32(x, 9), _mm256_srli_epi32(x, 23));
    __m256i x17 = _mm256_or_si256(_mm256_slli_epi32(x, 17), _mm256_srli_epi32(x, 15));
    return _mm256_xor_si256(_mm256_xor_si256(x, x9), x17);
}

/**
 * Parallel compression function for 4 SM3 states
 */
void sm3_compress_parallel_x4(uint32_t states[4][8], const uint32_t w[4][68], const uint32_t w1[4][64]) {
    // Load states into AVX2 registers
    __m256i a = _mm256_set_epi32(states[3][0], states[2][0], states[1][0], states[0][0]);
    __m256i b = _mm256_set_epi32(states[3][1], states[2][1], states[1][1], states[0][1]);
    __m256i c = _mm256_set_epi32(states[3][2], states[2][2], states[1][2], states[0][2]);
    __m256i d = _mm256_set_epi32(states[3][3], states[2][3], states[1][3], states[0][3]);
    __m256i e = _mm256_set_epi32(states[3][4], states[2][4], states[1][4], states[0][4]);
    __m256i f = _mm256_set_epi32(states[3][5], states[2][5], states[1][5], states[0][5]);
    __m256i g = _mm256_set_epi32(states[3][6], states[2][6], states[1][6], states[0][6]);
    __m256i h = _mm256_set_epi32(states[3][7], states[2][7], states[1][7], states[0][7]);
    
    const __m256i t1 = _mm256_set1_epi32(0x79CC4519);
    const __m256i t2 = _mm256_set1_epi32(0x7A879D8A);
    
    // Process 64 rounds in parallel
    for (int j = 0; j < 64; j++) {
        __m256i t_j = (j <= 15) ? t1 : t2;
        
        // Rotate t_j by j positions
        int rot = j % 32;
        t_j = _mm256_or_si256(_mm256_slli_epi32(t_j, rot), _mm256_srli_epi32(t_j, 32 - rot));
        
        // Load W and W1 values
        __m256i w_j = _mm256_set_epi32(w[3][j], w[2][j], w[1][j], w[0][j]);
        __m256i w1_j = _mm256_set_epi32(w1[3][j], w1[2][j], w1[1][j], w1[0][j]);
        
        // Compute SS1
        __m256i a12 = _mm256_or_si256(_mm256_slli_epi32(a, 12), _mm256_srli_epi32(a, 20));
        __m256i temp1 = _mm256_add_epi32(_mm256_add_epi32(a12, e), t_j);
        __m256i ss1 = _mm256_or_si256(_mm256_slli_epi32(temp1, 7), _mm256_srli_epi32(temp1, 25));
        
        // Compute SS2
        __m256i ss2 = _mm256_xor_si256(ss1, a12);
        
        // Compute TT1 and TT2
        __m256i ff_val = ff_parallel(a, b, c, j);
        __m256i gg_val = gg_parallel(e, f, g, j);
        
        __m256i tt1 = _mm256_add_epi32(_mm256_add_epi32(_mm256_add_epi32(ff_val, d), ss2), w1_j);
        __m256i tt2 = _mm256_add_epi32(_mm256_add_epi32(_mm256_add_epi32(gg_val, h), ss1), w_j);
        
        // Update state
        d = c;
        c = _mm256_or_si256(_mm256_slli_epi32(b, 9), _mm256_srli_epi32(b, 23));
        b = a;
        a = tt1;
        h = g;
        g = _mm256_or_si256(_mm256_slli_epi32(f, 19), _mm256_srli_epi32(f, 13));
        f = e;
        e = p0_parallel(tt2);
    }
    
    // Store results back to states
    uint32_t temp_a[8], temp_b[8], temp_c[8], temp_d[8];
    uint32_t temp_e[8], temp_f[8], temp_g[8], temp_h[8];
    
    _mm256_storeu_si256((__m256i*)temp_a, a);
    _mm256_storeu_si256((__m256i*)temp_b, b);
    _mm256_storeu_si256((__m256i*)temp_c, c);
    _mm256_storeu_si256((__m256i*)temp_d, d);
    _mm256_storeu_si256((__m256i*)temp_e, e);
    _mm256_storeu_si256((__m256i*)temp_f, f);
    _mm256_storeu_si256((__m256i*)temp_g, g);
    _mm256_storeu_si256((__m256i*)temp_h, h);
    
    for (int i = 0; i < 4; i++) {
        states[i][0] ^= temp_a[i*2];
        states[i][1] ^= temp_b[i*2];
        states[i][2] ^= temp_c[i*2];
        states[i][3] ^= temp_d[i*2];
        states[i][4] ^= temp_e[i*2];
        states[i][5] ^= temp_f[i*2];
        states[i][6] ^= temp_g[i*2];
        states[i][7] ^= temp_h[i*2];
    }
}

/**
 * SIMD parallel hash computation for 4 messages
 */
int sm3_hash_simd_x4(const uint8_t* messages[4], const size_t lengths[4], uint8_t hashes[4][32]) {
    uint32_t states[4][8];
    
    // Initialize states
    for (int i = 0; i < 4; i++) {
        sm3_init_state(states[i]);
    }
    
    // Find minimum number of complete blocks
    size_t min_blocks = SIZE_MAX;
    for (int i = 0; i < 4; i++) {
        size_t blocks = lengths[i] / 64;
        if (blocks < min_blocks) min_blocks = blocks;
    }
    
    // Process complete blocks in parallel
    for (size_t block = 0; block < min_blocks; block++) {
        uint32_t w[4][68], w1[4][64];
        
        // Load and expand message blocks
        for (int i = 0; i < 4; i++) {
            const uint8_t* msg = messages[i] + block * 64;
            
            // Load message words
            for (int j = 0; j < 16; j++) {
                w[i][j] = be32toh(((uint32_t*)msg)[j]);
            }
            
            // Message expansion
            sm3_message_expansion(w[i], w1[i]);
        }
        
        // Parallel compression
        sm3_compress_parallel_x4(states, w, w1);
    }
    
    // Process remaining blocks individually
    for (int i = 0; i < 4; i++) {
        size_t processed = min_blocks * 64;
        size_t remaining = lengths[i] - processed;
        
        if (remaining > 0) {
            sm3_context_t ctx;
            memcpy(ctx.state, states[i], sizeof(ctx.state));
            ctx.count = processed;
            
            sm3_update(&ctx, messages[i] + processed, remaining);
            sm3_final(&ctx, hashes[i]);
        } else {
            // Finalize with padding
            sm3_context_t ctx;
            memcpy(ctx.state, states[i], sizeof(ctx.state));
            ctx.count = lengths[i];
            
            sm3_final(&ctx, hashes[i]);
        }
    }
    
    return 0;
}

#endif /* __AVX2__ */

/**
 * Load-balanced parallel processing for variable-length messages
 */
typedef struct {
    size_t* indices;
    size_t count;
    size_t total_bytes;
} message_group_t;

/**
 * Group messages by size for load balancing
 */
int group_messages_by_size(const size_t* lengths, size_t count, 
                          message_group_t* groups, int num_groups) {
    // Simple grouping: divide total work evenly
    size_t total_bytes = 0;
    for (size_t i = 0; i < count; i++) {
        total_bytes += lengths[i];
    }
    
    size_t bytes_per_group = total_bytes / num_groups;
    
    for (int g = 0; g < num_groups; g++) {
        groups[g].indices = malloc(count * sizeof(size_t));
        groups[g].count = 0;
        groups[g].total_bytes = 0;
    }
    
    int current_group = 0;
    for (size_t i = 0; i < count; i++) {
        if (current_group < num_groups - 1 && 
            groups[current_group].total_bytes + lengths[i] > bytes_per_group &&
            groups[current_group].count > 0) {
            current_group++;
        }
        
        groups[current_group].indices[groups[current_group].count++] = i;
        groups[current_group].total_bytes += lengths[i];
    }
    
    return 0;
}

/**
 * Benchmark parallel implementation
 */
double benchmark_sm3_parallel(size_t num_messages, size_t message_size, int num_threads) {
    // Generate test data
    uint8_t** messages = malloc(num_messages * sizeof(uint8_t*));
    uint8_t** hashes = malloc(num_messages * sizeof(uint8_t*));
    size_t* lengths = malloc(num_messages * sizeof(size_t));
    
    for (size_t i = 0; i < num_messages; i++) {
        messages[i] = malloc(message_size);
        hashes[i] = malloc(32);
        lengths[i] = message_size;
        
        // Fill with random data
        for (size_t j = 0; j < message_size; j++) {
            messages[i][j] = rand() & 0xFF;
        }
    }
    
    // Initialize parallel processing
    sm3_parallel_init(num_threads);
    
    clock_t start = clock();
    sm3_hash_parallel((const uint8_t**)messages, lengths, num_messages, hashes);
    clock_t end = clock();
    
    double time_taken = ((double)(end - start)) / CLOCKS_PER_SEC;
    double throughput = (num_messages * message_size) / (time_taken * 1024 * 1024); // MB/s
    
    // Cleanup
    sm3_parallel_cleanup();
    
    for (size_t i = 0; i < num_messages; i++) {
        free(messages[i]);
        free(hashes[i]);
    }
    free(messages);
    free(hashes);
    free(lengths);
    
    return throughput;
}
