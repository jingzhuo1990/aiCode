"""代码修改器"""

from typing import Optional, Dict, Any
from ..models.base import AIModel
from .file_handler import FileHandler


class CodeModifier:
    """AI 代码修改器"""

    def __init__(self, model: AIModel, file_handler: FileHandler):
        self.model = model
        self.file_handler = file_handler

    async def modify_code(
        self,
        original_code: str,
        instruction: str,
        language: str = "python",
        context: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> str:
        """
        修改代码

        Args:
            original_code: 原始代码
            instruction: 修改指令
            language: 编程语言
            context: 额外上下文
            max_tokens: 最大生成token数
            temperature: 温度参数

        Returns:
            修改后的代码
        """
        system_prompt = f"""你是一个专业的 {language} 代码修改助手。
你的任务是根据用户的指令修改现有代码。

修改代码时请遵循以下原则：
1. 保持代码的整体结构和风格一致
2. 只修改必要的部分，不要改动无关代码
3. 确保修改后的代码功能正确
4. 保持或改进代码的可读性
5. 添加必要的注释说明修改内容

请只返回完整的修改后的代码，不要添加额外的解释。
"""

        prompt = f"""原始代码：
```{language}
{original_code}
```

修改要求：
{instruction}
"""

        if context:
            prompt += f"\n\n上下文信息：\n{context}"

        prompt += "\n\n请返回完整的修改后的代码："

        modified_code = await self.model.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # 清理可能的代码块标记
        modified_code = self._clean_code_output(modified_code)

        return modified_code

    async def modify_file(
        self,
        file_path: str,
        instruction: str,
        backup: bool = True,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        修改文件

        Args:
            file_path: 文件路径
            instruction: 修改指令
            backup: 是否备份原文件
            dry_run: 是否只预览不实际修改

        Returns:
            包含修改结果的字典
        """
        # 读取原文件
        original_code = await self.file_handler.read_file(file_path)

        # 获取文件信息
        file_info = self.file_handler.get_file_info(file_path)
        extension = file_info["extension"]

        # 推断编程语言
        language = self._get_language_from_extension(extension)

        # 分析原始代码结构
        original_structure = self.file_handler.analyze_code_structure(
            original_code, extension
        )

        # 修改代码
        modified_code = await self.modify_code(
            original_code=original_code,
            instruction=instruction,
            language=language,
        )

        # 分析修改后的代码结构
        modified_structure = self.file_handler.analyze_code_structure(
            modified_code, extension
        )

        result = {
            "file_path": file_path,
            "original_lines": original_structure["total_lines"],
            "modified_lines": modified_structure["total_lines"],
            "language": language,
            "dry_run": dry_run,
            "backup_created": False,
        }

        if not dry_run:
            # 备份原文件
            if backup:
                backup_path = f"{file_path}.backup"
                await self.file_handler.write_file(backup_path, original_code)
                result["backup_created"] = True
                result["backup_path"] = backup_path

            # 写入修改后的代码
            await self.file_handler.write_file(file_path, modified_code)
            result["modified"] = True
        else:
            result["modified"] = False
            result["preview"] = modified_code[:500]  # 预览前500个字符

        return result

    async def refactor_code(
        self,
        code: str,
        refactor_type: str = "general",
        language: str = "python",
    ) -> str:
        """
        重构代码

        Args:
            code: 原始代码
            refactor_type: 重构类型（general, performance, readability等）
            language: 编程语言

        Returns:
            重构后的代码
        """
        refactor_instructions = {
            "general": "全面重构这段代码，提高代码质量、可读性和可维护性",
            "performance": "优化这段代码的性能，减少时间和空间复杂度",
            "readability": "提高代码的可读性，使其更易于理解",
            "security": "增强代码的安全性，修复潜在的安全漏洞",
            "simplify": "简化代码逻辑，减少不必要的复杂性",
        }

        instruction = refactor_instructions.get(
            refactor_type,
            refactor_instructions["general"]
        )

        return await self.modify_code(
            original_code=code,
            instruction=instruction,
            language=language,
        )

    async def add_documentation(
        self,
        code: str,
        language: str = "python",
    ) -> str:
        """
        为代码添加文档字符串和注释

        Args:
            code: 原始代码
            language: 编程语言

        Returns:
            添加文档后的代码
        """
        instruction = f"""为这段代码添加完整的文档和注释：
1. 为每个函数/方法添加文档字符串（docstring）
2. 为复杂的逻辑添加行内注释
3. 在文件顶部添加模块说明
4. 遵循 {language} 的文档规范
"""

        return await self.modify_code(
            original_code=code,
            instruction=instruction,
            language=language,
        )

    @staticmethod
    def _get_language_from_extension(extension: str) -> str:
        """
        从文件扩展名推断编程语言

        Args:
            extension: 文件扩展名

        Returns:
            编程语言名称
        """
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "c++",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
        }

        return language_map.get(extension.lower(), "text")

    @staticmethod
    def _clean_code_output(code: str) -> str:
        """清理代码输出"""
        if code.startswith("```"):
            lines = code.split("\n")
            if len(lines) > 1:
                code = "\n".join(lines[1:])

        if code.endswith("```"):
            code = code[:-3].rstrip()

        return code.strip()
