"""增强的工具系统 - 修复 bug 并添加更多实用工具"""

from typing import Callable, Dict, Any, List, Optional
from dataclasses import dataclass
import json
import os
import subprocess
import glob as glob_module
import shutil


@dataclass
class Tool:
    """工具定义"""

    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any]

    def execute(self, **kwargs) -> Any:
        """执行工具"""
        return self.func(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
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
        """获取所有工具的描述"""
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


# === 文件操作工具 ===

def read_file_sync(path: str) -> str:
    """同步读取文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file_sync(path: str, content: str) -> str:
    """同步写入文件"""
    try:
        # 创建目录（如果不存在）
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def append_to_file(path: str, content: str) -> str:
    """追加内容到文件"""
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully appended to {path}"
    except Exception as e:
        return f"Error appending to file: {str(e)}"


def list_directory(path: str = ".", pattern: str = "*") -> str:
    """列出目录内容"""
    try:
        full_pattern = os.path.join(path, pattern)
        files = glob_module.glob(full_pattern)
        if not files:
            return f"No files found matching {pattern} in {path}"

        result = [f"Files in {path} matching {pattern}:"]
        for f in sorted(files)[:50]:  # 最多显示 50 个
            size = os.path.getsize(f) if os.path.isfile(f) else 0
            file_type = "DIR" if os.path.isdir(f) else "FILE"
            result.append(f"  [{file_type}] {f} ({size} bytes)")

        if len(files) > 50:
            result.append(f"  ... and {len(files) - 50} more files")

        return "\n".join(result)
    except Exception as e:
        return f"Error listing directory: {str(e)}"


def delete_file(path: str) -> str:
    """删除文件"""
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"Successfully deleted file: {path}"
        elif os.path.isdir(path):
            return f"Error: {path} is a directory. Use delete_directory instead."
        else:
            return f"Error: {path} does not exist"
    except Exception as e:
        return f"Error deleting file: {str(e)}"


def copy_file(source: str, destination: str) -> str:
    """复制文件"""
    try:
        shutil.copy2(source, destination)
        return f"Successfully copied {source} to {destination}"
    except Exception as e:
        return f"Error copying file: {str(e)}"


def move_file(source: str, destination: str) -> str:
    """移动文件"""
    try:
        shutil.move(source, destination)
        return f"Successfully moved {source} to {destination}"
    except Exception as e:
        return f"Error moving file: {str(e)}"


def get_file_info(path: str) -> str:
    """获取文件信息"""
    try:
        if not os.path.exists(path):
            return f"Error: {path} does not exist"

        stat = os.stat(path)
        info = [
            f"File: {path}",
            f"Size: {stat.st_size} bytes",
            f"Type: {'Directory' if os.path.isdir(path) else 'File'}",
            f"Modified: {stat.st_mtime}",
        ]

        if os.path.isfile(path):
            _, ext = os.path.splitext(path)
            info.append(f"Extension: {ext}")

            # 尝试读取行数（文本文件）
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                info.append(f"Lines: {lines}")
            except:
                pass

        return "\n".join(info)
    except Exception as e:
        return f"Error getting file info: {str(e)}"


# === 命令执行工具 ===

def run_command(command: str, timeout: int = 30) -> str:
    """执行 shell 命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        output.append(f"Exit code: {result.returncode}")

        return "\n".join(output) if output else "Command executed (no output)"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def run_python_code(code: str) -> str:
    """执行 Python 代码"""
    try:
        # 保存到临时文件并执行
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            ['python', temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        # 清理临时文件
        os.remove(temp_path)

        output = []
        if result.stdout:
            output.append(f"Output:\n{result.stdout}")
        if result.stderr:
            output.append(f"Errors:\n{result.stderr}")

        return "\n".join(output) if output else "Code executed successfully (no output)"
    except Exception as e:
        return f"Error executing Python code: {str(e)}"


# === 搜索工具 ===

def search_in_file(path: str, query: str, case_sensitive: bool = False) -> str:
    """在文件中搜索文本"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        query_to_search = query if case_sensitive else query.lower()
        matches = []

        for i, line in enumerate(lines, 1):
            line_to_search = line if case_sensitive else line.lower()
            if query_to_search in line_to_search:
                matches.append(f"  Line {i}: {line.rstrip()}")

        if not matches:
            return f"No matches found for '{query}' in {path}"

        result = [f"Found {len(matches)} matches for '{query}' in {path}:"]
        result.extend(matches[:20])  # 最多显示 20 个
        if len(matches) > 20:
            result.append(f"  ... and {len(matches) - 20} more matches")

        return "\n".join(result)
    except Exception as e:
        return f"Error searching file: {str(e)}"


def search_files(directory: str, query: str, file_pattern: str = "*.py") -> str:
    """在多个文件中搜索"""
    try:
        pattern = os.path.join(directory, "**", file_pattern)
        files = glob_module.glob(pattern, recursive=True)

        results = []
        for file_path in files[:50]:  # 最多搜索 50 个文件
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if query.lower() in content.lower():
                    results.append(file_path)
            except:
                continue

        if not results:
            return f"No files found containing '{query}'"

        output = [f"Found '{query}' in {len(results)} files:"]
        output.extend([f"  - {f}" for f in results[:20]])
        if len(results) > 20:
            output.append(f"  ... and {len(results) - 20} more files")

        return "\n".join(output)
    except Exception as e:
        return f"Error searching files: {str(e)}"


# === Git 工具 ===

def git_status() -> str:
    """获取 git 状态"""
    return run_command("git status")


def git_diff(file_path: str = "") -> str:
    """查看 git diff"""
    cmd = f"git diff {file_path}" if file_path else "git diff"
    return run_command(cmd)


def git_log(count: int = 5) -> str:
    """查看 git 日志"""
    return run_command(f"git log --oneline -n {count}")


# === 创建增强的工具注册表 ===

def create_enhanced_tools() -> ToolRegistry:
    """创建增强的工具集"""
    registry = ToolRegistry()

    # === 文件操作工具 ===

    registry.register(Tool(
        name="read_file",
        description="Read the contents of a file",
        func=read_file_sync,
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["path"]
        }
    ))

    registry.register(Tool(
        name="write_file",
        description="Write content to a file (creates directories if needed)",
        func=write_file_sync,
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    ))

    registry.register(Tool(
        name="append_file",
        description="Append content to an existing file",
        func=append_to_file,
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "Content to append"}
            },
            "required": ["path", "content"]
        }
    ))

    registry.register(Tool(
        name="list_directory",
        description="List files in a directory",
        func=list_directory,
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path", "default": "."},
                "pattern": {"type": "string", "description": "File pattern (e.g., '*.py')", "default": "*"}
            },
            "required": []
        }
    ))

    registry.register(Tool(
        name="get_file_info",
        description="Get detailed information about a file",
        func=get_file_info,
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"}
            },
            "required": ["path"]
        }
    ))

    registry.register(Tool(
        name="copy_file",
        description="Copy a file to a new location",
        func=copy_file,
        parameters={
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source file path"},
                "destination": {"type": "string", "description": "Destination file path"}
            },
            "required": ["source", "destination"]
        }
    ))

    registry.register(Tool(
        name="move_file",
        description="Move/rename a file",
        func=move_file,
        parameters={
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source file path"},
                "destination": {"type": "string", "description": "Destination file path"}
            },
            "required": ["source", "destination"]
        }
    ))

    registry.register(Tool(
        name="delete_file",
        description="Delete a file",
        func=delete_file,
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to delete"}
            },
            "required": ["path"]
        }
    ))

    # === 命令执行工具 ===

    registry.register(Tool(
        name="run_command",
        description="Execute a shell command",
        func=run_command,
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"},
                "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30}
            },
            "required": ["command"]
        }
    ))

    registry.register(Tool(
        name="run_python",
        description="Execute Python code",
        func=run_python_code,
        parameters={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"}
            },
            "required": ["code"]
        }
    ))

    # === 搜索工具 ===

    registry.register(Tool(
        name="search_in_file",
        description="Search for text in a file",
        func=search_in_file,
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "query": {"type": "string", "description": "Text to search for"},
                "case_sensitive": {"type": "boolean", "description": "Case sensitive search", "default": False}
            },
            "required": ["path", "query"]
        }
    ))

    registry.register(Tool(
        name="search_files",
        description="Search for text across multiple files",
        func=search_files,
        parameters={
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory to search in"},
                "query": {"type": "string", "description": "Text to search for"},
                "file_pattern": {"type": "string", "description": "File pattern", "default": "*.py"}
            },
            "required": ["directory", "query"]
        }
    ))

    # === Git 工具 ===

    registry.register(Tool(
        name="git_status",
        description="Get git repository status",
        func=git_status,
        parameters={"type": "object", "properties": {}, "required": []}
    ))

    registry.register(Tool(
        name="git_diff",
        description="Show git diff",
        func=git_diff,
        parameters={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Specific file to diff", "default": ""}
            },
            "required": []
        }
    ))

    registry.register(Tool(
        name="git_log",
        description="Show git commit history",
        func=git_log,
        parameters={
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "Number of commits to show", "default": 5}
            },
            "required": []
        }
    ))

    return registry
