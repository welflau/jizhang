#!/bin/bash

# smoke_test.sh - Category CRUD API Smoke Test
# 用途: 测试分类管理的后端API端点

set -e

BASE_URL="http://localhost:8080"
API_URL="$BASE_URL/api"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 临时变量存储
INCOME_CATEGORY_ID=""
EXPENSE_CATEGORY_ID=""

# 打印函数
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASSED_TESTS=$((PASSED_TESTS + 1))
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAILED_TESTS=$((FAILED_TESTS + 1))
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# HTTP 请求函数
http_get() {
    curl -s -w "\n%{http_code}" "$1"
}

http_post() {
    curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$2" "$1"
}

http_put() {
    curl -s -w "\n%{http_code}" -X PUT -H "Content-Type: application/json" -d "$2" "$1"
}

http_delete() {
    curl -s -w "\n%{http_code}" -X DELETE "$1"
}

# 检查响应状态码
check_status() {
    local response="$1"
    local expected="$2"
    local body=$(echo "$response" | head -n -1)
    local status=$(echo "$response" | tail -n 1)
    
    if [ "$status" = "$expected" ]; then
        return 0
    else
        echo "Expected: $expected, Got: $status"
        echo "Response: $body"
        return 1
    fi
}

# 检查服务是否运行
check_server() {
    print_header "检查服务器状态"
    print_test "服务器连接测试"
    
    if curl -s -f "$BASE_URL" > /dev/null 2>&1; then
        print_success "服务器运行正常"
        return 0
    else
        print_error "服务器未运行或无法连接"
        echo "请确保服务器在 $BASE_URL 上运行"
        exit 1
    fi
}

