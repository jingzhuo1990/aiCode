# 🔗 将 Skills 集成到 Agent 的指南

## 📌 当前状态

**现在**：Skills 和 Agent 是分离的
```
CLI
 ├─ skill-run (直接调用 Skills)
 └─ run (使用 Agent，只有 Tools)
```

**问题**：Agent 不知道 Skills 存在，不能自动使用

---

## 🎯 目标

让 Agent 能够自动读取和使用 Skills：

```
Agent
 ├─ Tools (基础操作)
 └─ Skills (高级能力，内部使用 Tools)
```

---

## 🛠️ 实现方案

### 方案 1：Skills 作为特殊的 Tools（推荐）

#### 步骤 1：修改 `unified_agent.py`

```python
# aicode/architectures/unified_agent.py

from ..skills import create_default_skills, SkillExecutionContext
from .tools_enhanced import Tool

class UnifiedAgent:
    def __init__(self, model, memory_dir, verbose):
        self.model = model
        self.verbose = verbose
        self.memory = MemoryManager(storage_dir=memory_dir)

        # 基础组件
        self.file_handler = FileHandler()
        self.code_generator = CodeGenerator(model)
        self.code_modifier = CodeModifier(model, self.file_handler)

        # 创建工具注册表
        self.tool_registry = create_enhanced_tools()

        # 🆕 创建技能注册表
        self.skill_registry = create_default_skills()

        # 🆕 把 Skills 注册为 Tools
        self._register_skills_as_tools()

        # 初始化 Agents
        self.react_agent = ReActAgent(
            model=model,
            tool_registry=self.tool_registry,  # 现在包含 Skills！
            memory_manager=self.memory,
            verbose=verbose,
        )

        self.plan_execute_agent = PlanExecuteAgent(
            model=model,
            tool_registry=self.tool_registry,  # 现在包含 Skills！
            memory_manager=self.memory,
            verbose=verbose,
        )

    def _register_skills_as_tools(self):
        """把所有 Skills 包装成 Tools"""
        for skill in self.skill_registry.list_skills():
            tool = self._wrap_skill_as_tool(skill)
            self.tool_registry.register(tool)

            if self.verbose:
                print(f"  ✓ Registered skill as tool: {tool.name}")

    def _wrap_skill_as_tool(self, skill) -> Tool:
        """包装单个 Skill 为 Tool"""

        # 创建闭包保存 skill 引用
        def create_wrapper(skill_instance):
            async def skill_wrapper(**kwargs):
                # 创建 Skill 执行上下文
                context = SkillExecutionContext(
                    tools={
                        name: tool.func
                        for name, tool in self.tool_registry.tools.items()
                        if not name.startswith('skill_')  # 避免循环
                    },
                    working_dir=".",
                    memory=self.memory,
                    metadata={"invoked_by": "agent"}
                )

                # 执行 Skill
                result = await skill_instance.execute(context, **kwargs)

                # 格式化返回结果
                if result["success"]:
                    output = f"✓ {result['message']}\n\n"
                    if result.get("steps"):
                        output += "Execution Steps:\n"
                        for step in result["steps"]:
                            output += f"  • {step}\n"
                    if result.get("data"):
                        output += f"\nResult Data: {result['data']}\n"
                    return output
                else:
                    return f"✗ Skill failed: {result['message']}"

            return skill_wrapper

        # 创建 Tool 对象
        return Tool(
            name=f"skill_{skill.name}",
            description=f"[HIGH-LEVEL SKILL] {skill.description}\n"
                       f"Category: {skill.category}\n"
                       f"This skill internally uses: {', '.join(skill.required_tools)}",
            parameters=skill.parameters,
            func=create_wrapper(skill)
        )
```

#### 步骤 2：在 Agent System Prompt 中说明

```python
# aicode/architectures/react_agent.py

class ReActAgent:
    def _build_system_prompt(self):
        tools_list = self.tools.get_all_tools()

        # 分离普通 Tools 和 Skills
        regular_tools = [t for t in tools_list if not t.name.startswith('skill_')]
        skill_tools = [t for t in tools_list if t.name.startswith('skill_')]

        system_prompt = f"""You are an intelligent coding agent...

## Available Tools (Basic Operations)

{self._format_tools(regular_tools)}

## Available Skills (High-Level Capabilities)

{self._format_tools(skill_tools)}

## When to Use What

**Use Skills when**:
- Task requires multiple steps (e.g., "refactor this file")
- Need complex logic (e.g., "review code and suggest improvements")
- Want automated workflows (e.g., "setup project structure")

**Use Tools when**:
- Need atomic operations (e.g., "read this file")
- Skills don't cover your need
- Building custom workflows step-by-step

**Example Decision Process**:
User: "Refactor code.py"
→ Use skill_code_refactor (handles read + analyze + write + backup)

User: "Read code.py"
→ Use read_file tool (simple atomic operation)

...
"""
        return system_prompt
```

---

## 📊 使用示例

### 示例 1：Agent 自动使用 Skill

```bash
# 运行 Agent
python -m aicode.cli_agent run "重构 calculator.py 文件" --provider local
```

