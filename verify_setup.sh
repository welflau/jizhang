#!/bin/bash

echo "=========================================="
echo "用户注册与登录系统 - 环境验证脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查结果统计
PASS=0
FAIL=0

# 检查函数
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 已安装 (版本: $($1 --version 2>&1 | head -n 1))"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 未安装"
        ((FAIL++))
        return 1
    fi
}

check_python_package() {
    if python3 -c "import $1" 2>/dev/null; then
        VERSION=$(python3 -c "import $1; print($1.__version__)" 2>/dev/null || echo "未知版本")
        echo -e "${GREEN}✓${NC} Python包 $1 已安装 (版本: $VERSION)"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗${NC} Python包 $1 未安装"
        ((FAIL++))
        return 1
    fi
}

check_node_package() {
    if npm list $1 &> /dev/null || npm list -g $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} Node包 $1 已安装"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗${NC} Node包 $1 未安装"
        ((FAIL++))
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} 文件存在: $1"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗${NC} 文件缺失: $1"
        ((FAIL++))
        return 1
    fi
}

check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} 目录存在: $1"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗${NC} 目录缺失: $1"
        ((FAIL++))
        return 1
    fi
}

echo "1. 检查基础环境"
echo "----------------------------------------"
check_command python3
check_command node
check_command npm
check_command pip3
echo ""

echo "2. 检查Python版本要求 (>= 3.8)"
echo "----------------------------------------"
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$PYTHON_VERSION >= 3.8" | bc -l) )); then
    echo -e "${GREEN}✓${NC} Python版本符合要求: $PYTHON_VERSION"
    ((PASS++))
else
    echo -e "${RED}✗${NC} Python版本过低: $PYTHON_VERSION (需要 >= 3.8)"
    ((FAIL++))
fi
echo ""

echo "3. 检查Node版本要求 (>= 14)"
echo "----------------------------------------"
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -ge 14 ]; then
    echo -e "${GREEN}✓${NC} Node版本符合要求: $(node -v)"
    ((PASS++))
else
    echo -e "${RED}✗${NC} Node版本过低: $(node -v) (需要 >= 14)"
    ((FAIL++))
fi
echo ""

echo "4. 检查后端Python依赖"
echo "----------------------------------------"
check_python_package fastapi
check_python_package uvicorn
check_python_package pydantic
check_python_package sqlalchemy
check_python_package bcrypt
check_python_package "jose" # PyJWT
check_python_package passlib
check_python_package "python_multipart"
echo ""

echo "5. 检查项目目录结构"
echo "----------------------------------------"
check_directory "backend"
check_directory "frontend"
check_directory "backend/app"
check_directory "backend/app/models"
check_directory "backend/app/routes"
check_directory "backend/app/utils"
check_directory "frontend/src"
check_directory "frontend/src/components"
check_directory "frontend/src/services"
echo ""

echo "6. 检查关键配置文件"
echo "----------------------------------------"
check_file "backend/.env"
check_file "backend/requirements.txt"
check_file "backend/main.py"
check_file "frontend/package.json"
check_file "frontend/.env"
echo ""

echo "7. 检查环境变量配置"
echo "----------------------------------------"
if [ -f "backend/.env" ]; then
    if grep -q "SECRET_KEY" backend/.env; then
        echo -e "${GREEN}✓${NC} SECRET_KEY 已配置"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} SECRET_KEY 未配置"
        ((FAIL++))
    fi
    
    if grep -q "DATABASE_URL" backend/.env; then
        echo -e "${GREEN}✓${NC} DATABASE_URL 已配置"
        ((PASS++))
    else
        echo -e "${YELLOW}!${NC} DATABASE_URL 未配置 (可选)"
    fi
    
    if grep -q "JWT_SECRET_KEY" backend/.env; then
        echo -e "${GREEN}✓${NC} JWT_SECRET_KEY 已配置"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} JWT_SECRET_KEY 未配置"
        ((FAIL++))
    fi
else
    echo -e "${RED}✗${NC} backend/.env 文件不存在"
fi
echo ""

echo "8. 检查前端React依赖"
echo "----------------------------------------"
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} node_modules 目录存在"
    ((PASS++))
    
    cd frontend
    check_node_package "react"
    check_node_package "react-router-dom"
    check_node_package "axios"
    cd ..
else
    echo -e "${RED}✗${NC} node_modules 目录不存在，请运行: cd frontend && npm install"
    ((FAIL++))
fi
echo ""

echo "9. 检查数据库连接"
echo "----------------------------------------"
if [ -f "backend/.env" ]; then
    DB_URL=$(grep "DATABASE_URL" backend/.env | cut -d'=' -f2)
    if [ ! -z "$DB_URL" ]; then
        if [[ $DB_URL == sqlite* ]]; then
            DB_FILE=$(echo $DB_URL | sed 's/sqlite:\/\/\///')
            if [ -f "$DB_FILE" ]; then
                echo -e "${GREEN}✓${NC} SQLite数据库文件存在: $DB_FILE"
                ((PASS++))
            else
                echo -e "${YELLOW}!${NC} SQLite数据库文件不存在，将在首次运行时创建"
            fi
        else
            echo -e "${YELLOW}!${NC} 使用外部数据库，请确保数据库服务正在运行"
        fi
    fi
fi
echo ""

echo "10. 检查端口占用"
echo "----------------------------------------"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}!${NC} 端口 8000 已被占用 (后端默认端口)"
else
    echo -e "${GREEN}✓${NC} 端口 8000 可用"
    ((PASS++))
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}!${NC} 端口 3000 已被占用 (前端默认端口)"
else
    echo -e "${GREEN}✓${NC} 端口 3000 可用"
    ((PASS++))
fi
echo ""

echo "=========================================="
echo "验证结果汇总"
echo "=========================================="
echo -e "通过: ${GREEN}$PASS${NC}"
echo -e "失败: ${RED}$FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ 所有检查通过！环境配置完成。${NC}"
    echo ""
    echo "后续步骤："
    echo "1. 启动后端: cd backend && uvicorn main:app --reload"
    echo "2. 启动前端: cd frontend && npm start"
    echo "3. 访问应用: http://localhost:3000"
    exit 0
else
    echo -e "${RED}✗ 存在 $FAIL 项配置问题，请修复后重新验证。${NC}"
    echo ""
    echo "常见解决方案："
    echo "- 安装Python依赖: cd backend && pip3 install -r requirements.txt"
    echo "- 安装Node依赖: cd frontend && npm install"
    echo "- 创建环境变量文件: cp backend/.env.example backend/.env"
    echo "- 配置SECRET_KEY: 在backend/.env中设置随机密钥"
    exit 1
fi