# 测试创建收入分类
test_create_income_category() {
    print_header "测试创建收入分类"
    
    print_test "创建收入分类 - 工资"
    local response=$(http_post "$API_URL/categories" '{
        "name": "工资",
        "type": "income",
        "icon": "💰",
        "color": "#4CAF50"
    }')
    
    if check_status "$response" "201"; then
        print_success "成功创建收入分类"
        INCOME_CATEGORY_ID=$(echo "$response" | head -n -1 | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        print_info "分类ID: $INCOME_CATEGORY_ID"
    else
        print_error "创建收入分类失败"
    fi
    
    print_test "创建收入分类 - 奖金"
    response=$(http_post "$API_URL/categories" '{
        "name": "奖金",
        "type": "income",
        "icon": "🎁",
        "color": "#8BC34A"
    }')
    
    if check_status "$response" "201"; then
        print_success "成功创建第二个收入分类"
    else
        print_error "创建第二个收入分类失败"
    fi
}

# 测试创建支出分类
test_create_expense_category() {
    print_header "测试创建支出分类"
    
    print_test "创建支出分类 - 餐饮"
    local response=$(http_post "$API_URL/categories" '{
        "name": "餐饮",
        "type": "expense",
        "icon": "🍔",
        "color": "#FF5722"
    }')
    
    if check_status "$response" "201"; then
        print_success "成功创建支出分类"
        EXPENSE_CATEGORY_ID=$(echo "$response" | head -n -1 | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        print_info "分类ID: $EXPENSE_CATEGORY_ID"
    else
        print_error "创建支出分类失败"
    fi
    
    print_test "创建支出分类 - 交通"
    response=$(http_post "$API_URL/categories" '{
        "name": "交通",
        "type": "expense",
        "icon": "🚗",
        "color": "#2196F3"
    }')
    
    if check_status "$response" "201"; then
        print_success "成功创建第二个支出分类"
    else
        print_error "创建第二个支出分类失败"
    fi
}

# 测试数据校验
test_validation() {
    print_header "测试数据校验"
    
    print_test "创建分类 - 缺少名称"
    local response=$(http_post "$API_URL/categories" '{
        "type": "income",
        "icon": "💰"
    }')
    
    if check_status "$response" "400"; then
        print_success "正确拒绝缺少名称的请求"
    else
        print_error "应该拒绝缺少名称的请求"
    fi
    
    print_test "创建分类 - 无效类型"
    response=$(http_post "$API_URL/categories" '{
        "name": "测试",
        "type": "invalid_type",
        "icon": "💰"
    }')
    
    if check_status "$response" "400"; then
        print_success "正确拒绝无效类型"
    else
        print_error "应该拒绝无效类型"
    fi
    
    print_test "创建分类 - 空名称"
    response=$(http_post "$API_URL/categories" '{
        "name": "",
        "type": "income",
        "icon": "💰"
    }')
    
    if check_status "$response" "400"; then
        print_success "正确拒绝空名称"
    else
        print_error "应该拒绝空名称"
    fi
}

# 测试获取分类列表
test_get_categories() {
    print_header "测试获取分类列表"
    
    print_test "获取所有分类"
    local response=$(http_get "$API_URL/categories")
    
    if check_status "$response" "200"; then
        local body=$(echo "$response" | head -n -1)
        if echo "$body" | grep -q "income" && echo "$body" | grep -q "expense"; then
            print_success "成功获取分类列表（包含收入和支出分组）"
        else
            print_error "分类列表格式不正确"
        fi
    else
        print_error "获取分类列表失败"
    fi
    
    print_test "获取收入分类"
    response=$(http_get "$API_URL/categories?type=income")
    
    if check_status "$response" "200"; then
        print_success "成功获取收入分类"
    else
        print_error "获取收入分类失败"
    fi
    
    print_test "获取支出分类"
    response=$(http_get "$API_URL/categories?type=expense")
    
    if check_status "$response" "200"; then
        print_success "成功获取支出分类"
    else
        print_error "获取支出分类失败"
    fi
}

# 测试更新分类
test_update_category() {
    print_header "测试更新分类"
    
    if [ -z "$INCOME_CATEGORY_ID" ]; then
        print_error "没有可用的分类ID进行更新测试"
        return
    fi
    
    print_test "更新分类名称和图标"
    local response=$(http_put "$API_URL/categories/$INCOME_CATEGORY_ID" '{
        "name": "工资收入",
        "icon": "💵",
        "color": "#4CAF50"
    }')
    
    if check_status "$response" "200"; then
        print_success "成功更新分类"
    else
        print_error "更新分类失败"
    fi
    
    print_test "更新不存在的分类"
    response=$(http_put "$API_URL/categories/nonexistent-id" '{
        "name": "测试",
        "icon": "💰"
    }')
    
    if check_status "$response" "404"; then
        print_success "正确处理不存在的分类"
    else
        print_error "应该返回404"
    fi
    
    print_test "更新分类 - 无效数据"
    response=$(http_put "$API_URL/categories/$INCOME_CATEGORY_ID" '{
        "name": ""
    }')
    
    if check_status "$response" "400"; then
        print_success "正确拒绝无效更新数据"
    else
        print_error "应该拒绝无效更新数据"
    fi
}

# 测试删除分类（无关联记录）
test_delete_category_no_records() {
    print_header "测试删除分类（无关联记录）"
    
    print_test "创建临时分类用于删除"
    local response=$(http_post "$API_URL/categories" '{
        "name": "临时分类",
        "type": "expense",
        "icon": "🗑️",
        "color": "#9E9E9E"
    }')
    
    local temp_id=$(echo "$response" | head -n -1 | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$temp_id" ]; then
        print_test "删除无关联记录的分类"
        response=$(http_delete "$API_URL/categories/$temp_id")
        
        if check_status "$response" "200"; then
            print_success "成功删除分类"
        else
            print_error "删除分类失败"
        fi
    else
        print_error "无法创建临时分类"
    fi
    
    print_test "删除不存在的分类"
    response=$(http_delete "$API_URL/categories/nonexistent-id")
    
    if check_status "$response" "404"; then
        print_success "正确处理不存在的分类"
    else
        print_error "应该返回404"
    fi
}

# 测试删除分类（有关联记录）
test_delete_category_with_records() {
    print_header "测试删除分类（有关联记录）"
    
    if [ -z "$EXPENSE_CATEGORY_ID" ]; then
        print_error "没有可用的分类ID进行测试"
        return
    fi
    
    print_test "创建关联记录"
    local response=$(http_post "$API_URL/records" '{
        "amount": 50.00,
        "category_id": "'"$EXPENSE_CATEGORY_ID"'",
        "type": "expense",
        "date": "2024-01-15",
        "description": "测试记录"
    }')
    
    if check_status "$response" "201"; then
        print_info "成功创建关联记录"
        
        print_test "尝试删除有关联记录的分类"
        response=$(http_delete "$API_URL/categories/$EXPENSE_CATEGORY_ID")
        
        if check_status "$response" "400" || check_status "$response" "409"; then
            print_success "正确阻止删除有关联记录的分类"
        else
            print_error "应该阻止删除有关联记录的分类"
        fi
    else
        print_info "无法创建关联记录，跳过此测试"
    fi
}

# 测试并发和边界情况
test_edge_cases() {
    print_header "测试边界情况"
    
    print_test "创建重名分类"
    local response=$(http_post "$API_URL/categories" '{
        "name": "工资",
        "type": "income",
        "icon": "💰"
    }')
    
    # 根据业务逻辑，可能允许或不允许重名
    local status=$(echo "$response" | tail -n 1)
    print_info "重名分类响应状态: $status"
    
    print_test "创建超长名称分类"
    response=$(http_post "$API_URL/categories" '{
        "name": "这是一个非常非常非常非常非常非常非常非常非常非常长的分类名称用于测试边界情况",
        "type": "income",
        "icon": "💰"
    }')
    
    status=$(echo "$response" | tail -n 1)
    if [ "$status" = "400" ] || [ "$status" = "201" ]; then
        print_success "正确处理超长名称"
    else
        print_error "超长名称处理异常"
    fi
    
    print_test "特殊字符处理"
    response=$(http_post "$API_URL/categories" '{
        "name": "测试<script>alert(1)</script>",
        "type": "income",
        "icon": "💰"
    }')
    
    status=$(echo "$response" | tail -n 1)
    print_info "特殊字符响应状态: $status"
}

# 测试权限验证（如果实现了认证）
test_authorization() {
    print_header "测试权限验证"
    
    print_test "无认证令牌访问（如果需要）"
    # 这里假设API可能需要认证，根据实际情况调整
    print_info "权限测试需要根据实际认证机制实现"
}

# 性能测试
test_performance() {
    print_header "性能测试"
    
    print_test "批量创建分类"
    local start_time=$(date +%s)
    
    for i in {1..10}; do
        http_post "$API_URL/categories" '{
            "name": "性能测试分类'$i'",
            "type": "expense",
            "icon": "📊",
            "color": "#607D8B"
        }' > /dev/null 2>&1
    done
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    print_info "创建10个分类耗时: ${duration}秒"
    
    if [ $duration -lt 5 ]; then
        print_success "性能测试通过"
    else
        print_error "性能可能需要优化"
    fi
}

# 清理测试数据
cleanup() {
    print_header "清理测试数据"
    print_info "测试完成，可以手动清理数据或重置数据库"
}

# 打印测试摘要
print_summary() {
    echo ""
    print_header "测试摘要"
    echo -e "总测试数: ${BLUE}$TOTAL_TESTS${NC}"
    echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "失败: ${RED}$FAILED_TESTS${NC}"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}✓ 所有测试通过！${NC}"
        exit 0
    else
        echo -e "\n${RED}✗ 有测试失败${NC}"
        exit 1
    fi
}

# 主测试流程
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║   Category CRUD API Smoke Test        ║"
    echo "║   分类管理API冒烟测试                  ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_server
    
    test_create_income_category
    test_create_expense_category
    test_validation
    test_get_categories
    test_update_category
    test_delete_category_no_records
    test_delete_category_with_records
    test_edge_cases
    test_authorization
    test_performance
    
    cleanup
    print_summary
}

# 运行测试
main