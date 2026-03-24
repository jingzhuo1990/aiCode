#!/bin/bash

# 快速启动脚本 - 一键配置和测试

echo "=========================================="
echo "  AI Coding Agent - Quick Start"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: 检查并激活虚拟环境
echo "Step 1: Checking virtual environment..."
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
fi

source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Step 2: 安装依赖
echo "Step 2: Installing dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 3: 配置环境变量
echo "Step 3: Configuring environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠ .env file created. Please edit it to add your API keys:${NC}"
    echo "   nano .env"
    echo ""
    echo "   Add at least one of:"
    echo "   ANTHROPIC_API_KEY=sk-ant-xxxxx"
    echo "   OPENAI_API_KEY=sk-xxxxx"
    echo ""
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# Step 4: 创建记忆目录
echo "Step 4: Setting up memory directory..."
mkdir -p .aicode_memory
echo -e "${GREEN}✓ Memory directory created${NC}"
echo ""

# Step 5: 测试安装
echo "Step 5: Testing installation..."
./test_installation.sh

echo ""
echo "=========================================="
echo "  🎉 Setup Complete!"
echo "=========================================="
echo ""
echo "Quick commands to try:"
echo ""
echo "1. Check configuration:"
echo "   python -m aicode info"
echo ""
echo "2. Generate code:"
echo "   python -m aicode generate 'create a fibonacci function'"
echo ""
echo "3. Use Agent mode:"
echo "   python -m aicode.cli_agent run 'analyze this directory'"
echo ""
echo "4. Interactive session:"
echo "   python -m aicode.cli_agent interactive"
echo ""
echo "5. Start API server:"
echo "   ./run_server.sh"
echo ""
echo "For more details, see START_HERE.md"
echo ""
