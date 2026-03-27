# 🤖 AI Code - Intelligent Coding Agent

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**一个强大的 AI 编程助手，支持多模型、多架构、本地部署**

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [文档](#-文档) • [示例](#-示例)

</div>

---

## ✨ 功能特性

### 🎯 核心能力

- **🤖 智能 Agent 系统**
  - 🔄 **ReAct 架构**: 推理 + 行动循环，适合探索性任务
  - 📋 **Plan-Execute 架构**: 规划 + 执行，适合结构化任务
  - 🧠 **Auto 模式**: 自动选择最佳架构

- **🛠️ 16+ 实用工具**
  - 📁 文件操作（读写、复制、移动、删除）
  - 💻 命令执行（shell、Python 代码）
  - 🔍 代码搜索（单文件、多文件）
  - 🔧 Git 集成（status、diff、log）

- **🎯 10+ 高级技能 (Skills)**
  - 🧑‍💻 代码重构、生成测试、代码审查
  - 📁 项目初始化、文件备份、清理
  - 🔀 智能提交、创建分支、PR 审查

- **💾 记忆系统**
  - 📝 短期记忆：会话上下文（自动管理）
  - 🗄️ 长期记忆：持久化存储（分类、标签、重要度）
  - 🔍 RAG 语义检索：FAISS + Sentence Transformers

- **🌐 多模型支持**
  - ☁️ **Claude** (Anthropic)
  - ☁️ **GPT** (OpenAI)
  - ☁️ **Qwen** (阿里云)
  - 🏠 **本地模型** (LM Studio / Ollama)

---

## 🚀 快速开始

### 1️⃣ 安装

\`\`\`bash
# 克隆仓库
git clone https://github.com/yourusername/aiCode.git
cd aiCode

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt
\`\`\`

### 2️⃣ 配置

\`\`\`bash
# 复制配置模板
cp .env.example .env

# 编辑配置（本地模型 - 推荐）
LOCAL_MODEL_BASE_URL=http://localhost:1234/v1
LOCAL_MODEL_NAME=qwen3.5-9b
\`\`\`

### 3️⃣ 使用

\`\`\`bash
# 交互式会话（推荐）
python -m aicode.cli_agent interactive --provider local

# 单次任务
python -m aicode.cli_agent run "分析当前目录的所有 Python 文件" --provider local

# 代码生成
python -m aicode generate "创建一个快速排序函数" --provider local
\`\`\`

---

## 📖 文档

- 📘 [本地模型快速上手](USE_LOCAL_MODEL.md) - 30 秒配置
- 📗 [本地模型详细指南](LOCAL_MODEL_GUIDE.md) - 完整文档
- 📙 [Agent 工具说明](AGENT_TOOLS.md) - 16 个工具详解
- 📕 [故障排查指南](TROUBLESHOOTING.md) - 问题解决

---

## 💡 示例

### 交互式会话

\`\`\`bash
python -m aicode.cli_agent interactive --provider local
\`\`\`

\`\`\`
You: 创建一个 data 文件夹并在里面创建 config.json
Agent: [执行任务]

You: 在 config.json 中添加数据库配置
Agent: [读取、修改、保存]

You: 列出 data 文件夹的所有文件
Agent: [列出文件]
\`\`\`

### Agent 任务执行

\`\`\`bash
# 自动选择架构
python -m aicode.cli_agent run "创建一个 FastAPI 项目结构" --provider local

# 代码分析
python -m aicode.cli_agent run "分析所有 Python 文件，找出未使用的导入" --provider local

# 自动化任务
python -m aicode.cli_agent run "读取 app.log，提取错误并保存到 errors.txt" --provider local
\`\`\`

---

## 🛠️ 可用工具（16 个）

### 📁 文件操作
`read_file` • `write_file` • `append_file` • `list_directory` • `get_file_info` • `copy_file` • `move_file` • `delete_file`

### 💻 命令执行
`run_command` • `run_python`

### 🔍 搜索
`search_in_file` • `search_files`

### 🔧 Git
`git_status` • `git_diff` • `git_log`

详见：[AGENT_TOOLS.md](AGENT_TOOLS.md)

---

## 🏠 本地模型优势

- ✅ **完全免费** - 无 API 费用
- ✅ **完全隐私** - 代码不离开电脑
- ✅ **无限使用** - 不受限额
- ✅ **离线工作** - 无需网络

快速配置指南：[USE_LOCAL_MODEL.md](USE_LOCAL_MODEL.md)

---

## 📊 项目架构

\`\`\`
aiCode/
├── aicode/
│   ├── models/              # AI 模型（Claude, GPT, Qwen, Local）
│   ├── architectures/       # Agent 架构（ReAct, Plan-Execute）
│   ├── memory/              # 记忆系统（短期、长期）
│   ├── agent/               # 基础组件
│   └── cli_agent.py         # Agent CLI
├── docs/                    # 文档
└── requirements.txt
\`\`\`

---

## 📄 许可证

MIT License

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个星标！**

Made with ❤️ by AI Coding Agent

</div>
