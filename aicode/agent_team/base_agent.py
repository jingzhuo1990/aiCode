"""Base Agent - 智能体基类"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
from enum import Enum
from .message import Message, MessageType, MessageQueue, MessagePriority
import asyncio


class AgentRole(Enum):
    """Agent 角色"""
    COORDINATOR = "coordinator"  # 协调者
    SPECIALIST = "specialist"    # 专家
    WORKER = "worker"           # 工作者
    ANALYZER = "analyzer"       # 分析者


class AgentStatus(Enum):
    """Agent 状态"""
    IDLE = "idle"           # 空闲
    BUSY = "busy"           # 忙碌
    WAITING = "waiting"     # 等待
    ERROR = "error"         # 错误
    OFFLINE = "offline"     # 离线


class BaseAgent(ABC):
    """
    智能体基类

    所有专业 Agent 都继承此类
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: AgentRole,
        capabilities: List[str],
        description: str = "",
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.capabilities = set(capabilities)
        self.description = description

        # 状态
        self.status = AgentStatus.IDLE

        # 消息队列
        self.inbox = MessageQueue()
        self.outbox = MessageQueue()

        # 消息处理器映射
        self._message_handlers: Dict[MessageType, callable] = {}
        self._register_default_handlers()

        # 协作相关
        self.team_agents: Dict[str, "BaseAgent"] = {}  # 其他 Agent

        # 统计
        self.stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
        }

    def _register_default_handlers(self):
        """注册默认消息处理器"""
        self._message_handlers[MessageType.CAPABILITY_QUERY] = self._handle_capability_query
        self._message_handlers[MessageType.STATUS_UPDATE] = self._handle_status_update
        self._message_handlers[MessageType.HEARTBEAT] = self._handle_heartbeat

    # === 消息发送 ===

    def send_message(
        self,
        receiver_id: str,
        message_type: MessageType,
        content: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
        **kwargs
    ) -> Message:
        """发送消息"""
        message = Message(
            message_type=message_type,
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            content=content,
            priority=priority,
            **kwargs
        )
        self.outbox.push(message)
        self.stats["messages_sent"] += 1
        return message

    def broadcast_message(
        self,
        message_type: MessageType,
        content: Any,
        exclude: Optional[Set[str]] = None
    ):
        """广播消息给所有团队成员"""
        exclude = exclude or set()
        for agent_id in self.team_agents:
            if agent_id not in exclude:
                self.send_message(agent_id, message_type, content)

    # === 消息接收 ===

    def receive_message(self, message: Message):
        """接收消息"""
        self.inbox.push(message)
        self.stats["messages_received"] += 1

    async def process_messages(self, max_messages: int = 10):
        """处理收件箱中的消息"""
        processed = 0
        while processed < max_messages:
            message = self.inbox.pop()
            if not message:
                break

            await self._process_single_message(message)
            processed += 1

        return processed

    async def _process_single_message(self, message: Message):
        """处理单条消息"""
        try:
            handler = self._message_handlers.get(message.message_type)
            if handler:
                await handler(message)
            else:
                await self.handle_message(message)
        except Exception as e:
            print(f"[{self.name}] Error processing message: {e}")
            # 发送错误消息
            self.send_message(
                message.sender_id,
                MessageType.ERROR,
                {"error": str(e), "original_message_id": message.message_id}
            )

    # === 消息处理器 ===

    @abstractmethod
    async def handle_message(self, message: Message):
        """处理消息（子类实现）"""
        pass

    async def _handle_capability_query(self, message: Message):
        """处理能力查询"""
        response = {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "capabilities": list(self.capabilities),
            "status": self.status.value,
            "description": self.description,
        }
        reply = message.create_reply(
            response,
            MessageType.CAPABILITY_RESPONSE
        )
        self.outbox.push(reply)

    async def _handle_status_update(self, message: Message):
        """处理状态更新"""
        # 更新其他 Agent 的状态信息
        agent_id = message.content.get("agent_id")
        if agent_id in self.team_agents:
            # 可以存储状态信息
            pass

    async def _handle_heartbeat(self, message: Message):
        """处理心跳"""
        # 回复心跳
        reply = message.create_reply(
            {"status": self.status.value},
            MessageType.HEARTBEAT
        )
        self.outbox.push(reply)

    # === 能力检查 ===

    def can_handle(self, task_type: str) -> bool:
        """检查是否能处理某类任务"""
        return task_type in self.capabilities

    def add_capability(self, capability: str):
        """添加能力"""
        self.capabilities.add(capability)

    def remove_capability(self, capability: str):
        """移除能力"""
        self.capabilities.discard(capability)

    # === 团队管理 ===

    def register_team_agent(self, agent: "BaseAgent"):
        """注册团队成员"""
        self.team_agents[agent.agent_id] = agent

    def unregister_team_agent(self, agent_id: str):
        """注销团队成员"""
        self.team_agents.pop(agent_id, None)

    def get_team_agent(self, agent_id: str) -> Optional["BaseAgent"]:
        """获取团队成员"""
        return self.team_agents.get(agent_id)

    # === 状态管理 ===

    def set_status(self, status: AgentStatus):
        """设置状态"""
        old_status = self.status
        self.status = status

        # 广播状态变更
        if old_status != status:
            self.broadcast_message(
                MessageType.STATUS_UPDATE,
                {
                    "agent_id": self.agent_id,
                    "old_status": old_status.value,
                    "new_status": status.value,
                }
            )

    # === 任务执行 ===

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务（子类实现）

        Args:
            task: 任务描述

        Returns:
            执行结果
        """
        pass

    # === 工具方法 ===

    def get_info(self) -> Dict[str, Any]:
        """获取 Agent 信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "status": self.status.value,
            "capabilities": list(self.capabilities),
            "description": self.description,
            "stats": self.stats,
            "inbox_size": self.inbox.size(),
            "outbox_size": self.outbox.size(),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, name={self.name}, status={self.status.value})>"
