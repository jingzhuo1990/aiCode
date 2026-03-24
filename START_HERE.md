# 🚀 项目启动指南

## 第一步：安装依赖

```bash
cd /Users/jingzhuo/PycharmProjects/aiCode

# 激活虚拟环境
source .venv/bin/activate

# 安装所有依赖
pip install -r requirements.txt
```

## 第二步：配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器
```

在 `.env` 文件中至少配置一个 API key：

```env
# 推荐使用 Claude
ANTHROPIC_API_KEY=sk-ant-xxxxx

# 或者使用 OpenAI
OPENAI_API_KEY=sk-xxxxx
```

## 第三步：验证安装

```bash
# 查看配置信息
python -m aicode info

# 应该看到 API Key 状态为 "已设置 ✓"
```

## 第四步：尝试基础功能

### 1. 代码生成（简单模式）

```bash
# 生成一个简单的函数
python -m aicode generate "创建一个 Python 函数来计算两个数的最大公约数"

# 保存到文件
python -m aicode generate "创建一个快速排序算法" -o quicksort.py
```

### 2. 代码分析

```bash
# 先创建一个测试文件
echo 'def add(a, b):
    return a + b' > test.py

# 分析这个文件
python -m aicode analyze test.py
```

### 3. 代码修改

```bash
# 修改刚才创建的文件
python -m aicode modify test.py "添加类型注解和文档字符串" --dry-run

# 如果预览效果好，去掉 --dry-run 真正修改
python -m aicode modify test.py "添加类型注解和文档字符串"
```

## 第五步：尝试 Agent 模式（高级功能）

### 1. ReAct Agent - 自动探索和执行

```bash
# 使用 Agent 执行复杂任务
python -m aicode.cli_agent run "分析当前目录的 Python 文件，找出所有函数定义" --mode react

# 或者让 Agent 自动选择模式
python -m aicode.cli_agent run "创建一个新文件 calculator.py，包含加减乘除四个函数"
```

### 2. Plan-Execute Agent - 规划式执行

```bash
# 使用规划模式
python -m aicode.cli_agent run "重构 test.py 文件，使其更加专业" --mode plan
```

### 3. 交互式会话

```bash
# 启动交互式 Agent
python -m aicode.cli_agent interactive

# 然后可以持续对话：
# You: 帮我创建一个用户管理类
# You: 再添加一个验证邮箱的方法
# You: memory  (查看记忆统计)
# You: exit    (退出)
```

## 第六步：启动 API 服务器

```bash
# 启动服务器
./run_server.sh

# 或者直接运行
python -m aicode.server
```

访问 http://localhost:8000/docs 查看 API 文档

## 快速测试命令集合

```bash
# ===== 基础功能测试 =====

# 1. 生成代码
python -m aicode generate "创建一个二分查找函数" -o binary_search.py

# 2. 查看配置
python -m aicode info

# 3. 分析代码
python -m aicode analyze binary_search.py

# 4. 重构代码
python -m aicode refactor binary_search.py --type readability


# ===== Agent 模式测试 =====

# 5. 使用 ReAct Agent
python -m aicode.cli_agent run "创建一个 todo.txt 文件并写入三个待办事项" --mode react

# 6. 使用 Plan-Execute Agent
python -m aicode.cli_agent run "分析 binary_search.py 并创建对应的测试文件" --mode plan

# 7. 查看可用工具
python -m aicode.cli_agent list-tools

# 8. 记忆管理
python -m aicode.cli_agent remember "default_language" "python" --category user_preferences
python -m aicode.cli_agent search "python" --category user_preferences
python -m aicode.cli_agent memory-stats


# ===== API 测试 =====

# 9. 启动 API 服务器（在新终端）
python -m aicode.server

# 10. 测试 API（在另一个终端）
curl http://localhost:8000/

curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "创建一个 Hello World 函数", "provider": "claude"}'
```

## 常见问题

### Q1: 提示 "未设置 API KEY"

**解决**:
```bash
# 检查 .env 文件是否存在
ls -la .env

# 确保 API key 已正确设置
cat .env | grep API_KEY

# 如果没有，重新配置
cp .env.example .env
nano .env
```

### Q2: 导入错误

**解决**:
```bash
# 重新安装依赖
pip install -r requirements.txt

# 或安装项目
pip install -e .
```

### Q3: Agent 模式找不到

**解决**:
```bash
# 确保新创建的文件都在
ls -la aicode/cli_agent.py
ls -la aicode/architectures/
ls -la aicode/memory/

# Agent 模式使用独立的命令
python -m aicode.cli_agent --help
```

### Q4: 记忆目录权限问题

**解决**:
```bash
# 创建记忆目录并设置权限
mkdir -p .aicode_memory
chmod 755 .aicode_memory
```

## 项目结构快速参考

```
aicode/
├── cli.py              # 基础 CLI (generate, modify, analyze)
├── cli_agent.py        # Agent CLI (react, plan-execute)
├── server.py           # API 服务器
├── agent/              # 代码生成、修改、文件处理
├── models/             # AI 模型集成 (Claude, OpenAI)
├── memory/             # 记忆系统 (短期、长期)
└── architectures/      # ReAct 和 Plan-Execute
```

## 下一步建议

1. **熟悉基础命令**: 先用简单的 `generate`、`modify` 命令
2. **尝试 Agent 模式**: 体验 ReAct 和 Plan-Execute 的强大功能
3. **使用交互式会话**: `python -m aicode.cli_agent interactive` 更自然
4. **启动 API 服务**: 集成到你的其他项目中
5. **查看文档**: 阅读 `QUICKSTART.md` 和 `ARCHITECTURE.md` 了解更多

## 获取帮助

```bash
# 查看所有命令
python -m aicode --help

# 查看 Agent 命令
python -m aicode.cli_agent --help

# 查看具体命令的帮助
python -m aicode generate --help
python -m aicode.cli_agent run --help
```

---

**准备好了吗？从第一步开始吧！** 🚀
