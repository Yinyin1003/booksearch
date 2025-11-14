# GitHub 部署步骤

## 1. 创建 GitHub 仓库

1. 访问 [GitHub](https://github.com)
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - **Repository name**: `booksearch`（或你喜欢的名字）
   - **Description**: 智能书籍搜索系统
   - **Visibility**: Public（公开）或 Private（私有）
   - **不要**勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

## 2. 初始化本地 Git 仓库

在项目目录中执行：

```bash
cd /Users/zhouyinyin/Downloads/booksearch1

# 初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 智能书籍搜索系统"

# 添加远程仓库（替换为你的仓库URL）
git remote add origin https://github.com/你的用户名/booksearch.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 3. 部署到云端

### 选项 A: Railway（推荐）

1. **访问 Railway**
   - 打开 https://railway.app
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 授权 Railway 访问你的 GitHub
   - 选择 `booksearch` 仓库

3. **自动部署**
   - Railway 会自动检测 Python 项目
   - 自动安装依赖
   - 自动部署

4. **获取 URL**
   - 部署完成后，Railway 会提供一个公开 URL
   - 例如：`https://booksearch-production.up.railway.app`

5. **配置环境变量（可选）**
   - 在 Railway Dashboard → Variables
   - 添加：`FLASK_DEBUG=False`

### 选项 B: Render

1. **访问 Render**
   - 打开 https://render.com
   - 使用 GitHub 账号登录

2. **创建 Web Service**
   - 点击 "New" → "Web Service"
   - 连接你的 GitHub 仓库

3. **配置**
   - **Name**: `booksearch`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

4. **部署**
   - 点击 "Create Web Service"
   - Render 会自动部署

### 选项 C: Heroku

1. **安装 Heroku CLI**
   ```bash
   brew tap heroku/brew && brew install heroku
   ```

2. **登录 Heroku**
   ```bash
   heroku login
   ```

3. **创建应用**
   ```bash
   heroku create booksearch-yourname
   ```

4. **部署**
   ```bash
   git push heroku main
   ```

## 4. 上传书架图片

部署完成后，你需要上传 `bookshelf.jpg`：

### 方法 1: 通过 Web 界面
1. 访问部署后的网站
2. 在管理界面使用图片上传功能

### 方法 2: 通过 Git
1. 将 `bookshelf.jpg` 添加到仓库
2. 提交并推送：
   ```bash
   git add bookshelf.jpg
   git commit -m "Add bookshelf image"
   git push
   ```
3. 平台会自动重新部署

## 5. 测试部署

1. **访问网站**
   - 打开部署后的 URL
   - 测试管理界面功能

2. **测试语音搜索**
   - 访问 `/preview` 页面
   - 点击麦克风图标
   - 说出书名测试搜索

## 6. 更新代码

以后更新代码时：

```bash
# 修改代码后
git add .
git commit -m "更新说明"
git push

# 平台会自动重新部署
```

## 常见问题

### Q: 部署失败怎么办？
A: 查看平台日志：
- Railway: Dashboard → Deployments → 查看日志
- Render: Dashboard → Logs
- Heroku: `heroku logs --tail`

### Q: 图片无法显示？
A: 确保 `bookshelf.jpg` 已上传，检查文件路径

### Q: 语音识别不工作？
A: 确保使用 HTTPS（Web Speech API 需要安全连接）

### Q: 如何自定义域名？
A: 
- Railway: Settings → Domains → 添加自定义域名
- Render: Settings → Custom Domain
- Heroku: Settings → Domains → Add Domain

## 下一步

- ✅ 代码已推送到 GitHub
- ✅ 已部署到云端
- ✅ 网站可以访问
- 📸 上传书架图片
- 🎤 测试语音搜索功能

享受你的智能书籍搜索系统！🎉

