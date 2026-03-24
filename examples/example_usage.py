"""使用示例"""

import asyncio
from aicode.models.claude import ClaudeModel
from aicode.agent.code_generator import CodeGenerator
from aicode.agent.code_modifier import CodeModifier
from aicode.agent.file_handler import FileHandler


async def example_generate():
    """代码生成示例"""
    print("=== 代码生成示例 ===\n")

    # 初始化模型（需要设置环境变量 ANTHROPIC_API_KEY）
    model = ClaudeModel(
        api_key="your-api-key-here",
        model_name="claude-sonnet-4-6"
    )

    # 创建代码生成器
    generator = CodeGenerator(model)

    # 生成函数
    prompt = "创建一个 Python 函数，计算两个数的最大公约数"
    code = await generator.generate_code(prompt, language="python")

    print("生成的代码：")
    print(code)
    print("\n" + "="*50 + "\n")


async def example_modify():
    """代码修改示例"""
    print("=== 代码修改示例 ===\n")

    # 准备测试代码
    original_code = """
def calculate(a, b):
    return a + b
"""

    print("原始代码：")
    print(original_code)

    # 初始化模型和修改器
    model = ClaudeModel(
        api_key="your-api-key-here",
        model_name="claude-sonnet-4-6"
    )
    file_handler = FileHandler()
    modifier = CodeModifier(model, file_handler)

    # 修改代码
    instruction = "添加类型注解和文档字符串"
    modified_code = await modifier.modify_code(
        original_code=original_code,
        instruction=instruction,
        language="python"
    )

    print("\n修改后的代码：")
    print(modified_code)
    print("\n" + "="*50 + "\n")


async def example_refactor():
    """代码重构示例"""
    print("=== 代码重构示例 ===\n")

    code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""

    print("原始代码：")
    print(code)

    # 初始化
    model = ClaudeModel(
        api_key="your-api-key-here",
        model_name="claude-sonnet-4-6"
    )
    file_handler = FileHandler()
    modifier = CodeModifier(model, file_handler)

    # 重构代码（提高可读性）
    refactored = await modifier.refactor_code(
        code=code,
        refactor_type="readability",
        language="python"
    )

    print("\n重构后的代码：")
    print(refactored)
    print("\n" + "="*50 + "\n")


async def example_explain():
    """代码解释示例"""
    print("=== 代码解释示例 ===\n")

    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

    print("要分析的代码：")
    print(code)

    # 初始化
    model = ClaudeModel(
        api_key="your-api-key-here",
        model_name="claude-sonnet-4-6"
    )
    generator = CodeGenerator(model)

    # 解释代码
    explanation = await generator.explain_code(code, language="python")

    print("\n代码分析：")
    print(explanation)
    print("\n" + "="*50 + "\n")


async def main():
    """运行所有示例"""
    print("\n" + "="*50)
    print("AI Coding Agent 使用示例")
    print("="*50 + "\n")

    print("注意：请先设置环境变量或修改代码中的 API key\n")

    # 取消注释以运行特定示例
    # await example_generate()
    # await example_modify()
    # await example_refactor()
    # await example_explain()

    print("示例代码准备完成！")
    print("请设置 API key 后取消注释相应函数来运行示例。")


if __name__ == "__main__":
    asyncio.run(main())
