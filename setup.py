"""安装脚本"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aicode",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI Coding Agent - 智能编码助手",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aicode",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.40.0",
        "openai>=1.58.0",
        "fastapi>=0.115.0",
        "uvicorn>=0.32.0",
        "pydantic>=2.10.0",
        "pydantic-settings>=2.6.0",
        "click>=8.1.7",
        "rich>=13.9.0",
        "python-dotenv>=1.0.0",
        "aiofiles>=24.1.0",
        "tiktoken>=0.8.0",
    ],
    entry_points={
        "console_scripts": [
            "aicode=aicode.cli:cli",
            "aicode-server=aicode.server:start_server",
        ],
    },
)
