#!/usr/bin/env python
"""测试 Skills 与 Agent 的集成"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_agent_with_skills():
    """测试 Agent 是否能看到 Skills"""
    print("=" * 60)
    print("测试 Agent Skills 集成")
    print("=" * 60)

    # 1. 导入并创建 Agent
    print("\n[1/3] 创建 UnifiedAgent...")
    try:
        from aicode.models.local import LocalModel
        from aicode.architectures.unified_agent import UnifiedAgent

        # 创建本地模型（不会真正调用）
        model = LocalModel(
            base_url="http://localhost:1234/v1",
            model_name="test-model"
        )

        # 创建 Agent（会打印注册的技能）
        agent = UnifiedAgent(model=model, verbose=True)
        print("✓ UnifiedAgent 创建成功")

    except Exception as e:
        print(f"✗ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 2. 检查工具列表
    print("\n[2/3] 检查工具列表...")
    try:
        all_tools = agent.list_tools()
        print(f"  - 总工具数: {len(all_tools)}")

        # 分离普通工具和技能工具
        regular_tools = [t for t in all_tools if not t.startswith('skill_')]
        skill_tools = [t for t in all_tools if t.startswith('skill_')]

        print(f"  - 普通工具: {len(regular_tools)}")
        print(f"  - 技能工具: {len(skill_tools)}")

        if skill_tools:
            print("\n  已注册的技能工具:")
            for skill_tool in sorted(skill_tools):
                print(f"    • {skill_tool}")
            print("\n✓ Skills 已成功集成到 Agent！")
        else:
            print("\n✗ 没有找到技能工具")
            return False

    except Exception as e:
        print(f"✗ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 3. 检查技能工具的详细信息
    print("\n[3/3] 检查技能工具详情...")
    try:
        # 检查一个技能工具的详细信息
        skill_name = "skill_code_refactor"
        tool_info = agent.get_tool_info(skill_name)

        if tool_info:
            print(f"\n  示例技能: {skill_name}")
            print(f"  - 描述: {tool_info['description'][:100]}...")
            print(f"  - 参数: {list(tool_info['parameters']['properties'].keys())}")
            print("\n✓ 技能工具信息正确")
        else:
            print(f"\n✗ 无法获取 {skill_name} 的信息")
            return False

    except Exception as e:
        print(f"✗ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✅ 集成测试成功！Agent 现在可以使用 Skills 了")
    print("=" * 60)
    return True


async def show_integration_examples():
    """展示如何使用集成后的 Agent"""
    print("\n\n" + "=" * 60)
    print("使用示例")
    print("=" * 60)

    print("""
现在 Agent 可以在推理中自动使用 Skills！

示例 1: Agent 自动使用代码重构技能
-----------------------------------------
python -m aicode.cli_agent run "重构 calculator.py 文件" --provider local

Agent 会推理：
  → 用户想重构文件
  → 我看到有 skill_code_refactor 工具
  → 这个技能会自动处理读取、分析、重构、备份
  → 使用 skill_code_refactor


示例 2: Agent 自动创建项目
-----------------------------------------
python -m aicode.cli_agent run "创建一个名为 myapp 的 Python 项目" --provider local

Agent 会推理：
  → 需要创建项目结构
  → 我看到有 skill_project_setup 工具
  → 使用 skill_project_setup


示例 3: Agent 组合使用多个技能
-----------------------------------------
python -m aicode.cli_agent run "创建项目 todoapp，添加测试，然后提交" --provider local

Agent 会推理：
  → 步骤1: 使用 skill_project_setup 创建项目
  → 步骤2: 使用 skill_add_tests 添加测试
  → 步骤3: 使用 skill_commit_changes 提交

对比：
------
❌ 之前: Skills 只能通过 CLI 手动调用
   python -m aicode.cli_agent skill-run code_refactor -p file_path=test.py

✅ 现在: Agent 可以在推理中自动选择和使用 Skills
   python -m aicode.cli_agent run "重构 test.py" --provider local
""")


if __name__ == "__main__":
    print("\n🎯 测试 Skills 与 Agent 集成\n")

    # 运行测试
    success = asyncio.run(test_agent_with_skills())

    if success:
        # 显示使用示例
        asyncio.run(show_integration_examples())
        print("\n✅ 集成完成！现在可以使用 Agent 自动调用 Skills 了\n")
    else:
        print("\n❌ 集成测试失败，请检查错误信息\n")
        sys.exit(1)
