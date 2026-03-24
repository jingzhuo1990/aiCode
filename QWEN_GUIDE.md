# 🚀 Qwen (通义千问) 使用指南

## 快速配置

### 1. 获取 API Key

如果你还没有 Qwen API Key：
1. 访问阿里云通义千问控制台: https://dashscope.console.aliyun.com/
2. 创建 API Key
3. 复制你的 API Key (格式: `sk-xxxxx`)

### 2. 配置到项目

```bash
# 编辑 .env 文件
nano .env

# 添加你的 Qwen API Key
QWEN_API_KEY=sk-your-qwen-api-key-here

# 设置 Qwen 为默认提供商（可选）
DEFAULT_PROVIDER=qwen
DEFAULT_MODEL=qwen-coder-plus
```

## 可用的 Qwen 模型

### 通用模型

| 模型名称 | 说明 | 适用场景 |
|---------|------|---------|
| `qwen-max` | 最强大的模型 | 复杂推理、深度分析 |
| `qwen-plus` | 性能均衡 | 日常任务、通用场景 |
| `qwen-turbo` | 快速响应 | 简单任务、快速迭代 |
| `qwen-long` | 长文本模型 | 大文件分析、长代码 |

### 代码专用模型 ⭐ 推荐

| 模型名称 | 说明 | 适用场景 |
|---------|------|---------|
| `qwen-coder-plus` ⭐ | 代码优化版（推荐） | 代码生成、重构、分析 |
| `qwen-coder-turbo` | 代码快速版 | 简单代码生成 |

**建议**：对于编程任务，使用 `qwen-coder-plus` 获得最佳效果！

## 使用示例

### 基础 CLI 使用

```bash
# 1. 使用默认配置（如果在 .env 中设置了 DEFAULT_PROVIDER=qwen）
python -m aicode generate "创建一个快速排序算法"

# 2. 明确指定使用 Qwen
python -m aicode generate "创建一个快速排序算法" --provider qwen

# 3. 使用特定的 Qwen 模型
python -m aicode generate "创建一个二叉树类" --provider qwen --model qwen-coder-plus

# 4. 代码修改
python -m aicode modify app.py "添加错误处理" --provider qwen --model qwen-coder-plus

# 5. 代码分析
python -m aicode analyze complex_code.py --provider qwen

# 6. 代码重构
python -m aicode refactor old_code.py --type performance --provider qwen
```

### Agent 模式使用

```bash
# 1. ReAct Agent
python -m aicode.cli_agent run "分析当前目录的 Python 文件，找出所有函数" \
  --provider qwen --model qwen-coder-plus

# 2. Plan-Execute Agent
python -m aicode.cli_agent run "创建一个完整的用户管理系统" \
  --mode plan --provider qwen --model qwen-coder-plus

# 3. 交互式会话
python -m aicode.cli_agent interactive --provider qwen --model qwen-coder-plus

# 4. 自动模式（让 Agent 自动选择 ReAct 或 Plan）
python -m aicode.cli_agent run "重构这个项目的所有 Python 文件" \
  --mode auto --provider qwen
```

### Python 代码集成

```python
import asyncio
from aicode.models.qwen import QwenModel
from aicode.agent.code_generator import CodeGenerator

async def main():
    # 初始化 Qwen 模型
    model = QwenModel(
        api_key="your-qwen-api-key",
        model_name="qwen-coder-plus"  # 推荐用于编程
    )

    # 创建代码生成器
    generator = CodeGenerator(model)

    # 生成代码
    code = await generator.generate_code(
        prompt="创建一个 Python 装饰器用于计时函数执行时间",
        language="python"
    )

    print(code)

asyncio.run(main())
```

### API 服务器使用

```bash
# 启动服务器
python -m aicode.server

# 使用 Qwen 生成代码
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "创建一个单例模式的实现",
    "provider": "qwen",
    "model": "qwen-coder-plus",
    "language": "python"
  }'

# 使用 Qwen 分析代码
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
    "provider": "qwen",
    "model": "qwen-coder-plus",
    "language": "python"
  }'
```

## 模型选择建议

### 对于代码生成任务

