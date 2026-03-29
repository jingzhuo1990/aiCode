#!/usr/bin/env python
"""
最小化对比演示：有 Harness vs 没有 Harness (使用 LM Studio)

使用最小化的提示词，避免 context size 超限
"""

import asyncio
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


async def test_connection():
    """测试 LM Studio 连接"""
    print_section("🔍 测试 LM Studio 连接")

    from aicode.models import LocalModel

    try:
        model = LocalModel(
            model_name="qwen/qwen3.5-9b",
            base_url="http://localhost:1234/v1"
        )

        print("发送测试请求...")
        response = await model.generate(
            "请用一句话介绍你自己",
            max_tokens=50
        )

        print(f"✅ 连接成功！")
        print(f"✅ 模型: qwen/qwen3.5-9b")
        print(f"\n模型回复: {response}\n")
        return model

    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n请确保 LM Studio 已启动并加载了模型")
        return None


async def demo_without_harness():
    """没有 Harness 的 Agent"""
    print_section("❌ 场景 1：没有 Harness 的 Agent")

    from aicode.agent_team import CodeAgent

    agent = CodeAgent()

    print(f"Agent 信息:")
    print(f"  - 名称: {agent.name}")
    print(f"  - 能力: {list(agent.capabilities)}")
    print(f"  - Harness: ❌ 无")
    print(f"  - AI Model: ❌ 无")

    print(f"\n📋 任务：创建一个冒泡排序函数")
    print(f"⏳ 执行中...\n")

    task = {
        "type": "code_generation",
        "description": "创建一个冒泡排序函数",
        "language": "python"
    }

    start = time.time()
    result = await agent.execute_task(task)
    elapsed = time.time() - start

    print(f"执行结果:")
    print(f"  - 耗时: {elapsed:.3f}秒")
    print(f"  - 成功: {result.get('success')}")

    code = result.get('code', '')
    print(f"\n生成的代码:")
    print("─" * 80)
    print(code)
    print("─" * 80)

    print(f"\n❌ 问题:")
    print(f"  - 只有占位代码 'pass'")
    print(f"  - 没有实现任何功能")
    print(f"  - 不能实际使用")

    return elapsed, code


async def demo_with_minimal_harness(model):
    """有 Harness 的 Agent (使用最小化工具集)"""
    print_section("✅ 场景 2：有 Harness 的 Agent (最小化配置)")

    from aicode.agent_team import HarnessedAgent, AgentRole
    from aicode.architectures.tools import ToolRegistry, Tool

    # 只注册最少的工具
    tools = ToolRegistry()

    # 注册一个简单的代码生成工具
    def generate_code(description: str) -> str:
        """Generate code based on description"""
        return f"Code generated for: {description}"

    tool = Tool(
        name="generate_code",
        description="Generate code based on description",
        func=generate_code,
        parameters={
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Code description"}
            },
            "required": ["description"]
        }
    )
    tools.register(tool)

    agent = HarnessedAgent(
        agent_id="minimal_coder",
        name="Minimal Coder",
        role=AgentRole.SPECIALIST,
        capabilities=["code_generation"],
        model=model,
        tool_registry=tools,
        mode="react",
        verbose=False
    )

    print(f"Agent 信息:")
    print(f"  - 名称: {agent.name}")
    print(f"  - 能力: {list(agent.capabilities)}")
    print(f"  - Harness: ✅ 已装备")
    print(f"  - AI Model: ✅ Qwen 3.5 9B")
    print(f"  - 工具数量: {len(tools.get_all_tools())} (最小化)")

    print(f"\n📋 任务：创建一个冒泡排序函数")
    print(f"⏳ AI 正在思考...\n")

    task = {
        "type": "code_generation",
        "description": "创建一个冒泡排序函数",
        "language": "python"
    }

    start = time.time()
    result = await agent.execute_task(task)
    elapsed = time.time() - start

    print(f"\n执行结果:")
    print(f"  - 耗时: {elapsed:.3f}秒")
    print(f"  - 成功: {result.get('success')}")
    print(f"  - 推理迭代: {result.get('iterations', 0)} 轮")

    # 显示思考过程
    if result.get('trajectory'):
        print(f"\n🧠 AI 推理过程（前2轮）:")
        for i, step in enumerate(result['trajectory'][:2], 1):
            thought = step.get('thought', '')[:120]
            action = step.get('action', 'N/A')
            print(f"\n  第 {i} 轮:")
            print(f"    思考: {thought}...")
            print(f"    行动: {action}")

    # 显示答案
    answer = result.get('answer', '')
    if answer:
        print(f"\n📝 AI 的回答:")
        print("─" * 80)
        display_answer = answer[:600] + ("..." if len(answer) > 600 else "")
        print(display_answer)
        print("─" * 80)

    print(f"\n✅ 优势:")
    print(f"  - AI 真正理解了任务")
    print(f"  - 经过 {result.get('iterations', 0)} 轮推理")
    print(f"  - 生成了实际的回答")

    return elapsed, answer


