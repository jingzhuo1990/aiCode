# 🎯 Skills System 使用指南

## 📋 目录

- [什么是 Skills？](#什么是-skills)
- [Skills vs Tools](#skills-vs-tools)
- [可用技能列表](#可用技能列表)
- [使用方法](#使用方法)
- [自定义技能](#自定义技能)
- [最佳实践](#最佳实践)

---

## 🤔 什么是 Skills？

**Skills（技能）** 是建立在 Tools 之上的**更高层次抽象**，用于执行**复杂的多步骤任务**。

### 核心概念

```
Skills = 多个 Tools + 业务逻辑 + 决策能力
```

**示例**：
- **Tool**: `read_file` - 读取单个文件
- **Skill**: `code_refactor` - 读取文件 → 分析问题 → 应用重构 → 备份 → 写入

---

## 🔀 Skills vs Tools

| 特性 | Tools | Skills |
|-----|-------|--------|
| **抽象层次** | 低 - 原子操作 | 高 - 业务流程 |
| **复杂度** | 简单 - 单一功能 | 复杂 - 多步骤 |
| **可组合性** | ✅ 被 Skills 组合 | ✅ 可组合多个 Tools |
| **业务逻辑** | ❌ 无 | ✅ 有 |
| **决策能力** | ❌ 无 | ✅ 有 |
| **示例** | `read_file`, `write_file` | `code_refactor`, `add_tests` |

### 示例对比

**使用 Tools（需要多次调用）**：
```bash
# 步骤 1: 读取文件
python -m aicode.cli_agent tool-call read_file --path code.py

# 步骤 2: 手动分析...
# 步骤 3: 手动重构...
# 步骤 4: 创建备份
python -m aicode.cli_agent tool-call copy_file --src code.py --dest code.py.bak

# 步骤 5: 写入新代码
python -m aicode.cli_agent tool-call write_file --path code.py --content "..."
```

**使用 Skills（一次调用）**：
```bash
# 一条命令完成所有步骤！
python -m aicode.cli_agent skill-run code_refactor -p file_path=code.py -p focus=naming
```

---

## 📚 可用技能列表

### 🧑‍💻 Code Skills (代码相关)

#### 1. **code_refactor** - 代码重构

自动重构代码，提高可读性和可维护性。

**功能**：
- ✅ 分析代码问题（命名、结构、文档）
- ✅ 应用重构规则
- ✅ 自动备份原文件
- ✅ 生成重构报告

**参数**：
- `file_path` (必需): 要重构的文件路径
- `focus` (可选): 重构重点
  - `naming` - 改进变量命名
  - `structure` - 优化代码结构
  - `documentation` - 添加文档
  - `general` - 综合重构（默认）

**使用示例**：
```bash
# 综合重构
python -m aicode.cli_agent skill-run code_refactor -p file_path=mycode.py

# 专注于命名优化
python -m aicode.cli_agent skill-run code_refactor \
  -p file_path=mycode.py \
  -p focus=naming

# 在特定目录执行
python -m aicode.cli_agent skill-run code_refactor \
  -p file_path=src/main.py \
  --working-dir /path/to/project
```

**输出**：
```
✓ Skill executed successfully!

Message: Code refactored successfully. Backup at: mycode.py.bak

Execution Steps:
  • Reading file: mycode.py
  • Analyzing code issues...
  • Applying refactoring (focus: naming)...
  • Creating backup: mycode.py.bak
  • Writing refactored code to: mycode.py

Result Data:
{
  "original_lines": 150,
  "refactored_lines": 145,
  "issues_found": 3,
  "backup_path": "mycode.py.bak"
}
```

---

#### 2. **add_tests** - 生成单元测试

为指定文件自动生成单元测试框架。

**功能**：
- ✅ 分析源文件中的函数
- ✅ 生成测试文件结构
- ✅ 支持 pytest 和 unittest
- ✅ 自动创建 tests 目录

**参数**：
- `file_path` (必需): 要测试的文件路径
- `test_framework` (可选): 测试框架
  - `pytest` - 使用 pytest（默认）
  - `unittest` - 使用标准库 unittest

**使用示例**：
```bash
# 使用 pytest（默认）
python -m aicode.cli_agent skill-run add_tests -p file_path=calculator.py

# 使用 unittest
python -m aicode.cli_agent skill-run add_tests \
  -p file_path=calculator.py \
  -p test_framework=unittest
```

**生成的测试文件**（pytest）：
```python
"""Tests for calculator"""

import pytest
from calculator import *


def test_add():
    """Test add function"""
    # TODO: Implement test
    pass


def test_subtract():
    """Test subtract function"""
    # TODO: Implement test
    pass
```

---

#### 3. **generate_doc** - 生成项目文档

自动生成项目文档（README、API 文档等）。

**功能**：
- ✅ 扫描项目结构
- ✅ 生成 README.md 模板
- ✅ 包含项目结构图
- ✅ 添加常用章节

**参数**：
- `project_dir` (可选): 项目目录（默认当前目录）
- `doc_type` (可选): 文档类型
  - `readme` - README.md（默认）
  - `api` - API 文档
  - `guide` - 使用指南

**使用示例**：
```bash
# 生成 README
python -m aicode.cli_agent skill-run generate_doc

# 生成 API 文档
python -m aicode.cli_agent skill-run generate_doc \
  -p project_dir=. \
  -p doc_type=api
```

---

#### 4. **code_review** - 代码审查

自动审查代码质量并提供改进建议。

**功能**：
- ✅ 检查代码长度
- ✅ 检查文档完整性
- ✅ 检查异常处理
- ✅ 检查类型注解
- ✅ 生成审查报告

**参数**：
- `file_path` (必需): 要审查的文件路径

**使用示例**：
```bash
python -m aicode.cli_agent skill-run code_review -p file_path=app.py
```

**输出报告**：
```markdown
# Code Review: app.py

## Summary

- Lines of code: 250
- Issues found: 3

## Issues

1. **[WARNING]** File is very long (>300 lines), consider splitting
2. **[ERROR]** Missing error handling for I/O operations
3. **[INFO]** Consider adding type hints

```

---

### 📁 File Skills (文件操作)

#### 5. **project_setup** - 项目初始化

创建标准项目结构和配置文件。

**功能**：
- ✅ 创建目录结构
- ✅ 生成 README.md
- ✅ 创建 .gitignore
- ✅ 初始化配置文件
- ✅ 支持多种项目类型

**参数**：
- `project_name` (必需): 项目名称
- `project_type` (可选): 项目类型
  - `python` - Python 项目（默认）
  - `node` - Node.js 项目
  - `general` - 通用项目

**使用示例**：
```bash
# Python 项目
python -m aicode.cli_agent skill-run project_setup \
  -p project_name=my_app \
  -p project_type=python

# Node.js 项目
python -m aicode.cli_agent skill-run project_setup \
  -p project_name=my_app \
  -p project_type=node
```

**生成的 Python 项目结构**：
```
my_app/
├── README.md
├── .gitignore
├── requirements.txt
├── my_app/
│   ├── __init__.py
│   └── main.py
└── tests/
    ├── __init__.py
    └── test_main.py
```

---

#### 6. **backup_files** - 文件备份

智能备份文件或目录。

**功能**：
- ✅ 支持单文件备份
- ✅ 支持整个目录备份
- ✅ 自动添加时间戳
- ✅ 保持目录结构

**参数**：
- `source` (必需): 要备份的源路径
- `backup_dir` (可选): 备份目录（默认 `backups`）

**使用示例**：
```bash
# 备份单个文件
python -m aicode.cli_agent skill-run backup_files -p source=config.json

# 备份整个目录
python -m aicode.cli_agent skill-run backup_files \
  -p source=src \
  -p backup_dir=daily_backups
```

**备份结构**：
```
backups/
└── 20260327_143000/
    ├── config.json
    └── ...
```

---

#### 7. **cleanup** - 清理临时文件

清理项目中的临时文件和缓存。

**功能**：
- ✅ 递归扫描目录
- ✅ 删除匹配的文件
- ✅ 支持自定义模式
- ✅ 安全删除

**参数**：
- `directory` (可选): 要清理的目录（默认当前目录）
- `patterns` (可选): 要删除的文件模式（数组）
  - 默认: `*.pyc`, `*.pyo`, `__pycache__`, `*.log`, `*.tmp`

**使用示例**：
```bash
# 使用默认模式
python -m aicode.cli_agent skill-run cleanup

# 自定义模式
python -m aicode.cli_agent skill-run cleanup \
  -p directory=./build \
  -p patterns='["*.o", "*.obj", "*.tmp"]'
```

---

### 🔀 Git Skills (版本控制)

#### 8. **commit_changes** - 智能提交

自动分析变更并生成提交信息。

**功能**：
- ✅ 检查 git 状态
- ✅ 分析代码变更
- ✅ 自动生成提交信息
- ✅ 智能添加文件

**参数**：
- `message` (可选): 提交信息（不提供则自动生成）
- `files` (可选): 要提交的文件列表（不提供则提交全部）

**使用示例**：
```bash
# 自动生成提交信息
python -m aicode.cli_agent skill-run commit_changes

# 自定义提交信息
python -m aicode.cli_agent skill-run commit_changes \
  -p message="feat: add new feature"

# 只提交特定文件
python -m aicode.cli_agent skill-run commit_changes \
  -p message="fix: update config" \
  -p files='["config.py", "settings.json"]'
```

---

#### 9. **create_branch** - 创建分支

创建并切换到新分支。

**功能**：
- ✅ 检查当前分支
- ✅ 切换到源分支（可选）
- ✅ 创建新分支
- ✅ 自动切换

**参数**：
- `branch_name` (必需): 新分支名称
- `from_branch` (可选): 从哪个分支创建（默认当前分支）

**使用示例**：
```bash
# 从当前分支创建
python -m aicode.cli_agent skill-run create_branch \
  -p branch_name=feature/new-api

# 从 main 分支创建
python -m aicode.cli_agent skill-run create_branch \
  -p branch_name=feature/new-api \
  -p from_branch=main
```

---

#### 10. **review_pr** - PR 代码审查

审查 Pull Request 的代码变更。

**功能**：
- ✅ 对比两个分支的差异
- ✅ 分析提交历史
- ✅ 检查变更规模
- ✅ 检查测试覆盖
- ✅ 生成审查报告
- ✅ 给出合并建议

**参数**：
- `base_branch` (可选): 基准分支（默认 `main`）
- `target_branch` (可选): 目标分支（默认当前分支）

**使用示例**：
```bash
# 审查当前分支 vs main
python -m aicode.cli_agent skill-run review_pr

# 审查特定分支对比
python -m aicode.cli_agent skill-run review_pr \
  -p base_branch=main \
  -p target_branch=feature/new-api
```

**审查报告**：
```markdown
# PR Review: feature/new-api → main

## Summary

- **Commits**: 5
- **Files changed**: 12
- **Additions**: +345
- **Deletions**: -78

## Commits

```
abc1234 feat: add new API endpoint
def5678 test: add unit tests
...
```

## Issues (2)

1. **[WARNING]** Large changeset (>1000 lines), consider splitting
2. **[INFO]** No documentation updates found

## Recommendation

💬 **COMMENT** - Minor issues to address
```

---

## 🚀 使用方法

### 1. 列出所有技能

```bash
# 查看所有技能
python -m aicode.cli_agent skill-list

# 按分类查看
python -m aicode.cli_agent skill-list --category code
python -m aicode.cli_agent skill-list --category file
python -m aicode.cli_agent skill-list --category git
```

### 2. 执行技能

```bash
# 基本语法
python -m aicode.cli_agent skill-run <skill_name> -p key1=value1 -p key2=value2

# 示例
python -m aicode.cli_agent skill-run code_refactor -p file_path=mycode.py
```

### 3. 查看统计信息

```bash
python -m aicode.cli_agent skill-stats
```

---

## 🔧 自定义技能

### 创建自定义技能

1. **继承 Skill 基类**：

```python
from aicode.skills.base import Skill, SkillExecutionContext
from typing import Dict, Any


class MyCustomSkill(Skill):
    """我的自定义技能"""

    def __init__(self):
        super().__init__(
            name="my_custom_skill",
            description="执行自定义任务",
            category="custom",
            required_tools=["read_file", "write_file"],
            parameters={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "输入文件路径"
                    },
                    "option": {
                        "type": "string",
                        "description": "选项",
                        "default": "default"
                    }
                },
                "required": ["input_file"]
            }
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        input_file: str,
        option: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """执行技能逻辑"""
        steps = []

        # 1. 使用工具
        steps.append(f"Reading {input_file}")
        content = context.tools["read_file"](input_file)

        # 2. 处理逻辑
        steps.append(f"Processing with option: {option}")
        result_content = self._process(content, option)

        # 3. 写入结果
        output_file = f"{input_file}.out"
        steps.append(f"Writing to {output_file}")
        context.tools["write_file"](output_file, result_content)

        return {
            "success": True,
            "message": f"Processed {input_file}",
            "data": {
                "input_file": input_file,
                "output_file": output_file,
                "option": option
            },
            "steps": steps
        }

    def _process(self, content: str, option: str) -> str:
        """自定义处理逻辑"""
        # 在这里实现你的业务逻辑
        return content.upper() if option == "uppercase" else content
```

2. **注册技能**：

```python
from aicode.skills import SkillRegistry

registry = SkillRegistry()
registry.register(MyCustomSkill())
```

3. **使用技能**：

```bash
python -m aicode.cli_agent skill-run my_custom_skill \
  -p input_file=test.txt \
  -p option=uppercase
```

---

## 💡 最佳实践

### 1. **选择合适的抽象层次**

```python
# ❌ 不好 - 为简单操作创建 Skill
class ReadFileSkill(Skill):
    # 这应该是一个 Tool，不是 Skill
    pass

# ✅ 好 - 为复杂流程创建 Skill
class AnalyzeCodebaseSkill(Skill):
    # 读取多个文件 + 分析 + 生成报告
    pass
```

### 2. **技能应该是独立的**

```python
# ✅ 好 - 技能不依赖外部状态
async def execute(self, context: SkillExecutionContext, **kwargs):
    # 所有需要的信息通过参数传入
    file_path = kwargs["file_path"]
    ...
```

### 3. **提供清晰的执行步骤**

```python
steps = []
steps.append("Step 1: Reading source files...")
steps.append("Step 2: Analyzing code...")
steps.append("Step 3: Generating report...")

return {"success": True, "steps": steps, ...}
```

### 4. **处理错误优雅**

```python
try:
    result = context.tools["some_tool"](...)
    if "Error" in result:
        return {
            "success": False,
            "message": f"Tool failed: {result}",
            "data": None,
            "steps": steps
        }
except Exception as e:
    return {
        "success": False,
        "message": f"Unexpected error: {str(e)}",
        "data": None,
        "steps": steps
    }
```

### 5. **提供有用的元数据**

```python
return {
    "success": True,
    "message": "Task completed",
    "data": {
        "files_processed": 10,
        "total_lines": 1500,
        "issues_found": 3,
        "output_file": "report.md"
    },
    "steps": steps
}
```

---

## 🎯 Skills vs Tools vs Agent

```
┌─────────────────────────────────────────┐
│              Agent (决策层)              │
│  • 理解任务                              │
│  • 制定计划                              │
│  • 调用 Skills                           │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│           Skills (业务逻辑层)            │
│  • 多步骤流程                            │
│  • 业务决策                              │
│  • 调用 Tools                            │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│           Tools (执行层)                 │
│  • 原子操作                              │
│  • 直接调用 API/系统                     │
└─────────────────────────────────────────┘
```

**示例**：

```
User: "重构这个项目的所有 Python 文件"

├─ Agent 分析:
│  • 需要处理多个文件
│  • 需要代码重构能力
│  • 需要生成报告
│
├─ Agent 调用 Skill:
│  └─ code_refactor_project (自定义 Skill)
│     ├─ 使用 Tool: list_directory
│     ├─ 对每个文件:
│     │  └─ 调用 Skill: code_refactor
│     │     ├─ 使用 Tool: read_file
│     │     ├─ 使用 Tool: copy_file (备份)
│     │     └─ 使用 Tool: write_file
│     └─ 生成报告
│
└─ 返回结果给 User
```

---

## 📊 Skills 架构图

```
aicode/
├── skills/
│   ├── __init__.py          # 导出和注册
│   ├── base.py              # Skill 基类和注册表
│   ├── code_skills.py       # 代码相关技能
│   ├── file_skills.py       # 文件操作技能
│   └── git_skills.py        # Git 相关技能
├── architectures/
│   └── tools_enhanced.py    # Tools 定义
└── cli_agent.py             # CLI 命令
```

---

## 🔮 未来增强

### 1. **技能组合**

```python
# 组合多个技能
skill_chain = SkillChain([
    "backup_files",
    "code_refactor",
    "add_tests",
    "commit_changes"
])

result = await skill_chain.execute(context)
```

### 2. **条件执行**

```python
# 基于条件执行不同技能
if analysis.needs_refactor:
    await registry.execute_skill("code_refactor", ...)
elif analysis.needs_tests:
    await registry.execute_skill("add_tests", ...)
```

### 3. **技能学习**

```python
# 从执行历史中学习
skill.learn_from_execution(result)
skill.optimize_parameters()
```

---

**Skills 让你的 AI Agent 更强大、更智能！** 🚀

快速开始：

```bash
# 列出所有技能
python -m aicode.cli_agent skill-list

# 重构你的代码
python -m aicode.cli_agent skill-run code_refactor -p file_path=mycode.py

# 生成测试
python -m aicode.cli_agent skill-run add_tests -p file_path=mycode.py
```
