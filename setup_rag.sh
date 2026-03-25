#!/bin/bash
# RAG 记忆系统快速安装脚本

echo "🧠 RAG 记忆系统安装"
echo "=" 
echo ""

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo "✓ 找到虚拟环境"
    source .venv/bin/activate
else
    echo "⚠️  未找到虚拟环境，使用系统 Python"
fi

# 安装依赖
echo ""
echo "📦 安装依赖..."
pip install faiss-cpu sentence-transformers

# 更新 requirements.txt
echo ""
echo "📝 更新 requirements.txt..."
if ! grep -q "faiss-cpu" requirements.txt; then
    echo "faiss-cpu>=1.7.4" >> requirements.txt
fi
if ! grep -q "sentence-transformers" requirements.txt; then
    echo "sentence-transformers>=2.2.0" >> requirements.txt
fi

# 运行测试
echo ""
echo "🧪 运行测试..."
python test_rag.py

echo ""
echo "=" 
echo "✅ 安装完成！"
echo "="
echo ""
echo "快速使用:"
echo "  python -m aicode.cli_agent remember 'key' 'value' --use-rag"
echo "  python -m aicode.cli_agent semantic-search '查询'"
echo ""
