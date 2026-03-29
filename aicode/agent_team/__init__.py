"""
Agent Team - 多智能体协作系统

支持多个 Agent 协作完成复杂任务，使用 A2A 协议进行通信。

核心组件：
- BaseAgent: Agent 基类
- TeamCoordinator: 团队协调器
- AgentHarness: Agent 运行环境（集成 AI、Tools、Skills、Memory）
- HarnessedAgent: 带 Harness 的增强 Agent
- Specialized Agents: 专业 Agent（Code, File, Analysis, Planner）
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
from .agent_harness import AgentHarness, HarnessedAgent

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

    # Harness (Agent 运行环境)
    "AgentHarness",
    "HarnessedAgent",

    # Specialized Agents
    "CodeAgent",
    "FileAgent",
    "AnalysisAgent",
    "PlannerAgent",
]
