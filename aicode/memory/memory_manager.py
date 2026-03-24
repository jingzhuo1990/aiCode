"""记忆管理器 - 统一管理短期和长期记忆"""

from typing import Optional, Dict, Any, List
from .short_term import ShortTermMemory
from .long_term import LongTermMemory


class MemoryManager:
    """记忆管理器 - 整合短期和长期记忆"""

    def __init__(self, storage_dir: str = ".aicode_memory"):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(storage_dir=storage_dir)

    # === 短期记忆接口 ===

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """添加消息到短期记忆"""
        self.short_term.add_message(role, content, metadata)

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.short_term.get_conversation_history()

    def get_recent_context(self, last_n: int = 5) -> str:
        """获取最近的上下文摘要"""
        messages = self.short_term.get_messages(last_n=last_n)
        context_parts = []
        for msg in messages:
            context_parts.append(f"[{msg.role}]: {msg.content[:200]}")
        return "\n".join(context_parts)

    def clear_short_term(self):
        """清空短期记忆"""
        self.short_term.clear()

    # === 长期记忆接口 ===

    def remember(
        self,
        key: str,
        value: Any,
        category: str = "general",
        tags: Optional[List[str]] = None,
        importance: int = 5,
    ):
        """存储到长期记忆"""
        self.long_term.store(key, value, category, tags, importance)

    def recall(self, key: str) -> Optional[Any]:
        """从长期记忆检索"""
        return self.long_term.retrieve(key)

    def search_memories(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Any]:
        """搜索长期记忆"""
        entries = self.long_term.search(query=query, category=category, tags=tags)
        return [entry.to_dict() for entry in entries]

    def forget(self, key: str) -> bool:
        """从长期记忆删除"""
        return self.long_term.delete(key)

    # === 整合功能 ===

    def get_full_context(self, include_long_term: bool = True) -> str:
        """
        获取完整上下文（短期 + 长期记忆）

        Args:
            include_long_term: 是否包含长期记忆

        Returns:
            格式化的上下文字符串
        """
        context_parts = []

        # 长期记忆
        if include_long_term:
            long_term_context = self.long_term.export_to_text()
            if long_term_context:
                context_parts.append(long_term_context)

        # 短期记忆
        short_term_context = self.short_term.get_context_summary()
        if short_term_context:
            context_parts.append("\n=== Current Session ===\n" + short_term_context)

        return "\n\n".join(context_parts)

    def save_important_from_conversation(self, min_length: int = 100):
        """
        从当前对话中提取重要信息保存到长期记忆
        这个方法可以在会话结束时调用，或定期调用

        Args:
            min_length: 消息最小长度才考虑保存
        """
        messages = self.short_term.get_messages()

        for msg in messages:
            # 只保存助手的重要回复
            if msg.role != "assistant":
                continue

            if len(msg.content) < min_length:
                continue

            # 根据元数据判断重要性
            metadata = msg.metadata

            # 代码生成/修改相关的保存到长期记忆
            if "code_generated" in metadata or "file_modified" in metadata:
                key = f"task_{msg.timestamp.strftime('%Y%m%d_%H%M%S')}"
                self.remember(
                    key=key,
                    value={
                        "content": msg.content[:500],  # 保存摘要
                        "metadata": metadata,
                    },
                    category="tasks",
                    importance=7,
                )

    def remember_codebase_info(self, project_path: str, info: Dict[str, Any]):
        """记住代码库信息"""
        key = f"codebase_{project_path.replace('/', '_')}"
        self.remember(
            key=key,
            value=info,
            category="codebase",
            tags=["project", "structure"],
            importance=8,
        )

    def remember_user_preference(self, preference_name: str, preference_value: Any):
        """记住用户偏好"""
        self.remember(
            key=f"pref_{preference_name}",
            value=preference_value,
            category="user_preferences",
            tags=["preference"],
            importance=9,
        )

    def get_user_preferences(self) -> Dict[str, Any]:
        """获取所有用户偏好"""
        entries = self.long_term.search(category="user_preferences")
        preferences = {}
        for entry in entries:
            pref_name = entry.key.replace("pref_", "")
            preferences[pref_name] = entry.value
        return preferences

    def remember_code_pattern(self, pattern_name: str, pattern_info: Dict[str, Any]):
        """记住代码模式"""
        self.remember(
            key=f"pattern_{pattern_name}",
            value=pattern_info,
            category="patterns",
            tags=["code", "pattern"],
            importance=6,
        )

    def get_relevant_patterns(self, query: str) -> List[Dict[str, Any]]:
        """获取相关的代码模式"""
        entries = self.long_term.search(query=query, category="patterns")
        return [entry.to_dict() for entry in entries[:5]]

    def cleanup(self, days: int = 90):
        """清理旧记忆"""
        deleted = self.long_term.cleanup_old_memories(days=days, min_importance=7)
        return deleted

    def get_statistics(self) -> Dict[str, Any]:
        """获取记忆系统统计信息"""
        return {
            "short_term": self.short_term.get_stats(),
            "long_term": self.long_term.get_stats(),
        }

    def export_session(self, filepath: str):
        """导出当前会话"""
        self.short_term.save_to_file(filepath)

    def import_session(self, filepath: str):
        """导入会话"""
        self.short_term = ShortTermMemory.load_from_file(filepath)
