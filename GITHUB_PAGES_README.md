# GitHub Pages 部署完整指南

## 📋 方案概述

由于 GitHub Pages 只支持静态网站，我们需要：
- **前端**：部署到 GitHub Pages（免费）
- **后端**：部署到 Railway/Render（免费）

## 🎯 完整步骤

### 第一步：部署后端 API

#### 选项 A: Railway（推荐）

1. 访问 https://railway.app
2. 使用 GitHub 登录
3. New Project → Deploy from GitHub repo
4. 选择你的仓库
5. 等待自动部署
6. 复制部署 URL，例如：`https://booksearch-api.railway.app`

#### 选项 B: Render

1. 访问 https://render.com
2. 使用 GitHub 登录
3. New → Web Service
4. 连接仓库
5. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1`
6. 部署后复制 URL

### 第二步：准备前端文件

```bash
# 运行脚本
./setup_github_pages.sh

# 或手动执行
mkdir -p docs
cp -r static docs/
cp templates/index.html docs/index.html
cp bookshelf.jpg docs/  # 如果有
```

### 第三步：配置 API 地址

编辑 `docs/static/js/config.js`：

```javascript
backendUrl: 'https://your-backend-url.railway.app',  // 改为你的后端地址
```

### 第四步：修改 HTML 引用

确保 `docs/index.html` 中引用了配置文件和 JS：

```html
<head>
    ...
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    ...
    <script src="static/js/config.js"></script>
    <script src="static/js/app.js"></script>
</body>
```

### 第五步：提交并推送

```bash
git add docs/
git commit -m "Add GitHub Pages deployment"
git push
```

### 第六步：启用 GitHub Pages

1. GitHub 仓库 → **Settings**
2. 左侧菜单 → **Pages**
3. **Source**: Deploy from a branch
4. **Branch**: main
5. **Folder**: /docs
6. 点击 **Save**

### 第七步：等待部署

- 等待 1-2 分钟
- 访问：`https://你的用户名.github.io/booksearch/`

## 🔧 配置说明

### API 配置（config.js）

```javascript
const API_CONFIG = {
    isGitHubPages: window.location.hostname.includes('github.io'),
    backendUrl: 'https://your-backend-url.railway.app',
    getBaseUrl: function() {
        return this.isGitHubPages ? this.backendUrl : '';
    }
};
```

### CORS 配置（后端已添加）

后端 `app.py` 已添加 CORS 支持，允许 GitHub Pages 访问 API。

## ✅ 检查清单

- [ ] 后端已部署并获取 URL
- [ ] `docs/` 目录已创建
- [ ] 前端文件已复制到 `docs/`
- [ ] `config.js` 中的后端 URL 已更新
- [ ] HTML 文件引用了正确的 JS 文件
- [ ] 代码已提交到 GitHub
- [ ] GitHub Pages 已启用
- [ ] 网站可以访问

## 🐛 常见问题

### Q: API 请求失败（CORS 错误）

**A**: 确保后端 `app.py` 中已添加 `flask-cors` 并启用 CORS。

### Q: 图片无法显示

**A**: 确保 `bookshelf.jpg` 在 `docs/` 目录中。

### Q: 功能不工作

**A**: 
1. 打开浏览器 Console（F12）
2. 查看错误信息
3. 检查 API 地址是否正确

### Q: GitHub Pages 显示 404

**A**: 
1. 确保 `docs/` 目录存在
2. 确保 GitHub Pages 设置正确（Source: /docs）
3. 等待几分钟让 GitHub 部署

## 💡 推荐方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **GitHub Pages + Railway** | 前端免费，后端免费 | 需要配置两个服务 |
| **Railway 完整部署** | 一键部署，简单 | 需要 Railway 账号 |

**建议**：如果只是想快速上线，直接用 Railway 部署完整应用更简单！

## 📚 相关文档

- `DEPLOY.md` - 完整部署指南
- `SETUP_GITHUB.md` - GitHub 设置步骤
- `RENDER_SETUP.md` - Render 配置

---

**需要帮助？** 查看浏览器 Console 的错误信息，或检查后端日志。

