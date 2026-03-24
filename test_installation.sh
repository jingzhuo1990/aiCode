#!/bin/bash

# 测试安装脚本 - 验证项目是否正确安装

echo "=========================================="
echo "  AI Coding Agent - Installation Test"
echo "=========================================="
echo ""

# 切换到项目目录
cd "$(dirname "$0")"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
PASS=0
FAIL=0

# 测试函数
test_step() {
    local description=$1
    local command=$2

    echo -n "Testing: $description ... "

    if eval $command > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAIL++))
        return 1
    fi
}

echo "1. Checking Python Environment"
echo "================================"

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✓${NC} Virtual environment activated: $VIRTUAL_ENV"
else
    echo -e "${YELLOW}⚠${NC} Virtual environment not activated"
    echo "   Run: source .venv/bin/activate"
fi

# 检查 Python 版本
PYTHON_VERSION=$(python --version 2>&1)
echo "Python version: $PYTHON_VERSION"

echo ""
echo "2. Checking Project Structure"
echo "================================"

test_step "aicode package exists" "[ -d 'aicode' ]"
test_step "CLI module exists" "[ -f 'aicode/cli.py' ]"
test_step "Agent CLI exists" "[ -f 'aicode/cli_agent.py' ]"
test_step "Server module exists" "[ -f 'aicode/server.py' ]"
test_step "Memory module exists" "[ -d 'aicode/memory' ]"
test_step "Architectures module exists" "[ -d 'aicode/architectures' ]"

echo ""
echo "3. Checking Dependencies"
echo "================================"

test_step "anthropic package" "python -c 'import anthropic'"
test_step "openai package" "python -c 'import openai'"
test_step "fastapi package" "python -c 'import fastapi'"
test_step "click package" "python -c 'import click'"
test_step "rich package" "python -c 'import rich'"
test_step "pydantic package" "python -c 'import pydantic'"

echo ""
echo "4. Checking Configuration"
echo "================================"

test_step ".env.example exists" "[ -f '.env.example' ]"

if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"

    if grep -q "ANTHROPIC_API_KEY=sk-" .env 2>/dev/null; then
        echo -e "${GREEN}✓${NC} ANTHROPIC_API_KEY configured"
    elif grep -q "ANTHROPIC_API_KEY=" .env 2>/dev/null; then
        echo -e "${YELLOW}⚠${NC} ANTHROPIC_API_KEY present but may not be set"
    else
        echo -e "${RED}✗${NC} ANTHROPIC_API_KEY not found"
    fi

    if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        echo -e "${GREEN}✓${NC} OPENAI_API_KEY configured"
    elif grep -q "OPENAI_API_KEY=" .env 2>/dev/null; then
        echo -e "${YELLOW}⚠${NC} OPENAI_API_KEY present but may not be set"
    fi
else
    echo -e "${RED}✗${NC} .env file not found"
    echo "   Run: cp .env.example .env"
fi

echo ""
echo "5. Testing Basic Imports"
echo "================================"

test_step "Import config" "python -c 'from aicode.config import settings'"
test_step "Import models" "python -c 'from aicode.models import ClaudeModel, OpenAIModel'"
test_step "Import agents" "python -c 'from aicode.agent import CodeGenerator, CodeModifier'"
test_step "Import memory" "python -c 'from aicode.memory import MemoryManager'"
test_step "Import architectures" "python -c 'from aicode.architectures import ReActAgent, PlanExecuteAgent'"

echo ""
echo "6. Testing CLI Commands"
echo "================================"

test_step "CLI help command" "python -m aicode --help"
test_step "CLI info command" "python -m aicode info"
test_step "Agent CLI help" "python -m aicode.cli_agent --help"

echo ""
echo "=========================================="
echo "  Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASS${NC}"
if [ $FAIL -gt 0 ]; then
    echo -e "${RED}Failed: $FAIL${NC}"
else
    echo -e "Failed: 0"
fi
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Your installation is ready.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure your API keys in .env file"
    echo "2. Try: python -m aicode generate 'create a hello world function'"
    echo "3. Or read START_HERE.md for more examples"
else
    echo -e "${RED}✗ Some tests failed. Please check the errors above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "1. Install dependencies: pip install -r requirements.txt"
    echo "2. Create .env file: cp .env.example .env"
    echo "3. Activate venv: source .venv/bin/activate"
fi

echo ""
