#!/bin/bash

# 密码学项目全套快速验证脚本 v2.0
# Quick verification script for all cryptography projects

echo "🔐 密码学项目作业集合 - 快速验证脚本"
echo "=============================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 验证结果统计
total_tests=0
passed_tests=0

# 函数：打印状态
print_status() {
    ((total_tests++))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        ((passed_tests++))
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

echo -e "${BLUE}开始验证六个密码学项目...${NC}"
echo ""

# Project 1: SM4分组密码实现与优化
echo -e "${YELLOW}📋 Project 1: SM4分组密码实现与优化${NC}"
if [ -d "project1" ]; then
    cd project1
    
    # 检查演示脚本
    if [ -f "demo_simple.py" ]; then
        python3 demo_simple.py >/dev/null 2>&1
        print_status $? "SM4功能验证"
    else
        # 编译测试
        make clean >/dev/null 2>&1
        if make >/dev/null 2>&1; then
            print_status 0 "SM4编译验证"
        else
            print_status 1 "SM4编译验证"
        fi
    fi
    cd ..
else
    print_status 1 "SM4功能验证 (目录不存在)"
fi
echo ""

# Project 2: 数字水印
echo -e "${YELLOW}📋 Project 2: 基于数字水印的图片泄露检测${NC}"
if [ -d "project2" ]; then
    cd project2
    if [ -f "simple_demo.py" ]; then
        python3 simple_demo.py >/dev/null 2>&1
        print_status $? "数字水印功能验证"
    else
        print_status 1 "数字水印功能验证"
    fi
    cd ..
else
    print_status 1 "数字水印功能验证 (目录不存在)"
fi
echo ""

# Project 3: Poseidon2哈希算法的Circom电路实现
echo -e "${YELLOW}📋 Project 3: Poseidon2哈希算法的Circom电路实现${NC}"
if [ -d "project3" ]; then
    cd project3
    if [ -f "scripts/demo.js" ]; then
        node scripts/demo.js >/dev/null 2>&1
        print_status $? "Circom电路演示"
    else
        print_status 1 "Circom电路演示"
    fi
    cd ..
else
    print_status 1 "Circom电路演示 (目录不存在)"
fi
echo ""

# Project 4: SM3哈希函数实现与安全分析
echo -e "${YELLOW}📋 Project 4: SM3哈希函数实现与安全分析${NC}"
if [ -d "project4" ]; then
    cd project4
    if [ -f "demo_simple.py" ]; then
        python3 demo_simple.py >/dev/null 2>&1
        print_status $? "SM3功能演示"
    else
        make clean >/dev/null 2>&1
        if make >/dev/null 2>&1; then
            print_status 0 "SM3编译验证"
        else
            print_status 1 "SM3编译验证"
        fi
    fi
    cd ..
else
    print_status 1 "SM3功能验证 (目录不存在)"
fi
echo ""

# Project 5: SM2椭圆曲线密码实现与攻击分析
echo -e "${YELLOW}📋 Project 5: SM2椭圆曲线密码实现与攻击分析${NC}"
if [ -d "project5" ]; then
    cd project5
    if [ -f "demo_simple.py" ]; then
        python3 demo_simple.py --quick >/dev/null 2>&1
        print_status $? "SM2功能演示"
    else
        print_status 1 "SM2功能演示"
    fi
    cd ..
else
    print_status 1 "SM2功能验证 (目录不存在)"
fi
echo ""

# Project 6: Google Password Checkup协议实现
echo -e "${YELLOW}📋 Project 6: Google Password Checkup协议实现${NC}"
if [ -d "project6" ]; then
    cd project6
    if [ -f "demo_simple.py" ]; then
        python3 demo_simple.py >/dev/null 2>&1
        print_status $? "Password Checkup协议验证"
    else
        print_status 1 "Password Checkup协议验证"
    fi
    cd ..
else
    print_status 1 "Password Checkup验证 (目录不存在)"
fi
echo ""

# 总结
echo "=============================================="
echo -e "${BLUE}验证完成！${NC}"
echo ""

# 计算通过率
if [ $total_tests -gt 0 ]; then
    pass_rate=$((passed_tests * 100 / total_tests))
    echo -e "${GREEN}🎉 验证通过率: $passed_tests/$total_tests ($pass_rate%)${NC}"
    
    if [ $pass_rate -eq 100 ]; then
        echo -e "${GREEN}✨ 完美！所有项目验证通过！${NC}"
    elif [ $pass_rate -ge 80 ]; then
        echo -e "${GREEN}🎯 很好！大部分项目功能正常！${NC}"
    else
        echo -e "${YELLOW}⚠️  需要进一步调试一些项目${NC}"
    fi
else
    echo -e "${RED}❌ 未找到任何可验证的项目${NC}"
fi

echo ""
echo "验证脚本执行完成！"
