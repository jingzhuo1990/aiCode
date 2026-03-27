"""代码相关技能"""

import os
import re
from typing import Dict, Any
from .base import Skill, SkillExecutionContext


class CodeRefactorSkill(Skill):
    """代码重构技能"""

    def __init__(self):
        super().__init__(
            name="code_refactor",
            description="重构指定文件的代码，提高可读性和可维护性",
            category="code",
            required_tools=["read_file", "write_file", "run_python"],
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要重构的文件路径"
                    },
                    "focus": {
                        "type": "string",
                        "description": "重构重点（如 naming, structure, performance）",
                        "default": "general"
                    }
                },
                "required": ["file_path"]
            }
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        file_path: str,
        focus: str = "general",
        **kwargs
    ) -> Dict[str, Any]:
        """执行代码重构"""
        steps = []

        # 1. 读取原文件
        steps.append(f"Reading file: {file_path}")
        original_code = context.tools["read_file"](file_path)

        if "Error" in original_code:
            return {
                "success": False,
                "message": original_code,
                "data": None,
                "steps": steps
            }

        # 2. 分析代码问题
        steps.append("Analyzing code issues...")
        issues = self._analyze_code(original_code, focus)

        # 3. 应用重构
        steps.append(f"Applying refactoring (focus: {focus})...")
        refactored_code = self._refactor(original_code, issues, focus)

        # 4. 备份原文件
        backup_path = f"{file_path}.bak"
        steps.append(f"Creating backup: {backup_path}")
        context.tools["write_file"](backup_path, original_code)

        # 5. 写入重构后的代码
        steps.append(f"Writing refactored code to: {file_path}")
        write_result = context.tools["write_file"](file_path, refactored_code)

        return {
            "success": "Error" not in write_result,
            "message": f"Code refactored successfully. Backup at: {backup_path}",
            "data": {
                "original_lines": len(original_code.split('\n')),
                "refactored_lines": len(refactored_code.split('\n')),
                "issues_found": len(issues),
                "backup_path": backup_path
            },
            "steps": steps
        }

    def _analyze_code(self, code: str, focus: str) -> list:
        """分析代码问题"""
        issues = []

        # 检查命名
        if focus in ["general", "naming"]:
            # 查找单字符变量名（排除循环变量）
            single_char_vars = re.findall(r'\b[a-z]\s*=', code)
            if single_char_vars:
                issues.append("Found single-character variable names")

        # 检查函数长度
        if focus in ["general", "structure"]:
            lines = code.split('\n')
            if len(lines) > 200:
                issues.append("File is too long (>200 lines)")

        # 检查缺少文档字符串
        if focus in ["general", "documentation"]:
            if '"""' not in code and "'''" not in code:
                issues.append("Missing docstrings")

        return issues

    def _refactor(self, code: str, issues: list, focus: str) -> str:
        """应用重构"""
        refactored = code

        # 添加文档字符串（如果缺失）
        if "Missing docstrings" in issues:
            # 为函数添加简单的 docstring
            def_pattern = r'(def\s+\w+\([^)]*\):)\n(\s+)'
            refactored = re.sub(
                def_pattern,
                r'\1\n\2"""TODO: Add docstring"""\n\2',
                refactored
            )

        # 格式化（移除多余空行）
        lines = refactored.split('\n')
        cleaned_lines = []
        prev_empty = False

        for line in lines:
            is_empty = line.strip() == ''
            if is_empty and prev_empty:
                continue
            cleaned_lines.append(line)
            prev_empty = is_empty

        return '\n'.join(cleaned_lines)


class AddTestsSkill(Skill):
    """添加单元测试技能"""

    def __init__(self):
        super().__init__(
            name="add_tests",
            description="为指定文件生成单元测试",
            category="code",
            required_tools=["read_file", "write_file"],
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要测试的文件路径"
                    },
                    "test_framework": {
                        "type": "string",
                        "description": "测试框架（pytest, unittest）",
                        "default": "pytest"
                    }
                },
                "required": ["file_path"]
            }
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        file_path: str,
        test_framework: str = "pytest",
        **kwargs
    ) -> Dict[str, Any]:
        """生成测试文件"""
        steps = []

        # 1. 读取源文件
        steps.append(f"Reading source file: {file_path}")
        source_code = context.tools["read_file"](file_path)

        if "Error" in source_code:
            return {
                "success": False,
                "message": source_code,
                "data": None,
                "steps": steps
            }

        # 2. 分析函数
        steps.append("Analyzing functions...")
        functions = self._extract_functions(source_code)

        # 3. 生成测试代码
        steps.append(f"Generating tests using {test_framework}...")
        test_code = self._generate_test_code(
            file_path, functions, test_framework
        )

        # 4. 确定测试文件路径
        test_file = self._get_test_file_path(file_path)
        steps.append(f"Writing test file: {test_file}")

        # 5. 写入测试文件
        write_result = context.tools["write_file"](test_file, test_code)

        return {
            "success": "Error" not in write_result,
            "message": f"Test file created: {test_file}",
            "data": {
                "test_file": test_file,
                "functions_tested": len(functions),
                "test_framework": test_framework
            },
            "steps": steps
        }

    def _extract_functions(self, code: str) -> list:
        """提取函数定义"""
        pattern = r'def\s+(\w+)\s*\([^)]*\):'
        return re.findall(pattern, code)

    def _get_test_file_path(self, file_path: str) -> str:
        """获取测试文件路径"""
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)

        # tests/test_<name>.py
        tests_dir = os.path.join(dir_name, "tests")
        return os.path.join(tests_dir, f"test_{name}{ext}")

    def _generate_test_code(
        self, file_path: str, functions: list, framework: str
    ) -> str:
        """生成测试代码"""
        module_name = os.path.splitext(os.path.basename(file_path))[0]

        if framework == "pytest":
            code = f"""\"\"\"Tests for {module_name}\"\"\"

import pytest
from {module_name} import *


"""
            for func in functions:
                code += f"""def test_{func}():
    \"\"\"Test {func} function\"\"\"
    # TODO: Implement test
    pass


"""
        else:  # unittest
            code = f"""\"\"\"Tests for {module_name}\"\"\"

import unittest
from {module_name} import *


class Test{module_name.title()}(unittest.TestCase):
"""
            for func in functions:
                code += f"""
    def test_{func}(self):
        \"\"\"Test {func} function\"\"\"
        # TODO: Implement test
        pass
"""
            code += """

if __name__ == '__main__':
    unittest.main()
"""

        return code


