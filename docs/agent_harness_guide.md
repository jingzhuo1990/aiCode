# Agent Harness 使用指南

## 📋 概述

**Agent Harness** 是为 Agent Team 系统提供的运行环境，它为每个 Agent 赋予完整的 AI 能力。

### 核心能力

```
┌─────────────────────────────────────────────┐
│          Agent Harness 架构                  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ AI Model │  │  Tools   │  │  Skills  │ │
│  │  思考能力  │  │  工具执行  │  │  专业技能  │ │
│  └──────────┘  └──────────┘  └──────────┘ │
│                                             │
│  ┌──────────┐  ┌──────────┐               │
│  │  Memory  │  │ Reasoning│               │
│  │  记忆系统  │  │  推理架构  │               │
│  └──────────┘  └──────────┘               │
│                                             │
│              BaseAgent                      │
│         (消息通信、协作能力)                   │
└─────────────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 基础使用：为普通 Agent 添加 Harness

```python
from aicode.agent_team import CodeAgent, AgentHarness
from aicode.models.claude import ClaudeModel
from aicode.architectures.tools_enhanced import create_enhanced_tools

# 创建模型
model = ClaudeModel(api_key="your-api-key")

# 创建工具
tools = create_enhanced_tools()

# 创建普通 Agent
code_agent = CodeAgent()

# 添加 Harness
harness = AgentHarness(
    agent=code_agent,
    model=model,
    tool_registry=tools,
    mode="react",  # react / plan / auto
    verbose=True
)

# 执行任务
result = await harness.execute_task({
    "type": "code_generation",
    "description": "创建快速排序函数",
    "language": "python"
})
```

### 2. 使用 HarnessedAgent（推荐）

HarnessedAgent 是自带 Harness 的 Agent，更简洁：

```python
from aicode.agent_team import HarnessedAgent, AgentRole
from aicode.models.claude import ClaudeModel
from aicode.architectures.tools_enhanced import create_enhanced_tools

model = ClaudeModel(api_key="your-api-key")
tools = create_enhanced_tools()

# 创建智能 Agent（自带 Harness）
smart_agent = HarnessedAgent(
    agent_id="smart_code_agent",
    name="Smart Code Expert",
    role=AgentRole.SPECIALIST,
    capabilities=["code_generation", "code_review", "bug_fix"],
    model=model,
    tool_registry=tools,
    mode="auto",  # 自动选择推理模式
    verbose=True
)

# 直接执行任务
result = await smart_agent.execute_task({
    "type": "code_generation",
    "description": "创建二叉搜索树插入函数"
})
```

### 3. 在 Team 中使用 Harness

```python
from aicode.agent_team import TeamCoordinator, HarnessedAgent, AgentRole
from aicode.models.claude import ClaudeModel
from aicode.architectures.tools_enhanced import create_enhanced_tools

model = ClaudeModel(api_key="your-api-key")
tools = create_enhanced_tools()

# 创建团队
team = TeamCoordinator("Smart AI Team")

# 创建多个智能 Agent
code_agent = HarnessedAgent(
    agent_id="smart_coder",
    name="Smart Coder",
    role=AgentRole.SPECIALIST,
    capabilities=["code_generation", "code_review"],
    model=model,
    tool_registry=tools
)

analysis_agent = HarnessedAgent(
    agent_id="smart_analyst",
    name="Smart Analyst",
    role=AgentRole.ANALYZER,
    capabilities=["analyze_data", "generate_report"],
    model=model,
    tool_registry=tools
)

# 添加到团队
team.add_agent(code_agent)
team.add_agent(analysis_agent)

# 团队会自动将任务分配给合适的智能 Agent
result = await team.assign_task({
    "type": "code_generation",
    "description": "创建用户认证系统"
})
```

## 🎯 核心功能

### 1. 推理模式

Harness 支持三种推理模式：

#### ReAct 模式（适合探索性任务）
```python
harness = AgentHarness(
    agent=agent,
    model=model,
    mode="react"
)
```

**特点**：
- 思考 → 行动 → 观察 → 循环
- 适合需要迭代探索的任务
- 灵活应对不确定性

**适用场景**：
- 代码调试
- 问题诊断
- 信息搜索

#### Plan-Execute 模式（适合结构化任务）
```python
harness = AgentHarness(
    agent=agent,
    model=model,
    mode="plan"
)
```

**特点**：
- 先规划整体方案
- 再按步骤执行
- 适合结构清晰的任务

**适用场景**：
- 项目搭建
- 系统重构
- 架构设计

#### Auto 模式（自动选择）
```python
harness = AgentHarness(
    agent=agent,
    model=model,
    mode="auto"  # 根据任务自动选择
)
```

### 2. 工具管理

```python
from aicode.architectures.tools_enhanced import Tool

