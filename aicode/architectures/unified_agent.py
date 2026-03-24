"""统一 Agent 接口 - 支持 ReAct 和 Plan-Execute 两种模式"""

from typing import Optional, Dict, Any, Literal, List
from ..models.base import AIModel
from ..memory.memory_manager import MemoryManager
from .react_agent import ReActAgent
from .plan_execute_agent import PlanExecuteAgent
from .tools_enhanced import ToolRegistry, create_enhanced_tools
from ..agent.file_handler import FileHandler
from ..agent.code_generator import CodeGenerator
from ..agent.code_modifier import CodeModifier


class UnifiedAgent:
    """
    统一 Agent 接口

    支持两种模式：
    - ReAct: 适合需要探索和迭代的复杂任务
    - Plan-Execute: 适合需要整体规划的结构化任务
    """

    def __init__(
        self,
        model: AIModel,
        memory_dir: str = ".aicode_memory",
        verbose: bool = True,
    ):
        self.model = model
        self.verbose = verbose

        # 初始化记忆管理器
        self.memory = MemoryManager(storage_dir=memory_dir)

        # 初始化基础组件
        self.file_handler = FileHandler()
        self.code_generator = CodeGenerator(model)
        self.code_modifier = CodeModifier(model, self.file_handler)

        # 创建工具注册表
        self.tool_registry = create_enhanced_tools()

        # 初始化两种 Agent
        self.react_agent = ReActAgent(
            model=model,
            tool_registry=self.tool_registry,
            memory_manager=self.memory,
            verbose=verbose,
        )

        self.plan_execute_agent = PlanExecuteAgent(
            model=model,
            tool_registry=self.tool_registry,
            memory_manager=self.memory,
            verbose=verbose,
        )

    async def run(
        self,
        task: str,
        mode: Literal["react", "plan", "auto"] = "auto",
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        执行任务

        Args:
            task: 任务描述
            mode: 执行模式 (react/plan/auto)
            context: 额外上下文

        Returns:
            执行结果
        """
        # 自动选择模式
        if mode == "auto":
            mode = await self._choose_mode(task)
            if self.verbose:
                print(f"\n[Auto Mode] Selected: {mode.upper()}")

        # 执行
        if mode == "react":
            result = await self.react_agent.run(task, context)
            result["mode"] = "react"
            if self.verbose:
                print("\n" + self.react_agent.get_execution_summary(result))
        else:  # plan
            result = await self.plan_execute_agent.run(task, context)
            result["mode"] = "plan-execute"
            if self.verbose:
                print("\n" + self.plan_execute_agent.get_execution_summary(result))

        # 保存重要信息到长期记忆
        self._save_to_long_term_memory(task, result)

        return result

    async def _choose_mode(self, task: str) -> Literal["react", "plan"]:
        """
        自动选择执行模式

        ReAct 适合:
        - 需要探索的任务
        - 不确定性高的任务
        - 需要动态调整的任务

        Plan-Execute 适合:
        - 结构化的任务
        - 步骤明确的任务
        - 需要整体规划的任务
        """
        system_prompt = """Analyze the task and determine which execution mode is more suitable.

ReAct mode: Best for exploratory tasks, uncertain requirements, need for dynamic adjustment
Plan-Execute mode: Best for structured tasks, clear steps, need for overall planning

Respond with ONLY one word: "react" or "plan"
"""

        response = await self.model.generate(
            prompt=f"Task: {task}\n\nWhich mode should we use?",
            system_prompt=system_prompt,
            max_tokens=50,
            temperature=0.3,
        )

        mode = response.strip().lower()
        if "react" in mode:
            return "react"
        else:
            return "plan"

    def _save_to_long_term_memory(self, task: str, result: Dict[str, Any]):
        """保存执行结果到长期记忆"""
        # 保存任务执行记录
        from datetime import datetime
        task_key = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.memory.remember(
            key=task_key,
            value={
                "task": task,
                "mode": result.get("mode", "unknown"),
                "success": result.get("success", False),
                "summary": result.get("summary", result.get("answer", ""))[:500],
            },
            category="tasks",
            tags=["task", result.get("mode", "unknown")],
            importance=7 if result.get("success") else 5,
        )

    # === 记忆管理接口 ===

    def remember(self, key: str, value: Any, category: str = "general", importance: int = 5):
        """保存到长期记忆"""
        self.memory.remember(key, value, category=category, importance=importance)

    def recall(self, key: str) -> Optional[Any]:
        """从长期记忆检索"""
        return self.memory.recall(key)

    def search_memory(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """搜索记忆"""
        return self.memory.search_memories(query=query, category=category)

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计"""
        return self.memory.get_statistics()

    def clear_short_term_memory(self):
        """清空短期记忆"""
        self.memory.clear_short_term()

    def export_session(self, filepath: str):
        """导出会话"""
        self.memory.export_session(filepath)

    def import_session(self, filepath: str):
        """导入会话"""
        self.memory.import_session(filepath)

    # === 工具管理接口 ===

    def register_tool(self, tool):
        """注册新工具"""
        self.tool_registry.register(tool)

    def list_tools(self) -> List[str]:
        """列出所有可用工具"""
        return [tool.name for tool in self.tool_registry.get_all_tools()]

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具信息"""
        tool = self.tool_registry.get_tool(tool_name)
        if tool:
            return tool.to_dict()
        return None
