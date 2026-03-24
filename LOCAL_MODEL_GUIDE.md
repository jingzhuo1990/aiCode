# 🏠 本地模型使用指南（LM Studio）

## ✅ 你的配置

- **模型**: Qwen3.5-9B
- **部署工具**: LM Studio
- **API 地址**: http://localhost:1234/v1 (LM Studio 默认)

## 🚀 快速配置（30 秒）

### 1. 确保 LM Studio 服务器运行中

在 LM Studio 中：
1. 加载你的 Qwen3.5-9B 模型
2. 点击 "Start Server" 按钮
3. 确认服务器运行在 `http://localhost:1234`

### 2. 配置项目

```bash
# 编辑配置文件
nano .env

# 添加这两行
LOCAL_MODEL_BASE_URL=http://localhost:1234/v1
LOCAL_MODEL_NAME=qwen3.5-9b

# 可选：设为默认模型
DEFAULT_PROVIDER=local
DEFAULT_MODEL=qwen3.5-9b
```

### 3. 立即使用！

```bash
# 方式 1：明确指定使用本地模型
python -m aicode generate "创建一个快速排序函数" --provider local

# 方式 2：如果设为默认，直接使用
python -m aicode generate "创建一个快速排序函数"

# 方式 3：Agent 模式
python -m aicode.cli_agent interactive --provider local
```

## 💻 完整使用示例

### 基础功能

```bash
# 1. 代码生成
python -m aicode generate "创建一个计算斐波那契数列的函数" \
  --provider local --model qwen3.5-9b

# 2. 保存到文件
python -m aicode generate "创建一个 Web 爬虫" \
  --provider local -o crawler.py

# 3. 代码分析
python -m aicode analyze your_code.py --provider local

# 4. 代码修改
python -m aicode modify old_code.py "添加错误处理" --provider local

# 5. 代码重构
python -m aicode refactor messy_code.py --type readability --provider local
```

### Agent 模式（推荐）

```bash
# 1. ReAct Agent - 自动推理和行动
python -m aicode.cli_agent run \
  "分析当前目录的所有 Python 文件" \
  --provider local --model qwen3.5-9b

# 2. Plan-Execute Agent - 规划式执行
python -m aicode.cli_agent run \
  "创建一个用户管理系统，包含增删改查" \
  --mode plan --provider local

# 3. 交互式会话（最推荐）
python -m aicode.cli_agent interactive --provider local

# 然后你可以持续对话：
# You: 帮我创建一个数据库连接类
# Agent: [生成代码]
# You: 添加一个重连机制
# Agent: [基于上下文继续工作]
```

## 🎯 验证配置

```bash
# 查看配置信息
python -m aicode info

# 应该看到：
# Local Model: http://localhost:1234/v1 (qwen3.5-9b)
```

## 🔧 高级配置

### 修改模型名称

```bash
# 在 .env 中
LOCAL_MODEL_NAME=qwen3.5-9b  # 或者 LM Studio 中显示的任何名称
```

### 修改端口（如果 LM Studio 使用不同端口）

```bash
# 在 .env 中
LOCAL_MODEL_BASE_URL=http://localhost:8080/v1  # 改为你的实际端口
```

### 使用命令行参数覆盖

虽然目前不支持命令行直接指定 base_url，但你可以修改配置文件或使用环境变量：

```bash
# 临时使用不同的地址
LOCAL_MODEL_BASE_URL=http://localhost:5000/v1 python -m aicode generate "test" --provider local
```

## 📊 性能建议

### Qwen3.5-9B 性能特点

- ✅ **中等大小**: 9B 参数，速度和质量平衡
- ✅ **适合日常编程**: 代码生成、分析、重构
- ✅ **响应较快**: 本地运行，无网络延迟
- ⚠️ **复杂任务**: 可能不如更大模型（如 70B+）

### 推荐使用场景

```bash
# ✅ 适合：日常代码生成
python -m aicode generate "创建一个排序函数" --provider local

# ✅ 适合：代码重构
python -m aicode refactor old_code.py --provider local

# ✅ 适合：快速原型
python -m aicode.cli_agent run "创建一个简单的 CLI 工具" --provider local

# ⚠️ 复杂任务：可能需要更强模型
# 对于非常复杂的架构设计，考虑使用云端大模型
python -m aicode.cli_agent run "设计微服务架构" --provider claude
```

## 🆚 对比其他方案