```bash
# 复杂算法、架构设计 → qwen-coder-plus
python -m aicode generate "实现一个 LRU 缓存" \
  --provider qwen --model qwen-coder-plus

# 简单函数、工具脚本 → qwen-coder-turbo
python -m aicode generate "写一个读取 CSV 的函数" \
  --provider qwen --model qwen-coder-turbo
```

### 对于代码分析任务

```bash
# 深度分析、重构建议 → qwen-coder-plus
python -m aicode analyze large_project.py \
  --provider qwen --model qwen-coder-plus

# 快速检查、简单分析 → qwen-plus
python -m aicode analyze simple.py \
  --provider qwen --model qwen-plus
```

### 对于 Agent 任务

```bash
# 复杂多步骤任务 → qwen-coder-plus
python -m aicode.cli_agent run "构建一个完整的 REST API" \
  --mode plan --provider qwen --model qwen-coder-plus

# 探索性任务 → qwen-plus
python -m aicode.cli_agent run "分析项目结构" \
  --mode react --provider qwen --model qwen-plus
```

## Qwen 的优势

### ✅ 中文支持更好
```bash
# Qwen 对中文理解更准确
python -m aicode generate "创建一个处理中文文本的分词器" --provider qwen
```

### ✅ 代码专用模型
```bash
# qwen-coder-plus 专门针对编程任务优化
python -m aicode generate "实现红黑树的插入和删除" \
  --provider qwen --model qwen-coder-plus
```

### ✅ 性价比高
- Qwen 的定价通常比国际模型更优惠
- 适合大量代码生成需求

### ✅ 国内访问稳定
- 服务器在国内，延迟更低
- 不需要特殊网络配置

## 性能对比

| 任务类型 | Claude | OpenAI | Qwen | 推荐 |
|---------|--------|--------|------|------|
| 复杂算法 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Claude/OpenAI |
| 日常编程 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Qwen Coder |
| 中文代码 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Qwen |
| 长文本 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Claude/Qwen Long |
| 响应速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Qwen Turbo |
| 性价比 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Qwen |

## 完整配置示例

### .env 文件配置

```env
# 配置所有模型（可选）
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
QWEN_API_KEY=sk-xxxxx

# 使用 Qwen 作为默认
DEFAULT_PROVIDER=qwen
DEFAULT_MODEL=qwen-coder-plus

# 其他配置
MAX_TOKENS=8000
TEMPERATURE=0.7
```

### 混合使用策略

```bash
# 策略：根据任务特点选择最佳模型

# 1. 复杂架构设计 → Claude
python -m aicode.cli_agent run "设计一个微服务架构" \
  --provider claude --model claude-opus-4-6

# 2. 日常代码生成 → Qwen Coder
python -m aicode generate "创建一个数据库连接池" \
  --provider qwen --model qwen-coder-plus

# 3. 快速原型 → Qwen Turbo
python -m aicode generate "写一个简单的 HTTP 服务器" \
  --provider qwen --model qwen-turbo

# 4. 长文件分析 → Qwen Long
python -m aicode analyze very_long_file.py \
  --provider qwen --model qwen-long
```

## 常见问题

### Q1: Qwen API Key 在哪里获取？

访问: https://dashscope.console.aliyun.com/apiKey

### Q2: 是否支持其他阿里云模型？

当前支持通义千问系列。如需其他模型，可以参考 `qwen.py` 自行扩展。

### Q3: Qwen 和 Claude/OpenAI 哪个更好？

- **Qwen**: 中文更好、性价比高、国内稳定
- **Claude**: 推理能力强、代码质量高
- **OpenAI**: 生态完善、社区支持好

建议：根据任务和预算灵活选择！

### Q4: 可以同时配置多个模型吗？

可以！配置所有 API Key，使用时通过 `--provider` 参数切换。

## 下一步

1. **配置你的 Qwen API Key**: `nano .env`
2. **测试基础功能**: `python -m aicode info`
3. **尝试代码生成**: `python -m aicode generate "your task" --provider qwen`
4. **体验 Agent 模式**: `python -m aicode.cli_agent interactive --provider qwen`

---

**享受 Qwen 带来的强大编程体验！** 🚀
