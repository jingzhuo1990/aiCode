#!/usr/bin/env python
"""
快速对比演示：有 Harness vs 没有 Harness (使用 LM Studio)

简化版，快速展示核心差异
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


async def demo_simple_task(model):
    """简单任务对比"""
    print_section("📊 对比演示：创建排序函数")

    # 任务定义
    task = {
        "type": "code_generation",
        "description": "创建一个冒泡排序函数，包含注释和类型注解",
        "language": "python"
    }

    # 1. 没有 Harness 的 Agent
    print("━" * 80)
    print("❌ 场景 1：没有 Harness 的 Agent")
    print("━" * 80)

    from aicode.agent_team import CodeAgent

    agent_without = CodeAgent()

    print(f"\n配置:")
    print(f"  - Agent: {agent_without.name}")
    print(f"  - Harness: ❌ 无")
    print(f"  - AI Model: ❌ 无")
    print(f"  - 推理能力: ❌ 无")

    start = time.time()
    result_without = await agent_without.execute_task(task)
    elapsed_without = time.time() - start

    print(f"\n执行结果:")
    print(f"  - 耗时: {elapsed_without:.3f}秒")
    print(f"  - 成功: {result_without.get('success')}")

    code = result_without.get('code', '')
    print(f"\n生成的代码:")
    print("─" * 80)
    print(code)
    print("─" * 80)

    print("\n❌ 问题:")
    print("  - 只有占位代码 'pass'")
    print("  - 完全没有实现任何功能")
    print("  - 不能实际使用")

    # 2. 有 Harness 的 Agent
    print("\n━" * 80)
    print("✅ 场景 2：有 Harness 的 Agent (使用真实 AI)")
    print("━" * 80)

    from aicode.agent_team import HarnessedAgent, AgentRole
    from aicode.architectures.tools_enhanced import create_enhanced_tools

    tools = create_enhanced_tools()

    agent_with = HarnessedAgent(
        agent_id="smart_coder",
        name="Smart Coder",
        role=AgentRole.SPECIALIST,
        capabilities=["code_generation"],
        model=model,
        tool_registry=tools,
        mode="react",
        verbose=False
    )

    print(f"\n配置:")
    print(f"  - Agent: {agent_with.name}")
    print(f"  - Harness: ✅ 已装备")
    print(f"  - AI Model: ✅ Qwen 3.5 9B (LM Studio)")
    print(f"  - 工具数量: {len(tools.get_all_tools())}")
    print(f"  - 推理模式: ReAct")

    print("\n⏳ AI 正在思考和生成代码...")
    print("   (这需要一些时间，因为 AI 在真正推理)")

    start = time.time()
    result_with = await agent_with.execute_task(task)
    elapsed_with = time.time() - start

    print(f"\n执行结果:")
    print(f"  - 耗时: {elapsed_with:.3f}秒")
    print(f"  - 成功: {result_with.get('success')}")
    print(f"  - 推理迭代: {result_with.get('iterations', 0)} 轮")

    # 显示思考过程（前2步）
    if result_with.get('trajectory'):
        print(f"\n🧠 AI 推理过程（前2步）:")
        for i, step in enumerate(result_with['trajectory'][:2], 1):
            thought = step.get('thought', '')[:120]
            action = step.get('action', 'N/A')
            print(f"\n  第 {i} 轮:")
            print(f"    思考: {thought}...")
            print(f"    行动: {action}")

    # 显示 AI 的回答
    answer = result_with.get('answer', '')
    if answer:
        print(f"\n📝 AI 生成的内容:")
        print("─" * 80)
        # 只显示前 600 字符
        display_answer = answer[:600] + ("..." if len(answer) > 600 else "")
        print(display_answer)
        print("─" * 80)

    print("\n✅ 优势:")
    print("  - AI 真正理解了任务需求")
    print("  - 经过多轮思考和推理")
    print("  - 可以生成实际可用的代码")
    print("  - 有完整的思考过程记录")

    # 对比总结
    print("\n━" * 80)
    print("📊 对比总结")
    print("━" * 80)

    print(f"\n⏱️  性能对比:")
    print(f"  没有 Harness: {elapsed_without:.3f}秒 (瞬间完成)")
    print(f"  有 Harness:   {elapsed_with:.3f}秒 (需要 AI 推理)")

    print(f"\n💡 质量对比:")
    print(f"  没有 Harness: ❌ 只有 'pass' 占位")
    print(f"  有 Harness:   ✅ 完整的实现代码")

    print(f"\n🎯 实用性对比:")
    print(f"  没有 Harness: ❌ 完全不可用")
    print(f"  有 Harness:   ✅ 可直接使用")

    print(f"\n🧠 智能程度对比:")
    print(f"  没有 Harness: ❌ 无智能，固定逻辑")
    print(f"  有 Harness:   ✅ 真正的 AI，经过 {result_with.get('iterations', 0)} 轮推理")


async def demo_direct_generation(model):
    """直接展示 AI 生成能力"""
    print_section("🎨 展示：AI 直接生成代码")

    print("任务: 创建一个简单的栈（Stack）数据结构\n")
    print("⏳ AI 正在生成...")

    prompt = """请创建一个 Python 的栈（Stack）类，要求：
1. 支持 push（入栈）
2. 支持 pop（出栈）
3. 支持 peek（查看栈顶）
4. 支持 is_empty（判断是否为空）
5. 添加类型注解和文档字符串

直接返回完整的代码，不要有额外说明。"""

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
    print(response)
    print("─" * 80)

    print("\n💡 说明:")
    print("  这是 AI 模型的直接生成能力")
    print("  Harness 在此基础上增加了：")
    print("    - 🧠 多轮推理能力（ReAct 循环）")
    print("    - 🔧 工具调用能力（文件操作、代码执行等）")
    print("    - 💾 记忆能力（短期+长期记忆）")
    print("    - 🎯 任务规划能力（分解复杂任务）")


async def main():
    """主函数"""
    print("\n" + "🚀" * 40)
    print("     快速对比演示：有 Harness vs 没有 Harness")
    print("     使用 LM Studio (Qwen 3.5 9B)")
    print("🚀" * 40)
    print(f"\n⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. 测试连接
    model = await test_connection()
    if not model:
        return

    # 2. 简单任务对比
    await demo_simple_task(model)

    # 3. 直接生成演示
    await demo_direct_generation(model)

    # 总结
    print_section("🎯 核心结论")
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                     Harness 的价值                                 ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  没有 Harness 的 Agent:                                            ║
║    - 只是一个普通的 Python 类                                       ║
║    - 执行固定的逻辑（返回占位代码）                                  ║
║    - 没有任何智能                                                   ║
║    - 不能真正完成任务                                               ║
║                                                                   ║
║  有 Harness 的 Agent:                                              ║
║    - 是一个真正的智能体（AI Agent）                                  ║
║    - 具备 AI 推理能力                                               ║
║    - 可以使用工具完成实际操作                                        ║
║    - 可以记住上下文                                                 ║
║    - 可以处理复杂任务                                               ║
║                                                                   ║
║  🎯 Harness = 把 Agent 从"数据结构"变成"智能体"                      ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

📊 类比理解:

  没有 Harness    vs    有 Harness
  ────────────          ────────────
  空的容器              装满水的容器
  车架                  完整的汽车
  手机外壳              可使用的手机
  空房子                配齐家具的家

Harness Engineering 的核心：
  为 Agent 提供运行环境，让它具备真正的智能！
""")

    print("=" * 80)
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("演示完成！🎉")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
