"""A2A (Agent-to-Agent) 消息协议"""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from enum import Enum
from datetime import datetime
import uuid


class MessageType(Enum):
    """消息类型"""
    # 任务相关
    TASK_REQUEST = "task_request"      # 任务请求
    TASK_RESPONSE = "task_response"    # 任务响应
    TASK_DELEGATE = "task_delegate"    # 任务委托
    TASK_COMPLETE = "task_complete"    # 任务完成

    # 查询相关
    QUERY = "query"                    # 查询请求
    QUERY_RESPONSE = "query_response"  # 查询响应

    # 协调相关
    STATUS_UPDATE = "status_update"    # 状态更新
    CAPABILITY_QUERY = "capability_query"  # 能力查询
    CAPABILITY_RESPONSE = "capability_response"  # 能力响应

    # 协作相关
    COLLABORATION_REQUEST = "collaboration_request"  # 协作请求
    COLLABORATION_ACCEPT = "collaboration_accept"    # 接受协作
    COLLABORATION_REJECT = "collaboration_reject"    # 拒绝协作

    # 系统相关
    HEARTBEAT = "heartbeat"            # 心跳
    ERROR = "error"                    # 错误
    INFO = "info"                      # 信息


class MessagePriority(Enum):
    """消息优先级"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class Message:
    """
    A2A 协议消息

    遵循标准的 Agent-to-Agent 通信协议
    """
    # 必需字段
    message_type: MessageType
    sender_id: str
    receiver_id: str
    content: Any

    # 元数据
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    priority: MessagePriority = MessagePriority.NORMAL

    # 关联字段
    reply_to: Optional[str] = None  # 回复哪条消息
    conversation_id: Optional[str] = None  # 会话 ID

    # 附加数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "reply_to": self.reply_to,
            "conversation_id": self.conversation_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """从字典创建"""
        return cls(
            message_id=data["message_id"],
            message_type=MessageType(data["message_type"]),
            sender_id=data["sender_id"],
            receiver_id=data["receiver_id"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            priority=MessagePriority(data["priority"]),
            reply_to=data.get("reply_to"),
            conversation_id=data.get("conversation_id"),
            metadata=data.get("metadata", {}),
        )

    def create_reply(
        self,
        content: Any,
        message_type: MessageType = MessageType.TASK_RESPONSE
    ) -> "Message":
        """创建回复消息"""
        return Message(
            message_type=message_type,
            sender_id=self.receiver_id,  # 回复时交换发送者和接收者
            receiver_id=self.sender_id,
            content=content,
            reply_to=self.message_id,
            conversation_id=self.conversation_id or self.message_id,
            priority=self.priority,
        )


class MessageQueue:
    """消息队列"""

    def __init__(self):
        self.messages: list[Message] = []

    def push(self, message: Message):
        """添加消息（按优先级排序）"""
        self.messages.append(message)
        # 按优先级和时间排序
        self.messages.sort(
            key=lambda m: (m.priority.value, m.timestamp),
            reverse=True
        )

    def pop(self) -> Optional[Message]:
        """取出最高优先级的消息"""
        if self.messages:
            return self.messages.pop(0)
        return None

    def peek(self) -> Optional[Message]:
        """查看最高优先级的消息（不移除）"""
        if self.messages:
            return self.messages[0]
        return None

    def get_by_id(self, message_id: str) -> Optional[Message]:
        """根据 ID 获取消息"""
        for msg in self.messages:
            if msg.message_id == message_id:
                return msg
        return None

    def filter_by_sender(self, sender_id: str) -> list[Message]:
        """过滤特定发送者的消息"""
        return [m for m in self.messages if m.sender_id == sender_id]

    def filter_by_type(self, message_type: MessageType) -> list[Message]:
        """过滤特定类型的消息"""
        return [m for m in self.messages if m.message_type == message_type]

    def size(self) -> int:
        """队列大小"""
        return len(self.messages)

    def clear(self):
        """清空队列"""
        self.messages.clear()
