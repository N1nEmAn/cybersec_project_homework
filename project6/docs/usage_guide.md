# 使用指南

## 1. 快速开始

### 1.1 环境准备

确保您的系统已安装Python 3.8或更高版本：

```bash
python --version  # 应显示Python 3.8+
```

### 1.2 安装依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 或者使用虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 1.3 基本使用示例

```python
from src.ddh_psi import DDHPSIProtocol

# 准备数据
party1_data = ["apple", "banana", "cherry", "date"]
party2_data = [
    ("apple", 10),    # apple的关联值为10
    ("banana", 20),   # banana的关联值为20
    ("grape", 30),    # grape不在party1中
    ("date", 40)      # date的关联值为40
]

# 运行协议
protocol = DDHPSIProtocol()
intersection_size, intersection_sum = protocol.run_protocol(party1_data, party2_data)

print(f"交集大小: {intersection_size}")        # 输出: 3
print(f"交集总和: {intersection_sum}")          # 输出: 70 (10+20+40)
```

## 2. 详细使用说明

### 2.1 数据格式要求

**Party1数据格式**：
```python
# 列表形式，每个元素可以是字符串或字节
party1_data = ["item1", "item2", "item3"]
# 或者
party1_data = [b"item1", b"item2", b"item3"]
```

**Party2数据格式**：
```python
# 元组列表，每个元组包含(元素, 关联值)
party2_data = [
    ("item1", 100),    # item1的关联值为100
    ("item2", 200),    # item2的关联值为200
    ("item4", 300)     # item4的关联值为300
]
```

**注意事项**：
- 元素必须是可序列化的（字符串、字节串或整数）
- 关联值必须是整数
- 集合元素不能重复
- 空集合会返回(0, 0)

### 2.2 高级配置

```python
from src.ddh_psi import DDHPSIProtocol
from src.elliptic_curve import EllipticCurveGroup
from src.paillier_encryption import PaillierEncryption

# 自定义椭圆曲线参数
curve_group = EllipticCurveGroup(curve_name="prime256v1")

# 自定义Paillier参数
paillier = PaillierEncryption(key_size=2048)  # 更高安全性

# 创建协议实例
protocol = DDHPSIProtocol(
    curve_group=curve_group,
    paillier_encryption=paillier
)
```

### 2.3 分步执行

如果需要更细粒度的控制，可以分步执行协议：

```python
from src.ddh_psi import DDHPSIParty1, DDHPSIParty2

# 创建协议参与方
party1 = DDHPSIParty1(party1_data)
party2 = DDHPSIParty2(party2_data)

# 第一轮：Party1计算并发送
round1_message = party1.round1()

# 第二轮：Party2处理并回复
round2_message = party2.round2(round1_message)

# 第三轮：Party1最终计算
round3_message = party1.round3(round2_message)

# 获取结果
intersection_size, intersection_sum = party2.get_result(round3_message)
```

## 3. 性能优化指南

### 3.1 数据预处理

**排序优化**：
```python
# 对大型数据集进行预排序可以提高性能
party1_data = sorted(party1_data)
party2_data = sorted(party2_data, key=lambda x: x[0])
```

**批处理**：
```python
# 对于超大数据集，可以分批处理
def batch_process(large_data, batch_size=1000):
    results = []
    for i in range(0, len(large_data), batch_size):
        batch = large_data[i:i+batch_size]
        result = process_batch(batch)
        results.append(result)
    return combine_results(results)
```

### 3.2 并行计算

```python
import multiprocessing as mp

def parallel_hash_computation(data_chunks):
    """并行计算哈希值"""
    with mp.Pool() as pool:
        results = pool.map(compute_hash_chunk, data_chunks)
    return flatten(results)
```

### 3.3 内存管理

```python
# 使用生成器处理大型数据集
def data_generator(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield line.strip()

# 流式处理
party1_data = data_generator('party1_data.txt')
```

## 4. 错误处理和调试

### 4.1 常见错误及解决方案

**错误1：椭圆曲线点无效**
```python
# 错误信息: Invalid elliptic curve point
# 解决方案: 检查输入数据格式
try:
    result = protocol.run_protocol(party1_data, party2_data)
except ValueError as e:
    print(f"输入数据错误: {e}")
    # 检查数据格式和编码
```

**错误2：Paillier密钥不匹配**
```python
# 错误信息: Paillier key mismatch
# 解决方案: 确保使用相同的密钥参数
paillier = PaillierEncryption(key_size=1024)
protocol = DDHPSIProtocol(paillier_encryption=paillier)
```

**错误3：数据量过大导致内存溢出**
```python
# 解决方案: 使用流式处理或分批处理
def process_large_dataset(data, max_batch_size=10000):
    if len(data) > max_batch_size:
        return batch_process(data, max_batch_size)
    else:
        return protocol.run_protocol(data)
```

### 4.2 调试模式

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ddh_psi')

# 在协议中添加调试信息
protocol = DDHPSIProtocol(debug=True)
```

### 4.3 性能分析

```python
import time
import cProfile

def profile_protocol():
    start_time = time.time()
    result = protocol.run_protocol(party1_data, party2_data)
    end_time = time.time()
    
    print(f"执行时间: {end_time - start_time:.2f}秒")
    return result