### 本地模型 vs 云端模型

| 特性 | 本地模型 (LM Studio) | 云端模型 (Claude/GPT) |
|-----|---------------------|---------------------|
| **成本** | ✅ 免费（仅硬件） | ⚠️ 按使用付费 |
| **速度** | ✅ 无网络延迟 | ⚠️ 受网络影响 |
| **隐私** | ✅ 完全本地 | ⚠️ 发送到云端 |
| **质量** | ⚠️ 取决于模型大小 | ✅ 通常更强 |
| **硬件要求** | ⚠️ 需要好的 GPU/CPU | ✅ 无要求 |

### 混合使用策略（推荐）

```bash
# 日常代码生成 → 本地模型（免费、快速）
python -m aicode generate "日常任务" --provider local

# 复杂架构设计 → Claude（质量更高）
python -m aicode.cli_agent run "复杂设计任务" --provider claude

# 快速原型 → 本地模型
python -m aicode generate "快速测试" --provider local

# 生产代码 → 云端模型（更可靠）
python -m aicode generate "生产代码" --provider qwen --model qwen-coder-plus
```

## 🐛 常见问题

### Q1: 提示连接错误

```
Error: Connection refused
```

**解决**:
1. 确保 LM Studio 服务器正在运行
2. 检查端口是否正确（默认 1234）
3. 在 LM Studio 中点击 "Start Server"

### Q2: 模型响应很慢

**原因**: 9B 模型需要一定的计算资源

**优化**:
- 确保有足够的 RAM（建议 16GB+）
- 使用 GPU 加速（如果可用）
- 在 LM Studio 中调整生成参数
- 减小 `max_tokens` 参数

### Q3: 生成质量不理想

**建议**:
```bash
# 1. 调整温度参数
python -m aicode generate "task" --provider local --temperature 0.3

# 2. 使用更具体的提示词
python -m aicode generate "创建一个使用递归的快速排序函数，包含详细注释" --provider local

# 3. 对于复杂任务，使用云端模型
python -m aicode generate "复杂任务" --provider qwen --model qwen-coder-plus
```

### Q4: 如何更换模型？

在 LM Studio 中：
1. 下载新模型（如 Qwen2-14B）
2. 加载新模型
3. 更新 `.env` 中的 `LOCAL_MODEL_NAME`
4. 重启你的命令

## 🎓 支持的其他本地工具

虽然当前针对 LM Studio 配置，但也支持其他工具：

### Ollama
```bash
# .env 配置
LOCAL_MODEL_BASE_URL=http://localhost:11434/v1
LOCAL_MODEL_NAME=qwen:7b
```

### vLLM
```bash
# .env 配置
LOCAL_MODEL_BASE_URL=http://localhost:8000/v1
LOCAL_MODEL_NAME=qwen3.5-9b
```

### Text Generation WebUI
```bash
# .env 配置
LOCAL_MODEL_BASE_URL=http://localhost:5000/v1
LOCAL_MODEL_NAME=qwen-9b
```

## 📚 下一步

1. ✅ **配置完成**: 编辑 `.env` 文件
2. ✅ **启动 LM Studio**: 确保服务器运行
3. ✅ **测试连接**: `python -m aicode info`
4. ✅ **开始使用**: `python -m aicode generate "test" --provider local`
5. ✅ **交互式体验**: `python -m aicode.cli_agent interactive --provider local`

## 💡 快速测试命令

```bash
# 确保 LM Studio 正在运行，然后：

# 测试 1：简单生成
python -m aicode generate "写一个 Hello World 函数" --provider local

# 测试 2：代码分析
echo "def add(a, b): return a + b" > test.py
python -m aicode analyze test.py --provider local

# 测试 3：Agent 模式
python -m aicode.cli_agent run \
  "创建一个 greet.py 文件，包含一个问候函数" \
  --provider local

# 测试 4：交互式（最推荐）
python -m aicode.cli_agent interactive --provider local
```

---

**享受完全免费、隐私安全的本地 AI 编程助手！** 🚀

## 🎁 额外福利

使用本地模型的优势：
- ✅ **完全免费** - 无 API 费用
- ✅ **完全隐私** - 代码不离开你的电脑
- ✅ **无限使用** - 不受 API 限额限制
- ✅ **离线工作** - 无需网络连接
- ✅ **响应快速** - 无网络延迟

现在开始使用吧！
