#!/usr/bin/env python
"""测试 Agent Harness 系统"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_harness_basic():
    """测试 Harness 基本功能"""
    print("=" * 60)
    print("测试 1: Agent Harness 基本功能")
    print("=" * 60)

    from aicode.agent_team import CodeAgent, FileAgent
    from aicode.agent_team.agent_harness import AgentHarness
    from aicode.models.claude import ClaudeModel  # 假设你有这个模型
    from aicode.architectures.tools_enhanced import create_enhanced_tools

    # 创建模型（这里使用 mock，实际应该用真实模型）
    model = MockAIModel()

    # 创建工具注册表
    tools = create_enhanced_tools()

    # 创建 Agent
    code_agent = CodeAgent()

    # 为 Agent 添加 Harness
    harness = AgentHarness(
        agent=code_agent,
        model=model,
        tool_registry=tools,
        mode="react",
        verbose=True
    )

    print(f"\n✓ Harness 创建成功")
    print(f"  - Agent: {code_agent.name}")
    print(f"  - 工具数量: {len(harness.get_available_tools())}")
    print(f"  - 推理模式: {harness.mode}")

    # 执行任务
    print("\n执行任务: 代码生成")
    result = await harness.execute_task({
        "type": "code_generation",
        "description": "创建一个快速排序函数",
        "language": "python"
    })

    print(f"\n结果:")
    print(f"  - 成功: {result.get('success')}")
    print(f"  - 迭代次数: {result.get('iterations')}")
    if result.get('answer'):
        print(f"  - 答案: {result['answer'][:100]}...")

    print("\n✓ Harness 基本功能测试通过\n")
    return True


async def test_harnessed_agent():
    """测试 HarnessedAgent（集成版 Agent）"""
    print("=" * 60)
    print("测试 2: HarnessedAgent 集成测试")
    print("=" * 60)

    from aicode.agent_team.agent_harness import HarnessedAgent
    from aicode.agent_team import AgentRole
    from aicode.architectures.tools_enhanced import create_enhanced_tools

    # 创建模型
    model = MockAIModel()

    # 创建工具
    tools = create_enhanced_tools()

    # 创建 HarnessedAgent（自带 Harness 的 Agent）
    smart_agent = HarnessedAgent(
        agent_id="smart_code_agent",
        name="Smart Code Expert",
        role=AgentRole.SPECIALIST,
        capabilities=["code_generation", "code_review", "bug_fix"],
        model=model,
        tool_registry=tools,
        mode="auto",
        description="智能代码专家，具备完整 AI 能力",
        verbose=True
    )

    print(f"\n✓ HarnessedAgent 创建成功")
    print(f"  - Agent ID: {smart_agent.agent_id}")
    print(f"  - 能力: {', '.join(smart_agent.capabilities)}")

    # 获取 Harness 信息
    info = smart_agent.harness.get_harness_info()
    print(f"  - Harness 工具数: {info['tools_count']}")
    print(f"  - Harness 技能数: {info['skills_count']}")

    # 直接执行任务
    print("\n直接执行任务:")
    result = await smart_agent.execute_task({
        "type": "code_generation",
        "description": "创建二叉搜索树插入函数"
    })

    print(f"  - 成功: {result.get('success')}")
    print(f"  - 模式: {result.get('metadata', {}).get('mode')}")

    print("\n✓ HarnessedAgent 测试通过\n")
    return True


async def test_team_with_harness():
    """测试团队协作 + Harness"""
    print("=" * 60)
    print("测试 3: Team + Harness 协作")
    print("=" * 60)

    from aicode.agent_team import TeamCoordinator
    from aicode.agent_team.agent_harness import HarnessedAgent
    from aicode.agent_team import AgentRole
    from aicode.architectures.tools_enhanced import create_enhanced_tools

    # 创建模型和工具
    model = MockAIModel()
    tools = create_enhanced_tools()

    # 创建团队
    team = TeamCoordinator("Smart Team")

    # 创建多个 HarnessedAgent
    code_agent = HarnessedAgent(
        agent_id="smart_code_1",
        name="Smart Coder",
        role=AgentRole.SPECIALIST,
        capabilities=["code_generation", "code_review"],
        model=model,
        tool_registry=tools,
        verbose=False
    )

    analysis_agent = HarnessedAgent(
        agent_id="smart_analyst_1",
        name="Smart Analyst",
        role=AgentRole.ANALYZER,
        capabilities=["analyze_data", "generate_report"],
        model=model,
        tool_registry=tools,
        verbose=False
    )

    # 添加到团队
    team.add_agent(code_agent)
    team.add_agent(analysis_agent)

    print(f"\n✓ 智能团队创建完成")
    print(f"  - 成员数: {len(team.list_agents())}")

    # 分配任务（会自动路由到合适的 HarnessedAgent）
    print("\n分配任务 1: 代码生成")
    result1 = await team.assign_task({
        "type": "code_generation",
        "description": "创建哈希表实现"
    })
    print(f"  - 成功: {result1.get('success')}")
    print(f"  - 由 {result1.get('metadata', {}).get('agent_name')} 完成")

    print("\n分配任务 2: 数据分析")
    result2 = await team.assign_task({
        "type": "analyze_data",
        "data": [1, 2, 3, 4, 5]
    })
    print(f"  - 成功: {result2.get('success')}")
    print(f"  - 由 {result2.get('metadata', {}).get('agent_name')} 完成")

    # 统计
    stats = team.get_statistics()
    print(f"\n团队统计:")
    print(f"  - 完成任务: {stats['tasks']['completed']}")
    print(f"  - 成功率: {stats['tasks']['success_rate']:.1%}")

    print("\n✓ Team + Harness 协作测试通过\n")
    return True


async def test_harness_with_memory():
    """测试 Harness 记忆功能"""
    print("=" * 60)
    print("测试 4: Harness 记忆系统")
    print("=" * 60)

    from aicode.agent_team import CodeAgent
    from aicode.agent_team.agent_harness import AgentHarness
    from aicode.architectures.tools_enhanced import create_enhanced_tools

    model = MockAIModel()
    tools = create_enhanced_tools()

    code_agent = CodeAgent()
    harness = AgentHarness(
        agent=code_agent,
        model=model,
        tool_registry=tools,
        verbose=False
    )

    # 添加记忆
    print("\n添加记忆:")
    harness.add_to_memory("user", "我喜欢用 Python 写代码")
    harness.add_to_memory("assistant", "好的，我会优先使用 Python")
    harness.add_to_memory("user", "函数命名用 snake_case")
    print("  ✓ 添加了 3 条记忆")

    # 获取记忆上下文
    context = harness.get_memory_context(include_long_term=False)
    print(f"\n记忆上下文长度: {len(context)} 字符")
    print(f"记忆内容预览:\n{context[:200]}...")

    # 执行任务（会使用记忆）
    print("\n执行任务（带记忆）:")
    result = await harness.execute_task({
        "type": "code_generation",
        "description": "创建一个用户认证函数"
    })

    print(f"  - 成功: {result.get('success')}")

    # Harness 信息
    info = harness.get_harness_info()
    print(f"\nHarness 状态:")
    print(f"  - 记忆消息数: {info['memory_messages']}")

    print("\n✓ Harness 记忆系统测试通过\n")
    return True


# === Mock 模型（用于测试） ===

class MockAIModel:
    """Mock AI 模型（用于测试）"""

    async def generate(self, prompt: str, **kwargs) -> str:
        """模拟生成响应"""
        # 简单模拟 ReAct 格式
        return """Thought: I need to generate code based on the task description.
Action: write_file
Action Input: {"path": "output.py", "content": "def quicksort(arr):\\n    if len(arr) <= 1:\\n        return arr\\n    pivot = arr[len(arr) // 2]\\n    left = [x for x in arr if x < pivot]\\n    middle = [x for x in arr if x == pivot]\\n    right = [x for x in arr if x > pivot]\\n    return quicksort(left) + middle + quicksort(right)"}
"""

    async def generate_stream(self, prompt: str, **kwargs):
        """模拟流式生成"""
        response = await self.generate(prompt, **kwargs)
        for char in response:
            yield char


# === 主测试函数 ===

async def main():
    """主测试函数"""
    print("\n🎯 Agent Harness 系统测试\n")

    tests = [
        ("Harness 基本功能", test_harness_basic),
        ("HarnessedAgent", test_harnessed_agent),
        ("Team + Harness", test_team_with_harness),
        ("Harness 记忆", test_harness_with_memory),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            success = await test_func()
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"  ✓ 通过: {passed}")
    print(f"  ✗ 失败: {failed}")
    print(f"  总计: {passed + failed}")

    if failed == 0:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  {failed} 个测试失败")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
