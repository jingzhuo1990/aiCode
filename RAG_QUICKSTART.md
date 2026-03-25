# 🚀 RAG 长期记忆快速上手

## 📋 3 步开始使用

### 第 1 步：安装依赖

```bash
# 方法 1: 使用自动脚本（推荐）
./setup_rag.sh

# 方法 2: 手动安装
pip install faiss-cpu sentence-transformers
```

### 第 2 步：测试

```bash
python test_rag.py
```

### 第 3 步：使用

```bash
# 存储记忆（使用 --use-rag 标志）
python -m aicode.cli_agent remember \
  "error_handling" \
  "使用 try-except 捕获异常并记录日志" \
  --use-rag \
  --category patterns \
  --importance 8

# 语义搜索
python -m aicode.cli_agent semantic-search "如何处理错误"
```

---

## 💡 RAG vs 关键词检索

### 关键词检索（现有）

```bash
python -m aicode.cli_agent search "错误处理"
```

**只能找到**：
- ✅ 包含 "错误" 或 "处理" 的记忆
- ❌ 找不到 "异常捕获"
- ❌ 找不到 "try-except"

### 语义检索（RAG）

```bash
python -m aicode.cli_agent semantic-search "如何处理错误"
```

**可以找到**：
- ✅ "错误处理方法"
- ✅ "异常捕获最佳实践"
- ✅ "try-except 使用指南"
- ✅ 任何语义相似的内容

---

## 📊 示例对比

### 存储 3 条记忆

```bash
python -m aicode.cli_agent remember \
  "error_handling" \
  "使用 try-except 捕获异常并记录到日志系统" \
  --use-rag --category patterns

python -m aicode.cli_agent remember \
  "exception_best_practice" \
  "捕获特定异常类型，避免裸 except" \
  --use-rag --category patterns

python -m aicode.cli_agent remember \
  "jwt_auth" \
  "使用 JWT token 实现无状态认证" \
  --use-rag --category patterns
```

### 搜索 "如何处理错误"

#### 关键词搜索

```bash
python -m aicode.cli_agent search "如何处理错误"
```

结果：
```
1. error_handling ✓
2. exception_best_practice ✗ (因为不包含 "错误" 或 "处理")
```

#### 语义搜索（RAG）

```bash
python -m aicode.cli_agent semantic-search "如何处理错误"
```

结果：
```
1. error_handling (相似度: 0.85) ✓
2. exception_best_practice (相似度: 0.78) ✓
3. logging_errors (相似度: 0.65) ✓
```

即使记忆中没有 "如何" "处理" "错误" 这些词，RAG 也能通过**语义理解**找到相关内容！

---

## 🎯 何时使用 RAG？

### ✅ 推荐使用 RAG

1. **代码模式和最佳实践**
   ```bash
   python -m aicode.cli_agent remember "pattern_name" "..." --use-rag
   ```

2. **项目架构和设计决策**
   ```bash
   python -m aicode.cli_agent remember "architecture" "..." --use-rag
   ```

3. **问题解决方案**
   ```bash
   python -m aicode.cli_agent remember "solution" "..." --use-rag
   ```

### ⚠️ 不需要 RAG

1. **简单配置项**
   ```bash
   python -m aicode.cli_agent remember "config_item" "value"  # 无需 --use-rag
   ```

2. **临时数据**
   ```bash
   python -m aicode.cli_agent remember "temp" "..."  # 无需 --use-rag
   ```

---

## 🔧 配置选项

### 默认配置（推荐）

```python
from aicode.memory.memory_manager import MemoryManager

# 自动启用 RAG（如果依赖已安装）
memory = MemoryManager(enable_rag=True)
```

### 禁用 RAG

```python
# 只使用传统长期记忆
memory = MemoryManager(enable_rag=False)
```

### 自定义模型

```python
from aicode.memory.rag_memory import RAGMemory

# 使用不同的 embedding 模型
rag = RAGMemory(
    storage_dir=".aicode_memory",
    model_name="paraphrase-MiniLM-L6-v2"  # 或其他模型
)
```

---

## 📦 依赖说明

### FAISS

- **用途**: 高效向量相似度搜索
- **大小**: ~10MB
- **CPU vs GPU**:
  - `faiss-cpu`: 适合大多数场景
  - `faiss-gpu`: 如果有 CUDA GPU

### Sentence Transformers

- **用途**: 生成文本 embeddings
- **大小**: 模型 ~100MB（首次下载）
- **模型**: `all-MiniLM-L6-v2`（384 维，质量/速度平衡）

---

## 🚨 故障排查

### 问题 1: 导入错误

```python
ImportError: RAG dependencies not installed.
```

**解决**:
```bash
pip install faiss-cpu sentence-transformers
```

### 问题 2: 首次启动慢

```
Loading embedding model: all-MiniLM-L6-v2...
Downloading... [这会花 1-2 分钟]
```

**原因**: 首次下载模型（~100MB）

**解决**: 等待下载完成，后续启动会很快

### 问题 3: RAG 未启用

```bash
python -m aicode.cli_agent semantic-search "query"
# 提示: RAG 未启用
```

**原因**: 依赖未安装或初始化失败

**检查**:
```bash
python -c "from aicode.memory.rag_memory import is_rag_available; print(is_rag_available())"
```

---

## 📈 性能参考

### 首次启动

```
Time: ~10-120 秒（下载模型）
```

### 后续启动

```
Time: ~0.5 秒（加载缓存模型）
```

### 添加记忆

```
100 条: ~5 秒
1000 条: ~30 秒
```

### 搜索

```
100 条记忆: ~50ms
1000 条记忆: ~200ms
10000 条记忆: ~500ms
```

---

## 🎓 完整文档

详细实现指南：[RAG_IMPLEMENTATION_GUIDE.md](RAG_IMPLEMENTATION_GUIDE.md)

---

## ✅ 检查清单

开始使用 RAG 前，确认：

- [ ] 已安装 `faiss-cpu`
- [ ] 已安装 `sentence-transformers`
- [ ] 运行 `python test_rag.py` 成功
- [ ] 至少存储了 3-5 条记忆
- [ ] 尝试语义搜索

---

**现在你可以开始使用强大的语义检索了！** 🚀

```bash
# 快速测试
python test_rag.py

# 开始使用
python -m aicode.cli_agent remember "key" "value" --use-rag
python -m aicode.cli_agent semantic-search "查询"
```