# 添加自定义工具
def my_custom_tool(param: str) -> str:
    return f"Processed: {param}"

tool = Tool(
    name="custom_tool",
    description="My custom tool",
    func=my_custom_tool,
    parameters={
        "param": {
            "type": "string",
            "description": "Input parameter"
        }
    }
)

harness.add_tool(tool)

# 查看可用工具
tools = harness.get_available_tools()
print(f"Available tools: {tools}")
```

### 3. 技能系统

```python
from aicode.skills import Skill

# 添加自定义技能
skill = Skill(
    name="code_optimization",
    description="优化代码性能",
    execute_func=my_optimization_function
)

harness.add_skill(skill)

# 执行技能
result = await harness.execute_skill(
    "code_optimization",
    code="def slow_function(): ..."
)
```

### 4. 记忆管理

```python
# 添加记忆
harness.add_to_memory("user", "我喜欢用 TypeScript")
harness.add_to_memory("assistant", "好的，我会优先使用 TypeScript")

# 获取记忆上下文
context = harness.get_memory_context(include_long_term=True)

# 清除短期记忆
harness.clear_short_term_memory()

# Harness 会在执行任务时自动使用记忆
result = await harness.execute_task({
    "type": "code_generation",
    "description": "创建一个 API 客户端"
})
# 生成的代码会使用 TypeScript
```

## 📊 实际案例

### 案例 1：智能代码生成

```python
# 创建智能代码 Agent
code_agent = HarnessedAgent(
    agent_id="smart_coder",
    name="AI Coder",
    role=AgentRole.SPECIALIST,
    capabilities=["code_generation"],
    model=claude_model,
    tool_registry=tools,
    mode="react"
)

# 执行复杂任务
result = await code_agent.execute_task({
    "type": "code_generation",
    "description": """
    创建一个带缓存的 HTTP 客户端类，要求：
    1. 支持 GET/POST/PUT/DELETE 方法
    2. 自动重试机制
    3. 缓存 GET 请求结果
    4. 支持请求超时设置
    """,
    "language": "python"
})

# Agent 会：
# 1. 思考如何设计这个类
# 2. 使用文件工具创建代码文件
# 3. 生成完整的实现
# 4. 返回结果
```

### 案例 2：多 Agent 协作开发

```python
# 创建开发团队
team = TeamCoordinator("Dev Team")

# 规划 Agent
planner = HarnessedAgent(
    agent_id="planner",
    name="Project Planner",
    role=AgentRole.SPECIALIST,
    capabilities=["task_planning", "task_decomposition"],
    model=claude_model,
    tool_registry=tools
)

# 代码 Agent
coder = HarnessedAgent(
    agent_id="coder",
    name="Code Generator",
    role=AgentRole.SPECIALIST,
    capabilities=["code_generation"],
    model=claude_model,
    tool_registry=tools
)

# 测试 Agent
tester = HarnessedAgent(
    agent_id="tester",
    name="Test Engineer",
    role=AgentRole.SPECIALIST,
    capabilities=["test_generation"],
    model=claude_model,
    tool_registry=tools
)

team.add_agent(planner)
team.add_agent(coder)
team.add_agent(tester)

# 工作流
workflow = [
    {
        "type": "decompose_task",
        "description": "开发用户认证系统"
    },
    {
        "type": "code_generation",
        "description": "实现登录功能"
    },
    {
        "type": "test_generation",
        "description": "为登录功能编写测试"
    }
]

results = await team.execute_workflow(workflow)
```

### 案例 3：带记忆的持续对话

```python
# 创建 Agent
agent = HarnessedAgent(
    agent_id="assistant",
    name="Code Assistant",
    role=AgentRole.SPECIALIST,
    capabilities=["code_generation", "code_review"],
    model=claude_model,
    tool_registry=tools
)

# 第一次对话
agent.harness.add_to_memory("user", "我在开发一个电商系统")
result1 = await agent.execute_task({
    "type": "code_generation",
    "description": "创建商品模型"
})

