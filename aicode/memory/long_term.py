"""长期记忆 - 持久化存储重要信息"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import hashlib


class MemoryEntry:
    """记忆条目"""

    def __init__(
        self,
        key: str,
        value: Any,
        category: str = "general",
        tags: Optional[List[str]] = None,
        importance: int = 5,
    ):
        self.key = key
        self.value = value
        self.category = category
        self.tags = tags or []
        self.importance = importance  # 1-10, 重要程度
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.access_count = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "tags": self.tags,
            "importance": self.importance,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        entry = cls(
            key=data["key"],
            value=data["value"],
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            importance=data.get("importance", 5),
        )
        entry.created_at = datetime.fromisoformat(data["created_at"])
        entry.updated_at = datetime.fromisoformat(data["updated_at"])
        entry.access_count = data.get("access_count", 0)
        return entry


class LongTermMemory:
    """长期记忆 - 持久化存储"""

    def __init__(self, storage_dir: str = ".aicode_memory"):
        """
        Args:
            storage_dir: 存储目录路径
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.memories: Dict[str, MemoryEntry] = {}
        self.index_file = self.storage_dir / "memory_index.json"

        self._load_index()

    def store(
        self,
        key: str,
        value: Any,
        category: str = "general",
        tags: Optional[List[str]] = None,
        importance: int = 5,
    ):
        """
        存储记忆

        Args:
            key: 记忆键
            value: 记忆值
            category: 分类（codebase, user_preferences, patterns, etc）
            tags: 标签列表
            importance: 重要程度 1-10
        """
        if key in self.memories:
            # 更新现有记忆
            entry = self.memories[key]
            entry.value = value
            entry.updated_at = datetime.now()
            entry.importance = max(entry.importance, importance)
            if tags:
                entry.tags = list(set(entry.tags + tags))
        else:
            # 创建新记忆
            entry = MemoryEntry(
                key=key,
                value=value,
                category=category,
                tags=tags,
                importance=importance,
            )
            self.memories[key] = entry

        self._save_index()

    def retrieve(self, key: str) -> Optional[Any]:
        """
        检索记忆

        Args:
            key: 记忆键

        Returns:
            记忆值，如果不存在返回 None
        """
        if key in self.memories:
            entry = self.memories[key]
            entry.access_count += 1
            entry.updated_at = datetime.now()
            self._save_index()
            return entry.value
        return None

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_importance: int = 0,
    ) -> List[MemoryEntry]:
        """
        搜索记忆

        Args:
            query: 搜索关键词
            category: 分类筛选
            tags: 标签筛选
            min_importance: 最低重要程度

        Returns:
            匹配的记忆条目列表
        """
        results = []

        for entry in self.memories.values():
            # 重要程度筛选
            if entry.importance < min_importance:
                continue

            # 分类筛选
            if category and entry.category != category:
                continue

            # 标签筛选
            if tags and not any(tag in entry.tags for tag in tags):
                continue

            # 关键词搜索
            if query:
                query_lower = query.lower()
                if (query_lower not in entry.key.lower() and
                    query_lower not in str(entry.value).lower() and
                    not any(query_lower in tag.lower() for tag in entry.tags)):
                    continue

            results.append(entry)

        # 按重要程度和访问频率排序
        results.sort(
            key=lambda e: (e.importance, e.access_count, e.updated_at),
            reverse=True
        )

        return results

    def delete(self, key: str) -> bool:
        """
        删除记忆

        Args:
            key: 记忆键

        Returns:
            是否成功删除
        """
        if key in self.memories:
            del self.memories[key]
            self._save_index()
            return True
        return False

    def get_category_summary(self, category: str) -> Dict[str, Any]:
        """获取某个分类的摘要"""
        entries = [e for e in self.memories.values() if e.category == category]

        return {
            "category": category,
            "count": len(entries),
            "total_importance": sum(e.importance for e in entries),
            "most_accessed": max(entries, key=lambda e: e.access_count).key if entries else None,
            "latest_update": max(entries, key=lambda e: e.updated_at).updated_at.isoformat() if entries else None,
        }

    def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        return list(set(e.category for e in self.memories.values()))

    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        tags = set()
        for entry in self.memories.values():
            tags.update(entry.tags)
        return list(tags)

    def export_to_text(self) -> str:
        """导出为文本格式，用于提供给模型"""
        if not self.memories:
            return "No long-term memories stored."

        lines = ["=== Long-term Memory ===\n"]

        # 按分类组织
        categories = self.get_all_categories()
        for category in categories:
            entries = [e for e in self.memories.values() if e.category == category]
            if not entries:
                continue

            lines.append(f"\n## {category.upper()} ({len(entries)} items)")

            # 按重要程度排序
            entries.sort(key=lambda e: e.importance, reverse=True)

            for entry in entries[:10]:  # 每个分类最多显示10个
                lines.append(f"\n- {entry.key}: {entry.value}")
                if entry.tags:
                    lines.append(f"  Tags: {', '.join(entry.tags)}")

        return "\n".join(lines)

    def cleanup_old_memories(self, days: int = 90, min_importance: int = 7):
        """
        清理旧的低重要度记忆

        Args:
            days: 超过多少天的记忆
            min_importance: 低于此重要度的记忆会被清理
        """
        current_time = datetime.now()
        to_delete = []

        for key, entry in self.memories.items():
            age_days = (current_time - entry.updated_at).days
            if age_days > days and entry.importance < min_importance:
                to_delete.append(key)

        for key in to_delete:
            del self.memories[key]

        if to_delete:
            self._save_index()

        return len(to_delete)

    def _save_index(self):
        """保存索引到文件"""
        data = {
            "memories": {k: v.to_dict() for k, v in self.memories.items()},
            "last_updated": datetime.now().isoformat(),
        }

        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_index(self):
        """从文件加载索引"""
        if not self.index_file.exists():
            return

        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.memories = {
                k: MemoryEntry.from_dict(v)
                for k, v in data.get("memories", {}).items()
            }
        except Exception as e:
            print(f"Warning: Failed to load memory index: {e}")
            self.memories = {}

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.memories:
            return {
                "total_memories": 0,
                "categories": {},
                "total_tags": 0,
            }

        category_counts = {}
        for entry in self.memories.values():
            category_counts[entry.category] = category_counts.get(entry.category, 0) + 1

        return {
            "total_memories": len(self.memories),
            "categories": category_counts,
            "total_tags": len(self.get_all_tags()),
            "most_important": max(self.memories.values(), key=lambda e: e.importance).key,
            "most_accessed": max(self.memories.values(), key=lambda e: e.access_count).key,
        }
