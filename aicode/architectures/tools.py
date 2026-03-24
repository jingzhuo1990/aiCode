"""工具系统 - 为 ReAct Agent 提供工具"""

from typing import Callable, Dict, Any, List, Optional
from dataclasses import dataclass
import json


@dataclass
class Tool:
    """工具定义"""

    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any]  # JSON Schema 格式的参数定义

    def execute(self, **kwargs) -> Any:
        """执行工具"""
        return self.func(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于提示词）"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self.tools.get(name)

    def get_all_tools(self) -> List[Tool]:
        """获取所有工具"""
        return list(self.tools.values())

    def get_tools_description(self) -> str:
        """获取所有工具的描述（用于提示词）"""
        descriptions = ["Available tools:"]
        for tool in self.tools.values():
            descriptions.append(f"\n- {tool.name}: {tool.description}")
            descriptions.append(f"  Parameters: {json.dumps(tool.parameters, indent=2)}")
        return "\n".join(descriptions)

    def execute_tool(self, name: str, **kwargs) -> Any:
        """执行工具"""
        tool = self.get_tool(name)
        if tool is None:
            raise ValueError(f"Tool '{name}' not found")

        return tool.execute(**kwargs)


def create_default_tools(file_handler, code_generator, code_modifier) -> ToolRegistry:
    """创建默认工具集"""
    registry = ToolRegistry()

    # 读取文件工具
    read_file_tool = Tool(
        name="read_file",
        description="Read the contents of a file",
        func=lambda path: __import__('asyncio').run(file_handler.read_file(path)),
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["path"]
        }
    )
    registry.register(read_file_tool)

    # 写入文件工具
    write_file_tool = Tool(
        name="write_file",
        description="Write content to a file",
        func=lambda path, content: __import__('asyncio').run(
            file_handler.write_file(path, content)
        ),
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    )
    registry.register(write_file_tool)

    # 列出文件工具
    list_files_tool = Tool(
        name="list_files",
        description="List files in a directory",
        func=lambda directory, pattern=None, recursive=False: file_handler.list_files(
            directory, pattern, recursive
        ),
        parameters={
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path"},
                "pattern": {"type": "string", "description": "File pattern (e.g., '*.py')"},
                "recursive": {"type": "boolean", "description": "Search recursively"}
            },
            "required": ["directory"]
        }
    )
    registry.register(list_files_tool)

    # 分析代码结构工具
    analyze_structure_tool = Tool(
        name="analyze_code_structure",
        description="Analyze the structure of code (imports, classes, functions)",
        func=lambda path: __import__('asyncio').run(_analyze_code(file_handler, path)),
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the code file"}
            },
            "required": ["path"]
        }
    )
    registry.register(analyze_structure_tool)

    # 生成代码工具
    generate_code_tool = Tool(
        name="generate_code",
        description="Generate code based on a description",
        func=lambda prompt, language="python": __import__('asyncio').run(
            code_generator.generate_code(prompt, language)
        ),
        parameters={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Description of the code to generate"},
                "language": {"type": "string", "description": "Programming language"}
            },
            "required": ["prompt"]
        }
    )
    registry.register(generate_code_tool)

    # 修改代码工具
    modify_code_tool = Tool(
        name="modify_code",
        description="Modify existing code based on instructions",
        func=lambda path, instruction: __import__('asyncio').run(
            _modify_code_file(file_handler, code_modifier, path, instruction)
        ),
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to modify"},
                "instruction": {"type": "string", "description": "Modification instructions"}
            },
            "required": ["path", "instruction"]
        }
    )
    registry.register(modify_code_tool)

    # 搜索代码工具
    search_code_tool = Tool(
        name="search_code",
        description="Search for patterns in code files",
        func=lambda directory, query, file_pattern="*.py": _search_in_files(
            file_handler, directory, query, file_pattern
        ),
        parameters={
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory to search"},
                "query": {"type": "string", "description": "Search query"},
                "file_pattern": {"type": "string", "description": "File pattern to search"}
            },
            "required": ["directory", "query"]
        }
    )
    registry.register(search_code_tool)

    return registry


# 辅助函数
async def _analyze_code(file_handler, path: str) -> Dict[str, Any]:
    """分析代码结构"""
    content = await file_handler.read_file(path)
    file_info = file_handler.get_file_info(path)
    structure = file_handler.analyze_code_structure(content, file_info["extension"])
    return structure


async def _modify_code_file(file_handler, code_modifier, path: str, instruction: str) -> Dict[str, Any]:
    """修改代码文件"""
    result = await code_modifier.modify_file(path, instruction, backup=True, dry_run=False)
    return result


def _search_in_files(file_handler, directory: str, query: str, file_pattern: str) -> List[Dict[str, Any]]:
    """在文件中搜索"""
    files = file_handler.list_files(directory, pattern=file_pattern, recursive=True)
    results = []

    for filepath in files[:20]:  # 限制搜索文件数量
        try:
            import asyncio
            content = asyncio.run(file_handler.read_file(filepath))
            if query.lower() in content.lower():
                lines = content.split('\n')
                matching_lines = [
                    {"line_num": i + 1, "content": line}
                    for i, line in enumerate(lines)
                    if query.lower() in line.lower()
                ][:5]  # 每个文件最多5行
                results.append({
                    "file": filepath,
                    "matches": matching_lines
                })
        except Exception:
            continue

    return results[:10]  # 最多返回10个文件的结果
