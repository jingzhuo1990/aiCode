# 🔍 RAG 长期记忆实现指南

## 📋 目录

- [为什么需要 RAG？](#为什么需要-rag)
- [实现方案对比](#实现方案对比)
- [推荐方案：本地 RAG](#推荐方案本地-rag)
- [完整实现步骤](#完整实现步骤)
- [代码实现](#代码实现)
- [使用示例](#使用示例)

---

## 🤔 为什么需要 RAG？

### 当前系统的限制

```python
# ❌ 当前只支持关键词匹配
memory.search("如何处理错误")
# 只能找到包含 "处理" 或 "错误" 关键词的记忆
# 找不到 "异常捕获" "try-except" 等语义相似的内容
```

### RAG 的优势

```python
# ✅ RAG 支持语义检索
rag_memory.semantic_search("如何处理错误")
# 可以找到：
# - "异常捕获最佳实践"
# - "try-except 使用指南"
# - "错误日志记录方法"
# 即使关键词不匹配，但语义相似
```

### 对比表

| 特性 | 关键词检索 | RAG 语义检索 |
|-----|-----------|-------------|
| **匹配方式** | 子串匹配 | 语义相似度 |
| **查询** | "错误处理" | "如何处理错误" |
| **能找到** | "错误处理方法" | "异常捕获"、"try-except" |
| **准确性** | 精确但狭窄 | 更智能更广 |
| **实现难度** | 简单 | 中等 |
| **性能** | 快 | 稍慢（需要向量计算） |

---

## 🎯 实现方案对比

### 方案 A：本地 RAG（推荐 ⭐）

**技术栈**：
- **向量数据库**: FAISS (Facebook AI Similarity Search)
- **Embedding 模型**: sentence-transformers (如 `all-MiniLM-L6-v2`)

**优点**：
- ✅ **完全免费** - 无 API 费用
- ✅ **完全本地** - 数据不离开电脑
- ✅ **离线可用** - 无需网络
- ✅ **快速** - 本地推理

**缺点**：
- ⚠️ 需要下载模型（~100MB）
- ⚠️ 初次启动稍慢（加载模型）
- ⚠️ Embedding 质量略低于 OpenAI

**依赖**：
```bash
pip install faiss-cpu sentence-transformers
# 或 GPU 版本
pip install faiss-gpu sentence-transformers
```

---

### 方案 B：云端 RAG

**技术栈**：
- **向量数据库**: Pinecone / Weaviate Cloud
- **Embedding 模型**: OpenAI embeddings (`text-embedding-3-small`)

**优点**：
- ✅ Embedding 质量最好
- ✅ 无需本地计算资源
- ✅ 易于扩展

**缺点**：
- ❌ 需要 API key
- ❌ 有费用（embeddings: $0.02/1M tokens）
- ❌ 需要网络
- ❌ 数据发送到云端

**依赖**：
```bash
pip install pinecone-client openai
# 或
pip install weaviate-client openai
```

---

### 方案 C：混合 RAG

**技术栈**：
- **向量数据库**: FAISS（本地）
- **Embedding 模型**: OpenAI embeddings（云端）

**优点**：
- ✅ Embedding 质量好
- ✅ 数据存储本地

**缺点**：
- ⚠️ 仍需 API key
- ⚠️ 仍有 embedding 费用
- ⚠️ 需要网络

---

### 方案 D：Chroma（本地一体化）

**技术栈**：
- **向量数据库**: ChromaDB
- **Embedding 模型**: 内置（sentence-transformers）

**优点**：
- ✅ 一体化解决方案
- ✅ API 简单
- ✅ 完全本地

**缺点**：
- ⚠️ 包较重
- ⚠️ 相对较新

**依赖**：
```bash
pip install chromadb
```

---

## 🏆 推荐方案：本地 RAG

**方案：FAISS + sentence-transformers**

原因：
1. ✅ 与项目理念一致（支持本地部署）
2. ✅ 免费无限使用
3. ✅ 隐私安全
4. ✅ 性能好
5. ✅ 轻量级

---

## 📝 完整实现步骤

### 步骤 1：安装依赖

```bash
# 进入项目目录
cd /Users/jingzhuo/PycharmProjects/aiCode

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install faiss-cpu sentence-transformers

# 更新 requirements.txt
echo "faiss-cpu>=1.7.4" >> requirements.txt
echo "sentence-transformers>=2.2.0" >> requirements.txt
```

### 步骤 2：创建 RAG 记忆类

创建文件：`aicode/memory/rag_memory.py`

### 步骤 3：更新 MemoryManager

修改：`aicode/memory/memory_manager.py`

### 步骤 4：更新 CLI 命令

修改：`aicode/cli_agent.py`

### 步骤 5：测试

```bash
python -m aicode.cli_agent semantic-search "如何处理错误"
```

---

## 💻 代码实现

### 1. `aicode/memory/rag_memory.py`

```python
"""RAG 记忆系统 - 基于向量检索的语义搜索"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


class RAGMemory:
    """RAG 长期记忆 - 支持语义检索"""

    def __init__(
        self,
        storage_dir: str = ".aicode_memory",
        model_name: str = "all-MiniLM-L6-v2",
        enable_cache: bool = True
    ):
        """
        Args:
            storage_dir: 存储目录
            model_name: Sentence-Transformers 模型名称
            enable_cache: 是否启用模型缓存
        """
        if not RAG_AVAILABLE:
            raise ImportError(
                "RAG dependencies not installed. "
                "Run: pip install faiss-cpu sentence-transformers"
            )

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 向量数据库文件
        self.index_file = self.storage_dir / "faiss_index.bin"
        self.metadata_file = self.storage_dir / "rag_metadata.json"

        # 加载 Embedding 模型
        print(f"Loading embedding model: {model_name}...")
        cache_dir = self.storage_dir / "model_cache" if enable_cache else None
        self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        # FAISS 索引
        self.index = None
        self.metadata: List[Dict[str, Any]] = []

        # 加载现有索引
        self._load_index()

    def add(
        self,
        key: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        添加记忆到 RAG 系统

        Args:
            key: 记忆唯一标识
            content: 记忆内容（用于生成 embedding）
            metadata: 元数据（分类、标签、重要度等）
        """
        # 生成 embedding
        embedding = self.model.encode([content])[0]

        # 初始化索引（如果还没有）
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.embedding_dim)

        # 添加到 FAISS 索引
        self.index.add(np.array([embedding], dtype=np.float32))

        # 保存元数据
        meta = {
            "key": key,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "index_id": len(self.metadata)  # FAISS 中的索引位置
        }
        self.metadata.append(meta)

        # 保存到磁盘
        self._save_index()

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        语义搜索

        Args:
            query: 查询文本
            top_k: 返回最相似的 K 个结果
            category: 分类过滤
            min_similarity: 最小相似度阈值（0-1）

        Returns:
            搜索结果列表，包含 key, content, score, metadata
        """
        if self.index is None or len(self.metadata) == 0:
            return []

        # 生成查询向量
        query_embedding = self.model.encode([query])[0]

        # 搜索
        k = min(top_k * 2, len(self.metadata))  # 多取一些，因为要过滤
        distances, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32),
            k
        )

        # 整理结果
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]

            # 分类过滤
            if category and meta["metadata"].get("category") != category:
                continue

            # 计算相似度分数（L2 距离转换为相似度）
            similarity = 1 / (1 + dist)

            # 相似度阈值过滤
            if similarity < min_similarity:
                continue

            results.append({
                "key": meta["key"],
                "content": meta["content"],
                "score": float(similarity),
                "distance": float(dist),
                "metadata": meta["metadata"],
                "created_at": meta["created_at"]
            })

        # 按相似度排序
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]

    def update(self, key: str, content: str, metadata: Optional[Dict] = None):
        """
        更新记忆（重新生成 embedding）

        Args:
            key: 记忆键
            content: 新内容
            metadata: 新元数据
        """
        # 找到并删除旧记忆
        for i, meta in enumerate(self.metadata):
            if meta["key"] == key:
                # FAISS 不支持直接删除，需要重建索引
                self.metadata.pop(i)
                break

        # 添加新记忆
        self.add(key, content, metadata)

        # 重建索引
        self._rebuild_index()

    def delete(self, key: str) -> bool:
        """
        删除记忆

        Args:
            key: 记忆键

        Returns:
            是否成功删除
        """
        # 找到并删除
        for i, meta in enumerate(self.metadata):
            if meta["key"] == key:
                self.metadata.pop(i)
                self._rebuild_index()
                return True

        return False

    def get_all_keys(self) -> List[str]:
        """获取所有记忆键"""
        return [meta["key"] for meta in self.metadata]

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        categories = {}
        for meta in self.metadata:
            cat = meta["metadata"].get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_memories": len(self.metadata),
            "categories": categories,
            "embedding_dim": self.embedding_dim,
            "model": self.model.get_model_name() if hasattr(self.model, 'get_model_name') else "unknown"
        }

    def _save_index(self):
        """保存索引到磁盘"""
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_file))

        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

    def _load_index(self):
        """从磁盘加载索引"""
        if self.index_file.exists():
            try:
                self.index = faiss.read_index(str(self.index_file))
            except Exception as e:
                print(f"Warning: Failed to load FAISS index: {e}")
                self.index = None

        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load metadata: {e}")
                self.metadata = []

    def _rebuild_index(self):
        """重建 FAISS 索引（删除后需要）"""
        if not self.metadata:
            self.index = None
            self._save_index()
            return

        # 重新生成所有 embeddings
        contents = [meta["content"] for meta in self.metadata]
        embeddings = self.model.encode(contents)

        # 创建新索引
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(np.array(embeddings, dtype=np.float32))

        # 更新 index_id
        for i, meta in enumerate(self.metadata):
            meta["index_id"] = i

        self._save_index()


def is_rag_available() -> bool:
    """检查 RAG 依赖是否可用"""
    return RAG_AVAILABLE
```

---

### 2. 更新 `aicode/memory/memory_manager.py`

在现有 MemoryManager 中添加 RAG 支持：

```python
"""记忆管理器 - 统一管理短期、长期和 RAG 记忆"""

from typing import Optional, Dict, Any, List
from .short_term import ShortTermMemory
from .long_term import LongTermMemory

# RAG 记忆（可选）
try:
    from .rag_memory import RAGMemory, is_rag_available
    RAG_AVAILABLE = is_rag_available()
except ImportError:
    RAG_AVAILABLE = False


class MemoryManager:
    """记忆管理器 - 整合短期、长期和 RAG 记忆"""

    def __init__(
        self,
        storage_dir: str = ".aicode_memory",
        enable_rag: bool = True
    ):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(storage_dir=storage_dir)

        # RAG 记忆（如果可用且启用）
        self.rag_memory = None
        if enable_rag and RAG_AVAILABLE:
            try:
                self.rag_memory = RAGMemory(storage_dir=storage_dir)
                print("✓ RAG memory system initialized")
            except Exception as e:
                print(f"Warning: Failed to initialize RAG: {e}")
                self.rag_memory = None

    # === 现有方法保持不变 ===
    # ... (之前的所有方法)

    # === 新增 RAG 方法 ===

    def remember_with_rag(
        self,
        key: str,
        value: Any,
        category: str = "general",
        tags: Optional[List[str]] = None,
        importance: int = 5,
    ):
        """
        同时存储到长期记忆和 RAG 系统

        Args:
            key: 记忆键
            value: 记忆值
            category: 分类
            tags: 标签
            importance: 重要程度
        """
        # 存储到传统长期记忆
        self.long_term.store(key, value, category, tags, importance)

        # 存储到 RAG（如果可用）
        if self.rag_memory:
            content = f"{key}: {str(value)}"
            metadata = {
                "category": category,
                "tags": tags or [],
                "importance": importance
            }
            self.rag_memory.add(key, content, metadata)

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        语义搜索（使用 RAG）

        Args:
            query: 查询文本
            top_k: 返回结果数量
            category: 分类过滤

        Returns:
            搜索结果列表
        """
        if not self.rag_memory:
            # 降级到关键词搜索
            print("Warning: RAG not available, falling back to keyword search")
            return self.search_memories(query=query, category=category)

        return self.rag_memory.semantic_search(
            query=query,
            top_k=top_k,
            category=category
        )

    def is_rag_enabled(self) -> bool:
        """检查 RAG 是否启用"""
        return self.rag_memory is not None
```

---

### 3. 更新 CLI 命令 `aicode/cli_agent.py`

添加新的语义搜索命令：

```python
@agent_cli.command()
@click.argument("query")
@click.option("--top-k", default=5, type=int, help="返回结果数量")
@click.option("--category", help="分类过滤")
@click.option("--memory-dir", default=".aicode_memory", help="记忆存储目录")
def semantic_search(query, top_k, category, memory_dir):
    """语义搜索长期记忆（RAG）"""
    from .memory.memory_manager import MemoryManager

    memory = MemoryManager(storage_dir=memory_dir, enable_rag=True)

    if not memory.is_rag_enabled():
        console.print("[red]RAG 未启用。请安装: pip install faiss-cpu sentence-transformers[/red]")
        return

    console.print(f"\n[cyan]语义搜索:[/cyan] {query}\n")

    results = memory.semantic_search(query=query, top_k=top_k, category=category)

    if not results:
        console.print("[yellow]没有找到相关结果[/yellow]")
        return

    for i, result in enumerate(results, 1):
        console.print(f"{i}. [bold]{result['key']}[/bold] (相似度: {result['score']:.3f})")
        console.print(f"   内容: {result['content'][:200]}...")
        console.print(f"   分类: {result['metadata'].get('category', 'N/A')}")
        console.print()


@agent_cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--category", default="general", help="记忆分类")
@click.option("--importance", default=5, type=int, help="重要程度 (1-10)")
@click.option("--use-rag", is_flag=True, help="同时存储到 RAG 系统")
@click.option("--memory-dir", default=".aicode_memory", help="记忆存储目录")
def remember(key, value, category, importance, use_rag, memory_dir):
    """保存信息到长期记忆"""
    from .memory.memory_manager import MemoryManager

    memory = MemoryManager(storage_dir=memory_dir, enable_rag=use_rag)

    if use_rag and memory.is_rag_enabled():
        memory.remember_with_rag(key, value, category=category, importance=importance)
        console.print(f"[green]✓ 已保存到长期记忆和 RAG 系统[/green]")
    else:
        memory.remember(key, value, category=category, importance=importance)
        console.print(f"[green]✓ 已保存到长期记忆[/green]")

    console.print(f"[cyan]键:[/cyan] {key}")
    console.print(f"[cyan]值:[/cyan] {value}")
    console.print(f"[cyan]分类:[/cyan] {category}, [cyan]重要度:[/cyan] {importance}")
```

---

## 🚀 使用示例

### 安装依赖

```bash
cd /Users/jingzhuo/PycharmProjects/aiCode
source .venv/bin/activate
pip install faiss-cpu sentence-transformers
```

### 存储记忆到 RAG

```bash
# 使用 --use-rag 标志
python -m aicode.cli_agent remember \
  "error_handling_pattern" \
  "使用 try-except 捕获异常，记录到日志，返回友好错误信息" \
  --category patterns \
  --importance 8 \
  --use-rag

python -m aicode.cli_agent remember \
  "exception_best_practice" \
  "捕获特定异常类型，避免裸 except，使用 finally 清理资源" \
  --category patterns \
  --importance 8 \
  --use-rag

python -m aicode.cli_agent remember \
  "logging_errors" \
  "使用 logging.exception() 记录错误堆栈，便于调试" \
  --category patterns \
  --importance 7 \
  --use-rag
```

### 语义搜索

```bash
# 搜索 "如何处理错误"
python -m aicode.cli_agent semantic-search "如何处理错误" --top-k 5

# 结果会包含：
# 1. error_handling_pattern (相似度: 0.85)
# 2. exception_best_practice (相似度: 0.82)
# 3. logging_errors (相似度: 0.78)
# 即使查询词是 "如何处理错误"，也能找到 "异常"、"日志" 等相关内容
```

### 在代码中使用

```python
from aicode.memory.memory_manager import MemoryManager

# 初始化（启用 RAG）
memory = MemoryManager(enable_rag=True)

# 存储记忆
memory.remember_with_rag(
    key="auth_jwt_pattern",
    value="使用 JWT token 实现无状态认证，存储在 HTTP-only cookie",
    category="patterns",
    importance=8
)

# 语义搜索
results = memory.semantic_search("如何实现用户认证", top_k=3)
for result in results:
    print(f"{result['key']}: {result['content']} (score: {result['score']})")
```

---

## 📊 性能对比

### 首次启动

```bash
# 第一次会下载模型（~100MB）
Loading embedding model: all-MiniLM-L6-v2...
Downloading model... [████████████████████] 100%
✓ RAG memory system initialized

# 后续启动很快（使用缓存）
Loading embedding model: all-MiniLM-L6-v2...
✓ RAG memory system initialized (0.5s)
```

### 搜索性能

| 记忆数量 | 关键词搜索 | RAG 语义搜索 |
|---------|-----------|-------------|
| 100 条 | ~1ms | ~50ms |
| 1000 条 | ~5ms | ~200ms |
| 10000 条 | ~20ms | ~500ms |

**结论**: RAG 稍慢但可接受，语义理解能力强大

---

## 🎯 最佳实践

### 1. 选择性使用 RAG

```bash
# 重要的、需要语义搜索的记忆用 RAG
python -m aicode.cli_agent remember "pattern_name" "..." --use-rag

# 临时的、结构化的记忆用传统方式
python -m aicode.cli_agent remember "temp_config" "..."
```

### 2. 混合搜索策略

```python
# 先用关键词（快）
keyword_results = memory.search_memories(query="认证")

if len(keyword_results) < 3:
    # 再用语义搜索（更全面）
    semantic_results = memory.semantic_search(query="认证")
```

### 3. 内容优化

```python
# ✅ 好的内容（描述性强）
memory.remember_with_rag(
    "jwt_auth",
    "JWT token 认证：生成签名 token，存储在 HTTP-only cookie，每次请求验证签名和过期时间",
    ...
)

# ❌ 不好的内容（过于简短）
memory.remember_with_rag(
    "auth",
    "JWT",
    ...
)
```

---

## 🔮 未来增强

### 可能的改进

1. **混合检索**
   ```python
   # 结合关键词和语义
   results = memory.hybrid_search(query, keyword_weight=0.3, semantic_weight=0.7)
   ```

2. **多模态检索**
   ```python
   # 支持代码片段检索
   results = memory.search_code(code_snippet)
   ```

3. **增量更新**
   ```python
   # 支持部分更新，无需重建索引
   memory.rag.partial_update(key, new_content)
   ```

4. **云端 Embedding**
   ```python
   # 可选使用 OpenAI embeddings（质量更好）
   memory = MemoryManager(
       enable_rag=True,
       rag_backend="openai"  # 或 "local"
   )
   ```

---

## 📚 参考资源

- [FAISS Documentation](https://faiss.ai/)
- [Sentence Transformers](https://www.sbert.net/)
- [Hugging Face Models](https://huggingface.co/models?pipeline_tag=sentence-similarity)

---

**现在你可以开始实现 RAG 长期记忆了！** 🚀

按照步骤执行，你的 Agent 将具备强大的语义检索能力。