# 详细性能分析
cProfile.run('profile_protocol()')
```

## 5. 安全使用建议

### 5.1 数据隐私保护

**敏感数据处理**：
```python
# 使用完毕后立即清理敏感数据
try:
    result = protocol.run_protocol(party1_data, party2_data)
finally:
    # 清理内存中的敏感数据
    del party1_data, party2_data
    import gc
    gc.collect()
```

**输入验证**：
```python
def validate_input(data):
    """验证输入数据的安全性"""
    if not data:
        raise ValueError("数据不能为空")
    
    if len(data) > 100000:  # 限制数据量
        raise ValueError("数据量过大，可能导致性能问题")
    
    # 检查数据类型和格式
    for item in data:
        if not isinstance(item, (str, bytes)):
            raise TypeError("不支持的数据类型")
```

### 5.2 网络安全

```python
# 在网络传输中使用TLS加密
import ssl
import socket

def secure_send(data, host, port):
    context = ssl.create_default_context()
    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            ssock.send(data)
```

### 5.3 访问控制

```python
# 实现简单的访问控制
class SecureDDHPSI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.protocol = DDHPSIProtocol()
    
    def run_protocol(self, party1_data, party2_data, client_key):
        if client_key != self.api_key:
            raise PermissionError("无效的API密钥")
        return self.protocol.run_protocol(party1_data, party2_data)
```

## 6. 实际应用场景

### 6.1 广告归因分析

```python
def advertising_attribution():
    # 广告商数据：用户ID列表
    advertiser_users = ["user1", "user2", "user3", "user4"]
    
    # 平台数据：用户ID和转化值
    platform_data = [
        ("user1", 100),  # user1带来100元收入
        ("user2", 150),  # user2带来150元收入
        ("user5", 200),  # user5不是广告商的用户
    ]
    
    protocol = DDHPSIProtocol()
    common_users, total_revenue = protocol.run_protocol(
        advertiser_users, platform_data
    )
    
    print(f"共同用户数: {common_users}")
    print(f"总收入: {total_revenue}元")
    return common_users, total_revenue
```

### 6.2 医疗数据分析

```python
def medical_data_analysis():
    # 医院A的患者ID
    hospital_a_patients = ["patient001", "patient002", "patient003"]
    
    # 医院B的患者ID和治疗费用
    hospital_b_data = [
        ("patient001", 5000),
        ("patient003", 3000),
        ("patient004", 2000),
    ]
    
    protocol = DDHPSIProtocol()
    common_patients, total_cost = protocol.run_protocol(
        hospital_a_patients, hospital_b_data
    )
    
    print(f"共同患者数: {common_patients}")
    print(f"总治疗费用: {total_cost}元")
```

### 6.3 金融风控

```python
def financial_risk_analysis():
    # 银行A的客户列表
    bank_a_customers = ["cust001", "cust002", "cust003"]
    
    # 银行B的客户和风险评分
    bank_b_data = [
        ("cust001", 85),  # 风险评分85
        ("cust002", 92),  # 风险评分92
        ("cust005", 78),
    ]
    
    protocol = DDHPSIProtocol()
    common_customers, avg_risk_score = protocol.run_protocol(
        bank_a_customers, bank_b_data
    )
    
    if common_customers > 0:
        avg_risk_score = avg_risk_score / common_customers
    
    print(f"共同客户数: {common_customers}")
    print(f"平均风险评分: {avg_risk_score:.2f}")
```

## 7. 最佳实践

### 7.1 数据准备

1. **数据清洗**：确保数据格式一致，去除重复项
2. **编码统一**：使用UTF-8编码处理文本数据
3. **大小写处理**：统一大小写或保持原样
4. **数据验证**：检查数据完整性和有效性

### 7.2 性能优化

1. **预排序**：对大型数据集进行排序
2. **批处理**：分批处理超大数据集
3. **并行计算**：利用多核处理器
4. **内存管理**：及时释放不需要的数据

### 7.3 安全考虑

1. **输入验证**：严格验证所有输入数据
2. **错误处理**：不要在错误信息中泄露敏感信息
3. **日志安全**：避免在日志中记录敏感数据
4. **密钥管理**：安全生成和存储密钥

## 8. 故障排除

### 8.1 性能问题

**问题**: 协议执行缓慢
**解决方案**:
1. 检查数据量大小，考虑分批处理
2. 启用并行计算
3. 优化硬件配置（CPU、内存）

**问题**: 内存使用过高
**解决方案**:
1. 使用流式处理
2. 及时清理中间结果
3. 减少同时处理的数据量

### 8.2 正确性问题

**问题**: 结果不正确
**解决方案**:
1. 验证输入数据格式
2. 检查数据编码是否一致
3. 运行测试用例验证实现

**问题**: 程序崩溃
**解决方案**:
1. 检查内存是否足够
2. 验证输入数据有效性
3. 查看详细错误日志

## 9. 联系和支持

### 9.1 技术文档

- 协议规范：`docs/protocol_specification.md`
- 安全分析：`docs/security_analysis.md`
- 实现细节：`docs/implementation_notes.md`

### 9.2 示例代码

- 基础示例：`examples/`目录
- 性能测试：`benchmarks/`目录
- 单元测试：`tests/`目录

### 9.3 常见问题

请查看项目README.md文件中的FAQ部分，或运行测试用例来验证安装是否正确。
