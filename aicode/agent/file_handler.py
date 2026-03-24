"""文件处理器"""

import os
import aiofiles
from pathlib import Path
from typing import Optional, List


class FileHandler:
    """处理文件读写操作"""

    @staticmethod
    async def read_file(file_path: str) -> str:
        """
        读取文件内容

        Args:
            file_path: 文件路径

        Returns:
            文件内容

        Raises:
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()

        return content

    @staticmethod
    async def write_file(file_path: str, content: str, create_dirs: bool = True) -> None:
        """
        写入文件

        Args:
            file_path: 文件路径
            content: 文件内容
            create_dirs: 如果目录不存在是否创建
        """
        if create_dirs:
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)

    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            包含文件信息的字典
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        stat = os.stat(file_path)
        path_obj = Path(file_path)

        return {
            "path": file_path,
            "name": path_obj.name,
            "extension": path_obj.suffix,
            "size": stat.st_size,
            "is_file": path_obj.is_file(),
            "is_dir": path_obj.is_dir(),
            "absolute_path": str(path_obj.absolute()),
        }

    @staticmethod
    def list_files(
        directory: str,
        pattern: Optional[str] = None,
        recursive: bool = False
    ) -> List[str]:
        """
        列出目录中的文件

        Args:
            directory: 目录路径
            pattern: 文件匹配模式（如 "*.py"）
            recursive: 是否递归搜索子目录

        Returns:
            文件路径列表
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"目录不存在: {directory}")

        path_obj = Path(directory)
        files = []

        if recursive:
            if pattern:
                files = [str(f) for f in path_obj.rglob(pattern) if f.is_file()]
            else:
                files = [str(f) for f in path_obj.rglob("*") if f.is_file()]
        else:
            if pattern:
                files = [str(f) for f in path_obj.glob(pattern) if f.is_file()]
            else:
                files = [str(f) for f in path_obj.glob("*") if f.is_file()]

        return files

    @staticmethod
    def analyze_code_structure(content: str, file_extension: str) -> dict:
        """
        简单分析代码结构

        Args:
            content: 文件内容
            file_extension: 文件扩展名

        Returns:
            代码结构信息
        """
        lines = content.split("\n")
        result = {
            "total_lines": len(lines),
            "non_empty_lines": len([l for l in lines if l.strip()]),
            "comment_lines": 0,
            "imports": [],
            "classes": [],
            "functions": [],
        }

        for line in lines:
            stripped = line.strip()

            if file_extension == ".py":
                if stripped.startswith("#"):
                    result["comment_lines"] += 1
                elif stripped.startswith("import ") or stripped.startswith("from "):
                    result["imports"].append(stripped)
                elif stripped.startswith("class "):
                    class_name = stripped.split("(")[0].replace("class ", "").strip(":")
                    result["classes"].append(class_name)
                elif stripped.startswith("def "):
                    func_name = stripped.split("(")[0].replace("def ", "")
                    result["functions"].append(func_name)

        return result
