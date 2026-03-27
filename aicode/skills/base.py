"""Skill 基类和注册表"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SkillExecutionContext:
    """技能执行上下文"""
    tools: Dict[str, Callable]  # 可用工具
    memory: Optional[Any] = None  # 记忆管理器
    working_dir: str = "."  # 工作目录
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据


class Skill(ABC):
    """技能基类"""

    def __init__(
        self,
        name: str,
        description: str,
        category: str = "general",
        required_tools: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            name: 技能名称
            description: 技能描述
            category: 分类（code, file, git, general）
            required_tools: 需要的工具列表
            parameters: 参数定义（JSON Schema）
        """
        self.name = name
        self.description = description
        self.category = category
        self.required_tools = required_tools or []
        self.parameters = parameters or {
            "type": "object",
            "properties": {},
            "required": []
        }

        # 统计信息
        self.execution_count = 0
        self.success_count = 0
        self.last_executed_at: Optional[datetime] = None

    @abstractmethod
    async def execute(
        self,
        context: SkillExecutionContext,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行技能

        Args:
            context: 执行上下文
            **kwargs: 技能参数

        Returns:
            执行结果字典：
            {
                "success": bool,
                "message": str,
                "data": Any,
                "steps": List[str]  # 执行步骤记录
            }
        """
        pass

    def validate_tools(self, available_tools: List[str]) -> bool:
        """验证所需工具是否可用"""
        return all(tool in available_tools for tool in self.required_tools)

    def record_execution(self, success: bool):
        """记录执行统计"""
        self.execution_count += 1
        if success:
            self.success_count += 1
        self.last_executed_at = datetime.now()

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        success_rate = (
            self.success_count / self.execution_count
            if self.execution_count > 0
            else 0.0
        )
        return {
            "name": self.name,
            "category": self.category,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "success_rate": success_rate,
            "last_executed_at": (
                self.last_executed_at.isoformat()
                if self.last_executed_at
                else None
            )
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于序列化）"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "required_tools": self.required_tools,
            "parameters": self.parameters,
            "stats": self.get_stats()
        }


class SkillRegistry:
    """技能注册表"""

    def __init__(self):
        self.skills: Dict[str, Skill] = {}

    def register(self, skill: Skill):
        """注册技能"""
        self.skills[skill.name] = skill

    def get(self, name: str) -> Optional[Skill]:
        """获取技能"""
        return self.skills.get(name)

    def list_skills(
        self,
        category: Optional[str] = None
    ) -> List[Skill]:
        """列出所有技能"""
        skills = list(self.skills.values())
        if category:
            skills = [s for s in skills if s.category == category]
        return skills

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return list(set(skill.category for skill in self.skills.values()))

    def search(self, query: str) -> List[Skill]:
        """搜索技能"""
        query_lower = query.lower()
        results = []

        for skill in self.skills.values():
            if (
                query_lower in skill.name.lower() or
                query_lower in skill.description.lower() or
                query_lower in skill.category.lower()
            ):
                results.append(skill)

        return results

    async def execute_skill(
        self,
        name: str,
        context: SkillExecutionContext,
        **kwargs
    ) -> Dict[str, Any]:
        """执行技能"""
        skill = self.get(name)
        if not skill:
            return {
                "success": False,
                "message": f"Skill '{name}' not found",
                "data": None,
                "steps": []
            }

        # 验证工具
        available_tools = list(context.tools.keys())
        if not skill.validate_tools(available_tools):
            missing = [
                t for t in skill.required_tools
                if t not in available_tools
            ]
            return {
                "success": False,
                "message": f"Missing required tools: {missing}",
                "data": None,
                "steps": []
            }

        # 执行技能
        try:
            result = await skill.execute(context, **kwargs)
            skill.record_execution(result.get("success", False))
            return result
        except Exception as e:
            skill.record_execution(False)
            return {
                "success": False,
                "message": f"Skill execution error: {str(e)}",
                "data": None,
                "steps": [f"Error: {str(e)}"]
            }

    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有技能的统计信息"""
        return {
            "total_skills": len(self.skills),
            "categories": self.get_categories(),
            "skills": [skill.get_stats() for skill in self.skills.values()]
        }
