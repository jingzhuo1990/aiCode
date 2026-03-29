"""专业 Agent 实现"""

from typing import Dict, Any, Optional
from .base_agent import BaseAgent, AgentRole, AgentStatus
from .message import Message, MessageType
from ..models.base import AIModel
from ..architectures.tools_enhanced import ToolRegistry


class CodeAgent(BaseAgent):
    """
    代码专家 Agent

    专注于：代码生成、重构、分析
    """

    def __init__(
        self,
        agent_id: str = "code_agent",
        model: Optional[AIModel] = None,
        tool_registry: Optional[ToolRegistry] = None
    ):
        super().__init__(
            agent_id=agent_id,
            name="Code Expert",
            role=AgentRole.SPECIALIST,
            capabilities=[
                "code_generation",
                "code_refactor",
                "code_review",
                "code_analysis",
                "bug_fix"
            ],
            description="专业代码处理 Agent，擅长代码生成、重构和分析"
        )
        self.model = model
        self.tool_registry = tool_registry

    async def handle_message(self, message: Message):
        """处理消息"""
        if message.message_type == MessageType.TASK_REQUEST:
            await self._handle_task_request(message)
        elif message.message_type == MessageType.QUERY:
            await self._handle_query(message)

    async def _handle_task_request(self, message: Message):
        """处理任务请求"""
        self.set_status(AgentStatus.BUSY)

        task = message.content
        try:
            result = await self.execute_task(task)
            reply = message.create_reply(result, MessageType.TASK_COMPLETE)
            self.stats["tasks_completed"] += 1
        except Exception as e:
            reply = message.create_reply(
                {"error": str(e)},
                MessageType.ERROR
            )
            self.stats["tasks_failed"] += 1

        self.outbox.push(reply)
        self.set_status(AgentStatus.IDLE)

    async def _handle_query(self, message: Message):
        """处理查询"""
        query = message.content.get("query", "")
        response = {"answer": f"Code Agent: {query} 的答案"}
        reply = message.create_reply(response, MessageType.QUERY_RESPONSE)
        self.outbox.push(reply)

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行代码任务"""
        task_type = task.get("type")

        if task_type == "code_generation":
            return await self._generate_code(task)
        elif task_type == "code_refactor":
            return await self._refactor_code(task)
        elif task_type == "code_review":
            return await self._review_code(task)
        else:
            return {"success": False, "error": f"Unknown task type: {task_type}"}

    async def _generate_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """生成代码"""
        description = task.get("description", "")
        # 这里可以调用 model 或 tools
        return {
            "success": True,
            "code": f"# Generated code for: {description}\npass",
            "language": task.get("language", "python")
        }

    async def _refactor_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """重构代码"""
        code = task.get("code", "")
        return {
            "success": True,
            "refactored_code": code.upper(),  # 示例
            "improvements": ["improved naming", "better structure"]
        }

    async def _review_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """审查代码"""
        code = task.get("code", "")
        return {
            "success": True,
            "issues": [
                {"severity": "warning", "message": "Long function detected"},
                {"severity": "info", "message": "Consider adding docstrings"}
            ],
            "score": 85
        }


class FileAgent(BaseAgent):
    """
    文件操作专家 Agent

    专注于：文件读写、搜索、管理
    """

    def __init__(
        self,
        agent_id: str = "file_agent",
        tool_registry: Optional[ToolRegistry] = None
    ):
        super().__init__(
            agent_id=agent_id,
            name="File Manager",
            role=AgentRole.WORKER,
            capabilities=[
                "file_read",
                "file_write",
                "file_search",
                "file_backup",
                "directory_management"
            ],
            description="专业文件操作 Agent，擅长文件系统管理"
        )
        self.tool_registry = tool_registry

    async def handle_message(self, message: Message):
        """处理消息"""
        if message.message_type == MessageType.TASK_REQUEST:
            await self._handle_task_request(message)

    async def _handle_task_request(self, message: Message):
        """处理任务请求"""
        self.set_status(AgentStatus.BUSY)

        task = message.content
        try:
            result = await self.execute_task(task)
            reply = message.create_reply(result, MessageType.TASK_COMPLETE)
            self.stats["tasks_completed"] += 1
        except Exception as e:
            reply = message.create_reply(
                {"error": str(e)},
                MessageType.ERROR
            )
            self.stats["tasks_failed"] += 1

        self.outbox.push(reply)
        self.set_status(AgentStatus.IDLE)

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行文件任务"""
        task_type = task.get("type")

        if task_type == "file_read":
            return await self._read_file(task)
        elif task_type == "file_write":
            return await self._write_file(task)
        elif task_type == "file_search":
            return await self._search_files(task)
        else:
            return {"success": False, "error": f"Unknown task type: {task_type}"}

    async def _read_file(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """读取文件"""
        file_path = task.get("file_path", "")
        # 使用 tool_registry 中的 read_file
        return {
            "success": True,
            "file_path": file_path,
            "content": f"Content of {file_path}"
        }

    async def _write_file(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """写入文件"""
        file_path = task.get("file_path", "")
        content = task.get("content", "")
        return {
            "success": True,
            "file_path": file_path,
            "bytes_written": len(content)
        }

    async def _search_files(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """搜索文件"""
        pattern = task.get("pattern", "")
        return {
            "success": True,
            "pattern": pattern,
            "matches": ["file1.py", "file2.py"]
        }


class AnalysisAgent(BaseAgent):
    """
    分析专家 Agent

    专注于：数据分析、报告生成、趋势识别
    """

    def __init__(
        self,
        agent_id: str = "analysis_agent",
        model: Optional[AIModel] = None
    ):
        super().__init__(
            agent_id=agent_id,
            name="Data Analyst",
            role=AgentRole.ANALYZER,
            capabilities=[
                "data_analysis",
                "report_generation",
                "trend_analysis",
                "summary_creation"
            ],
            description="专业数据分析 Agent，擅长分析和总结"
        )
        self.model = model

    async def handle_message(self, message: Message):
        """处理消息"""
        if message.message_type == MessageType.TASK_REQUEST:
            await self._handle_task_request(message)

    async def _handle_task_request(self, message: Message):
        """处理任务请求"""
        self.set_status(AgentStatus.BUSY)

        task = message.content
        try:
            result = await self.execute_task(task)
            reply = message.create_reply(result, MessageType.TASK_COMPLETE)
            self.stats["tasks_completed"] += 1
        except Exception as e:
            reply = message.create_reply(
                {"error": str(e)},
                MessageType.ERROR
            )
            self.stats["tasks_failed"] += 1

        self.outbox.push(reply)
        self.set_status(AgentStatus.IDLE)

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行分析任务"""
        task_type = task.get("type")

        if task_type == "analyze_data":
            return await self._analyze_data(task)
        elif task_type == "generate_report":
            return await self._generate_report(task)
        elif task_type == "summarize":
            return await self._summarize(task)
        else:
            return {"success": False, "error": f"Unknown task type: {task_type}"}

    async def _analyze_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """分析数据"""
        data = task.get("data", [])
        return {
            "success": True,
            "analysis": {
                "count": len(data),
                "summary": "Data analysis complete"
            }
        }

    async def _generate_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """生成报告"""
        data = task.get("data", {})
        return {
            "success": True,
            "report": f"# Report\n\nGenerated from: {data}"
        }

    async def _summarize(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """总结"""
        content = task.get("content", "")
        return {
            "success": True,
            "summary": f"Summary of: {content[:100]}..."
        }


class PlannerAgent(BaseAgent):
    """
    规划专家 Agent

    专注于：任务规划、分解、调度
    """

    def __init__(
        self,
        agent_id: str = "planner_agent",
        model: Optional[AIModel] = None
    ):
        super().__init__(
            agent_id=agent_id,
            name="Task Planner",
            role=AgentRole.SPECIALIST,
            capabilities=[
                "task_planning",
                "task_decomposition",
                "workflow_design",
                "dependency_analysis"
            ],
            description="专业任务规划 Agent，擅长任务分解和调度"
        )
        self.model = model

    async def handle_message(self, message: Message):
        """处理消息"""
        if message.message_type == MessageType.TASK_REQUEST:
            await self._handle_task_request(message)

    async def _handle_task_request(self, message: Message):
        """处理任务请求"""
        self.set_status(AgentStatus.BUSY)

        task = message.content
        try:
            result = await self.execute_task(task)
            reply = message.create_reply(result, MessageType.TASK_COMPLETE)
            self.stats["tasks_completed"] += 1
        except Exception as e:
            reply = message.create_reply(
                {"error": str(e)},
                MessageType.ERROR
            )
            self.stats["tasks_failed"] += 1

        self.outbox.push(reply)
        self.set_status(AgentStatus.IDLE)

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行规划任务"""
        task_type = task.get("type")

        if task_type == "plan_task":
            return await self._plan_task(task)
        elif task_type == "decompose_task":
            return await self._decompose_task(task)
        else:
            return {"success": False, "error": f"Unknown task type: {task_type}"}

    async def _plan_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """规划任务"""
        description = task.get("description", "")
        return {
            "success": True,
            "plan": {
                "steps": [
                    {"step": 1, "action": "分析需求"},
                    {"step": 2, "action": "设计方案"},
                    {"step": 3, "action": "执行实施"},
                ],
                "estimated_time": "30 minutes"
            }
        }

    async def _decompose_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """分解任务"""
        description = task.get("description", "")
        return {
            "success": True,
            "subtasks": [
                {
                    "id": "subtask_1",
                    "description": f"Subtask 1 for: {description}",
                    "agent_type": "code_agent"
                },
                {
                    "id": "subtask_2",
                    "description": f"Subtask 2 for: {description}",
                    "agent_type": "file_agent"
                }
            ]
        }
