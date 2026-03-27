"""文件操作相关技能"""

import os
import time
from typing import Dict, Any
from .base import Skill, SkillExecutionContext


class ProjectSetupSkill(Skill):
    """项目初始化技能"""

    def __init__(self):
        super().__init__(
            name="project_setup",
            description="创建标准项目结构",
            category="file",
            required_tools=["write_file", "list_directory"],
            parameters={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目名称"
                    },
                    "project_type": {
                        "type": "string",
                        "description": "项目类型（python, node, general）",
                        "default": "python"
                    }
                },
                "required": ["project_name"]
            }
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        project_name: str,
        project_type: str = "python",
        **kwargs
    ) -> Dict[str, Any]:
        """创建项目结构"""
        steps = []
        created_files = []

        project_dir = os.path.join(context.working_dir, project_name)

        # 根据项目类型创建文件
        if project_type == "python":
            files_to_create = {
                "README.md": self._get_readme_template(project_name),
                ".gitignore": self._get_python_gitignore(),
                "requirements.txt": "# Add your dependencies here\n",
                f"{project_name}/__init__.py": f'"""{project_name} package"""',
                f"{project_name}/main.py": self._get_python_main(),
                "tests/__init__.py": "",
                "tests/test_main.py": self._get_test_template(project_name),
            }
        elif project_type == "node":
            files_to_create = {
                "README.md": self._get_readme_template(project_name),
                ".gitignore": self._get_node_gitignore(),
                "package.json": self._get_package_json(project_name),
                "src/index.js": "// Main entry point\n",
                "tests/index.test.js": "// Tests\n",
            }
        else:
            files_to_create = {
                "README.md": self._get_readme_template(project_name),
                ".gitignore": "# Add patterns to ignore\n",
            }

        # 创建文件
        for file_path, content in files_to_create.items():
            full_path = os.path.join(project_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            steps.append(f"Creating {file_path}")
            context.tools["write_file"](full_path, content)
            created_files.append(file_path)

        return {
            "success": True,
            "message": f"Project '{project_name}' created successfully",
            "data": {
                "project_dir": project_dir,
                "project_type": project_type,
                "files_created": created_files
            },
            "steps": steps
        }

    def _get_readme_template(self, project_name: str) -> str:
        return f"""# {project_name}

## Overview

TODO: Add project description

## Installation

```bash
# TODO: Add installation instructions
```

## Usage

```bash
# TODO: Add usage examples
```

## Development

```bash
# TODO: Add development instructions
```

## License

TODO: Add license
"""

    def _get_python_gitignore(self) -> str:
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""

    def _get_node_gitignore(self) -> str:
        return """# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build
dist/
build/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"""

    def _get_python_main(self) -> str:
        return '''"""Main entry point"""


def main():
    """Main function"""
    print("Hello, World!")


if __name__ == "__main__":
    main()
'''

    def _get_test_template(self, project_name: str) -> str:
        return f'''"""Tests for {project_name}"""

import pytest
from {project_name}.main import main


def test_main():
    """Test main function"""
    # TODO: Add actual test
    assert True
'''

    def _get_package_json(self, project_name: str) -> str:
        return f'''{{
  "name": "{project_name}",
  "version": "0.1.0",
  "description": "TODO: Add description",
  "main": "src/index.js",
  "scripts": {{
    "test": "jest",
    "start": "node src/index.js"
  }},
  "keywords": [],
  "author": "",
  "license": "MIT"
}}
'''


class BackupFilesSkill(Skill):
    """文件备份技能"""

    def __init__(self):
        super().__init__(
            name="backup_files",
            description="备份指定文件或目录",
            category="file",
            required_tools=["copy_file", "list_directory"],
            parameters={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "要备份的源路径"
                    },
                    "backup_dir": {
                        "type": "string",
                        "description": "备份目录",
                        "default": "backups"
                    }
                },
                "required": ["source"]
            }
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        source: str,
        backup_dir: str = "backups",
        **kwargs
    ) -> Dict[str, Any]:
        """执行备份"""
        steps = []

        # 1. 创建备份目录
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        full_backup_dir = os.path.join(
            context.working_dir,
            backup_dir,
            timestamp
        )
        os.makedirs(full_backup_dir, exist_ok=True)
        steps.append(f"Created backup directory: {full_backup_dir}")

        # 2. 备份文件
        backed_up_files = []

        if os.path.isfile(source):
            # 单个文件
            dest = os.path.join(full_backup_dir, os.path.basename(source))
            result = context.tools["copy_file"](source, dest)
            if "Error" not in result:
                backed_up_files.append(dest)
                steps.append(f"Backed up: {source}")
        elif os.path.isdir(source):
            # 目录
            for root, _, files in os.walk(source):
                for file in files:
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, source)
                    dest_file = os.path.join(full_backup_dir, rel_path)

                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    result = context.tools["copy_file"](src_file, dest_file)

                    if "Error" not in result:
                        backed_up_files.append(dest_file)

            steps.append(f"Backed up directory: {source}")

        return {
            "success": len(backed_up_files) > 0,
            "message": f"Backed up {len(backed_up_files)} files to {full_backup_dir}",
            "data": {
                "backup_dir": full_backup_dir,
                "files_backed_up": len(backed_up_files),
                "timestamp": timestamp
            },
            "steps": steps
        }


class CleanupSkill(Skill):
    """清理临时文件技能"""

    def __init__(self):
        super().__init__(
            name="cleanup",
            description="清理临时文件和缓存",
            category="file",
            required_tools=["delete_file", "list_directory"],
            parameters={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "要清理的目录",
                        "default": "."
                    },
                    "patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要删除的文件模式",
                        "default": ["*.pyc", "*.pyo", "__pycache__", "*.log"]
                    }
                }
            }
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        directory: str = ".",
        patterns: list = None,
        **kwargs
    ) -> Dict[str, Any]:
        """执行清理"""
        if patterns is None:
            patterns = ["*.pyc", "*.pyo", "__pycache__", "*.log", "*.tmp"]

        steps = []
        deleted_files = []

        # 遍历目录
        for root, dirs, files in os.walk(directory):
            # 删除匹配的目录
            for dir_name in dirs:
                if dir_name in patterns:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        import shutil
                        shutil.rmtree(dir_path)
                        deleted_files.append(dir_path)
                        steps.append(f"Deleted directory: {dir_path}")
                    except Exception as e:
                        steps.append(f"Failed to delete {dir_path}: {e}")

            # 删除匹配的文件
            for file_name in files:
                for pattern in patterns:
                    if pattern.startswith("*"):
                        ext = pattern[1:]
                        if file_name.endswith(ext):
                            file_path = os.path.join(root, file_name)
                            result = context.tools["delete_file"](file_path)
                            if "Error" not in result:
                                deleted_files.append(file_path)
                                steps.append(f"Deleted: {file_path}")

        return {
            "success": True,
            "message": f"Cleanup completed: {len(deleted_files)} items deleted",
            "data": {
                "directory": directory,
                "deleted_count": len(deleted_files),
                "patterns": patterns
            },
            "steps": steps
        }