class GenerateDocSkill(Skill):
    """生成文档技能"""

    def __init__(self):
        super().__init__(
            name="generate_doc",
            description="为项目生成文档",
            category="code",
            required_tools=["read_file", "write_file", "list_directory"],
            parameters={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "项目目录",
                        "default": "."
                    },
                    "doc_type": {
                        "type": "string",
                        "description": "文档类型（api, readme, guide）",
                        "default": "readme"
                    }
                }
            }
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        project_dir: str = ".",
        doc_type: str = "readme",
        **kwargs
    ) -> Dict[str, Any]:
        """生成文档"""
        steps = []

        # 1. 扫描项目结构
        steps.append(f"Scanning project: {project_dir}")
        files = context.tools["list_directory"](project_dir)

        # 2. 生成文档内容
        steps.append(f"Generating {doc_type} documentation...")
        doc_content = self._generate_doc_content(project_dir, files, doc_type)

        # 3. 写入文档
        doc_file = os.path.join(project_dir, f"{doc_type.upper()}.md")
        steps.append(f"Writing documentation: {doc_file}")
        write_result = context.tools["write_file"](doc_file, doc_content)

        return {
            "success": "Error" not in write_result,
            "message": f"Documentation generated: {doc_file}",
            "data": {
                "doc_file": doc_file,
                "doc_type": doc_type,
                "files_analyzed": len(files.split('\n'))
            },
            "steps": steps
        }

    def _generate_doc_content(
        self, project_dir: str, files: str, doc_type: str
    ) -> str:
        """生成文档内容"""
        if doc_type == "readme":
            return f"""# {os.path.basename(project_dir)}

## Overview

TODO: Add project description

## Installation

```bash
pip install -r requirements.txt
```

## Usage

TODO: Add usage examples

## Project Structure

```
{files}
```

## Contributing

TODO: Add contributing guidelines

## License

TODO: Add license information
"""

        return f"# {doc_type.upper()} Documentation\n\nTODO: Generate {doc_type} documentation"


class CodeReviewSkill(Skill):
    """代码审查技能"""

    def __init__(self):
        super().__init__(
            name="code_review",
            description="审查代码质量并提供改进建议",
            category="code",
            required_tools=["read_file"],
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要审查的文件路径"
                    }
                },
                "required": ["file_path"]
            }
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        file_path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """执行代码审查"""
        steps = []

        # 1. 读取文件
        steps.append(f"Reading file: {file_path}")
        code = context.tools["read_file"](file_path)

        if "Error" in code:
            return {
                "success": False,
                "message": code,
                "data": None,
                "steps": steps
            }

        # 2. 分析代码
        steps.append("Analyzing code quality...")
        issues = self._review_code(code)

        # 3. 生成报告
        steps.append("Generating review report...")
        report = self._generate_report(file_path, code, issues)

        return {
            "success": True,
            "message": f"Code review completed: {len(issues)} issues found",
            "data": {
                "file": file_path,
                "issues": issues,
                "report": report
            },
            "steps": steps
        }

    def _review_code(self, code: str) -> list:
        """审查代码"""
        issues = []

        # 检查代码长度
        lines = code.split('\n')
        if len(lines) > 300:
            issues.append({
                "severity": "warning",
                "message": "File is very long (>300 lines), consider splitting"
            })

        # 检查文档
        if '"""' not in code:
            issues.append({
                "severity": "warning",
                "message": "Missing docstrings"
            })

        # 检查异常处理
        if 'try' not in code and ('open(' in code or 'request' in code):
            issues.append({
                "severity": "error",
                "message": "Missing error handling for I/O operations"
            })

        # 检查类型注解
        if '->' not in code and 'def ' in code:
            issues.append({
                "severity": "info",
                "message": "Consider adding type hints"
            })

        return issues

    def _generate_report(self, file_path: str, code: str, issues: list) -> str:
        """生成审查报告"""
        report = f"# Code Review: {file_path}\n\n"
        report += f"## Summary\n\n"
        report += f"- Lines of code: {len(code.split('\n'))}\n"
        report += f"- Issues found: {len(issues)}\n\n"

        if issues:
            report += "## Issues\n\n"
            for i, issue in enumerate(issues, 1):
                report += f"{i}. **[{issue['severity'].upper()}]** {issue['message']}\n"
        else:
            report += "No issues found! 🎉\n"

        return report
