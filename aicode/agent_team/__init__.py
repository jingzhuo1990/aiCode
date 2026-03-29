"""
Agent Team - 多智能体协作系统

支持多个 Agent 协作完成复杂任务，使用 A2A 协议进行通信。
"""

from .base_agent import BaseAgent, AgentRole
from .message import Message, MessageType, MessagePriority
from .coordinator import TeamCoordinator
from .specialized_agents import (
    CodeAgent,
    FileAgent,
    AnalysisAgent,
    PlannerAgent
)

__all__ = [
    # Base
    "BaseAgent",
    "AgentRole",

    # A2A Protocol
    "Message",
    "MessageType",
    "MessagePriority",

    # Coordinator
    "TeamCoordinator",

    # Specialized Agents
    "CodeAgent",
    "FileAgent",
    "AnalysisAgent",
    "PlannerAgent",
]
