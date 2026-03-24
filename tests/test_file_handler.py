"""文件处理器测试"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path

from aicode.agent.file_handler import FileHandler


@pytest.fixture
def temp_file():
    """创建临时文件"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("print('Hello, World!')\n")
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_read_file(temp_file):
    """测试读取文件"""
    handler = FileHandler()
    content = await handler.read_file(temp_file)
    assert "Hello, World!" in content


@pytest.mark.asyncio
async def test_write_file():
    """测试写入文件"""
    handler = FileHandler()
    temp_path = tempfile.mktemp(suffix='.py')

    try:
        test_content = "# Test file\nprint('test')"
        await handler.write_file(temp_path, test_content)

        # 验证文件已创建
        assert os.path.exists(temp_path)

        # 验证内容正确
        content = await handler.read_file(temp_path)
        assert content == test_content
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_get_file_info(temp_file):
    """测试获取文件信息"""
    handler = FileHandler()
    info = handler.get_file_info(temp_file)

    assert info['path'] == temp_file
    assert info['extension'] == '.py'
    assert info['is_file'] is True
    assert info['size'] > 0


def test_analyze_code_structure():
    """测试分析代码结构"""
    handler = FileHandler()

    code = """
# This is a comment
import os
from pathlib import Path

class MyClass:
    pass

def my_function():
    pass
"""

    result = handler.analyze_code_structure(code, '.py')

    assert result['total_lines'] > 0
    assert len(result['imports']) == 2
    assert 'MyClass' in result['classes']
    assert 'my_function' in result['functions']


if __name__ == "__main__":
    pytest.main([__file__])
