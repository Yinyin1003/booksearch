# 部署指南

本项目可以部署到多个平台，以下是详细的部署步骤。

## 部署选项

### 1. Railway（推荐 - 免费且简单）

Railway 提供免费额度，部署简单。

#### 步骤：

1. **准备代码**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **推送到 GitHub**
   - 在 GitHub 创建新仓库
   - 推送代码：
     ```bash
     git remote add origin https://github.com/你的用户名/booksearch.git
     git push -u origin main
     ```

3. **部署到 Railway**
   - 访问 [Railway.app](https://railway.app)
   - 使用 GitHub 账号登录
   - 点击 "New Project" → "Deploy from GitHub repo"
   - 选择你的仓库
   - Railway 会自动检测 Python 项目并部署
   - 部署完成后，Railway 会提供一个公开 URL

4. **配置环境变量（可选）**
   - 在 Railway 项目设置中添加环境变量：
     - `FLASK_DEBUG=False`（生产环境）

### 2. Render（免费选项）

Render 提供免费 tier，适合小型项目。

#### 步骤：

1. **准备代码**（同上）

2. **部署到 Render**
   - 访问 [Render.com](https://render.com)
   - 使用 GitHub 账号登录
   - 点击 "New" → "Web Service"
   - 连接你的 GitHub 仓库
   - 配置：
     - **Name**: booksearch
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python3 app.py`
   - 点击 "Create Web Service"
   - Render 会自动部署并提供 URL

3. **配置环境变量**
   - 在 Render Dashboard → Environment 中添加：
     - `PORT=10000`（Render 使用 10000 端口）
     - `FLASK_DEBUG=False`

### 3. Heroku（需要信用卡验证）

Heroku 提供免费 tier，但需要信用卡验证。

#### 步骤：

1. **安装 Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # 或访问 https://devcenter.heroku.com/articles/heroku-cli
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

5. **配置环境变量**
   ```bash
   heroku config:set FLASK_DEBUG=False
   ```

### 4. Vercel（需要配置）

Vercel 主要用于前端，但可以通过 Serverless Functions 运行 Flask。

#### 步骤：

1. **安装 Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **创建 vercel.json**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ]
   }
   ```

3. **部署**
   ```bash
   vercel
   ```

## 重要注意事项

### 1. 图片上传

当前系统需要 `bookshelf.jpg` 文件。部署后，你需要：

- **方法1：通过 Web 界面上传**
  - 访问部署后的网站
  - 在编辑界面使用图片上传功能

- **方法2：通过 Git 提交**
  - 将 `bookshelf.jpg` 添加到仓库
  - 推送到 GitHub
  - 重新部署

### 2. 文件存储

在生产环境中，文件修改可能不会持久化。建议：

- 使用数据库（如 PostgreSQL）存储书籍数据
- 使用云存储（如 AWS S3、Cloudinary）存储图片
- 或使用文件系统（Railway 和 Render 支持持久化存储）

### 3. 端口配置

不同平台使用不同的端口：
- **Railway**: 自动检测 `PORT` 环境变量
- **Render**: 使用 `PORT` 环境变量（默认 10000）
- **Heroku**: 自动设置 `PORT` 环境变量
- **Vercel**: 不需要配置端口

### 4. 依赖问题

如果部署时遇到依赖问题：

1. **更新 requirements.txt**
   ```bash
   pip freeze > requirements.txt
   ```

2. **检查 Python 版本**
   - 确保 `runtime.txt` 中的 Python 版本与平台兼容

### 5. 静态文件

确保静态文件和模板文件在正确位置：
- `static/` - CSS 和 JavaScript
- `templates/` - HTML 模板

## 快速部署检查清单

- [ ] 代码已推送到 GitHub
- [ ] `.gitignore` 已配置
- [ ] `requirements.txt` 包含所有依赖
- [ ] `Procfile` 已创建（Heroku/Railway）
- [ ] `runtime.txt` 已创建（Heroku）
- [ ] 环境变量已配置
- [ ] `bookshelf.jpg` 已上传或可通过界面上传
- [ ] 测试部署后的网站功能

## 故障排除

### 问题：部署失败

1. 检查日志：
   - Railway: Dashboard → Deployments → 查看日志
   - Render: Dashboard → Logs
   - Heroku: `heroku logs --tail`

2. 常见错误：
   - **ModuleNotFoundError**: 检查 `requirements.txt`
   - **Port already in use**: 确保使用环境变量 `PORT`
   - **File not found**: 检查文件路径

### 问题：网站无法访问

1. 检查 URL 是否正确
2. 检查环境变量配置
3. 查看部署日志

### 问题：图片无法显示

1. 确保 `bookshelf.jpg` 已上传
2. 检查文件路径
3. 检查静态文件配置

## 推荐配置

对于生产环境，建议：

1. **使用 Railway 或 Render**（免费且简单）
2. **配置环境变量**：
   ```
   FLASK_DEBUG=False
   PORT=5000
   ```
3. **使用数据库**存储书籍数据（可选）
4. **使用 CDN** 加速静态文件（可选）

## 支持

如有问题，请查看：
- Railway 文档: https://docs.railway.app
- Render 文档: https://render.com/docs
- Heroku 文档: https://devcenter.heroku.com