# 第二次对话（Agent 记得上下文）
agent.harness.add_to_memory("user", "现在需要添加购物车功能")
result2 = await agent.execute_task({
    "type": "code_generation",
    "description": "创建购物车功能"
})
# Agent 会基于之前的商品模型设计购物车

# 第三次对话
result3 = await agent.execute_task({
    "type": "code_review",
    "description": "审查购物车代码"
})
# Agent 会考虑整个电商系统的上下文
```

## 🔧 高级配置

### 1. 自定义推理策略

```python
class CustomHarness(AgentHarness):
    async def _choose_mode(self, task):
        # 自定义模式选择逻辑
        if task.get("complexity") == "high":
            return "plan"
        return "react"
```

### 2. Agent 专属工具集

```python
class SpecializedHarness(AgentHarness):
    def _register_agent_specific_tools(self):
        # 根据 Agent 能力注册专属工具
        if "code_generation" in self.agent.capabilities:
            self.add_tool(code_generation_tool)

        if "file_read" in self.agent.capabilities:
            self.add_tool(file_read_tool)
```

### 3. 监控和日志

```python
# 获取 Harness 状态
info = harness.get_harness_info()
print(f"""
Agent: {info['agent_name']}
Mode: {info['mode']}
Tools: {info['tools_count']}
Skills: {info['skills_count']}
Memory Messages: {info['memory_messages']}
""")
```

## 📈 性能优化

### 1. 记忆管理

```python
# 定期清理短期记忆
if harness.memory.short_term.messages > 100:
    harness.clear_short_term_memory()

# 只在必要时加载长期记忆
context = harness.get_memory_context(include_long_term=False)
```

### 2. 工具缓存

```python
# 复用工具注册表
shared_tools = create_enhanced_tools()

agent1 = HarnessedAgent(..., tool_registry=shared_tools)
agent2 = HarnessedAgent(..., tool_registry=shared_tools)
```

### 3. 并行执行

```python
# 多个 Agent 并行处理任务
tasks = [
    agent1.execute_task(task1),
    agent2.execute_task(task2),
    agent3.execute_task(task3)
]

results = await asyncio.gather(*tasks)
```

## 🎓 最佳实践

1. **选择合适的推理模式**
   - 探索性任务用 `react`
   - 结构化任务用 `plan`
   - 不确定时用 `auto`

2. **合理使用记忆**
   - 重要上下文存入记忆
   - 定期清理短期记忆
   - 关键信息存入长期记忆

3. **工具和技能分离**
   - 工具：底层操作（读写文件、执行命令）
   - 技能：高级能力（代码生成、分析）

4. **团队协作**
   - 创建专业化的 HarnessedAgent
   - 让 TeamCoordinator 自动分配任务
   - 利用消息系统实现 Agent 间通信

## 📚 API 参考

### AgentHarness

```python
class AgentHarness:
    def __init__(
        self,
        agent: BaseAgent,
        model: AIModel,
        tool_registry: Optional[ToolRegistry] = None,
        skill_registry: Optional[SkillRegistry] = None,
        memory_manager: Optional[MemoryManager] = None,
        mode: Literal["react", "plan", "auto"] = "auto",
        verbose: bool = False,
    )

    async def execute_task(
        self,
        task: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]

    async def execute_skill(
        self,
        skill_name: str,
        **kwargs
    ) -> Dict[str, Any]

    def add_tool(self, tool: Tool)
    def add_skill(self, skill: Skill)
    def add_to_memory(self, role: str, content: str, metadata: Optional[Dict] = None)
    def get_memory_context(self, include_long_term: bool = True) -> str
    def get_harness_info(self) -> Dict[str, Any]
```

### HarnessedAgent

```python
class HarnessedAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: AgentRole,
        capabilities: List[str],
        model: AIModel,
        tool_registry: Optional[ToolRegistry] = None,
        skill_registry: Optional[SkillRegistry] = None,
        mode: Literal["react", "plan", "auto"] = "auto",
        description: str = "",
        verbose: bool = False,
    )

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]
    async def handle_message(self, message: Message)
```

## 🤝 贡献

欢迎贡献新的：
- 推理策略
- 工具实现
- 技能定义
- 使用案例

---

**Happy Coding with Agent Harness! 🚀**
