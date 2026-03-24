# AI Coding Agent 架构文档

## 项目概述

AI Coding Agent 是一个基于大语言模型的智能编码助手，支持代码生成、修改、分析和重构等功能。项目采用模块化设计，支持多种 AI 模型，并提供 CLI 和 API 两种交互方式。

## 项目结构

```
aiCode/
├── aicode/                     # 主要代码目录
│   ├── __init__.py            # 包初始化
│   ├── __main__.py            # CLI 入口
│   ├── config.py              # 配置管理
│   ├── cli.py                 # 命令行接口
│   ├── server.py              # API 服务器
│   │
│   ├── models/                # AI 模型集成
│   │   ├── __init__.py
│   │   ├── base.py           # 模型基类
│   │   ├── claude.py         # Claude (Anthropic) 集成
│   │   └── openai.py         # OpenAI 集成
│   │
│   └── agent/                 # Agent 核心逻辑
│       ├── __init__.py
│       ├── code_generator.py  # 代码生成器
│       ├── code_modifier.py   # 代码修改器
│       └── file_handler.py    # 文件处理器
│
├── tests/                     # 测试文件
│   ├── __init__.py
│   └── test_file_handler.py
│
├── examples/                  # 使用示例
│   ├── example_usage.py      # Python 集成示例
│   └── api_examples.sh       # API 调用示例
│
├── .env.example              # 环境变量模板
├── .gitignore                # Git 忽略文件
├── requirements.txt          # 依赖包列表
├── setup.py                  # 安装脚本
├── README.md                 # 项目说明
├── QUICKSTART.md            # 快速开始指南
├── ARCHITECTURE.md          # 架构文档（本文件）
├── run_cli.sh               # CLI 启动脚本
└── run_server.sh            # 服务器启动脚本
```

## 核心模块

### 1. 配置管理 (config.py)

使用 Pydantic Settings 管理配置，支持从环境变量和 .env 文件读取配置。

**主要功能:**
- API keys 管理
- 默认模型配置
- 服务器配置
- 生成参数配置

### 2. 模型层 (models/)

#### 基类 (base.py)

定义了统一的 AI 模型接口:
- `generate()`: 单轮文本生成
- `chat()`: 多轮对话
- `get_model_info()`: 获取模型信息

#### Claude 集成 (claude.py)

集成 Anthropic 的 Claude 模型:
- 支持 Claude Opus 4.6, Sonnet 4.6, Haiku 4.5
- 使用 `AsyncAnthropic` 客户端
- 支持 system prompt
- 异步 API 调用

#### OpenAI 集成 (openai.py)

集成 OpenAI 的 GPT 模型:
- 支持 GPT-4, GPT-4-Turbo, GPT-3.5-Turbo
- 使用 `AsyncOpenAI` 客户端
- 兼容 OpenAI 消息格式
- 异步 API 调用

### 3. Agent 层 (agent/)

#### 文件处理器 (file_handler.py)

负责文件系统操作:
- 异步文件读写
- 文件信息获取
- 目录文件列表
- 代码结构分析

**主要方法:**
- `read_file()`: 读取文件
- `write_file()`: 写入文件
- `get_file_info()`: 获取文件信息
- `list_files()`: 列出文件
- `analyze_code_structure()`: 分析代码结构

#### 代码生成器 (code_generator.py)

使用 AI 模型生成代码:
- 通用代码生成
- 函数生成
- 类生成
- 代码解释

**主要方法:**
- `generate_code()`: 生成代码
- `generate_function()`: 生成函数
- `generate_class()`: 生成类
- `explain_code()`: 解释代码

**提示词工程:**
- 使用专业的 system prompt
- 强调代码质量和最佳实践
- 支持上下文信息
- 自动清理输出格式

#### 代码修改器 (code_modifier.py)

修改和重构现有代码:
- 代码修改
- 文件修改
- 代码重构
- 添加文档

**主要方法:**
- `modify_code()`: 修改代码
- `modify_file()`: 修改文件
- `refactor_code()`: 重构代码
- `add_documentation()`: 添加文档

**安全特性:**
- 支持备份原文件
- Dry-run 模式预览
- 保持代码风格一致
- 结构变化追踪

### 4. CLI 接口 (cli.py)

基于 Click 的命令行工具:
- 直观的命令结构
- Rich 库美化输出
- 进度指示器
- 彩色代码高亮

**命令列表:**
- `generate`: 生成代码
- `modify`: 修改代码
- `analyze`: 分析代码
- `refactor`: 重构代码
- `info`: 显示配置

