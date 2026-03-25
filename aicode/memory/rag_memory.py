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
            "model": "all-MiniLM-L6-v2"
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
