"""Team Coordinator - 团队协调器"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentStatus
from .message import Message, MessageType, MessagePriority
import asyncio


class TeamCoordinator:
    """
    团队协调器

    负责：
    - 管理多个 Agent
    - 任务分配和调度
    - Agent 间通信路由
    - 结果汇总
    """

    def __init__(self, team_name: str = "AI Team"):
        self.team_name = team_name
        self.agents: Dict[str, BaseAgent] = {}
        self.message_router: Dict[str, BaseAgent] = {}

        # 任务追踪
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[Dict[str, Any]] = []

    # === Agent 管理 ===

    def add_agent(self, agent: BaseAgent):
        """添加 Agent 到团队"""
        self.agents[agent.agent_id] = agent
        self.message_router[agent.agent_id] = agent

        # 让新 Agent 认识团队其他成员
        for other_agent in self.agents.values():
            if other_agent.agent_id != agent.agent_id:
                agent.register_team_agent(other_agent)
                other_agent.register_team_agent(agent)

        print(f"[{self.team_name}] Added agent: {agent.name} ({agent.agent_id})")

    def remove_agent(self, agent_id: str):
        """移除 Agent"""
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            self.message_router.pop(agent_id, None)

            # 从其他 Agent 中注销
            for other_agent in self.agents.values():
                other_agent.unregister_team_agent(agent_id)

            print(f"[{self.team_name}] Removed agent: {agent.name}")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """获取 Agent"""
        return self.agents.get(agent_id)

    def list_agents(self) -> List[BaseAgent]:
        """列出所有 Agent"""
        return list(self.agents.values())

    # === 任务分配 ===

    async def assign_task(
        self,
        task: Dict[str, Any],
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分配任务

        Args:
            task: 任务描述，需包含 'type' 字段
            agent_id: 指定 Agent ID，如果为 None 则自动选择

        Returns:
            任务执行结果
        """
        # 自动选择 Agent
        if agent_id is None:
            agent = self._select_agent_for_task(task)
            if not agent:
                return {
                    "success": False,
                    "error": "No suitable agent found for task"
                }
        else:
            agent = self.get_agent(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent {agent_id} not found"
                }

        print(f"[{self.team_name}] Assigning task to {agent.name}: {task.get('type')}")

        # 创建任务消息
        message = Message(
            message_type=MessageType.TASK_REQUEST,
            sender_id="coordinator",
            receiver_id=agent.agent_id,
            content=task,
            priority=MessagePriority.NORMAL
        )

        # 记录任务
        task_id = message.message_id
        self.active_tasks[task_id] = {
            "task": task,
            "agent_id": agent.agent_id,
            "message_id": message.message_id,
            "status": "pending"
        }

        # 发送消息
        agent.receive_message(message)

        # 等待处理
        result = await self._wait_for_task_completion(agent, task_id)

        return result

    def _select_agent_for_task(self, task: Dict[str, Any]) -> Optional[BaseAgent]:
        """根据任务选择合适的 Agent"""
        task_type = task.get("type", "")

        # 简单策略：检查能力匹配
        for agent in self.agents.values():
            if agent.status == AgentStatus.IDLE and agent.can_handle(task_type):
                return agent

        # 如果没有空闲的，选择一个忙碌但能处理的
        for agent in self.agents.values():
            if agent.can_handle(task_type):
                return agent

        return None

    async def _wait_for_task_completion(
        self,
        agent: BaseAgent,
        task_id: str,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """等待任务完成"""
        start_time = asyncio.get_event_loop().time()

        while True:
            # 检查超时
            if asyncio.get_event_loop().time() - start_time > timeout:
                self.active_tasks[task_id]["status"] = "timeout"
                return {
                    "success": False,
                    "error": "Task timeout"
                }

            # 处理 Agent 的消息
            await agent.process_messages(max_messages=5)

            # 检查 outbox 中是否有完成消息
            while agent.outbox.size() > 0:
                message = agent.outbox.pop()

                if message.message_type == MessageType.TASK_COMPLETE:
                    if message.reply_to == self.active_tasks[task_id]["message_id"]:
                        # 任务完成
                        self.active_tasks[task_id]["status"] = "completed"
                        self.completed_tasks.append(self.active_tasks.pop(task_id))
                        return message.content

                elif message.message_type == MessageType.ERROR:
                    if message.reply_to == self.active_tasks[task_id]["message_id"]:
                        # 任务失败
                        self.active_tasks[task_id]["status"] = "failed"
                        self.completed_tasks.append(self.active_tasks.pop(task_id))
                        return message.content

                else:
                    # 路由其他消息
                    self._route_message(message)

            # 短暂等待
            await asyncio.sleep(0.1)

    def _route_message(self, message: Message):
        """路由消息到目标 Agent"""
        receiver = self.message_router.get(message.receiver_id)
        if receiver:
            receiver.receive_message(message)

    # === 复杂任务协调 ===

    async def execute_workflow(
        self,
        workflow: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        执行工作流（多个任务按顺序执行）

        Args:
            workflow: 任务列表

        Returns:
            所有任务的结果
        """
        results = []

        print(f"[{self.team_name}] Executing workflow with {len(workflow)} tasks")

        for i, task in enumerate(workflow):
            print(f"[{self.team_name}] Step {i+1}/{len(workflow)}: {task.get('type')}")

            result = await self.assign_task(task)
            results.append(result)

            # 如果任务失败，可以选择中断或继续
            if not result.get("success", False):
                print(f"[{self.team_name}] Task failed: {result.get('error')}")
                # 这里可以选择 break 或 continue

        return results

    async def execute_parallel_tasks(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        并行执行多个任务

        Args:
            tasks: 任务列表

        Returns:
            所有任务的结果
        """
        print(f"[{self.team_name}] Executing {len(tasks)} tasks in parallel")

        # 创建并行任务
        task_futures = [
            self.assign_task(task)
            for task in tasks
        ]

        # 等待所有任务完成
        results = await asyncio.gather(*task_futures, return_exceptions=True)

        return results

    # === 查询和统计 ===

    async def query_agent_capabilities(self) -> Dict[str, Any]:
        """查询所有 Agent 的能力"""
        capabilities = {}

        for agent in self.agents.values():
            # 发送能力查询消息
            message = Message(
                message_type=MessageType.CAPABILITY_QUERY,
                sender_id="coordinator",
                receiver_id=agent.agent_id,
                content={}
            )
            agent.receive_message(message)

            # 处理消息
            await agent.process_messages()

            # 获取响应
            if agent.outbox.size() > 0:
                response = agent.outbox.pop()
                if response.message_type == MessageType.CAPABILITY_RESPONSE:
                    capabilities[agent.agent_id] = response.content

        return capabilities

    def get_team_status(self) -> Dict[str, Any]:
        """获取团队状态"""
        return {
            "team_name": self.team_name,
            "total_agents": len(self.agents),
            "agents": {
                agent_id: agent.get_info()
                for agent_id, agent in self.agents.items()
            },
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_messages_sent = sum(
            agent.stats["messages_sent"]
            for agent in self.agents.values()
        )
        total_messages_received = sum(
            agent.stats["messages_received"]
            for agent in self.agents.values()
        )
        total_tasks_completed = sum(
            agent.stats["tasks_completed"]
            for agent in self.agents.values()
        )
        total_tasks_failed = sum(
            agent.stats["tasks_failed"]
            for agent in self.agents.values()
        )

        return {
            "team_name": self.team_name,
            "agents_count": len(self.agents),
            "messages": {
                "sent": total_messages_sent,
                "received": total_messages_received,
            },
            "tasks": {
                "completed": total_tasks_completed,
                "failed": total_tasks_failed,
                "active": len(self.active_tasks),
                "success_rate": (
                    total_tasks_completed / (total_tasks_completed + total_tasks_failed)
                    if (total_tasks_completed + total_tasks_failed) > 0
                    else 0
                )
            }
        }

    # === 工具方法 ===

    def __repr__(self) -> str:
        return f"<TeamCoordinator(name={self.team_name}, agents={len(self.agents)})>"
