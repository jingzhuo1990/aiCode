# ⚡ Qwen 快速开始（1 分钟配置）

## 第 1 步：添加 API Key

```bash
# 编辑配置文件
nano .env

# 添加这一行（把 your-key 换成你的实际 API Key）
QWEN_API_KEY=sk-your-qwen-api-key-here
```

## 第 2 步：验证配置

```bash
python -m aicode info
# 应该看到 "Qwen API Key: 已设置 ✓"
```

## 第 3 步：立即使用！

### 🎯 最简单的使用方式

```bash
# 1. 代码生成（推荐用 qwen-coder-plus）
python -m aicode generate "创建一个快速排序函数" \
  --provider qwen --model qwen-coder-plus

# 2. 代码分析
python -m aicode analyze your_file.py --provider qwen

# 3. Agent 模式（最强大）
python -m aicode.cli_agent interactive \
  --provider qwen --model qwen-coder-plus
```

### 🚀 推荐模型

| 任务类型 | 推荐模型 | 命令示例 |
|---------|---------|---------|
| **代码生成** | `qwen-coder-plus` | `--provider qwen --model qwen-coder-plus` |
| **代码分析** | `qwen-coder-plus` | `--provider qwen --model qwen-coder-plus` |
| **快速原型** | `qwen-turbo` | `--provider qwen --model qwen-turbo` |
| **长文件** | `qwen-long` | `--provider qwen --model qwen-long` |

### 💡 设为默认（可选）

如果主要使用 Qwen，可以设为默认：

```bash
nano .env

# 修改这两行
DEFAULT_PROVIDER=qwen
DEFAULT_MODEL=qwen-coder-plus
```

然后就可以省略 `--provider` 参数：

```bash
# 直接使用，自动用 Qwen
python -m aicode generate "your task"
python -m aicode.cli_agent interactive
```

## ✨ 实际例子

```bash
# 例子 1: 生成一个 Web 服务器
python -m aicode generate "创建一个简单的 Flask Web 服务器" \
  --provider qwen --model qwen-coder-plus -o server.py

# 例子 2: 重构代码
python -m aicode modify old_code.py "添加类型注解和文档" \
  --provider qwen

# 例子 3: 使用 Agent 完成复杂任务
python -m aicode.cli_agent run \
  "创建一个用户管理系统，包含增删改查功能" \
  --provider qwen --model qwen-coder-plus
```

## 🎓 更多信息

- 详细文档：`QWEN_GUIDE.md`
- 通用指南：`START_HERE.md`
- 获取 API Key: https://dashscope.console.aliyun.com/

---

**就这么简单！开始使用 Qwen 吧！** 🚀
