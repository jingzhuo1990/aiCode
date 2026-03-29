# Agent Team 系统 - 完整指南

## 📋 目录

1. [概述](#概述)
2. [核心概念](#核心概念)
3. [架构设计](#架构设计)
4. [快速开始](#快速开始)
5. [专业 Agent 介绍](#专业-agent-介绍)
6. [高级特性](#高级特性)
7. [扩展指南](#扩展指南)
8. [最佳实践](#最佳实践)

---

## 概述

### 什么是 Agent Team？

Agent Team 是一个**多智能体协作系统**，允许多个专业 AI Agent 通过标准化的消息协议相互通信，共同完成复杂任务。

### 核心特性

- ✅ **A2A 协议**：基于 Agent-to-Agent 消息协议的标准化通信
- ✅ **角色分工**：不同 Agent 负责不同领域的专业任务
- ✅ **自动调度**：协调器自动选择最合适的 Agent 执行任务
- ✅ **并行执行**：支持多任务并发处理
- ✅ **工作流编排**：支持复杂的多步骤任务流程
- ✅ **消息路由**：优先级队列和智能消息路由

### 适用场景

- 🎯 复杂软件开发任务（规划、编码、测试、部署）
- 🎯 数据分析流水线（采集、处理、分析、报告）
- 🎯 多领域协作（代码生成 + 文件管理 + 质量分析）
- 🎯 需要专业分工的任务

---

## 核心概念

### 1. A2A 协议（Agent-to-Agent Protocol）

标准化的智能体间通信协议，定义了消息格式和交互模式。

#### 消息类型（MessageType）

```python
# 任务相关
TASK_REQUEST       # 任务请求
TASK_RESPONSE      # 任务响应
TASK_DELEGATE      # 任务委托
TASK_COMPLETE      # 任务完成

# 查询相关
QUERY              # 查询请求
QUERY_RESPONSE     # 查询响应

# 协调相关
STATUS_UPDATE      # 状态更新
CAPABILITY_QUERY   # 能力查询
CAPABILITY_RESPONSE # 能力响应

# 协作相关
COLLABORATION_REQUEST  # 协作请求
COLLABORATION_ACCEPT   # 接受协作
COLLABORATION_REJECT   # 拒绝协作

# 系统相关
HEARTBEAT          # 心跳
ERROR              # 错误
INFO               # 信息
```

#### 消息优先级（MessagePriority）

```python
LOW = 0      # 低优先级
NORMAL = 1   # 普通优先级
HIGH = 2     # 高优先级
URGENT = 3   # 紧急优先级
```

#### 消息结构

```python
@dataclass
class Message:
    message_type: MessageType    # 消息类型
    sender_id: str              # 发送者 ID
    receiver_id: str            # 接收者 ID
    content: Any                # 消息内容
    message_id: str             # 消息唯一 ID
    timestamp: datetime         # 时间戳
    priority: MessagePriority   # 优先级
    reply_to: Optional[str]     # 回复哪条消息
    conversation_id: Optional[str]  # 会话 ID
    metadata: Dict[str, Any]    # 附加元数据
```

### 2. Agent 角色（AgentRole）

```python
COORDINATOR = "coordinator"  # 协调者：管理团队和任务分配
SPECIALIST = "specialist"    # 专家：特定领域的深度能力
WORKER = "worker"           # 工作者：执行具体任务
ANALYZER = "analyzer"       # 分析者：数据分析和总结
```

### 3. Agent 状态（AgentStatus）

```python
IDLE = "idle"           # 空闲：可接受新任务
BUSY = "busy"           # 忙碌：正在执行任务
WAITING = "waiting"     # 等待：等待其他 Agent 响应
ERROR = "error"         # 错误：遇到异常
OFFLINE = "offline"     # 离线：不可用
```

---

## 架构设计

### 分层架构

```
┌─────────────────────────────────────────────────┐
│              应用层（Application）               │
│  - 工作流定义                                    │
│  - 任务编排                                      │
│  - 业务逻辑                                      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           协调层（TeamCoordinator）              │
│  - 任务分配                                      │
│  - Agent 管理                                    │
│  - 消息路由                                      │
│  - 结果汇总                                      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              Agent 层（BaseAgent）               │
│  - 专业能力                                      │
│  - 消息处理                                      │
│  - 任务执行                                      │
│  - 状态管理                                      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            消息层（A2A Protocol）                │
│  - 消息定义                                      │
│  - 消息队列                                      │
│  - 优先级排序                                    │
└─────────────────────────────────────────────────┘
```

### 核心组件

#### 1. Message（消息）
- 定义消息格式
- 支持回复和会话追踪
- 序列化/反序列化

#### 2. MessageQueue（消息队列）
- 优先级排序
- FIFO 保证
- 过滤和查询功能

#### 3. BaseAgent（基础 Agent）
```python
class BaseAgent(ABC):
    # 核心属性
    - agent_id: 唯一标识
    - name: Agent 名称
    - role: Agent 角色
    - capabilities: 能力列表
    - status: 当前状态

    # 消息系统
    - inbox: 收件箱队列
    - outbox: 发件箱队列

    # 核心方法
    - send_message(): 发送消息
    - receive_message(): 接收消息
    - process_messages(): 处理消息
    - execute_task(): 执行任务
    - can_handle(): 能力检查
```

#### 4. TeamCoordinator（团队协调器）
```python
class TeamCoordinator:
    # 核心功能
    - add_agent(): 添加 Agent
    - remove_agent(): 移除 Agent
    - assign_task(): 分配任务
    - execute_workflow(): 执行工作流
    - execute_parallel_tasks(): 并行执行

    # 选择策略
    - _select_agent_for_task(): 自动选择 Agent
    - _route_message(): 消息路由

    # 监控统计
    - get_team_status(): 团队状态
    - get_statistics(): 统计信息
```

### 数据流图

```
用户请求
   ↓
TeamCoordinator.assign_task()
   ↓
自动选择 Agent (基于能力匹配)
   ↓
创建 TASK_REQUEST 消息
   ↓
Agent.receive_message() → inbox
   ↓
Agent.process_messages()
   ↓
Agent.execute_task()
   ↓
创建 TASK_COMPLETE/ERROR 消息
   ↓
Agent.send_message() → outbox
   ↓
Coordinator 路由消息
   ↓
返回结果给用户
```

---

## 快速开始

### 1. 基本使用

```python
from aicode.agent_team import (
    TeamCoordinator,
    CodeAgent,
    FileAgent,
    AnalysisAgent
)

# 创建团队
team = TeamCoordinator("Dev Team")

# 添加专业 Agent
team.add_agent(CodeAgent())
team.add_agent(FileAgent())
team.add_agent(AnalysisAgent())

# 分配任务
result = await team.assign_task({
    "type": "code_generation",
    "description": "创建快速排序函数",
    "language": "python"
})

print(result)
# {
#     "success": True,
#     "code": "# Generated code...",
#     "language": "python"
# }
```

### 2. Agent 间通信

```python
# 创建两个 Agent
code_agent = CodeAgent()
file_agent = FileAgent()

# 注册为团队成员
code_agent.register_team_agent(file_agent)
file_agent.register_team_agent(code_agent)

# CodeAgent 向 FileAgent 发送查询
code_agent.send_message(
    file_agent.agent_id,
    MessageType.QUERY,
    {"query": "文件系统状态如何？"}
)

# 路由消息
msg = code_agent.outbox.pop()
file_agent.receive_message(msg)

# FileAgent 处理并回复
await file_agent.process_messages()
```

### 3. 工作流执行

```python
# 定义工作流
workflow = [
    {
        "type": "decompose_task",
        "description": "规划项目开发"
    },
    {
        "type": "code_generation",
        "description": "生成主程序代码",
        "language": "python"
    },
    {
        "type": "file_write",
        "file_path": "main.py",
        "content": "# Code content"
    },
    {
        "type": "generate_report",
        "data": {"files": ["main.py"]}
    }
]

# 执行工作流
results = await team.execute_workflow(workflow)

# 检查结果
for i, result in enumerate(results):
    print(f"步骤 {i+1}: {result.get('success')}")
```

### 4. 并行任务执行

```python
# 定义并行任务
tasks = [
    {"type": "code_generation", "description": "生成函数 A"},
    {"type": "code_generation", "description": "生成函数 B"},
    {"type": "file_search", "pattern": "*.py"},
    {"type": "analyze_data", "data": [1, 2, 3]}
]

# 并行执行
results = await team.execute_parallel_tasks(tasks)

# 所有任务同时执行，等待全部完成
for result in results:
    if isinstance(result, Exception):
        print(f"任务失败: {result}")
    else:
        print(f"任务成功: {result.get('success')}")
```

---

## 专业 Agent 介绍

### 1. CodeAgent（代码专家）

**角色**：SPECIALIST

**能力**：
- `code_generation` - 代码生成
- `code_refactor` - 代码重构
- `code_review` - 代码审查
- `code_analysis` - 代码分析
- `bug_fix` - Bug 修复

**使用示例**：
```python
code_agent = CodeAgent()

# 代码生成
result = await code_agent.execute_task({
    "type": "code_generation",
    "description": "快速排序算法",
    "language": "python"
})

# 代码审查
result = await code_agent.execute_task({
    "type": "code_review",
    "code": "def foo(): pass"
})
# 返回: {"success": True, "issues": [...], "score": 85}
```

### 2. FileAgent（文件管理专家）

**角色**：WORKER

**能力**：
- `file_read` - 文件读取
- `file_write` - 文件写入
- `file_search` - 文件搜索
- `file_backup` - 文件备份
- `directory_management` - 目录管理

**使用示例**：
```python
file_agent = FileAgent()

# 读取文件
result = await file_agent.execute_task({
    "type": "file_read",
    "file_path": "test.txt"
})

# 写入文件
result = await file_agent.execute_task({
    "type": "file_write",
    "file_path": "output.txt",
    "content": "Hello World"
})
# 返回: {"success": True, "bytes_written": 11}
```

### 3. AnalysisAgent（数据分析专家）

**角色**：ANALYZER

**能力**：
- `analyze_data` - 数据分析
- `generate_report` - 报告生成
- `trend_analysis` - 趋势分析
- `summary_creation` - 摘要生成

**使用示例**：
```python
analysis_agent = AnalysisAgent()

# 数据分析
result = await analysis_agent.execute_task({
    "type": "analyze_data",
    "data": [1, 2, 3, 4, 5]
})
# 返回: {"success": True, "analysis": {"count": 5, ...}}

# 生成报告
result = await analysis_agent.execute_task({
    "type": "generate_report",
    "data": {"feature": "用户认证", "files": ["auth.py"]}
})
```

### 4. PlannerAgent（规划专家）

**角色**：SPECIALIST

**能力**：
- `task_planning` - 任务规划
- `task_decomposition` - 任务分解
- `workflow_design` - 工作流设计
- `dependency_analysis` - 依赖分析

**使用示例**：
```python
planner_agent = PlannerAgent()

# 任务分解
result = await planner_agent.execute_task({
    "type": "decompose_task",
    "description": "开发用户认证功能"
})
# 返回: {
#     "success": True,
#     "subtasks": [
#         {"id": "subtask_1", "agent_type": "code_agent", ...},
#         {"id": "subtask_2", "agent_type": "file_agent", ...}
#     ]
# }
```

---

## 高级特性

### 1. 自动 Agent 选择

TeamCoordinator 会根据任务类型和 Agent 能力自动选择最合适的 Agent：

```python
def _select_agent_for_task(self, task: Dict[str, Any]) -> Optional[BaseAgent]:
    task_type = task.get("type")

    # 优先选择空闲且能处理的 Agent
    for agent in self.agents.values():
        if agent.status == AgentStatus.IDLE and agent.can_handle(task_type):
            return agent

    # 如果没有空闲的，选择忙碌但能处理的
    for agent in self.agents.values():
        if agent.can_handle(task_type):
            return agent

    return None
```

### 2. 消息优先级队列

MessageQueue 自动按优先级和时间排序：

```python
class MessageQueue:
    def push(self, message: Message):
        self.messages.append(message)
        # 优先级高的在前，时间早的在前
        self.messages.sort(
            key=lambda m: (m.priority.value, m.timestamp),
            reverse=True
        )
```

### 3. 任务超时控制

```python
# 在 assign_task 时设置超时
result = await team.assign_task(
    task={"type": "code_generation", ...},
    timeout=60.0  # 60 秒超时
)
```

### 4. 团队统计

```python
stats = team.get_statistics()
print(stats)
# {
#     "team_name": "Dev Team",
#     "agents_count": 4,
#     "messages": {
#         "sent": 120,
#         "received": 115
#     },
#     "tasks": {
#         "completed": 45,
#         "failed": 2,
#         "active": 3,
#         "success_rate": 0.957
#     }
# }
```

### 5. Agent 能力查询

```python
capabilities = await team.query_agent_capabilities()
for agent_id, cap in capabilities.items():
    print(f"{agent_id}: {cap['capabilities']}")
```

---

## 扩展指南

### 创建自定义 Agent

```python
from aicode.agent_team import BaseAgent, AgentRole, AgentStatus, Message, MessageType
from typing import Dict, Any

class CustomAgent(BaseAgent):
    """自定义 Agent"""

    def __init__(self, agent_id: str = "custom_agent"):
        super().__init__(
            agent_id=agent_id,
            name="Custom Agent",
            role=AgentRole.SPECIALIST,
            capabilities=[
                "custom_task_1",
                "custom_task_2"
            ],
            description="自定义专业 Agent"
        )

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

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get("type")

        if task_type == "custom_task_1":
            return await self._custom_task_1(task)
        elif task_type == "custom_task_2":
            return await self._custom_task_2(task)
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }

    async def _custom_task_1(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """自定义任务 1"""
        # 实现你的逻辑
        return {
            "success": True,
            "result": "Task 1 completed"
        }

    async def _custom_task_2(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """自定义任务 2"""
        # 实现你的逻辑
        return {
            "success": True,
            "result": "Task 2 completed"
        }

# 使用自定义 Agent
team = TeamCoordinator("My Team")
team.add_agent(CustomAgent())

result = await team.assign_task({
    "type": "custom_task_1",
    "data": "some data"
})
```

### 集成 AI 模型

```python
from aicode.models.base import AIModel
from aicode.architectures.tools_enhanced import ToolRegistry

class AICodeAgent(BaseAgent):
    """集成 AI 模型的 Agent"""

    def __init__(
        self,
        agent_id: str,
        model: AIModel,
        tool_registry: ToolRegistry
    ):
        super().__init__(
            agent_id=agent_id,
            name="AI Code Agent",
            role=AgentRole.SPECIALIST,
            capabilities=["smart_code_generation"],
            description="使用 AI 模型生成代码"
        )
        self.model = model
        self.tool_registry = tool_registry

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # 使用 AI 模型处理
        prompt = task.get("description")
        response = await self.model.generate(prompt)

        return {
            "success": True,
            "code": response,
            "model": self.model.name
        }
```

---

## 最佳实践

### 1. 任务设计

✅ **好的任务定义**：
```python
{
    "type": "code_generation",      # 明确的类型
    "description": "创建快速排序函数",  # 清晰的描述
    "language": "python",           # 必要的参数
    "requirements": [               # 详细的需求
        "支持升序和降序",
        "时间复杂度 O(n log n)"
    ]
}
```

❌ **不好的任务定义**：
```python
{
    "type": "do_something",  # 类型不明确
    "data": "code"          # 缺少描述和参数
}
```

### 2. 错误处理

```python
try:
    result = await team.assign_task(task)

    if not result.get("success"):
        # 处理任务失败
        error = result.get("error")
        print(f"任务失败: {error}")

except Exception as e:
    # 处理异常
    print(f"执行异常: {e}")
```

### 3. 工作流设计

按依赖关系组织任务：
```python
workflow = [
    # 第 1 步：规划（无依赖）
    {"type": "decompose_task", ...},

    # 第 2 步：并行生成多个模块
    # （使用 execute_parallel_tasks）

    # 第 3 步：集成代码（依赖第 2 步）
    {"type": "code_integration", ...},

    # 第 4 步：测试（依赖第 3 步）
    {"type": "run_tests", ...},

    # 第 5 步：生成报告（依赖所有步骤）
    {"type": "generate_report", ...}
]
```

### 4. 性能优化

```python
# ✅ 使用并行执行独立任务
tasks = [task1, task2, task3]  # 互不依赖
results = await team.execute_parallel_tasks(tasks)

# ❌ 不要顺序执行独立任务
results = []
for task in tasks:
    result = await team.assign_task(task)  # 慢！
    results.append(result)
```

### 5. 监控和调试

```python
# 定期检查团队状态
status = team.get_team_status()
print(f"活跃任务: {status['active_tasks']}")
print(f"已完成: {status['completed_tasks']}")

# 检查 Agent 状态
for agent_id, agent_info in status['agents'].items():
    print(f"{agent_info['name']}: {agent_info['status']}")
    print(f"  Inbox: {agent_info['inbox_size']}")
    print(f"  Outbox: {agent_info['outbox_size']}")
```

---

## 完整示例

### 示例：开发流程自动化

```python
import asyncio
from aicode.agent_team import (
    TeamCoordinator,
    PlannerAgent,
    CodeAgent,
    FileAgent,
    AnalysisAgent
)

async def main():
    # 1. 创建团队
    team = TeamCoordinator("Dev Team")
    team.add_agent(PlannerAgent())
    team.add_agent(CodeAgent())
    team.add_agent(FileAgent())
    team.add_agent(AnalysisAgent())

    # 2. 规划任务
    print("📋 第 1 步：任务规划")
    plan_result = await team.assign_task({
        "type": "decompose_task",
        "description": "开发用户认证功能"
    })

    subtasks = plan_result.get("subtasks", [])
    print(f"  分解为 {len(subtasks)} 个子任务")

    # 3. 并行生成代码
    print("\n💻 第 2 步：代码生成（并行）")
    code_tasks = [
        {"type": "code_generation", "description": "登录模块"},
        {"type": "code_generation", "description": "注册模块"},
        {"type": "code_generation", "description": "密码加密模块"}
    ]

    code_results = await team.execute_parallel_tasks(code_tasks)
    print(f"  生成 {len(code_results)} 个代码模块")

    # 4. 保存文件
    print("\n📁 第 3 步：保存代码文件")
    file_tasks = [
        {"type": "file_write", "file_path": "login.py", "content": code_results[0].get("code")},
        {"type": "file_write", "file_path": "register.py", "content": code_results[1].get("code")},
        {"type": "file_write", "file_path": "crypto.py", "content": code_results[2].get("code")}
    ]

    file_results = await team.execute_parallel_tasks(file_tasks)
    total_bytes = sum(r.get("bytes_written", 0) for r in file_results if not isinstance(r, Exception))
    print(f"  保存 {total_bytes} bytes")

    # 5. 生成报告
    print("\n📊 第 4 步：生成开发报告")
    report_result = await team.assign_task({
        "type": "generate_report",
        "data": {
            "feature": "用户认证",
            "files": ["login.py", "register.py", "crypto.py"],
            "lines": total_bytes // 30  # 估算
        }
    })

    # 6. 显示统计
    print("\n" + "="*60)
    stats = team.get_statistics()
    print("✅ 开发流程完成！")
    print(f"  - 参与 Agent: {stats['agents_count']}")
    print(f"  - 完成任务: {stats['tasks']['completed']}")
    print(f"  - 成功率: {stats['tasks']['success_rate']:.1%}")
    print(f"  - 消息交换: {stats['messages']['sent']} 条")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 总结

Agent Team 系统提供了：

1. **标准化协议**：A2A 消息协议确保 Agent 间清晰通信
2. **专业分工**：不同 Agent 负责不同领域的任务
3. **灵活编排**：支持顺序、并行、混合的工作流
4. **自动调度**：智能选择最合适的 Agent 执行任务
5. **易于扩展**：简单的接口，方便创建自定义 Agent

通过 Agent Team，你可以将复杂任务分解为多个专业化的子任务，由不同的 Agent 协作完成，大幅提升系统的能力和效率。

---

## 参考资料

- 源码位置：`aicode/agent_team/`
- 测试代码：`test_agent_team.py`
- 核心文件：
  - `message.py` - A2A 协议定义
  - `base_agent.py` - Agent 基类
  - `specialized_agents.py` - 专业 Agent 实现
  - `coordinator.py` - 团队协调器

**开始使用 Agent Team，构建强大的多智能体系统！** 🚀