**Agent 执行过程**：
```
🤖 Agent (ReAct Mode):

Thought: 用户想重构文件，我看到有 skill_code_refactor 这个高级技能，
        它会自动处理读取、分析、重构、备份、写入等步骤

Action: skill_code_refactor
Action Input: {
  "file_path": "calculator.py",
  "focus": "general"
}

Observation: ✓ Code refactored successfully. Backup at: calculator.py.bak

Execution Steps:
  • Reading file: calculator.py
  • Analyzing code issues...
  • Applying refactoring (focus: general)...
  • Creating backup: calculator.py.bak
  • Writing refactored code to: calculator.py

Thought: 重构完成！任务成功

Answer: 已成功重构 calculator.py 文件，改进了代码结构和可读性。
        原文件已备份到 calculator.py.bak
```

### 示例 2：复杂任务自动选择多个 Skills

```bash
python -m aicode.cli_agent run "创建一个新的 Python 项目叫 myapp，并提交到 git" --provider local
```

**Agent 执行过程**：
```
Thought: 需要两步：1) 创建项目结构 2) git 提交
        我看到 skill_project_setup 和 skill_commit_changes

Action: skill_project_setup
Action Input: {"project_name": "myapp", "project_type": "python"}

Observation: ✓ Project structure created...

Action: skill_commit_changes
Action Input: {"message": "Initial project setup"}

Observation: ✓ Changes committed...

Answer: 已创建 myapp 项目并提交到 git
```

### 示例 3：Agent 选择使用 Tool 而不是 Skill

```bash
python -m aicode.cli_agent run "读取 config.json 文件的内容" --provider local
```

**Agent 执行过程**：
```
Thought: 这是个简单的读取操作，直接用 read_file 工具即可

Action: read_file
Action Input: {"file_path": "config.json"}

Observation: {"api_key": "...", "model": "..."}

Answer: config.json 的内容是...
```

---

## 🎯 优势

### 1. Agent 自动决策
- Agent 会根据任务复杂度自动选择用 Skill 还是 Tool
- 复杂任务 → Skill (一步到位)
- 简单任务 → Tool (精确控制)

### 2. 保持向下兼容
- 用户仍然可以直接调用：`skill-run code_refactor ...`
- Agent 也可以在推理中自动使用
- 两种方式互不干扰

### 3. 易于扩展
```python
# 添加新 Skill
class MyNewSkill(Skill):
    ...

# 自动注册为 Tool
registry.register(MyNewSkill())

# Agent 立即可用！
```

---

## 🔄 完整数据流

```
用户任务: "重构 test.py"
    ↓
UnifiedAgent.run(task)
    ↓
    ├─ tool_registry 包含:
    │  ├─ read_file (Tool)
    │  ├─ write_file (Tool)
    │  ├─ skill_code_refactor (Tool 包装的 Skill)
    │  └─ ...
    ↓
ReActAgent.run(task)
    ↓
LLM 推理:
    Available: read_file, write_file, skill_code_refactor, ...
    Decision: 用 skill_code_refactor (复杂任务)
    ↓
调用 skill_code_refactor (实际是 Tool)
    ↓
Tool.func() 内部:
    ├─ 创建 SkillExecutionContext
    ├─ 调用 Skill.execute(context)
    │   └─ Skill 内部使用基础 Tools:
    │       ├─ context.tools["read_file"]("test.py")
    │       ├─ 分析和重构
    │       └─ context.tools["write_file"]("test.py", ...)
    └─ 返回格式化结果
    ↓
Agent 获得 Observation
    ↓
继续推理或完成任务
```

---

## 🚀 实施步骤

### 1. 备份当前代码
```bash
git add -A
git commit -m "backup before integrating skills"
```

### 2. 修改 unified_agent.py
- 导入 skills 模块
- 添加 `_register_skills_as_tools()` 方法
- 在 `__init__` 中调用

### 3. 可选：修改 react_agent.py
- 优化 system prompt 区分 Tools 和Skills
- 添加使用建议

### 4. 测试
```bash
# 测试 Agent 能否使用 Skills
python -m aicode.cli_agent run "重构 test.py" --provider local

# 测试原有 CLI 仍然工作
python -m aicode.cli_agent skill-run code_refactor -p file_path=test.py
```

### 5. 验证
- ✅ Agent 能自动使用 Skills
- ✅ CLI 直接调用仍然工作
- ✅ Tools 和 Skills 和谐共存

---

## 💡 进阶技巧

### 技巧 1：Skill 优先级

```python
# 在 system prompt 中建议优先使用 Skills
"""
When faced with a complex task, ALWAYS check if there's a skill_* tool first.
Skills are optimized workflows that handle multiple steps automatically.
"""
```

### 技巧 2：Skill 组合

```python
# Agent 可以组合多个 Skills
Thought: 需要完整的开发流程
Action: skill_project_setup
...
Action: skill_add_tests
...
Action: skill_commit_changes
```

### 技巧 3：动态启用/禁用 Skills

```python
class UnifiedAgent:
    def __init__(self, ..., enable_skills=True):
        if enable_skills:
            self._register_skills_as_tools()
```

---

## ✅ 总结

**改造前**：
```
Skills 是独立的 CLI 命令
Agent 只知道 Tools
```

**改造后**：
```
Skills 被包装成特殊的 Tools
Agent 可以自动使用 Skills
保持向下兼容
```

**好处**：
- 🎯 Agent 更智能（自动选择合适的抽象层次）
- 🔧 更强大（可以使用复杂的 Skills）
- 🔄 灵活（手动和自动两种方式）
- 🚀 易扩展（新 Skill 自动可用）
