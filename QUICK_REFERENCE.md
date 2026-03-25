# 🚀 快速参考

## Agent 命令

### 基础命令

```bash
# 查看帮助
python -m aicode.cli_agent --help

# 执行单次任务
python -m aicode.cli_agent run "任务描述" --provider local

# 交互式会话（推荐）
python -m aicode.cli_agent interactive --provider local

# 列出所有工具
python -m aicode.cli_agent list-tools
```

### 记忆管理

```bash
# 查看记忆统计（注意是 stats 不是 stat）
python -m aicode.cli_agent memory-stats

# 保存到长期记忆
python -m aicode.cli_agent remember "key" "value" \
  --category user_preferences \
  --importance 9

# 搜索记忆
python -m aicode.cli_agent search "关键词"
python -m aicode.cli_agent search "关键词" --category patterns
```

### 模式选择

```bash
# 自动选择模式
python -m aicode.cli_agent run "任务" --provider local

# 指定 ReAct 模式（探索性任务）
python -m aicode.cli_agent run "任务" --mode react --provider local

# 指定 Plan-Execute 模式（结构化任务）
python -m aicode.cli_agent run "任务" --mode plan --provider local
```

---

## 代码生成命令

```bash
# 代码生成
python -m aicode generate "创建快速排序函数" --provider local

# 保存到文件
python -m aicode generate "创建 Web 爬虫" -o crawler.py --provider local

# 代码分析
python -m aicode analyze your_code.py --provider local

# 代码修改
python -m aicode modify old.py "添加错误处理" --provider local
```

---

## 模型选择

```bash
# 本地模型（免费）
--provider local

# Claude
--provider claude --model claude-sonnet-4-6

# OpenAI
--provider openai --model gpt-4

# Qwen
--provider qwen --model qwen-coder-plus
```

---

## 常见错误

### ❌ 错误命令

```bash
python -m aicode.cli_agent memory-stat   # 缺少 's'
```

### ✅ 正确命令

```bash
python -m aicode.cli_agent memory-stats  # 正确
```

---

## 环境配置

```bash
# .env 文件
LOCAL_MODEL_BASE_URL=http://localhost:1234/v1
LOCAL_MODEL_NAME=qwen3.5-9b

# 验证配置
python -m aicode info
```

---

## 实用技巧

### 1. 交互式会话中的特殊命令

```
You: memory     # 查看记忆统计
You: clear      # 清空短期记忆
You: exit       # 退出
```

### 2. 组合使用

```bash
# 先分析，再修改
python -m aicode analyze code.py --provider local
python -m aicode modify code.py "根据分析结果优化" --provider local
```

### 3. 记住常用配置

```bash
# 记住编码风格
python -m aicode.cli_agent remember "style" "PEP 8, 4 spaces" --category user_preferences --importance 9

# 记住项目结构
python -m aicode.cli_agent remember "project_structure" "FastAPI + PostgreSQL" --category codebase --importance 8
```

---

## 📚 完整文档

- [README.md](README.md) - 项目概览
- [USE_LOCAL_MODEL.md](USE_LOCAL_MODEL.md) - 本地模型快速上手
- [AGENT_TOOLS.md](AGENT_TOOLS.md) - 16 个工具详解
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) - 记忆系统完整说明
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排查

---

**快速开始**: `python -m aicode.cli_agent interactive --provider local` 🚀
