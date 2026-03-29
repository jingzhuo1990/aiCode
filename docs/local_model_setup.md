# 本地模型配置指南

## 📋 概述

本指南帮助你配置本地大模型，用于运行真实的 Agent Harness 对比演示。

## 🚀 方案选择

### 方案 1：LM Studio（推荐，简单易用）

**优点**：
- 图形界面，易于使用
- 自动管理模型下载
- 内置 OpenAI 兼容 API
- 支持 macOS/Windows/Linux

**安装步骤**：

1. **下载 LM Studio**
   - 访问：https://lmstudio.ai/
   - 下载适合你系统的版本
   - 安装并启动

2. **下载模型**
   - 在 LM Studio 中搜索并下载模型，推荐：
     - `Qwen2.5-Coder-7B-Instruct` (代码能力强)
     - `Qwen2.5-7B-Instruct` (通用能力)
     - `Llama-3.2-3B-Instruct` (轻量级)

3. **启动本地服务器**
   - 在 LM Studio 中加载模型
   - 点击 "Local Server" 标签
   - 点击 "Start Server"
   - 默认地址：`http://localhost:1234`

4. **测试连接**
   ```bash
   curl http://localhost:1234/v1/models
   ```

5. **运行演示**
   ```bash
   python demo_real_harness_comparison.py
   ```

### 方案 2：Ollama（命令行，轻量级）

**优点**：
- 命令行工具，轻量
- 快速下载和切换模型
- 资源占用少

**安装步骤**：

1. **安装 Ollama**
   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.com/install.sh | sh

   # Windows
   # 下载安装包：https://ollama.com/download
   ```

2. **下载模型**
   ```bash
   # 推荐模型
   ollama pull qwen2.5-coder:7b    # 代码专用
   ollama pull qwen2.5:7b          # 通用
   ollama pull llama3.2:3b         # 轻量级
   ```

3. **启动服务**
   ```bash
   ollama serve
   ```
   默认地址：`http://localhost:11434`

4. **测试连接**
   ```bash
   curl http://localhost:11434/api/tags
   ```

5. **修改演示代码**

   编辑 `demo_real_harness_comparison.py` 中的 `check_local_model()` 函数：

   ```python
   # 在第 44 行修改模型名称
   model = LocalModel(
       model_name="qwen2.5-coder:7b",  # 改为你下载的模型
       base_url="http://localhost:11434/v1"
   )
   ```

6. **运行演示**
   ```bash
   python demo_real_harness_comparison.py
   ```

## 🎯 推荐模型

### 代码生成任务
| 模型 | 大小 | 特点 | 推荐度 |
|------|------|------|--------|
| Qwen2.5-Coder-7B | 7B | 专门针对代码优化 | ⭐⭐⭐⭐⭐ |
| CodeLlama-7B | 7B | Meta 的代码模型 | ⭐⭐⭐⭐ |
| DeepSeek-Coder-6.7B | 6.7B | 代码能力强 | ⭐⭐⭐⭐ |

### 通用任务
| 模型 | 大小 | 特点 | 推荐度 |
|------|------|------|--------|
| Qwen2.5-7B | 7B | 中英文都好 | ⭐⭐⭐⭐⭐ |
| Llama-3.2-3B | 3B | 轻量但能力强 | ⭐⭐⭐⭐ |
| Mistral-7B | 7B | 性能优秀 | ⭐⭐⭐⭐ |

### 硬件要求

| 模型大小 | 显存需求 | RAM 需求 | 推荐硬件 |
|---------|---------|---------|---------|
| 3B | 4GB | 8GB | 集成显卡/入门独显 |
| 7B | 8GB | 16GB | 中端独显 |
| 13B | 16GB | 32GB | 高端独显 |

## 🔧 常见问题

### 1. 连接超时

**问题**：无法连接到本地模型

**解决**：
```bash
# 检查服务是否启动
# LM Studio: 看界面是否显示 "Server Running"
# Ollama: 运行
ps aux | grep ollama

# 检查端口
netstat -an | grep 1234  # LM Studio
netstat -an | grep 11434 # Ollama
```

### 2. 模型加载失败

**问题**：模型无法加载或报错

**解决**：
- 确保下载完整（重新下载）
- 检查磁盘空间
- 尝试其他模型

### 3. 响应速度慢

**问题**：生成速度很慢

**解决**：
- 使用更小的模型（3B 而不是 7B）
- 减少 `max_tokens` 参数
- 确保没有其他程序占用 GPU

### 4. 内存不足

**问题**：OOM (Out of Memory)

**解决**：
- 使用更小的模型
- 关闭其他程序
- 使用量化版本（如 Q4_K_M）

## 🎮 使用演示

### 基础使用

```bash
# 1. 启动本地模型服务
# LM Studio: 图形界面启动
# Ollama:
ollama serve

# 2. 运行演示
python demo_real_harness_comparison.py
```

### 预期输出

演示将执行 4 个场景：
1. **基础对比**：相同任务，有/无 Harness 的差异
2. **复杂任务**：多需求任务的处理能力
3. **记忆系统**：连续对话的上下文保持
4. **统计对比**：批量任务的性能对比

每个场景都会显示：
- ⏱️ 耗时
- 🧠 推理过程
- 📝 生成结果
- 🔍 分析对比

## 📊 性能调优

### 提升速度

```python
# 在创建 model 时调整参数
model = LocalModel(
    model_name="qwen2.5-coder:7b",
    base_url="http://localhost:11434/v1"
)

# 执行时减少 tokens
result = await model.generate(
    prompt=prompt,
    max_tokens=1000,  # 减少到 1000
    temperature=0.3    # 降低温度提升确定性
)
```

### 提升质量

```python
# 使用更大的模型
model = LocalModel(
    model_name="qwen2.5-coder:14b",  # 使用 14B 版本
    base_url="http://localhost:11434/v1"
)

# 增加 tokens
result = await model.generate(
    prompt=prompt,
    max_tokens=4000,   # 增加到 4000
    temperature=0.7    # 适中的温度
)
```

## 🌐 在线 API 备选方案

如果无法运行本地模型，可以使用在线 API：

### 通义千问 (Qwen)

```python
from aicode.models import QwenModel

model = QwenModel(
    api_key="your-api-key",  # 从阿里云获取
    model_name="qwen-coder-plus"
)
```

获取 API Key：https://dashscope.aliyuncs.com/

### OpenAI

```python
from aicode.models import OpenAIModel

model = OpenAIModel(
    api_key="your-api-key",
    model_name="gpt-4"
)
```

## 📚 更多资源

- LM Studio 文档：https://lmstudio.ai/docs
- Ollama 文档：https://github.com/ollama/ollama
- 模型排行榜：https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard

## 🆘 获取帮助

遇到问题？

1. 查看日志输出
2. 检查网络连接
3. 尝试简单的测试用例
4. 提交 Issue：[项目 GitHub 地址]

---

**祝你使用愉快！🚀**
