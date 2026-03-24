# 🔧 故障排查指南

## 常见错误及解决方案

### 1. ❌ Invalid model identifier "claude-sonnet-4-6" (使用本地模型时)

**错误信息**:
```
openai.BadRequestError: Error code: 400 - {'error': {'message': 'Invalid model identifier "claude-sonnet-4-6". Please specify a valid downloaded model (e.g., qwen/qwen3.5-9b@q4_k_m, qwen/qwen3.5-9b, qwen3.5-9b).'
```

**原因**:
使用 `--provider local` 但 `.env` 文件中缺少本地模型配置，导致系统使用默认的 Claude 模型名称。

**解决方案**:

#### 方法 1: 配置 .env 文件（推荐）
```bash
# 编辑 .env 文件
nano .env

# 添加以下配置（必需！）
LOCAL_MODEL_BASE_URL=http://localhost:1234/v1
LOCAL_MODEL_NAME=qwen3.5-9b  # 替换为你的实际模型名称
```

#### 方法 2: 命令行指定模型名称
```bash
python -m aicode.cli_agent run "任务" --provider local --model qwen3.5-9b
```

#### 如何找到正确的模型名称？

在 LM Studio 中查看加载的模型名称，常见格式：
- `qwen3.5-9b`
- `qwen/qwen3.5-9b`
- `qwen/qwen3.5-9b@q4_k_m`

使用 LM Studio API 测试：
```bash
curl http://localhost:1234/v1/models
```

---

### 2. ❌ Connection refused / 连接被拒绝

**错误信息**:
```
httpcore.ConnectError: All connection attempts failed
```

**原因**: LM Studio 服务器未运行或端口不对

**解决方案**:

1. 确保 LM Studio 正在运行
2. 在 LM Studio 中点击 "Start Server" 按钮
3. 确认端口是 1234（默认）

检查端口：
```bash
# macOS/Linux
lsof -i :1234

# 或使用 curl 测试
curl http://localhost:1234/v1/models
```

如果端口不是 1234，修改 `.env`:
```bash
LOCAL_MODEL_BASE_URL=http://localhost:你的端口/v1
```

---

### 3. ❌ 未设置 API Key

**错误信息**:
```
错误: 未设置 ANTHROPIC_API_KEY
```

**原因**: 使用云端模型但未配置 API Key

**解决方案**:

编辑 `.env` 文件：
```bash
# Claude
ANTHROPIC_API_KEY=sk-ant-你的key

# OpenAI
OPENAI_API_KEY=sk-你的key

# Qwen
QWEN_API_KEY=sk-你的key
```

或使用本地模型（不需要 API Key）：
```bash
python -m aicode.cli_agent run "任务" --provider local
```

---

### 4. ⚠️ Agent 工具执行失败

**错误信息**:
```
create_default_tools.<locals>.<lambda>() missing 2 required positional arguments
```

**原因**: 使用了旧版本的工具系统

**解决方案**:

确保使用最新的 `tools_enhanced.py`：

检查 `unified_agent.py` 第 8 行：
```python
# ✅ 正确
from .tools_enhanced import ToolRegistry, create_enhanced_tools

# ❌ 错误（旧版本）
from .tools import ToolRegistry, create_default_tools
```

如果使用了旧版本，更新导入：
```bash
# 手动编辑 unified_agent.py
# 或重新克隆仓库
```

---

### 5. 🐌 响应速度慢

**症状**: Agent 执行任务需要很长时间

**原因**: 本地模型需要计算资源

**优化方案**:

1. **检查硬件资源**:
   - 确保有足够的 RAM（建议 16GB+）
   - 使用 GPU 加速（如果可用）

2. **在 LM Studio 中调整设置**:
   - 减小 Context Length
   - 启用 GPU 加速
   - 调整并行处理数

3. **混合使用策略**:
   ```bash
   # 简单任务用本地
   python -m aicode.cli_agent run "创建文件" --provider local

   # 复杂任务用云端
   python -m aicode.cli_agent run "设计架构" --provider claude
   ```

---

### 6. 📝 生成质量不理想

