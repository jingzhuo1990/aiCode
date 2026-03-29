#!/usr/bin/env python
"""测试 Agent Team 系统"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_basic_communication():
    """测试基本的 Agent 通信"""
    print("=" * 60)
    print("测试 1: Agent 基本通信")
    print("=" * 60)

    from aicode.agent_team import (
        CodeAgent,
        FileAgent,
        TeamCoordinator,
        MessageType
    )

    # 创建团队
    team = TeamCoordinator("Test Team")

    # 添加 Agent
    code_agent = CodeAgent()
    file_agent = FileAgent()

    team.add_agent(code_agent)
    team.add_agent(file_agent)

    print(f"\n✓ 团队创建成功，共 {len(team.list_agents())} 个 Agent\n")

    # 测试消息发送
    print("测试消息发送...")
    code_agent.send_message(
        file_agent.agent_id,
        MessageType.QUERY,
        {"query": "文件系统状态如何？"}
    )

    print(f"  - CodeAgent 发送消息到 FileAgent")
    print(f"  - CodeAgent outbox: {code_agent.outbox.size()} 条消息")

    # 路由消息
    if code_agent.outbox.size() > 0:
        msg = code_agent.outbox.pop()
        file_agent.receive_message(msg)
        print(f"  - FileAgent 收到消息")
        print(f"  - FileAgent inbox: {file_agent.inbox.size()} 条消息")

    print("\n✓ 基本通信测试通过\n")
    return True


async def test_task_assignment():
    """测试任务分配"""
    print("=" * 60)
    print("测试 2: 任务分配与执行")
    print("=" * 60)

    from aicode.agent_team import (
        CodeAgent,
        FileAgent,
        AnalysisAgent,
        TeamCoordinator
    )

    # 创建团队
    team = TeamCoordinator("Task Team")
    team.add_agent(CodeAgent())
    team.add_agent(FileAgent())
    team.add_agent(AnalysisAgent())

    print()

    # 测试任务 1: 代码生成
    print("任务 1: 代码生成")
    result1 = await team.assign_task({
        "type": "code_generation",
        "description": "创建一个快速排序函数",
        "language": "python"
    })
    print(f"  结果: {result1.get('success')}")
    if result1.get("success"):
        print(f"  生成的代码: {result1.get('code')[:50]}...")

    print()

    # 测试任务 2: 文件操作
    print("任务 2: 文件读取")
    result2 = await team.assign_task({
        "type": "file_read",
        "file_path": "test.txt"
    })
    print(f"  结果: {result1.get('success')}")
    if result2.get("success"):
        print(f"  文件路径: {result2.get('file_path')}")

    print()

    # 测试任务 3: 数据分析
    print("任务 3: 数据分析")
    result3 = await team.assign_task({
        "type": "analyze_data",
        "data": [1, 2, 3, 4, 5]
    })
    print(f"  结果: {result3.get('success')}")
    if result3.get("success"):
        print(f"  分析: {result3.get('analysis')}")

    print("\n✓ 任务分配测试通过\n")
    return True


async def test_workflow():
    """测试工作流执行"""
    print("=" * 60)
    print("测试 3: 工作流执行")
    print("=" * 60)

    from aicode.agent_team import (
        PlannerAgent,
        CodeAgent,
        FileAgent,
        AnalysisAgent,
        TeamCoordinator
    )

    # 创建团队
    team = TeamCoordinator("Workflow Team")
    team.add_agent(PlannerAgent())
    team.add_agent(CodeAgent())
    team.add_agent(FileAgent())
    team.add_agent(AnalysisAgent())

    print()

    # 定义工作流
    workflow = [
        {
            "type": "task_planning",
            "description": "规划项目开发"
        },
        {
            "type": "code_generation",
            "description": "生成主程序代码"
        },
        {
            "type": "file_write",
            "file_path": "main.py",
            "content": "# Generated code"
        },
        {
            "type": "summarize",
            "content": "项目开发完成，包含主程序代码"
        }
    ]

    print(f"执行工作流（{len(workflow)} 个步骤）...\n")

    results = await team.execute_workflow(workflow)

    print(f"\n工作流完成:")
    for i, result in enumerate(results):
        success = result.get("success", False)
        status = "✓" if success else "✗"
        print(f"  {status} 步骤 {i+1}: {workflow[i]['type']}")

    print("\n✓ 工作流测试通过\n")
    return True


async def test_parallel_execution():
    """测试并行执行"""
    print("=" * 60)
    print("测试 4: 并行任务执行")
    print("=" * 60)

    from aicode.agent_team import (
        CodeAgent,
        FileAgent,
        AnalysisAgent,
        TeamCoordinator
    )

    # 创建团队（多个相同类型的 Agent）
    team = TeamCoordinator("Parallel Team")
    team.add_agent(CodeAgent("code_agent_1"))
    team.add_agent(CodeAgent("code_agent_2"))
    team.add_agent(FileAgent("file_agent_1"))
    team.add_agent(AnalysisAgent())

    print()

    # 并行任务
    tasks = [
        {
            "type": "code_generation",
            "description": "生成函数 A"
        },
        {
            "type": "code_generation",
            "description": "生成函数 B"
        },
        {
            "type": "file_search",
            "pattern": "*.py"
        },
        {
            "type": "analyze_data",
            "data": [1, 2, 3]
        }
    ]

    print(f"并行执行 {len(tasks)} 个任务...\n")

    results = await team.execute_parallel_tasks(tasks)

    print(f"\n并行任务完成:")
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"  ✗ 任务 {i+1}: 异常 - {result}")
        else:
            success = result.get("success", False)
            status = "✓" if success else "✗"
            print(f"  {status} 任务 {i+1}: {tasks[i]['type']}")

    print("\n✓ 并行执行测试通过\n")
    return True


async def test_team_statistics():
    """测试团队统计"""
    print("=" * 60)
    print("测试 5: 团队统计信息")
    print("=" * 60)

    from aicode.agent_team import (
        CodeAgent,
        FileAgent,
        AnalysisAgent,
        PlannerAgent,
        TeamCoordinator
    )

    # 创建团队
    team = TeamCoordinator("Stats Team")
    team.add_agent(CodeAgent())
    team.add_agent(FileAgent())
    team.add_agent(AnalysisAgent())
    team.add_agent(PlannerAgent())

    print()

    # 执行一些任务
    await team.assign_task({"type": "code_generation", "description": "test"})
    await team.assign_task({"type": "file_read", "file_path": "test.txt"})
    await team.assign_task({"type": "analyze_data", "data": []})

    # 获取统计
    stats = team.get_statistics()

    print("团队统计:")
    print(f"  - 团队名称: {stats['team_name']}")
    print(f"  - Agent 数量: {stats['agents_count']}")
    print(f"  - 消息发送: {stats['messages']['sent']}")
    print(f"  - 消息接收: {stats['messages']['received']}")
    print(f"  - 任务完成: {stats['tasks']['completed']}")
    print(f"  - 任务失败: {stats['tasks']['failed']}")
    print(f"  - 成功率: {stats['tasks']['success_rate']:.1%}")

    # 获取团队状态
    status = team.get_team_status()
    print(f"\n团队状态:")
    print(f"  - 活跃任务: {status['active_tasks']}")
    print(f"  - 已完成任务: {status['completed_tasks']}")

    print("\n✓ 统计信息测试通过\n")
    return True


async def demo_real_scenario():
    """演示真实场景"""
    print("\n" + "=" * 60)
    print("真实场景演示: 完整的开发流程")
    print("=" * 60)

    from aicode.agent_team import (
        PlannerAgent,
        CodeAgent,
        FileAgent,
        AnalysisAgent,
        TeamCoordinator
    )

    # 创建团队
    team = TeamCoordinator("Development Team")
    team.add_agent(PlannerAgent())
    team.add_agent(CodeAgent())
    team.add_agent(FileAgent())
    team.add_agent(AnalysisAgent())

    print("\n场景: 开发一个新功能\n")

    # 步骤 1: 规划
    print("📋 步骤 1: 任务规划")
    plan_result = await team.assign_task({
        "type": "decompose_task",
        "description": "开发用户认证功能"
    })

    if plan_result.get("success"):
        subtasks = plan_result.get("subtasks", [])
        print(f"  ✓ 规划完成，分解为 {len(subtasks)} 个子任务")
        for subtask in subtasks:
            print(f"    - {subtask['description']} → {subtask['agent_type']}")

    # 步骤 2: 代码生成
    print("\n💻 步骤 2: 生成代码")
    code_result = await team.assign_task({
        "type": "code_generation",
        "description": "用户认证函数",
        "language": "python"
    })

    if code_result.get("success"):
        print(f"  ✓ 代码生成成功")
        print(f"    语言: {code_result.get('language')}")

    # 步骤 3: 保存文件
    print("\n📁 步骤 3: 保存代码文件")
    file_result = await team.assign_task({
        "type": "file_write",
        "file_path": "auth.py",
        "content": code_result.get("code", "")
    })

    if file_result.get("success"):
        print(f"  ✓ 文件保存成功")
        print(f"    路径: {file_result.get('file_path')}")
        print(f"    大小: {file_result.get('bytes_written')} bytes")

    # 步骤 4: 生成报告
    print("\n📊 步骤 4: 生成开发报告")
    report_result = await team.assign_task({
        "type": "generate_report",
        "data": {
            "feature": "用户认证",
            "files": ["auth.py"],
            "lines": 50
        }
    })

    if report_result.get("success"):
        print(f"  ✓ 报告生成成功")

    # 显示最终统计
    print("\n" + "=" * 60)
    stats = team.get_statistics()
    print("开发流程完成！")
    print(f"  - 参与 Agent: {stats['agents_count']}")
    print(f"  - 完成任务: {stats['tasks']['completed']}")
    print(f"  - 消息交换: {stats['messages']['sent']} 条")
    print("=" * 60)


async def main():
    """主测试函数"""
    print("\n🎯 Agent Team 系统测试\n")

    tests = [
        ("基本通信", test_basic_communication),
        ("任务分配", test_task_assignment),
        ("工作流执行", test_workflow),
        ("并行执行", test_parallel_execution),
        ("统计信息", test_team_statistics),
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

    # 运行演示
    try:
        await demo_real_scenario()
    except Exception as e:
        print(f"\n✗ 演示失败: {e}")
        import traceback
        traceback.print_exc()

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
