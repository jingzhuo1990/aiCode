"""短期记忆 - 保存当前会话上下文"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class Message:
    """消息对象"""

    def __init__(self, role: str, content: str, metadata: Optional[Dict] = None):
        self.role = role  # 'user', 'assistant', 'system', 'tool'
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        msg = cls(
            role=data["role"],
            content=data["content"],
            metadata=data.get("metadata", {}),
        )
        if "timestamp" in data:
            msg.timestamp = datetime.fromisoformat(data["timestamp"])
        return msg


class ShortTermMemory:
    """短期记忆 - 管理当前会话的对话历史"""

    def __init__(self, max_messages: int = 50, max_tokens: int = 8000):
        """
        Args:
            max_messages: 最多保存的消息数量
            max_tokens: 最大 token 数（简单估算：字符数 / 4）
        """
        self.messages: List[Message] = []
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """添加消息到历史"""
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        self._trim_messages()

    def add_user_message(self, content: str, metadata: Optional[Dict] = None):
        """添加用户消息"""
        self.add_message("user", content, metadata)

    def add_assistant_message(self, content: str, metadata: Optional[Dict] = None):
        """添加助手消息"""
        self.add_message("assistant", content, metadata)

    def add_system_message(self, content: str, metadata: Optional[Dict] = None):
        """添加系统消息"""
        self.add_message("system", content, metadata)

    def add_tool_message(self, tool_name: str, result: str, metadata: Optional[Dict] = None):
        """添加工具使用消息"""
        metadata = metadata or {}
        metadata["tool_name"] = tool_name
        self.add_message("tool", result, metadata)

    def get_messages(self, last_n: Optional[int] = None) -> List[Message]:
        """
        获取消息历史

        Args:
            last_n: 获取最后 N 条消息，None 表示全部
        """
        if last_n is None:
            return self.messages.copy()
        return self.messages[-last_n:]

    def get_conversation_history(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        获取对话历史（格式化为模型输入格式）

        Args:
            include_system: 是否包含系统消息
        """
        history = []
        for msg in self.messages:
            if not include_system and msg.role == "system":
                continue
            if msg.role == "tool":
                # 工具消息转换为用户消息
                history.append({
                    "role": "user",
                    "content": f"[Tool: {msg.metadata.get('tool_name', 'unknown')}]\n{msg.content}"
                })
            else:
                history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        return history

    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        if not self.messages:
            return "No conversation history."

        summary_parts = [f"Session: {self.session_id}"]
        summary_parts.append(f"Total messages: {len(self.messages)}")

        # 最近的几条消息
        recent = self.messages[-5:]
        summary_parts.append("\nRecent conversation:")
        for msg in recent:
            summary_parts.append(f"  [{msg.role}]: {msg.content[:100]}...")

        return "\n".join(summary_parts)

    def clear(self):
        """清空短期记忆"""
        self.messages = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _trim_messages(self):
        """修剪消息历史，保持在限制范围内"""
        # 按消息数量限制
        if len(self.messages) > self.max_messages:
            # 保留系统消息和最近的消息
            system_messages = [m for m in self.messages if m.role == "system"]
            other_messages = [m for m in self.messages if m.role != "system"]

            keep_count = self.max_messages - len(system_messages)
            self.messages = system_messages + other_messages[-keep_count:]

        # 按 token 数量限制（简单估算）
        total_tokens = sum(len(m.content) // 4 for m in self.messages)
        while total_tokens > self.max_tokens and len(self.messages) > 5:
            # 删除最早的非系统消息
            for i, msg in enumerate(self.messages):
                if msg.role != "system":
                    removed = self.messages.pop(i)
                    total_tokens -= len(removed.content) // 4
                    break

    def save_to_file(self, filepath: str):
        """保存到文件"""
        data = {
            "session_id": self.session_id,
            "messages": [m.to_dict() for m in self.messages],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filepath: str) -> "ShortTermMemory":
        """从文件加载"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        memory = cls()
        memory.session_id = data["session_id"]
        memory.messages = [Message.from_dict(m) for m in data["messages"]]
        return memory

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        role_counts = {}
        for msg in self.messages:
            role_counts[msg.role] = role_counts.get(msg.role, 0) + 1

        return {
            "session_id": self.session_id,
            "total_messages": len(self.messages),
            "role_distribution": role_counts,
            "estimated_tokens": sum(len(m.content) // 4 for m in self.messages),
        }
