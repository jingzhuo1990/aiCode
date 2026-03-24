# 🛠️ Agent 工具系统

## ✅ 已修复的问题

原有的 `tools.py` 存在 lambda 函数在异步上下文中参数传递的问题，已经通过 `tools_enhanced.py` 完全修复。

## 📦 可用工具列表（共 16 个）

### 📁 文件操作工具 (8 个)

#### 1. read_file
- **功能**: 读取文件内容
- **参数**:
  - `path` (string, 必需): 文件路径
- **示例**:
```bash
python -m aicode.cli_agent run "读取 hello.py 的内容" --provider local
```

#### 2. write_file
- **功能**: 写入文件（自动创建目录）
- **参数**:
  - `path` (string, 必需): 文件路径
  - `content` (string, 必需): 要写入的内容
- **示例**:
```bash
python -m aicode.cli_agent run "创建 test.txt，内容是 hello world" --provider local
```

#### 3. append_file
- **功能**: 追加内容到文件末尾
- **参数**:
  - `path` (string, 必需): 文件路径
  - `content` (string, 必需): 要追加的内容
- **示例**:
```bash
python -m aicode.cli_agent run "在 log.txt 末尾添加一行新日志" --provider local
```

#### 4. list_directory
- **功能**: 列出目录内容
- **参数**:
  - `path` (string, 可选): 目录路径，默认当前目录
  - `pattern` (string, 可选): 文件匹配模式，默认 "*"
- **示例**:
```bash
python -m aicode.cli_agent run "列出所有 Python 文件" --provider local
```

#### 5. get_file_info
- **功能**: 获取文件详细信息（大小、类型、修改时间、行数等）
- **参数**:
  - `path` (string, 必需): 文件路径
- **示例**:
```bash
python -m aicode.cli_agent run "显示 setup.py 的详细信息" --provider local
```

#### 6. copy_file
- **功能**: 复制文件
- **参数**:
  - `source` (string, 必需): 源文件路径
  - `destination` (string, 必需): 目标文件路径
- **示例**:
```bash
python -m aicode.cli_agent run "复制 test.txt 到 backup.txt" --provider local
```

#### 7. move_file
- **功能**: 移动/重命名文件
- **参数**:
  - `source` (string, 必需): 源文件路径
  - `destination` (string, 必需): 目标文件路径
- **示例**:
```bash
python -m aicode.cli_agent run "将 old.txt 重命名为 new.txt" --provider local
```

#### 8. delete_file
- **功能**: 删除文件
- **参数**:
  - `path` (string, 必需): 文件路径
- **示例**:
```bash
python -m aicode.cli_agent run "删除 test.txt" --provider local
```

---

### 💻 命令执行工具 (2 个)

#### 9. run_command
- **功能**: 执行 shell 命令
- **参数**:
  - `command` (string, 必需): 要执行的命令
  - `timeout` (integer, 可选): 超时时间（秒），默认 30
- **示例**:
```bash
python -m aicode.cli_agent run "使用 ls 列出当前目录的所有 .py 文件" --provider local
```

#### 10. run_python
- **功能**: 执行 Python 代码
- **参数**:
  - `code` (string, 必需): Python 代码
- **示例**:
```bash
python -m aicode.cli_agent run "运行 Python 代码计算 1+2+3+...+100" --provider local
```

---

### 🔍 搜索工具 (2 个)

#### 11. search_in_file
- **功能**: 在单个文件中搜索文本
- **参数**:
  - `path` (string, 必需): 文件路径
  - `query` (string, 必需): 搜索关键词
  - `case_sensitive` (boolean, 可选): 是否区分大小写，默认 false
- **示例**:
```bash
python -m aicode.cli_agent run "在 setup.py 中搜索 'version' 关键词" --provider local
```

#### 12. search_files
- **功能**: 在多个文件中搜索文本
- **参数**:
  - `directory` (string, 必需): 搜索目录
  - `query` (string, 必需): 搜索关键词
  - `file_pattern` (string, 可选): 文件匹配模式，默认 "*.py"
- **示例**:
```bash
python -m aicode.cli_agent run "在 aicode 目录中搜索所有包含 'AIModel' 的文件" --provider local
```

---

### 🔧 Git 工具 (3 个)

#### 13. git_status
- **功能**: 获取 git 仓库状态
- **参数**: 无
- **示例**:
```bash
python -m aicode.cli_agent run "查看 git 状态" --provider local
```

#### 14. git_diff
- **功能**: 查看 git 差异
- **参数**:
  - `file_path` (string, 可选): 特定文件路径，默认显示所有变更
- **示例**:
```bash
python -m aicode.cli_agent run "查看 config.py 的 git diff" --provider local
```

#### 15. git_log
- **功能**: 查看 git 提交历史
- **参数**:
  - `count` (integer, 可选): 显示提交数量，默认 5
- **示例**:
```bash
python -m aicode.cli_agent run "显示最近 10 次提交记录" --provider local
```

---

## 🚀 使用方式

### 方式 1: 自然语言描述任务

Agent 会自动选择合适的工具：

```bash
python -m aicode.cli_agent run "你的任务描述" --provider local
```

