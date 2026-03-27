#!/usr/bin/env python
"""测试 Skills 系统"""

import asyncio
import tempfile
import os
from pathlib import Path


async def test_skills():
    """测试技能系统"""
    print("=" * 60)
    print("测试 Skills 系统")
    print("=" * 60)

    # 1. 导入模块
    print("\n测试 1: 导入 Skills 模块")
    print("-" * 60)
    try:
        from aicode.skills import (
            create_default_skills,
            SkillExecutionContext,
            CodeRefactorSkill,
            AddTestsSkill,
            ProjectSetupSkill
        )
        from aicode.architectures.tools_enhanced import create_enhanced_tools
        print("✓ Skills 模块导入成功")
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

    # 2. 创建技能注册表
    print("\n测试 2: 创建技能注册表")
    print("-" * 60)
    try:
        skill_registry = create_default_skills()
        skills = skill_registry.list_skills()
        print(f"✓ 成功创建注册表")
        print(f"  - 总技能数: {len(skills)}")

        categories = skill_registry.get_categories()
        print(f"  - 分类: {', '.join(categories)}")

        for skill in skills:
            print(f"    • {skill.name} ({skill.category})")
    except Exception as e:
        print(f"✗ 创建注册表失败: {e}")
        return False

    # 3. 创建工具
    print("\n测试 3: 创建工具注册表")
    print("-" * 60)
    try:
        tool_registry = create_enhanced_tools()
        print(f"✓ 工具注册表创建成功")
        print(f"  - 总工具数: {len(tool_registry.tools)}")
    except Exception as e:
        print(f"✗ 创建工具失败: {e}")
        return False

    # 4. 测试代码审查技能
    print("\n测试 4: 测试 code_review 技能")
    print("-" * 60)
    try:
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as f:
            f.write('''def calculate(a, b):
    return a + b

def process_data(data):
    try:
        result = calculate(data[0], data[1])
        return result
    except:
        pass
''')
            test_file = f.name

        # 创建执行上下文
        context = SkillExecutionContext(
            tools={
                tool.name: tool.func
                for tool in tool_registry.tools.values()
            },
            working_dir=os.path.dirname(test_file)
        )

        # 执行技能
        result = await skill_registry.execute_skill(
            "code_review",
            context,
            file_path=test_file
        )

        print(f"✓ code_review 执行完成")
        print(f"  - 成功: {result['success']}")
        print(f"  - 消息: {result['message']}")
        print(f"  - 发现问题数: {len(result['data']['issues'])}")

        # 清理
        os.unlink(test_file)

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 5. 测试项目初始化技能
    print("\n测试 5: 测试 project_setup 技能")
    print("-" * 60)
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            context = SkillExecutionContext(
                tools={
                    tool.name: tool.func
                    for tool in tool_registry.tools.values()
                },
                working_dir=tmpdir
            )

            result = await skill_registry.execute_skill(
                "project_setup",
                context,
                project_name="test_project",
                project_type="python"
            )

            print(f"✓ project_setup 执行完成")
            print(f"  - 成功: {result['success']}")
            print(f"  - 创建的文件数: {len(result['data']['files_created'])}")
            print("  - 文件列表:")
            for file in result['data']['files_created']:
                print(f"    • {file}")

            # 验证文件是否创建
            project_dir = os.path.join(tmpdir, "test_project")
            readme = os.path.join(project_dir, "README.md")
            if os.path.exists(readme):
                print("  ✓ README.md 已创建")

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 6. 测试技能搜索
    print("\n测试 6: 测试技能搜索")
    print("-" * 60)
    try:
        results = skill_registry.search("code")
        print(f"✓ 搜索 'code' 找到 {len(results)} 个技能:")
        for skill in results:
            print(f"  • {skill.name}")
    except Exception as e:
        print(f"✗ 搜索失败: {e}")
        return False

    # 7. 测试技能统计
    print("\n测试 7: 测试技能统计")
    print("-" * 60)
    try:
        stats = skill_registry.get_all_stats()
        print(f"✓ 统计信息:")
        print(f"  - 总技能数: {stats['total_skills']}")
        print(f"  - 分类: {', '.join(stats['categories'])}")
    except Exception as e:
        print(f"✗ 获取统计失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    return True


async def demo_skills():
    """演示 Skills 功能"""
    print("\n\n" + "=" * 60)
    print("Skills 功能演示")
    print("=" * 60)

    from aicode.skills import create_default_skills
    skill_registry = create_default_skills()

    print("\n可用技能:")
    print("-" * 60)

    skills_by_category = {}
    for skill in skill_registry.list_skills():
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)

    for category, skills in sorted(skills_by_category.items()):
        print(f"\n[{category.upper()}]")
        for skill in skills:
            print(f"  • {skill.name}")
            print(f"    {skill.description}")
            print(f"    需要工具: {', '.join(skill.required_tools)}")

    print("\n" + "=" * 60)
    print("使用示例:")
    print("=" * 60)
    print("""
# 列出所有技能
python -m aicode.cli_agent skill-list

# 执行代码重构
python -m aicode.cli_agent skill-run code_refactor -p file_path=mycode.py

# 生成单元测试
python -m aicode.cli_agent skill-run add_tests -p file_path=mycode.py

# 创建新项目
python -m aicode.cli_agent skill-run project_setup -p project_name=myapp

# 智能提交代码
python -m aicode.cli_agent skill-run commit_changes

# 查看技能统计
python -m aicode.cli_agent skill-stats
""")


if __name__ == "__main__":
    print("\n🎯 Skills 系统测试\n")

    # 运行测试
    success = asyncio.run(test_skills())

    if success:
        # 运行演示
        asyncio.run(demo_skills())

        print("\n" + "=" * 60)
        print("🎉 Skills 系统测试成功！")
        print("=" * 60)
        print("\n下一步:")
        print("1. 阅读文档: SKILLS_GUIDE.md")
        print("2. 列出技能: python -m aicode.cli_agent skill-list")
        print("3. 执行技能: python -m aicode.cli_agent skill-run <skill_name> -p key=value")
    else:
        print("\n" + "=" * 60)
        print("⚠️  测试失败")
        print("=" * 60)
        print("\n请检查错误信息并修复问题")
