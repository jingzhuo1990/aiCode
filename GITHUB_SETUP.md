# 🚀 GitHub 上传指南

## 📋 步骤总览

你的代码已经在本地准备好了！现在只需要在 GitHub 上创建仓库并推送。

---

## 方法 1: 使用 GitHub CLI（最简单）

### 安装 GitHub CLI

```bash
# macOS
brew install gh

# 验证安装
gh --version
```

### 登录并创建仓库

```bash
# 登录 GitHub
gh auth login

# 创建仓库并推送（一键完成！）
gh repo create aiCode --public --source=. --remote=origin --push
```

**就这么简单！** 仓库会自动创建并推送。

---

## 方法 2: 手动在 GitHub 网站创建

### 第 1 步：在 GitHub 创建新仓库

1. 访问 https://github.com/new
2. 填写信息：
   - **Repository name**: `aiCode`
   - **Description**: `🤖 AI Code - Intelligent Coding Agent with multi-model support`
   - **Public** 或 **Private**（你选择）
   - ⚠️ **不要** 勾选 "Initialize this repository with a README"
   - ⚠️ **不要** 添加 .gitignore 或 license（我们已经有了）

3. 点击 **Create repository**

### 第 2 步：连接并推送

GitHub 会显示推送指令，你只需要运行：

```bash
# 添加远程仓库（替换 yourusername 为你的 GitHub 用户名）
git remote add origin https://github.com/yourusername/aiCode.git

# 推送代码
git branch -M main
git push -u origin main
```

---

## 方法 3: 使用 SSH（如果已配置 SSH key）

```bash
# 添加远程仓库（SSH 方式）
git remote add origin git@github.com:yourusername/aiCode.git

# 推送
git branch -M main
git push -u origin main
```

---

## ✅ 验证上传成功

推送完成后，访问你的仓库：

```
https://github.com/yourusername/aiCode
```

你应该能看到：
- ✅ 完整的项目文件
- ✅ 美化的 README.md
- ✅ 完整的文档
- ✅ 52 个文件

---

## 🎨 后续优化（可选）

### 添加主题标签

在仓库页面点击 ⚙️ Settings → Topics，添加：
```
ai, coding-assistant, agent, llm, claude, openai, qwen, local-model, python
```

### 添加描述

在仓库首页点击 ⚙️ 编辑，添加：
```
🤖 Intelligent AI Coding Agent with multi-model support (Claude, GPT, Qwen, Local)
```

### 设置项目网站（可选）

如果你有文档网站，在 Settings → GitHub Pages 中配置。

---

## 🔄 日常更新流程

以后更新代码很简单：

```bash
# 1. 查看改动
git status

# 2. 添加文件
git add .

# 3. 提交
git commit -m "feat: 添加新功能"

# 4. 推送
git push
```

---

## 📝 推荐的提交信息格式

使用约定式提交（Conventional Commits）：

```bash
git commit -m "feat: 添加新功能"       # 新功能
git commit -m "fix: 修复 bug"         # 修复
git commit -m "docs: 更新文档"        # 文档
git commit -m "refactor: 重构代码"    # 重构
git commit -m "test: 添加测试"        # 测试
git commit -m "chore: 更新依赖"       # 杂项
```

---

## 🆘 常见问题

### Q1: 推送被拒绝（rejected）

可能是远程仓库有内容，运行：
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Q2: 认证失败

确保：
- 使用了正确的用户名
- 如果使用 HTTPS，需要 Personal Access Token（不是密码）
- 或者改用 SSH 方式

创建 Personal Access Token：
https://github.com/settings/tokens

### Q3: 远程仓库地址错误

查看并修改：
```bash
# 查看远程仓库
git remote -v

# 修改地址
git remote set-url origin 新地址
```

---

## 🎉 完成！

推送成功后，你的项目就在 GitHub 上了！

分享链接：
```
https://github.com/yourusername/aiCode
```

---

**准备好了吗？选择上面的方法 1、2 或 3，开始推送吧！** 🚀
