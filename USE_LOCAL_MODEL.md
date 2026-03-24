# ⚡ 使用本地模型 - 超快速指南

## 🎯 30 秒配置

你的 LM Studio 已经运行了 Qwen3.5-9B，现在只需 3 步：

### 1️⃣ 配置文件
```bash
nano .env

# 添加这两行（必需！）
LOCAL_MODEL_BASE_URL=http://localhost:1234/v1
LOCAL_MODEL_NAME=qwen3.5-9b

# 注意：模型名称必须匹配 LM Studio 中显示的实际名称
# 常见名称：qwen3.5-9b, qwen/qwen3.5-9b, qwen/qwen3.5-9b@q4_k_m
```

### 2️⃣ 验证
```bash
python -m aicode info
# 看到 "Local Model: http://localhost:1234/v1 (qwen3.5-9b)" 就成功了
```

### 3️⃣ 立即使用
```bash
# 最简单的方式（自动使用 .env 中配置的模型名称）
python -m aicode generate "创建一个快速排序函数" --provider local

# Agent 模式（推荐）
python -m aicode.cli_agent run "创建一个快速排序函数" --provider local

# 交互式会话（最推荐）
python -m aicode.cli_agent interactive --provider local

# 如果需要指定不同的模型名称
python -m aicode.cli_agent run "任务" --provider local --model "qwen/qwen3.5-9b"
```

---

## 💡 为什么用本地模型？

- ✅ **完全免费** - 无 API 费用
- ✅ **完全隐私** - 代码不离开电脑
- ✅ **无限使用** - 不受限额
- ✅ **更快响应** - 无网络延迟

---

## 🚀 常用命令

```bash
# 代码生成
python -m aicode generate "你的需求" --provider local

# 代码修改
python -m aicode modify file.py "修改指令" --provider local

# 代码分析
python -m aicode analyze file.py --provider local

# Agent 模式（最强大）
python -m aicode.cli_agent run "你的任务" --provider local

# 交互式会话（最推荐）
python -m aicode.cli_agent interactive --provider local
```

---

## 🎁 设为默认（可选）

如果主要用本地模型，可以省略 `--provider local`：

```bash
nano .env

# 改这两行
DEFAULT_PROVIDER=local
DEFAULT_MODEL=qwen3.5-9b
```

然后直接：
```bash
python -m aicode generate "任务"
python -m aicode.cli_agent interactive
```

---

## 🆘 遇到问题？

### 连接失败
→ 确保 LM Studio 服务器在运行（点击 "Start Server"）

### 响应慢
→ 正常，本地 9B 模型需要一些时间

### 质量不够好
→ 尝试更具体的提示词，或用云端模型做复杂任务

---

**详细文档**: `LOCAL_MODEL_GUIDE.md`

**开始使用**: `python -m aicode.cli_agent interactive --provider local` 🚀