**症状**: 代码质量差或回答不准确

**解决方案**:

1. **使用更具体的提示词**:
   ```bash
   # ❌ 模糊
   python -m aicode generate "写个函数" --provider local

   # ✅ 具体
   python -m aicode generate "创建一个递归实现的快速排序函数，包含类型注解和详细注释" --provider local
   ```

2. **调整温度参数**:
   ```bash
   # 更确定性的输出（0.0-0.3）
   python -m aicode generate "任务" --provider local --temperature 0.2

   # 更有创造性的输出（0.7-1.0）
   python -m aicode generate "任务" --provider local --temperature 0.8
   ```

3. **复杂任务切换到云端模型**:
   ```bash
   python -m aicode generate "复杂架构设计" --provider claude --model claude-sonnet-4-6
   ```

---

### 7. 🔍 无法找到模型

**错误信息**:
```
Error code: 400 - {'error': {'message': 'Invalid model identifier...
```

**调试步骤**:

1. **查看 LM Studio 中的模型名称**（精确复制）

2. **测试 API 连接**:
   ```bash
   curl http://localhost:1234/v1/models
   ```

   查看返回的 `"id"` 字段，这就是正确的模型名称

3. **更新配置**:
   ```bash
   # .env
   LOCAL_MODEL_NAME=从API返回的id字段复制过来
   ```

---

### 8. 💾 记忆系统问题

**症状**: Agent 无法记住之前的对话

**解决方案**:

1. **检查记忆目录**:
   ```bash
   ls -la .aicode_memory/
   ```

2. **查看记忆统计**:
   ```bash
   python -m aicode.cli_agent memory-stats
   ```

3. **手动清理**:
   ```bash
   # 清空短期记忆（仅当前会话）
   # 在交互式会话中输入：clear

   # 删除所有记忆
   rm -rf .aicode_memory/
   ```

---

### 9. 🔐 权限问题

**错误信息**:
```
Permission denied: '/path/to/file'
```

**解决方案**:

1. **检查文件权限**:
   ```bash
   ls -l 文件路径
   ```

2. **修改权限**:
   ```bash
   chmod +w 文件路径  # 添加写权限
   chmod +r 文件路径  # 添加读权限
   ```

3. **使用绝对路径**:
   ```bash
   python -m aicode.cli_agent run "读取 /完整/路径/file.txt" --provider local
   ```

---

### 10. 📦 依赖问题

**错误信息**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**:

1. **重新安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **使用虚拟环境**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **更新过期的包**:
   ```bash
   pip install --upgrade anthropic openai dashscope
   ```

---

## 🆘 仍然无法解决？

### 调试模式

运行时添加详细日志：
```bash
# 暂不支持，但可以查看详细错误信息
python -m aicode.cli_agent run "任务" --provider local 2>&1 | tee debug.log
```

### 获取帮助

1. **查看配置**:
   ```bash
   python -m aicode info
   ```

2. **查看工具列表**:
   ```bash
   python -m aicode.cli_agent list-tools
   ```

3. **检查环境**:
   ```bash
   # Python 版本
   python --version  # 建议 3.9+

   # 已安装的包
   pip list | grep -E "anthropic|openai|dashscope"
   ```

---

## ✅ 快速检查清单

在报告问题前，请确认：

- [ ] LM Studio 服务器正在运行（端口 1234）
- [ ] `.env` 文件中已配置 `LOCAL_MODEL_BASE_URL` 和 `LOCAL_MODEL_NAME`
- [ ] 模型名称与 LM Studio 中显示的完全一致
- [ ] 可以通过 `curl http://localhost:1234/v1/models` 访问 API
- [ ] 已安装所有依赖：`pip install -r requirements.txt`
- [ ] Python 版本 >= 3.9

---

## 📚 相关文档

- **快速开始**: `USE_LOCAL_MODEL.md`
- **详细指南**: `LOCAL_MODEL_GUIDE.md`
- **工具说明**: `AGENT_TOOLS.md`
- **配置示例**: `.env.example`

---

**最后更新**: 2026-03-24