### 5. API 服务器 (server.py)

基于 FastAPI 的 RESTful API:
- 自动 API 文档
- 类型验证
- CORS 支持
- 异步处理

**端点列表:**
- `GET /`: 健康检查
- `POST /api/generate`: 生成代码
- `POST /api/modify`: 修改代码
- `POST /api/analyze`: 分析代码
- `POST /api/refactor`: 重构代码
- `GET /api/config`: 获取配置
- `GET /api/models`: 列出模型

## 数据流

### 代码生成流程

```
用户输入
  ↓
CLI/API 接口
  ↓
CodeGenerator
  ↓
AI Model (Claude/OpenAI)
  ↓
清理和格式化
  ↓
返回结果
```

### 代码修改流程

```
用户输入 + 文件路径
  ↓
FileHandler 读取文件
  ↓
CodeModifier
  ↓
AI Model 生成修改
  ↓
FileHandler 写入文件 (可选备份)
  ↓
返回修改结果
```

## 设计原则

### 1. 模块化设计

- 每个模块职责单一
- 清晰的接口定义
- 低耦合高内聚

### 2. 异步优先

- 所有 I/O 操作异步化
- 提高并发性能
- 响应式设计

### 3. 可扩展性

- 支持新增 AI 模型
- 支持新增功能命令
- 插件化架构

### 4. 类型安全

- 使用 Pydantic 进行数据验证
- 类型注解
- 运行时类型检查

### 5. 用户友好

- 清晰的错误提示
- 进度反馈
- 美观的输出格式

## 技术栈

### 核心依赖

- **anthropic**: Claude API 客户端
- **openai**: OpenAI API 客户端
- **fastapi**: Web 框架
- **uvicorn**: ASGI 服务器
- **pydantic**: 数据验证
- **click**: CLI 框架
- **rich**: 终端美化
- **aiofiles**: 异步文件 I/O

### 开发依赖

- **pytest**: 测试框架
- **pytest-asyncio**: 异步测试支持

## 扩展指南

### 添加新的 AI 模型

1. 在 `aicode/models/` 创建新的模型文件
2. 继承 `AIModel` 基类
3. 实现必需的方法
4. 在 `__init__.py` 中导出
5. 更新 CLI 和 API 的模型选择逻辑

示例:

```python
# aicode/models/new_provider.py
from .base import AIModel

class NewProviderModel(AIModel):
    def __init__(self, api_key: str, model_name: str):
        super().__init__(api_key, model_name)
        # 初始化客户端

    async def generate(self, prompt, ...):
        # 实现生成逻辑
        pass

    async def chat(self, messages, ...):
        # 实现对话逻辑
        pass

    def get_model_info(self):
        return {"provider": "new_provider", ...}
```

### 添加新的 Agent 功能

1. 在 `aicode/agent/` 创建新的 agent 文件
2. 实现核心逻辑
3. 在 CLI 和 API 中添加对应的命令/端点

### 添加新的 CLI 命令

```python
@cli.command()
@click.argument('...')
@click.option('...')
def new_command(...):
    """命令描述"""
    async def run():
        # 实现逻辑
        pass
    asyncio.run(run())
```

### 添加新的 API 端点

```python
@app.post("/api/new-endpoint")
async def new_endpoint(request: NewRequest):
    """端点描述"""
    try:
        # 实现逻辑
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 安全考虑

1. **API Key 保护**: 从环境变量读取，不硬编码
2. **文件备份**: 默认备份，防止数据丢失
3. **路径验证**: 验证文件路径安全性
4. **错误处理**: 完善的异常捕获和提示
5. **权限控制**: API 可以添加认证中间件

## 性能优化

1. **异步 I/O**: 提高并发处理能力
2. **流式输出**: 可以实现流式代码生成
3. **缓存机制**: 可以添加结果缓存
4. **批处理**: 支持批量文件处理

## 未来规划

- [ ] 支持更多 AI 模型 (Gemini, Llama 等)
- [ ] 添加代码测试生成功能
- [ ] 添加代码审查功能
- [ ] 支持多文件联动修改
- [ ] 添加版本控制集成
- [ ] Web UI 界面
- [ ] VS Code / JetBrains 插件
- [ ] 代码质量检查集成
- [ ] 性能分析集成

## 贡献指南

欢迎贡献！请遵循以下步骤:

1. Fork 项目
2. 创建功能分支
3. 编写测试
4. 提交代码
5. 发起 Pull Request

## 许可证

MIT License
