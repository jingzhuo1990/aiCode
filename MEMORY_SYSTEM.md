# 🧠 记忆系统详解

## 📋 目录

- [什么时候用短期记忆](#什么时候用短期记忆)
- [什么时候用长期记忆](#什么时候用长期记忆)
- [存储机制](#存储机制)
- [检索方式](#检索方式)
- [实战示例](#实战示例)

---

## 🔄 什么时候用短期记忆？

### 定义
**短期记忆 = 当前会话的对话上下文**

### 自动使用场景（无需手动操作）

系统会自动将以下内容存入短期记忆：

1. **用户输入** - 每次你发送的消息
2. **Agent 回复** - AI 的所有响应
3. **工具调用结果** - 执行工具后的输出
4. **系统提示** - 内部状态信息

### 特点

```python
# 配置
max_messages: 50        # 最多保留 50 条消息
max_tokens: 8000        # 约 8000 tokens（字符数 / 4）
```

#### ✅ 优点
- **自动管理** - 无需手动操作
- **即时访问** - 当前会话立即可用
- **自动修剪** - 超出限制时智能删除旧消息

#### ⚠️ 限制
- **临时性** - 会话结束后清空（除非导出）
- **容量限制** - 仅保留最近的消息
- **无分类** - 按时间顺序存储

### 生命周期

```
会话开始 → 消息累积 → 自动修剪 → 会话结束 → 清空
              ↓
         （可导出保存）
```

---

## 💾 什么时候用长期记忆？

### 定义
**长期记忆 = 持久化存储的重要信息**

### 手动使用场景

需要主动调用 `remember()` 存储：

#### 1️⃣ 用户偏好

```bash
# 记住编码风格
python -m aicode.cli_agent remember "coding_style" "使用 4 空格缩进，遵循 PEP 8" --category user_preferences --importance 9

# 记住语言偏好
python -m aicode.cli_agent remember "language" "中文" --category user_preferences
```

**应用场景**：
- 代码风格偏好
- 命名约定
- 文档格式
- 工具链选择

#### 2️⃣ 项目知识

```python
# 在代码中记住项目结构
memory_manager.remember_codebase_info(
    project_path="/path/to/project",
    info={
        "framework": "FastAPI",
        "database": "PostgreSQL",
        "main_modules": ["api", "models", "services"]
    }
)
```

**应用场景**：
- 项目架构
- 技术栈
- API 端点
- 数据库模式

#### 3️⃣ 代码模式

```python
# 记住常用模式
memory_manager.remember_code_pattern(
    pattern_name="error_handling",
    pattern_info={
        "pattern": "try-except with logging",
        "example": "...",
        "usage": "所有 API 调用"
    }
)
```

**应用场景**：
- 设计模式
- 最佳实践
- 常见 bug 修复
- 优化技巧

#### 4️⃣ 任务记录

```python
# Agent 自动记录重要任务
memory_manager.remember(
    key="task_20260325_150000",
    value={
        "task": "实现用户认证",
        "result": "成功",
        "files": ["auth.py", "middleware.py"]
    },
    category="tasks",
    importance=7
)
```

**应用场景**：
- 已完成任务
- 遇到的问题
- 解决方案
- 重要决策

### 特点

```python
# 配置
category: str          # 分类（codebase, user_preferences, patterns, tasks）
tags: List[str]        # 标签（可多个）
importance: int        # 重要程度 1-10
```

#### ✅ 优点
- **持久化** - 跨会话保存
- **结构化** - 分类、标签、重要度
- **可搜索** - 关键词、分类、标签检索
- **智能清理** - 自动删除旧的低重要度记忆

#### ⚠️ 注意
- **手动操作** - 需要显式调用
- **存储空间** - 长期累积需要清理
- **检索成本** - 需要搜索才能获取

### 生命周期

```
手动存储 → 持久化到磁盘 → 跨会话可用 → 自动清理（90天+低重要度）
```

---

## 💿 存储机制

### 短期记忆存储

#### 存储位置
```
内存（RAM）- Python 对象列表
```

#### 数据结构
```python
class Message:
    role: str            # 'user', 'assistant', 'system', 'tool'
    content: str         # 消息内容
    metadata: Dict       # 元数据
    timestamp: datetime  # 时间戳
```

#### 持久化（可选）
```python
# 导出会话
memory_manager.export_session("session_20260325.json")

# 导入会话
memory_manager.import_session("session_20260325.json")
```

**文件格式**：JSON
```json
{
  "session_id": "20260325_143000",
  "messages": [
    {
      "role": "user",
      "content": "创建一个快速排序函数",
      "metadata": {},
      "timestamp": "2026-03-25T14:30:00"
    }
  ]
}
```

---

### 长期记忆存储

#### 存储位置
```
.aicode_memory/memory_index.json
```

#### 数据结构
```python
class MemoryEntry:
    key: str              # 记忆键（唯一标识）
    value: Any            # 记忆值（任意类型）
    category: str         # 分类
    tags: List[str]       # 标签
    importance: int       # 重要程度 1-10
    created_at: datetime  # 创建时间
    updated_at: datetime  # 更新时间
    access_count: int     # 访问次数
```

#### 文件格式：JSON

```json
{
  "memories": {
    "coding_style": {
      "key": "coding_style",
      "value": "使用 4 空格缩进，遵循 PEP 8",
      "category": "user_preferences",
      "tags": ["style", "python"],
      "importance": 9,
      "created_at": "2026-03-25T14:00:00",
      "updated_at": "2026-03-25T14:00:00",
      "access_count": 5
    },
    "pattern_error_handling": {
      "key": "pattern_error_handling",
      "value": {
        "pattern": "try-except with logging",
        "example": "try: ... except Exception as e: logger.error(e)"
      },
      "category": "patterns",
      "tags": ["error", "pattern"],
      "importance": 6,
      "created_at": "2026-03-25T15:00:00",
      "updated_at": "2026-03-25T16:00:00",
      "access_count": 12
    }
  },
  "last_updated": "2026-03-25T16:00:00"
}
```

---

## 🔍 检索方式

### 短期记忆检索

#### 1. 获取全部对话历史

```python
history = memory_manager.get_conversation_history()
# 返回格式化的消息列表（用于模型输入）
```

#### 2. 获取最近 N 条消息

```python
recent = memory_manager.get_recent_context(last_n=5)
# 返回最近 5 条消息的摘要
```

#### 3. 获取上下文摘要

```python
summary = memory_manager.short_term.get_context_summary()
# 返回会话统计和最近消息
```

**特点**：
- ✅ **简单** - 按时间顺序访问
- ✅ **快速** - 内存中直接读取
- ❌ **无搜索** - 不支持关键词检索

---

### 长期记忆检索

#### 1️⃣ 关键词检索（已支持 ✅）

```bash
# CLI 命令
python -m aicode.cli_agent search "编码风格"

# Python API
entries = memory_manager.search_memories(query="编码风格")
```

**检索范围**：
- ✅ 记忆键（key）
- ✅ 记忆值（value）转字符串
- ✅ 标签（tags）

**实现方式**：
```python
def search(self, query: str):
    query_lower = query.lower()

    # 在 key、value、tags 中搜索
    if (query_lower in entry.key.lower() or
        query_lower in str(entry.value).lower() or
        any(query_lower in tag.lower() for tag in entry.tags)):
        results.append(entry)
```

**特点**：
- ✅ **简单** - 子串匹配
- ✅ **快速** - 遍历内存中的字典
- ❌ **精确性** - 无模糊匹配
- ❌ **语义理解** - 无语义相似度

#### 2️⃣ 分类检索（已支持 ✅）

```bash
# 搜索用户偏好
python -m aicode.cli_agent search "风格" --category user_preferences

# Python API
entries = memory_manager.search_memories(
    query="风格",
    category="user_preferences"
)
```

**可用分类**：
- `codebase` - 代码库信息
- `user_preferences` - 用户偏好
- `patterns` - 代码模式
- `tasks` - 任务记录
- `general` - 通用

#### 3️⃣ 标签检索（已支持 ✅）

```python
# 搜索带特定标签的记忆
entries = memory_manager.search_memories(
    tags=["python", "style"]
)
```

#### 4️⃣ 重要程度过滤（已支持 ✅）

```python
# 只检索重要程度 >= 7 的记忆
entries = memory_manager.long_term.search(
    query="认证",
    min_importance=7
)
```

#### 5️⃣ 直接键检索（已支持 ✅）

```python
# 通过唯一键直接获取
value = memory_manager.recall("coding_style")
```

**特点**：
- ✅ **最快** - O(1) 哈希表查找
- ✅ **精确** - 完全匹配

#### 6️⃣ 组合检索（已支持 ✅）

```python
# 多条件组合
entries = memory_manager.long_term.search(
    query="认证",              # 关键词
    category="patterns",      # 分类
    tags=["security"],        # 标签
    min_importance=6          # 最低重要度
)
```

---

### 🚫 当前不支持的检索方式

#### ❌ 语义检索（未实现）

**需要什么**：
- 向量数据库（如 FAISS、Pinecone、Weaviate）
- Embedding 模型（如 text-embedding-3-small）
- 相似度计算

**示例（如果实现）**：
```python
# 语义搜索
results = memory_manager.semantic_search(
    query="如何处理错误",
    top_k=5
)
# 返回语义相似的记忆，即使关键词不匹配
```

**为什么未实现**：
- 需要额外的依赖（向量数据库）
- 增加复杂度和存储成本
- 对于编程场景，关键词检索已足够

#### ❌ 模糊匹配（未实现）

**示例（如果实现）**：
```python
# 模糊搜索
results = memory_manager.fuzzy_search("cding_styl")  # 拼写错误
# 仍能匹配到 "coding_style"
```

**可用替代方案**：
- 使用更通用的关键词
- 搜索标签而不是键
- 使用分类过滤

---

## 📊 对比总结

| 特性 | 短期记忆 | 长期记忆 |
|-----|---------|---------|
| **存储位置** | 内存（RAM） | 磁盘（JSON 文件） |
| **生命周期** | 当前会话 | 持久化跨会话 |
| **容量限制** | 50 条消息 / 8000 tokens | 无硬性限制 |
| **自动管理** | ✅ 自动添加和修剪 | ❌ 手动存储 |
| **结构化** | ❌ 简单时间序列 | ✅ 分类/标签/重要度 |
| **检索方式** | 时间顺序 | 关键词/分类/标签 |
| **语义检索** | ❌ 不支持 | ❌ 不支持 |
| **模糊匹配** | ❌ 不支持 | ❌ 不支持 |
| **精确检索** | ✅ 按时间 | ✅ 按键/分类/标签 |
| **适用场景** | 当前对话上下文 | 跨会话知识存储 |

---

## 💡 实战示例

### 示例 1：交互式会话（自动使用短期记忆）

```bash
python -m aicode.cli_agent interactive --provider local
```

```
You: 创建一个 user.py 文件
Agent: [创建文件] ✅

You: 在里面添加一个 User 类
Agent: [读取 user.py，添加类，保存] ✅
# Agent 自动记住之前创建的文件路径

You: 给 User 类添加一个 email 属性
Agent: [读取 user.py，找到 User 类，添加属性] ✅
# Agent 从短期记忆中知道我们在讨论 User 类
```

**短期记忆内容**（自动）：
```
Message 1: [user] 创建一个 user.py 文件
Message 2: [assistant] 已创建 user.py
Message 3: [tool] write_file 执行成功
Message 4: [user] 在里面添加一个 User 类
Message 5: [assistant] 已添加 User 类
...
```

---

### 示例 2：记住用户偏好（手动使用长期记忆）

```bash
# 记住编码风格
python -m aicode.cli_agent remember \
  "coding_style" \
  "使用 TypeScript, 4 空格缩进, 优先使用 const" \
  --category user_preferences \
  --importance 9

# 记住测试框架
python -m aicode.cli_agent remember \
  "test_framework" \
  "使用 Jest 和 React Testing Library" \
  --category user_preferences \
  --importance 8
```

**以后 Agent 会自动应用这些偏好**：

```bash
You: 创建一个新组件
Agent: [生成代码时自动使用 TypeScript + 4 空格 + const]
```

---

### 示例 3：记住项目结构（代码中使用）

```python
from aicode.memory.memory_manager import MemoryManager

memory = MemoryManager()

# 记住项目信息
memory.remember_codebase_info(
    project_path="/Users/jingzhuo/project",
    info={
        "framework": "FastAPI",
        "database": "PostgreSQL + SQLAlchemy",
        "structure": {
            "api": "路由定义",
            "models": "数据模型",
            "services": "业务逻辑",
            "tests": "测试代码"
        },
        "conventions": {
            "imports": "绝对导入",
            "naming": "snake_case"
        }
    }
)

# 以后可以检索
info = memory.recall("codebase_/Users/jingzhuo/project")
```

---

### 示例 4：搜索记忆

```bash
# 搜索所有与 "认证" 相关的记忆
python -m aicode.cli_agent search "认证"

# 只搜索代码模式
python -m aicode.cli_agent search "认证" --category patterns

# 在代码中搜索
entries = memory_manager.search_memories(
    query="认证",
    category="patterns"
)

for entry in entries:
    print(f"{entry['key']}: {entry['value']}")
```

---

### 示例 5：查看记忆统计

```bash
python -m aicode.cli_agent memory-stats
```

输出：
```
Memory Statistics

Short-term Memory:
  Session: 20260325_143000
  Total messages: 23
  Estimated tokens: 1847

Long-term Memory:
  Total memories: 15
  Categories: {'user_preferences': 5, 'patterns': 6, 'tasks': 4}
  Total tags: 18
```

---

## 🎯 最佳实践

### 短期记忆

1. **无需手动操作** - 系统自动管理
2. **保持会话连续性** - 使用交互式模式
3. **必要时导出** - 保存重要会话

```bash
# 导出会话
memory_manager.export_session("important_session.json")
```

### 长期记忆

1. **记住用户偏好** - 减少重复说明
2. **记录项目知识** - 避免重复探索
3. **定期清理** - 删除过时记忆

```python
# 清理 90 天前且重要度 < 7 的记忆
memory_manager.cleanup(days=90)
```

4. **使用合适的重要度**：
   - 1-3: 临时信息
   - 4-6: 一般信息
   - 7-8: 重要信息
   - 9-10: 关键信息（用户偏好、核心架构）

5. **使用描述性的键**：
   ```python
   # ✅ 好
   "auth_jwt_implementation"

   # ❌ 不好
   "temp_1"
   ```

6. **添加标签便于检索**：
   ```python
   memory.remember(
       "auth_jwt_implementation",
       "...",
       tags=["auth", "jwt", "security", "python"]  # 多个相关标签
   )
   ```

---

## 🔮 未来改进方向

### 可能的增强功能

1. **向量检索（语义搜索）**
   ```python
   # 未来可能实现
   results = memory.semantic_search("如何处理错误")
   # 返回语义相似的记忆，即使关键词不同
   ```

2. **记忆自动提取**
   ```python
   # Agent 自动从对话中提取重要信息
   memory.auto_extract_from_conversation()
   ```

3. **记忆重要度自动调整**
   ```python
   # 根据访问频率自动调整重要度
   memory.auto_adjust_importance()
   ```

4. **记忆图谱**
   ```python
   # 记忆之间建立关联
   memory.link("auth_pattern", "jwt_implementation")
   ```

---

## 📚 相关命令参考

```bash
# 记忆管理
python -m aicode.cli_agent remember <key> <value>      # 存储
python -m aicode.cli_agent search <query>               # 搜索
python -m aicode.cli_agent memory-stats                 # 统计

# 交互式会话（自动使用短期记忆）
python -m aicode.cli_agent interactive --provider local
```

---

**记忆系统让你的 AI Agent 更智能、更个性化！** 🧠✨
