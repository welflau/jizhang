#!/bin/bash

# 启动后端服务
cd "$(dirname "$0")"

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3"
    exit 1
fi

# 检查依赖
if ! python3 -c "import flask" 2>/dev/null; then
    echo "正在安装依赖..."
    pip3 install flask flask-cors
fi

# 启动服务
echo "正在启动后端服务..."
python3 app.py