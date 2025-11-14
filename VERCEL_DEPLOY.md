# Vercel 部署指南

## Vercel 部署步骤

### 1. 安装 Vercel CLI（如果还没有）

```bash
npm i -g vercel
```

### 2. 登录 Vercel

```bash
vercel login
```

### 3. 在项目目录中部署

```bash
cd /Users/zhouyinyin/Downloads/booksearch1
vercel
```

按照提示操作：
- 选择项目范围（个人或团队）
- 确认项目名称
- 确认配置

### 4. 生产环境部署

```bash
vercel --prod
```

## 通过 GitHub 自动部署

### 1. 推送代码到 GitHub

```bash
git add .
git commit -m "准备 Vercel 部署"
git push
```

### 2. 在 Vercel Dashboard 连接仓库

1. 访问 https://vercel.com/dashboard
2. 点击 "Add New Project"
3. 导入你的 GitHub 仓库
4. Vercel 会自动检测配置并部署

## Vercel 配置说明

### 文件结构

```
booksearch/
├── api/
│   └── index.py          # Vercel Serverless Function 入口
├── app.py                # Flask 应用
├── vercel.json           # Vercel 配置文件
└── ...
```

### vercel.json 配置

- `builds`: 指定构建配置，使用 `@vercel/python`
- `routes`: 路由配置，所有请求转发到 `api/index.py`
- `functions`: 函数配置，设置最大执行时间（30秒）

## 重要注意事项

### 1. 文件大小限制

Vercel 对 Serverless Functions 有大小限制：
- 函数代码：最大 50MB
- 请求/响应：最大 4.5MB

如果遇到问题，可能需要：
- 优化图片大小
- 使用外部存储（如 Cloudinary）存储图片

### 2. 执行时间限制

- Hobby 计划：10秒
- Pro 计划：60秒
- 已配置为 30秒（需要 Pro 计划）

如果使用免费计划，可能需要优化代码或升级。

### 3. 静态文件

静态文件（CSS、JS、图片）会自动从 `static/` 目录提供。

### 4. 环境变量

在 Vercel Dashboard → Settings → Environment Variables 中设置：
- `FLASK_DEBUG=False`

### 5. 图片上传

由于 Vercel 是无服务器架构，文件写入可能不会持久化。建议：
- 使用外部存储服务（AWS S3、Cloudinary）
- 或使用数据库存储书籍数据

## 故障排除

### 问题：部署失败

1. **检查日志**
   ```bash
   vercel logs
   ```

2. **常见错误**
   - **ModuleNotFoundError**: 检查 `requirements.txt`
   - **Timeout**: 优化代码或升级计划
   - **File too large**: 优化依赖或使用外部存储

### 问题：路由不工作

确保 `vercel.json` 配置正确：
```json
{
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### 问题：静态文件无法访问

确保静态文件在 `static/` 目录，Vercel 会自动处理。

## 优化建议

### 1. 使用外部存储

对于生产环境，建议使用：
- **图片存储**: Cloudinary、AWS S3
- **数据库**: Vercel Postgres、MongoDB Atlas

### 2. 优化依赖

移除不必要的依赖以减少函数大小：
```bash
pip install --upgrade pip
pip install --target . --upgrade -r requirements.txt
```

### 3. 使用 Edge Functions（可选）

对于简单路由，可以使用 Vercel Edge Functions 提高性能。

## 与 Railway/Render 对比

| 特性 | Vercel | Railway | Render |
|------|--------|---------|--------|
| 免费额度 | ✅ 有 | ✅ 有 | ✅ 有 |
| Python 支持 | ⚠️ Serverless | ✅ 完整 | ✅ 完整 |
| 文件存储 | ❌ 临时 | ✅ 持久化 | ✅ 持久化 |
| 执行时间 | ⚠️ 有限制 | ✅ 无限制 | ✅ 无限制 |
| 部署速度 | ⚡ 很快 | 🚀 快 | 🚀 快 |

**建议**: 如果项目需要文件持久化存储，Railway 或 Render 可能更适合。

## 快速命令参考

```bash
# 部署到预览环境
vercel

# 部署到生产环境
vercel --prod

# 查看部署日志
vercel logs

# 查看部署列表
vercel ls

# 删除部署
vercel remove
```

## 下一步

1. ✅ 代码已准备好
2. 📤 推送到 GitHub
3. 🔗 在 Vercel 连接仓库
4. 🚀 自动部署
5. 📸 上传书架图片（可能需要外部存储）

享受你的部署！🎉

