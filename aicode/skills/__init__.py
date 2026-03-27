"""Skills System - 高级可复用能力

Skills 是建立在 Tools 之上的更高层次抽象，用于执行复杂的多步骤任务。
"""

from .base import Skill, SkillRegistry, SkillExecutionContext
from .code_skills import (
    CodeRefactorSkill,
    AddTestsSkill,
    GenerateDocSkill,
    CodeReviewSkill
)
from .file_skills import (
    ProjectSetupSkill,
    BackupFilesSkill,
    CleanupSkill
)
from .git_skills import (
    CommitChangesSkill,
    CreateBranchSkill,
    CodeReviewPRSkill
)

__all__ = [
    # Base
    "Skill",
    "SkillRegistry",
    "SkillExecutionContext",

    # Code skills
    "CodeRefactorSkill",
    "AddTestsSkill",
    "GenerateDocSkill",
    "CodeReviewSkill",

    # File skills
    "ProjectSetupSkill",
    "BackupFilesSkill",
    "CleanupSkill",

    # Git skills
    "CommitChangesSkill",
    "CreateBranchSkill",
    "CodeReviewPRSkill",
]


def create_default_skills() -> SkillRegistry:
    """创建默认技能注册表"""
    registry = SkillRegistry()

    # 注册代码技能
    registry.register(CodeRefactorSkill())
    registry.register(AddTestsSkill())
    registry.register(GenerateDocSkill())
    registry.register(CodeReviewSkill())

    # 注册文件技能
    registry.register(ProjectSetupSkill())
    registry.register(BackupFilesSkill())
    registry.register(CleanupSkill())

    # 注册 Git 技能
    registry.register(CommitChangesSkill())
    registry.register(CreateBranchSkill())
    registry.register(CodeReviewPRSkill())

    return registry
