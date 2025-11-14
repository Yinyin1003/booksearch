# GitHub Pages 部署指南

## ⚠️ 重要说明

**GitHub Pages 只支持静态网站**，无法运行 Flask 后端。

本项目需要：
- ✅ Flask 后端（API）
- ✅ 图片处理（OpenCV）
- ✅ 文件存储

## 🎯 解决方案

### 方案 1: 前端 GitHub Pages + 后端独立部署（推荐）

将前端部署到 GitHub Pages，后端部署到其他免费服务。

#### 步骤：

1. **部署后端到 Railway/Render**
   - 按照 `DEPLOY.md` 的说明部署 Flask 后端
   - 获取后端 URL，例如：`https://booksearch-api.railway.app`

2. **修改前端 API 地址**
   - 在 `static/js/app.js` 中修改 API 基础 URL
   - 指向你的后端服务

3. **部署前端到 GitHub Pages**
   - 创建 `docs/` 目录
   - 复制前端文件
   - 配置 GitHub Pages

### 方案 2: 使用 GitHub Actions 自动部署

使用 GitHub Actions 自动将项目部署到其他平台（Railway/Render）。

### 方案 3: 纯静态版本（功能受限）

创建一个纯前端的静态版本，但功能会受限（无法保存数据、无法处理图片）。

## 📋 方案 1 详细步骤

### 1. 准备前端文件

创建 `docs/` 目录并复制前端文件：

```bash
mkdir -p docs
cp -r static docs/
cp -r templates docs/
cp bookshelf.jpg docs/  # 如果需要
```

### 2. 修改 API 地址

在 `docs/static/js/app.js` 中，将所有 API 调用改为指向后端：

```javascript
// 修改 API 基础 URL
const API_BASE_URL = 'https://your-backend-url.railway.app';

// 修改所有 fetch 调用
fetch(`${API_BASE_URL}/api/books`)
```

### 3. 配置 GitHub Pages

1. 在 GitHub 仓库设置中：
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: main
   - Folder: /docs

2. 访问：`https://你的用户名.github.io/booksearch/`

## 🚀 方案 2: GitHub Actions 自动部署

创建 `.github/workflows/deploy.yml` 自动部署到 Railway。

## 💡 推荐方案

**最简单**：使用 Railway 部署完整应用（前端+后端）
- 一键部署
- 免费
- 不需要分离前后端

**如果一定要用 GitHub Pages**：使用方案 1（前端 GitHub Pages + 后端 Railway）

---

详细步骤请查看下面的文件。

