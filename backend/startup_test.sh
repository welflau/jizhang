#!/bin/bash

# 启动测试脚本 - 用于验证数据备份和恢复功能

set -e

echo "=========================================="
echo "启动后端服务测试"
echo "=========================================="

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import flask" 2>/dev/null || { echo "错误: 未安装 flask"; exit 1; }
python3 -c "import flask_cors" 2>/dev/null || { echo "错误: 未安装 flask-cors"; exit 1; }

# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=development
export DATABASE_PATH=./data/visits.db

# 创建数据目录
mkdir -p data

# 启动服务
echo "启动 Flask 服务..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo "=========================================="

python3 app.py
