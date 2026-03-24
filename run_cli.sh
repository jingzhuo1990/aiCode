#!/bin/bash

# AI Coding Agent CLI 启动脚本

# 确保在项目根目录
cd "$(dirname "$0")"

# 激活虚拟环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "错误: 虚拟环境不存在，请先运行: python -m venv .venv"
    exit 1
fi

# 检查是否安装了依赖
if ! python -c "import anthropic" 2>/dev/null; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在"
    echo "正在创建 .env 文件..."
    cp .env.example .env
    echo "请编辑 .env 文件并填入你的 API keys"
    exit 1
fi

# 运行 CLI
python -m aicode "$@"
