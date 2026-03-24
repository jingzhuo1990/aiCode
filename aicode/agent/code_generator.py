"""代码生成器"""

from typing import Optional
from ..models.base import AIModel


class CodeGenerator:
    """AI 代码生成器"""

    def __init__(self, model: AIModel):
        self.model = model

    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> str:
        """
        生成代码

        Args:
            prompt: 用户需求描述
            language: 编程语言
            context: 额外上下文信息
            max_tokens: 最大生成token数
            temperature: 温度参数

        Returns:
            生成的代码
        """
        system_prompt = f"""你是一个专业的 {language} 程序员和代码生成助手。
你的任务是根据用户的需求描述生成高质量、清晰、可维护的代码。

生成代码时请遵循以下原则：
1. 代码应该清晰、简洁、易于理解
2. 遵循 {language} 的最佳实践和编码规范
3. 添加必要的注释说明关键逻辑
4. 考虑错误处理和边界情况
5. 确保代码的可扩展性和可维护性

请只返回代码内容，不要添加额外的解释（除非在代码注释中）。
"""

        if context:
            prompt = f"上下文信息：\n{context}\n\n需求：\n{prompt}"

        code = await self.model.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # 清理可能的代码块标记
        code = self._clean_code_output(code)

        return code

    async def generate_function(
        self,
        function_description: str,
        function_name: Optional[str] = None,
        parameters: Optional[str] = None,
        return_type: Optional[str] = None,
        language: str = "python",
    ) -> str:
        """
        生成函数

        Args:
            function_description: 函数功能描述
            function_name: 函数名称
            parameters: 参数描述
            return_type: 返回值类型
            language: 编程语言

        Returns:
            生成的函数代码
        """
        prompt = f"生成一个函数：{function_description}"

        if function_name:
            prompt += f"\n函数名称：{function_name}"
        if parameters:
            prompt += f"\n参数：{parameters}"
        if return_type:
            prompt += f"\n返回值类型：{return_type}"

        return await self.generate_code(prompt, language=language)

    async def generate_class(
        self,
        class_description: str,
        class_name: Optional[str] = None,
        methods: Optional[list] = None,
        language: str = "python",
    ) -> str:
        """
        生成类

        Args:
            class_description: 类功能描述
            class_name: 类名称
            methods: 方法列表描述
            language: 编程语言

        Returns:
            生成的类代码
        """
        prompt = f"生成一个类：{class_description}"

        if class_name:
            prompt += f"\n类名称：{class_name}"
        if methods:
            prompt += f"\n需要的方法：{', '.join(methods)}"

        return await self.generate_code(prompt, language=language)

    async def explain_code(self, code: str, language: str = "python") -> str:
        """
        解释代码

        Args:
            code: 代码内容
            language: 编程语言

        Returns:
            代码解释
        """
        system_prompt = f"""你是一个专业的代码审查专家。
请分析并解释给定的 {language} 代码，包括：
1. 代码的主要功能和目的
2. 关键算法和逻辑
3. 潜在的问题或改进建议
4. 代码复杂度分析
"""

        prompt = f"请分析以下代码：\n\n```{language}\n{code}\n```"

        explanation = await self.model.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=3000,
            temperature=0.5,
        )

        return explanation

    @staticmethod
    def _clean_code_output(code: str) -> str:
        """
        清理代码输出，移除可能的 markdown 代码块标记

        Args:
            code: 原始代码

        Returns:
            清理后的代码
        """
        # 移除开头的代码块标记
        if code.startswith("```"):
            lines = code.split("\n")
            # 跳过第一行（```python 等）
            if len(lines) > 1:
                code = "\n".join(lines[1:])

        # 移除结尾的代码块标记
        if code.endswith("```"):
            code = code[:-3].rstrip()

        return code.strip()
