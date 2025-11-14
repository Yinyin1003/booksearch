# GitHub Pages 快速部署指南

## ⚠️ 重要说明

**GitHub Pages 只支持静态网站**，无法运行 Flask 后端。

你需要：
1. ✅ 前端部署到 GitHub Pages
2. ✅ 后端部署到 Railway/Render（免费）

## 🚀 快速步骤

### 步骤 1: 部署后端

1. **部署到 Railway**（推荐，最简单）
   - 访问 https://railway.app
   - 连接 GitHub 仓库
   - 自动部署
   - 获取后端 URL，例如：`https://booksearch-api.railway.app`

### 步骤 2: 准备前端文件

运行脚本：

```bash
./setup_github_pages.sh
```

或手动：

```bash
mkdir -p docs
cp -r static docs/
cp templates/index.html docs/
cp bookshelf.jpg docs/  # 如果有
```

### 步骤 3: 修改 API 地址

编辑 `docs/static/js/config.js`：

```javascript
backendUrl: 'https://your-backend-url.railway.app',  // 改为你的后端地址
```

### 步骤 4: 修改 HTML 文件

编辑 `docs/index.html`，在 `</head>` 之前添加：

```html
<script src="static/js/config.js"></script>
<script src="static/js/app.js"></script>
```

### 步骤 5: 提交到 GitHub

```bash
git add docs/
git commit -m "Add GitHub Pages files"
git push
```

### 步骤 6: 启用 GitHub Pages

1. GitHub 仓库 → Settings → Pages
2. Source: Deploy from a branch
3. Branch: main
4. Folder: /docs
5. Save

### 步骤 7: 访问

等待几分钟，访问：
```
https://你的用户名.github.io/booksearch/
```

## 📝 注意事项

1. **API 地址**：确保 `config.js` 中的后端 URL 正确
2. **CORS**：后端需要允许 GitHub Pages 域名的跨域请求
3. **HTTPS**：GitHub Pages 使用 HTTPS，后端也需要 HTTPS

## 🔧 如果遇到问题

### 问题 1: API 请求失败（CORS 错误）

在后端 `app.py` 中添加 CORS 支持：

```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### 问题 2: 图片无法显示

确保 `bookshelf.jpg` 在 `docs/` 目录中。

### 问题 3: 功能不工作

检查浏览器 Console（F12）查看错误信息。

## 💡 更简单的方案

**如果只是想快速上线**，建议直接使用 Railway 部署完整应用：
- ✅ 一键部署
- ✅ 前端+后端都在一个服务
- ✅ 不需要分离配置

详细步骤请查看 `DEPLOY.md`。

