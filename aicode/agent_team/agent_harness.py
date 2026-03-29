"""Agent Harness - Agent 运行环境

为 Agent Team 中的每个 Agent 提供完整的 AI 能力，包括：
- AI Model（思考和生成能力）
- Tools（工具执行能力）
- Skills（专业技能）
- Memory（记忆能力）
- 推理架构（ReAct、Plan-Execute）
"""

from typing import Optional, Dict, Any, List, Literal
from ..models.base import AIModel
from ..memory.memory_manager import MemoryManager
from ..architectures.react_agent import ReActAgent
from ..architectures.plan_execute_agent import PlanExecuteAgent
from ..architectures.tools_enhanced import ToolRegistry, Tool
from ..skills import SkillRegistry, Skill
from .base_agent import BaseAgent


class AgentHarness:
    """
    Agent 运行环境（Harness）

    为每个 Agent 提供：
    1. AI Model - 思考和决策能力
    2. Tools - 执行具体操作
    3. Skills - 领域专业技能
    4. Memory - 短期和长期记忆
    5. Reasoning - ReAct/Plan-Execute 推理架构

    使用示例:
        harness = AgentHarness(
            agent=code_agent,
            model=claude_model,
            mode="react"
        )

        result = await harness.execute_task({
            "type": "code_generation",
            "description": "创建快速排序函数"
        })
    """

    def __init__(
        self,
        agent: BaseAgent,
        model: AIModel,
        tool_registry: Optional[ToolRegistry] = None,
        skill_registry: Optional[SkillRegistry] = None,
        memory_manager: Optional[MemoryManager] = None,
        mode: Literal["react", "plan", "auto"] = "auto",
        verbose: bool = False,
    ):
        """
        初始化 Agent Harness

        Args:
            agent: 要增强的 BaseAgent
            model: AI 模型
            tool_registry: 工具注册表（可选）
            skill_registry: 技能注册表（可选）
            memory_manager: 记忆管理器（可选）
            mode: 推理模式 (react/plan/auto)
            verbose: 是否输出详细日志
        """
        self.agent = agent
        self.model = model
        self.mode = mode
        self.verbose = verbose

        # 初始化各个组件
        self.tools = tool_registry or ToolRegistry()
        self.skills = skill_registry or SkillRegistry()
        self.memory = memory_manager or MemoryManager(
            storage_dir=f".aicode_memory/agents/{agent.agent_id}"
        )

        # 为 Agent 创建专属的工具集
        self._register_agent_specific_tools()

        # 初始化推理引擎
        self.react_agent = ReActAgent(
            model=model,
            tool_registry=self.tools,
            memory_manager=self.memory,
            verbose=verbose
        )

        self.plan_execute_agent = PlanExecuteAgent(
            model=model,
            tool_registry=self.tools,
            memory_manager=self.memory,
            verbose=verbose
        )

    def _register_agent_specific_tools(self):
        """根据 Agent 能力注册专属工具"""
        # 这里可以根据 agent.capabilities 动态注册工具
        # 例如：如果 agent 有 "file_read" 能力，就注册文件读取工具
        pass

    async def execute_task(
        self,
        task: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行任务（核心方法）

        Args:
            task: 任务描述，需包含 'type' 和其他参数
            context: 额外上下文

        Returns:
            任务执行结果
        """
        if self.verbose:
            print(f"\n[{self.agent.name}] Executing task: {task.get('type')}")

        # 构建任务描述
        task_description = self._format_task_description(task)

        # 根据模式选择推理引擎
        mode = await self._choose_mode(task) if self.mode == "auto" else self.mode

        if mode == "react":
            result = await self.react_agent.run(task_description, context)
        else:  # plan
            result = await self.plan_execute_agent.run(task_description, context)

        # 转换为标准格式
        return self._format_result(result, task)

    def _format_task_description(self, task: Dict[str, Any]) -> str:
        """将任务字典格式化为自然语言描述"""
        task_type = task.get("type", "unknown")
        description = task.get("description", "")

        # 构建详细的任务描述
        parts = [f"Task Type: {task_type}"]

        if description:
            parts.append(f"Description: {description}")

        # 添加其他参数
        for key, value in task.items():
            if key not in ["type", "description"]:
                parts.append(f"{key}: {value}")

        return "\n".join(parts)

    async def _choose_mode(self, task: Dict[str, Any]) -> Literal["react", "plan"]:
        """自动选择推理模式"""
        task_type = task.get("type", "")

        # 简单策略：复杂任务用 plan，简单任务用 react
        complex_tasks = [
            "code_refactor",
            "project_setup",
            "architecture_design",
            "bug_investigation"
        ]

        if task_type in complex_tasks:
            return "plan"
        else:
            return "react"

    def _format_result(
        self,
        raw_result: Dict[str, Any],
        original_task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """格式化结果为标准格式"""
        return {
            "success": raw_result.get("success", False),
            "task_type": original_task.get("type"),
            "answer": raw_result.get("answer"),
            "iterations": raw_result.get("iterations", 0),
            "trajectory": raw_result.get("trajectory", []),
            "metadata": {
                "agent_id": self.agent.agent_id,
                "agent_name": self.agent.name,
                "mode": raw_result.get("mode", self.mode)
            }
        }

    # === 技能执行 ===

    async def execute_skill(
        self,
        skill_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行特定技能

        Args:
            skill_name: 技能名称
            **kwargs: 技能参数

        Returns:
            技能执行结果
        """
        skill = self.skills.get_skill(skill_name)
        if not skill:
            return {
                "success": False,
                "error": f"Skill '{skill_name}' not found"
            }

        # 执行技能
        try:
            result = await skill.execute(**kwargs)
            return {
                "success": True,
                "skill": skill_name,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "skill": skill_name
            }

    # === 工具管理 ===

    def add_tool(self, tool: Tool):
        """添加工具"""
        self.tools.register(tool)

    def add_skill(self, skill: Skill):
        """添加技能"""
        self.skills.register(skill)

    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        return [tool.name for tool in self.tools.get_all_tools()]

    def get_available_skills(self) -> List[str]:
        """获取可用技能列表"""
        return self.skills.list_skills()

    # === 记忆管理 ===

    def add_to_memory(self, role: str, content: str, metadata: Optional[Dict] = None):
        """添加信息到记忆"""
        self.memory.add_message(role, content, metadata)

    def get_memory_context(self, include_long_term: bool = True) -> str:
        """获取记忆上下文"""
        return self.memory.get_full_context(include_long_term)

    def clear_short_term_memory(self):
        """清除短期记忆"""
        self.memory.clear_short_term()

    # === 统计信息 ===

    def get_harness_info(self) -> Dict[str, Any]:
        """获取 Harness 信息"""
        return {
            "agent_id": self.agent.agent_id,
            "agent_name": self.agent.name,
            "mode": self.mode,
            "tools_count": len(self.tools.get_all_tools()),
            "skills_count": len(self.skills.list_skills()),
            "memory_messages": len(self.memory.short_term.messages),
        }


class HarnessedAgent(BaseAgent):
    """
    带 Harness 的 Agent（增强版 Agent）

    这是一个集成了 AgentHarness 的 BaseAgent 子类
    使用示例：
        agent = HarnessedAgent(
            agent_id="smart_code_agent",
            name="Smart Code Expert",
            capabilities=["code_generation", "code_review"],
            model=claude_model
        )
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        role,
        capabilities: List[str],
        model: AIModel,
        tool_registry: Optional[ToolRegistry] = None,
        skill_registry: Optional[SkillRegistry] = None,
        mode: Literal["react", "plan", "auto"] = "auto",
        description: str = "",
        verbose: bool = False,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities,
            description=description
        )

        # 创建 Harness
        self.harness = AgentHarness(
            agent=self,
            model=model,
            tool_registry=tool_registry,
            skill_registry=skill_registry,
            mode=mode,
            verbose=verbose
        )

    async def handle_message(self, message):
        """处理消息（使用 Harness 的能力）"""
        from .message import MessageType

        if message.message_type == MessageType.TASK_REQUEST:
            await self._handle_task_request(message)
        elif message.message_type == MessageType.QUERY:
            await self._handle_query(message)

    async def _handle_task_request(self, message):
        """处理任务请求"""
        from .message import MessageType
        from .base_agent import AgentStatus

        self.set_status(AgentStatus.BUSY)

        task = message.content
        try:
            # 使用 Harness 执行任务
            result = await self.harness.execute_task(task)
            reply = message.create_reply(result, MessageType.TASK_COMPLETE)
            self.stats["tasks_completed"] += 1
        except Exception as e:
            reply = message.create_reply(
                {"success": False, "error": str(e)},
                MessageType.ERROR
            )
            self.stats["tasks_failed"] += 1

        self.outbox.push(reply)
        self.set_status(AgentStatus.IDLE)

    async def _handle_query(self, message):
        """处理查询"""
        from .message import MessageType

        query_task = {
            "type": "query",
            "query": message.content.get("query", "")
        }

        result = await self.harness.execute_task(query_task)
        reply = message.create_reply(result, MessageType.QUERY_RESPONSE)
        self.outbox.push(reply)

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务（使用 Harness）"""
        return await self.harness.execute_task(task)
