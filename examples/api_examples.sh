#!/bin/bash

# API 使用示例脚本

echo "=== AI Coding Agent API 示例 ==="
echo ""

# 1. 健康检查
echo "1. 健康检查"
curl -X GET "http://localhost:8000/" | jq
echo -e "\n"

# 2. 获取配置信息
echo "2. 获取配置信息"
curl -X GET "http://localhost:8000/api/config" | jq
echo -e "\n"

# 3. 列出支持的模型
echo "3. 列出支持的模型"
curl -X GET "http://localhost:8000/api/models" | jq
echo -e "\n"

# 4. 生成代码
echo "4. 生成代码示例"
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "创建一个 Python 函数来判断一个数是否为质数",
    "provider": "claude",
    "language": "python"
  }' | jq
echo -e "\n"

# 5. 分析代码
echo "5. 分析代码示例"
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b):\n    return a + b",
    "provider": "claude",
    "language": "python"
  }' | jq
echo -e "\n"

# 6. 重构代码
echo "6. 重构代码示例"
curl -X POST "http://localhost:8000/api/refactor" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def calc(x,y):\n  z=x+y\n  return z",
    "refactor_type": "readability",
    "provider": "claude",
    "language": "python"
  }' | jq
echo -e "\n"

echo "=== 示例完成 ==="