示例：
```bash
# 文件操作
python -m aicode.cli_agent run "创建 data.json，内容是空的 JSON 对象" --provider local

# 多步骤任务
python -m aicode.cli_agent run "读取 test.txt，统计字数，然后将结果写入 count.txt" --provider local

# 代码分析
python -m aicode.cli_agent run "分析 hello.py 的代码结构" --provider local

# 搜索任务
python -m aicode.cli_agent run "找出所有包含 'async' 关键词的 Python 文件" --provider local
```

### 方式 2: 交互式会话

```bash
python -m aicode.cli_agent interactive --provider local
```

然后可以持续对话：
```
You: 创建一个 notes.txt 文件
Agent: [执行并反馈]
You: 在里面添加今天的日期
Agent: [读取、修改、保存]
You: 显示文件内容
Agent: [读取并显示]
```

### 方式 3: 查看可用工具

```bash
# 列出所有工具
python -m aicode.cli_agent list-tools

# 查看特定工具信息
python -m aicode.cli_agent list-tools --verbose
```

---

## 🎯 实战示例

### 示例 1: 项目文件管理

```bash
# 创建项目结构
python -m aicode.cli_agent run "创建以下文件：src/main.py, src/utils.py, tests/test_main.py" --provider local

# 复制配置文件模板
python -m aicode.cli_agent run "复制 config.example.py 到 config.py" --provider local

# 清理临时文件
python -m aicode.cli_agent run "删除所有 .pyc 文件" --provider local
```

### 示例 2: 代码分析和搜索

```bash
# 搜索特定函数
python -m aicode.cli_agent run "在 aicode 目录中找出所有定义了 'async def' 的文件" --provider local

# 分析代码行数
python -m aicode.cli_agent run "统计 aicode 目录下所有 Python 文件的总行数" --provider local

# 检查依赖
python -m aicode.cli_agent run "在所有 Python 文件中搜索 'import anthropic'" --provider local
```

### 示例 3: Git 工作流

```bash
# 检查状态
python -m aicode.cli_agent run "查看当前的 git 状态和最近的提交" --provider local

# 查看变更
python -m aicode.cli_agent run "显示所有已修改文件的 diff" --provider local

# 分析提交历史
python -m aicode.cli_agent run "显示最近 20 次提交，并总结变更内容" --provider local
```

### 示例 4: 自动化任务

```bash
# 日志分析
python -m aicode.cli_agent run "读取 app.log，找出所有 ERROR 行，并保存到 errors.txt" --provider local

# 代码格式化检查
python -m aicode.cli_agent run "运行 black --check . 命令，检查代码格式" --provider local

# 测试运行
python -m aicode.cli_agent run "运行 pytest 并将结果保存到 test_results.txt" --provider local
```

---

## 💡 技术细节

### 架构改进

- **原问题**: `tools.py` 使用 lambda 函数，在异步上下文中无法正确传递参数
- **解决方案**: `tools_enhanced.py` 使用直接函数引用
- **关键代码**:

```python
# ❌ 旧方式（有 bug）
Tool(
    name="read_file",
    func=lambda path: file_handler.read_file(path),  # Lambda 在 async 中有问题
    ...
)

# ✅ 新方式（已修复）
def read_file_sync(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

Tool(
    name="read_file",
    func=read_file_sync,  # 直接函数引用，参数传递正常
    ...
)
```

### 集成状态

- ✅ `tools_enhanced.py` 已创建并测试通过
- ✅ `unified_agent.py` 已更新使用新工具系统
- ✅ ReAct Agent 模式测试通过（读取、搜索、命令执行）
- ✅ Plan-Execute Agent 模式测试通过（文件创建）
- ✅ 所有 16 个工具均可正常使用

---

## 🎉 测试结果

### 测试 1: 文件写入 ✅
```bash
python -m aicode.cli_agent run "在当前目录创建一个test.txt文件,内容是hello world" --provider local
# 结果: 文件成功创建，内容正确
```

### 测试 2: 文件读取 ✅
```bash
python -m aicode.cli_agent run "读取test.txt文件的内容并告诉我里面有什么" --provider local
# 结果: 成功读取并返回 "hello world"
```

### 测试 3: 命令执行 ✅
```bash
python -m aicode.cli_agent run "使用ls命令列出当前目录的所有.py文件" --provider local
# 结果: 成功执行命令并返回文件列表（fib.py, fib_clean.py, hello.py, setup.py）
```

---

## 🚧 注意事项

1. **命令执行安全性**: `run_command` 工具可以执行任意 shell 命令，请谨慎使用
2. **文件操作**: 删除、移动操作不可逆，建议先备份重要文件
3. **超时设置**: 长时间运行的命令可能需要调整 timeout 参数
4. **Git 工具**: 需要在 git 仓库中使用 git 相关工具

---

## 📚 下一步

- ✅ 工具系统已修复
- ✅ 16 个实用工具已集成
- ✅ ReAct 和 Plan-Execute 模式均可用
- ✅ 本地模型完美支持

**开始使用**: `python -m aicode.cli_agent interactive --provider local`

享受强大的本地 AI Coding Agent！🚀