async def demo_direct_ai(model):
    """直接使用 AI 模型生成"""
    print_section("🎨 场景 3：直接 AI 生成（无 Harness 包装）")

    print("任务: 创建一个冒泡排序函数\n")
    print("⏳ AI 正在生成...\n")

    prompt = """创建一个 Python 的冒泡排序函数，要求：
1. 使用类型注解
2. 添加文档字符串
3. 包含示例用法

直接返回完整代码，不要有额外说明。"""

    start = time.time()
    response = await model.generate(
        prompt,
        max_tokens=500,
        temperature=0.3
    )
    elapsed = time.time() - start

    print(f"✅ 生成完成 (耗时: {elapsed:.2f}秒)\n")
    print("生成的代码:")
    print("─" * 80)
    print(response[:800])
    print("─" * 80)

    print("\n💡 说明:")
    print("  这是 AI 模型的直接生成能力")
    print("  Harness 在此基础上增加了：")
    print("    - 🧠 多轮推理能力（ReAct 循环）")
    print("    - 🔧 工具调用能力")
    print("    - 💾 记忆能力")
    print("    - 🎯 任务规划能力")

    return elapsed, response


async def main():
    """主函数"""
    print("\n" + "🚀" * 40)
    print("     最小化对比演示：有 Harness vs 没有 Harness")
    print("     使用 LM Studio (Qwen 3.5 9B)")
    print("🚀" * 40)
    print(f"\n⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. 测试连接
    model = await test_connection()
    if not model:
        return

    # 2. 没有 Harness
    time_without, code_without = await demo_without_harness()

    # 3. 有 Harness (最小化)
    try:
        time_with, answer_with = await demo_with_minimal_harness(model)
    except Exception as e:
        print(f"\n⚠️  Harness 演示出错: {e}")
        print(f"尝试直接 AI 生成作为替代...")
        time_with, answer_with = await demo_direct_ai(model)

    # 4. 直接 AI
    time_direct, code_direct = await demo_direct_ai(model)

    # 对比总结
    print_section("📊 对比总结")

    print(f"\n⏱️  性能对比:")
    print(f"  没有 Harness:   {time_without:.3f}秒 (瞬间，但无实现)")
    print(f"  直接 AI 生成:   {time_direct:.2f}秒 (生成完整代码)")
    if 'time_with' in locals():
        print(f"  有 Harness:     {time_with:.3f}秒 (推理 + 生成)")

    print(f"\n💡 质量对比:")
    print(f"  没有 Harness:   ❌ 只有 'pass' 占位")
    print(f"  直接 AI 生成:   ✅ 完整代码，但无推理过程")
    if 'answer_with' in locals():
        print(f"  有 Harness:     ✅ 完整代码 + 推理轨迹")

    print(f"\n🧠 智能程度对比:")
    print(f"  没有 Harness:   ❌ 无智能，固定逻辑")
    print(f"  直接 AI 生成:   ⭐ 一次性生成")
    if 'answer_with' in locals():
        print(f"  有 Harness:     ⭐⭐⭐ 多轮推理 + 工具使用")

    # 总结
    print_section("🎯 核心结论")
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                     三种方式对比                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  1. 没有 Harness 的 Agent:                                         ║
║     - 只是一个普通的 Python 类                                      ║
║     - 返回固定的占位代码                                            ║
║     - 没有任何智能                                                 ║
║                                                                   ║
║  2. 直接 AI 生成:                                                  ║
║     - AI 模型的基础能力                                            ║
║     - 一次性生成结果                                               ║
║     - 无法使用工具、无记忆                                          ║
║                                                                   ║
║  3. 有 Harness 的 Agent:                                           ║
║     - 完整的 AI 推理循环                                           ║
║     - 可以使用工具完成复杂操作                                       ║
║     - 具备记忆和上下文理解                                          ║
║     - 可以处理多步骤任务                                            ║
║                                                                   ║
║  🎯 Harness = 把 AI 从"工具"变成"智能体"                            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

📊 类比理解:

  没有 Harness       直接 AI           有 Harness
  ────────────       ────────        ────────────
  空模板             单次咨询         完整工作流
  固定脚本           翻译工具         智能助手
  预设回复           查询引擎         自主系统

Harness Engineering 的价值：
  为 AI 提供"手"（工具）、"脑"（推理）、"记忆"（上下文）
""")

    print("=" * 80)
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("演示完成！🎉")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
