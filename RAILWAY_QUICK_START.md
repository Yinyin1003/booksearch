# Railway 快速开始（3 步部署）

## ⚡ 超简单 3 步

### 1️⃣ 推送到 GitHub

```bash
cd /Users/zhouyinyin/Downloads/booksearch1

# 如果还没初始化 Git
git init
git add .
git commit -m "Initial commit"

# 如果还没推送到 GitHub
git remote add origin https://github.com/你的用户名/booksearch.git
git branch -M main
git push -u origin main
```

### 2️⃣ 部署到 Railway

1. 访问 https://railway.app
2. 点击 "Start a New Project"
3. 选择 "Deploy from GitHub repo"
4. 登录 GitHub 并授权
5. 选择你的 `booksearch` 仓库
6. **完成！** Railway 会自动部署

### 3️⃣ 获取 URL

部署完成后，Railway 会显示一个 URL，例如：
```
https://booksearch-production.up.railway.app
```

点击即可访问！

## ✅ 就这么简单！

Railway 会自动：
- ✅ 检测 Python 项目
- ✅ 安装依赖
- ✅ 启动应用
- ✅ 提供 HTTPS URL

## 📸 上传图片

部署后访问网站，在管理界面上传 `bookshelf.jpg` 即可。

## 🔄 更新代码

以后只需要：
```bash
git push
```

Railway 会自动重新部署！

---

**详细说明**：查看 `RAILWAY_DEPLOY.md`

