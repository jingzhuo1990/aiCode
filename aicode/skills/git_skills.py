"""Git 相关技能"""

import os
from typing import Dict, Any
from .base import Skill, SkillExecutionContext


class CommitChangesSkill(Skill):
    """提交代码变更技能"""

    def __init__(self):
        super().__init__(
            name="commit_changes",
            description="智能提交代码变更，自动生成提交信息",
            category="git",
            required_tools=["git_status", "git_diff", "run_command"],
            parameters={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "提交信息（可选，会自动生成）"
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要提交的文件列表（默认全部）"
                    }
                }
            }
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        message: str = None,
        files: list = None,
        **kwargs
    ) -> Dict[str, Any]:
        """执行提交"""
        steps = []

        # 1. 检查状态
        steps.append("Checking git status...")
        status = context.tools["git_status"](".")

        if "not a git repository" in status.lower():
            return {
                "success": False,
                "message": "Not a git repository",
                "data": None,
                "steps": steps
            }

        # 2. 查看变更
        steps.append("Analyzing changes...")
        diff = context.tools["git_diff"](".")

        # 3. 生成提交信息（如果未提供）
        if not message:
            steps.append("Generating commit message...")
            message = self._generate_commit_message(status, diff)

        # 4. 添加文件
        if files:
            for file in files:
                steps.append(f"Adding file: {file}")
                context.tools["run_command"](f"git add {file}")
        else:
            steps.append("Adding all changes...")
            context.tools["run_command"]("git add -A")

        # 5. 提交
        steps.append(f"Committing with message: {message}")
        commit_result = context.tools["run_command"](
            f'git commit -m "{message}"'
        )

        success = "Error" not in commit_result

        return {
            "success": success,
            "message": f"Changes committed: {message}",
            "data": {
                "commit_message": message,
                "files_added": files or "all",
                "commit_output": commit_result
            },
            "steps": steps
        }

    def _generate_commit_message(self, status: str, diff: str) -> str:
        """生成智能提交信息"""
        # 分析变更类型
        added = "new file:" in status
        modified = "modified:" in status
        deleted = "deleted:" in status

        if added and not modified and not deleted:
            return "feat: add new files"
        elif modified and not added and not deleted:
            return "fix: update existing files"
        elif deleted:
            return "refactor: remove files"
        else:
            return "chore: update project files"


class CreateBranchSkill(Skill):
    """创建分支技能"""

    def __init__(self):
        super().__init__(
            name="create_branch",
            description="创建并切换到新分支",
            category="git",
            required_tools=["run_command"],
            parameters={
                "type": "object",
                "properties": {
                    "branch_name": {
                        "type": "string",
                        "description": "分支名称"
                    },
                    "from_branch": {
                        "type": "string",
                        "description": "从哪个分支创建（默认当前分支）"
                    }
                },
                "required": ["branch_name"]
            }
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        branch_name: str,
        from_branch: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """创建分支"""
        steps = []

        # 1. 检查当前分支
        steps.append("Checking current branch...")
        current_branch = context.tools["run_command"](
            "git branch --show-current"
        ).strip()

        # 2. 切换到源分支（如果指定）
        if from_branch and from_branch != current_branch:
            steps.append(f"Switching to source branch: {from_branch}")
            context.tools["run_command"](f"git checkout {from_branch}")

        # 3. 创建并切换到新分支
        steps.append(f"Creating branch: {branch_name}")
        result = context.tools["run_command"](
            f"git checkout -b {branch_name}"
        )

        success = "Error" not in result and "fatal" not in result.lower()

        return {
            "success": success,
            "message": f"Branch '{branch_name}' created and checked out",
            "data": {
                "branch_name": branch_name,
                "from_branch": from_branch or current_branch,
                "output": result
            },
            "steps": steps
        }


class CodeReviewPRSkill(Skill):
    """PR 代码审查技能"""

    def __init__(self):
        super().__init__(
            name="review_pr",
            description="审查 Pull Request 的代码变更",
            category="git",
            required_tools=["git_diff", "git_log", "run_command"],
            parameters={
                "type": "object",
                "properties": {
                    "base_branch": {
                        "type": "string",
                        "description": "基准分支",
                        "default": "main"
                    },
                    "target_branch": {
                        "type": "string",
                        "description": "目标分支（默认当前分支）"
                    }
                }
            }
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        base_branch: str = "main",
        target_branch: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """审查 PR"""
        steps = []

        # 1. 获取当前分支
        if not target_branch:
            target_branch = context.tools["run_command"](
                "git branch --show-current"
            ).strip()

        steps.append(f"Reviewing changes: {target_branch} vs {base_branch}")

        # 2. 获取差异
        diff_cmd = f"git diff {base_branch}...{target_branch}"
        diff = context.tools["run_command"](diff_cmd)

        # 3. 获取提交历史
        log_cmd = f"git log {base_branch}..{target_branch} --oneline"
        log = context.tools["run_command"](log_cmd)

        # 4. 分析变更
        steps.append("Analyzing changes...")
        analysis = self._analyze_changes(diff, log)

        # 5. 生成审查报告
        steps.append("Generating review report...")
        report = self._generate_review_report(
            base_branch, target_branch, diff, log, analysis
        )

        return {
            "success": True,
            "message": f"PR review completed: {len(analysis['issues'])} issues found",
            "data": {
                "base_branch": base_branch,
                "target_branch": target_branch,
                "commits": len(log.split('\n')),
                "analysis": analysis,
                "report": report
            },
            "steps": steps
        }

    def _analyze_changes(self, diff: str, log: str) -> dict:
        """分析代码变更"""
        analysis = {
            "commits_count": len([l for l in log.split('\n') if l.strip()]),
            "files_changed": len([l for l in diff.split('\n') if l.startswith('+++ ')]),
            "additions": len([l for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]),
            "deletions": len([l for l in diff.split('\n') if l.startswith('-') and not l.startswith('---')]),
            "issues": []
        }

        # 检查大文件变更
        if analysis["additions"] + analysis["deletions"] > 1000:
            analysis["issues"].append({
                "severity": "warning",
                "message": "Large changeset (>1000 lines), consider splitting"
            })

        # 检查是否有测试
        if "test" not in diff.lower():
            analysis["issues"].append({
                "severity": "warning",
                "message": "No test files modified, consider adding tests"
            })

        # 检查是否有文档更新
        if ".md" not in diff and "doc" not in diff.lower():
            analysis["issues"].append({
                "severity": "info",
                "message": "No documentation updates found"
            })

        return analysis

    def _generate_review_report(
        self, base: str, target: str, diff: str, log: str, analysis: dict
    ) -> str:
        """生成审查报告"""
        report = f"""# PR Review: {target} → {base}

## Summary

- **Commits**: {analysis['commits_count']}
- **Files changed**: {analysis['files_changed']}
- **Additions**: +{analysis['additions']}
- **Deletions**: -{analysis['deletions']}

## Commits

```
{log}
```

## Issues ({len(analysis['issues'])})

"""
        if analysis["issues"]:
            for i, issue in enumerate(analysis["issues"], 1):
                report += f"{i}. **[{issue['severity'].upper()}]** {issue['message']}\n"
        else:
            report += "No issues found! ✅\n"

        report += "\n## Recommendation\n\n"
        if len(analysis["issues"]) == 0:
            report += "✅ **APPROVE** - Ready to merge\n"
        elif any(i["severity"] == "error" for i in analysis["issues"]):
            report += "❌ **REQUEST CHANGES** - Critical issues found\n"
        else:
            report += "💬 **COMMENT** - Minor issues to address\n"

        return report
