# 快速开始指南

## 1. 安装和配置

### 安装依赖

```bash
# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\activate  # Windows

# 安装依赖包
pip install -r requirements.txt
```

### 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加你的 API keys
# 至少需要配置一个 AI 提供商的 API key
```

在 `.env` 文件中设置：

```env
# 使用 Claude (推荐)
ANTHROPIC_API_KEY=sk-ant-xxx...

# 或使用 OpenAI
OPENAI_API_KEY=sk-xxx...

# 可选：修改默认设置
DEFAULT_PROVIDER=claude
DEFAULT_MODEL=claude-sonnet-4-6
```

## 2. CLI 命令行使用

### 基础命令

```bash
# 查看帮助
python -m aicode --help

# 查看配置信息
python -m aicode info
```

### 代码生成

```bash
# 生成代码（输出到终端）
python -m aicode generate "创建一个 Python 函数来计算斐波那契数列"

# 生成代码并保存到文件
python -m aicode generate "创建一个快速排序算法" -o quicksort.py

# 指定编程语言
python -m aicode generate "创建一个 REST API 客户端" --language javascript

# 使用不同的 AI 模型
python -m aicode generate "创建一个二叉树类" --provider openai --model gpt-4
```

### 代码修改

```bash
# 修改现有文件
python -m aicode modify app.py "添加错误处理和日志记录"

# 预览修改（不实际修改文件）
python -m aicode modify app.py "添加类型注解" --dry-run

# 修改文件但不备份
python -m aicode modify app.py "重命名变量" --no-backup
```

### 代码分析

```bash
# 分析代码文件
python -m aicode analyze app.py

# 使用特定模型分析
python -m aicode analyze complex_code.py --provider claude --model claude-opus-4-6
```

### 代码重构

```bash
# 通用重构
python -m aicode refactor old_code.py

# 性能优化重构
python -m aicode refactor slow_code.py --type performance

# 可读性重构
python -m aicode refactor messy_code.py --type readability

# 安全性重构
python -m aicode refactor insecure_code.py --type security

# 简化代码
python -m aicode refactor complex_code.py --type simplify

# 保存到新文件
python -m aicode refactor app.py --type general -o app_refactored.py
```

## 3. API 服务使用

### 启动服务器

```bash
# 启动 API 服务器
python -m aicode.server

# 或使用自定义端口
python -c "from aicode.server import start_server; start_server(port=9000)"
```

服务器将运行在 `http://localhost:8000`

### API 文档

启动服务器后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API 调用示例

#### 生成代码

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "创建一个 Python 函数来验证邮箱地址",
    "provider": "claude",
    "language": "python"
  }'
```

#### 修改代码

```bash
curl -X POST "http://localhost:8000/api/modify" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "app.py",
    "instruction": "添加类型注解",
    "provider": "claude",
    "backup": true
  }'
```

#### 分析代码

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
    "provider": "claude",
    "language": "python"
  }'
```

#### 重构代码

```bash
curl -X POST "http://localhost:8000/api/refactor" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def process(data):\n  result=[]\n  for i in data:\n    if i>0:\n      result.append(i*2)\n  return result",
    "refactor_type": "readability",
    "provider": "claude",
    "language": "python"
  }'
```

## 4. Python 代码集成

```python
import asyncio
from aicode.models.claude import ClaudeModel
from aicode.agent.code_generator import CodeGenerator

async def main():
    # 初始化模型
    model = ClaudeModel(
        api_key="your-api-key",
        model_name="claude-sonnet-4-6"
    )

    # 创建生成器
    generator = CodeGenerator(model)

    # 生成代码
    code = await generator.generate_code(
        prompt="创建一个计算器类",
        language="python"
    )

    print(code)

asyncio.run(main())
```

## 5. 常见问题

### API Key 未设置

```bash
错误: 未设置 ANTHROPIC_API_KEY
```

解决方法：在 `.env` 文件中配置相应的 API key

### 文件不存在

```bash
错误: 文件不存在: app.py
```

解决方法：确保文件路径正确，使用相对路径或绝对路径

### 模型不支持

```bash
错误: 不支持的提供商 'xxx'
```

解决方法：使用支持的提供商 `claude` 或 `openai`

## 6. 最佳实践

1. **先预览再修改**: 使用 `--dry-run` 标志预览修改
2. **保持备份**: 默认开启备份，重要文件修改前手动备份
3. **明确指令**: 提供清晰、具体的生成或修改指令
4. **选择合适的模型**:
   - 复杂任务使用 `claude-opus-4-6`
   - 一般任务使用 `claude-sonnet-4-6` (默认)
   - 简单任务使用 `claude-haiku-4-5`
5. **调整温度参数**:
   - 需要确定性输出时使用较低温度 (0.3-0.5)
   - 需要创意输出时使用较高温度 (0.7-0.9)

## 7. 下一步

- 查看 `examples/` 目录了解更多使用示例
- 阅读 `README.md` 了解完整功能
- 查看 API 文档了解所有可用端点
- 尝试集成到你的开发工作流中

祝你使用愉快！🚀
