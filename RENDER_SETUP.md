# Render 部署配置指南

## Render 配置步骤

### 1. 基本配置

在 Render Dashboard 创建 Web Service 时，需要填写以下信息：

#### **Name**（服务名称）
```
booksearch
```
或你喜欢的任何名字

#### **Environment**（环境）
```
Python 3
```

#### **Build Command**（构建命令）
```
pip install -r requirements.txt
```

#### **Start Command**（启动命令）⭐ **重要**
```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2 --worker-class sync
```

**参数说明**：
- `--timeout 120`: 超时时间 120 秒（处理图片生成等耗时操作）
- `--workers 2`: 使用 2 个 worker 进程
- `--worker-class sync`: 使用同步 worker

**注意**：
- `app:app` 第一个 `app` 是文件名（app.py），第二个 `app` 是 Flask 应用对象名
- `$PORT` 是 Render 自动提供的环境变量，不要修改
- 如果显示错误，确保没有 `$` 符号前的空格

### 2. 环境变量配置

在 Render Dashboard → Environment 中添加：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PORT` | `10000` | Render 默认端口（可选，Render 会自动设置） |
| `FLASK_DEBUG` | `False` | 生产环境关闭调试模式 |

**注意**：`PORT` 环境变量 Render 会自动设置，通常不需要手动添加。

### 3. 实例类型

- **Free**: 免费计划（适合测试）
- **Starter**: $7/月（适合小型项目）
- **Standard**: $25/月（适合生产环境）

### 4. 自动部署

- ✅ **Auto-Deploy**: 勾选此选项，每次推送到 GitHub 会自动重新部署

## 完整配置示例

### 创建 Web Service 时的配置

```
Name: booksearch
Environment: Python 3
Region: Singapore (或选择离你最近的)
Branch: main
Root Directory: . (留空或填 .)
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
Instance Type: Free
```

### 环境变量（可选）

```
FLASK_DEBUG=False
```

## 常见问题

### Q: Start Command 显示 "Required" 错误？

**A**: 确保填写了正确的命令：
```
gunicorn app:app --bind 0.0.0.0:$PORT
```

**检查清单**：
- ✅ 命令中没有多余的空格
- ✅ `app:app` 正确（第一个是文件名，第二个是应用对象）
- ✅ `$PORT` 前面有 `$` 符号
- ✅ 没有使用引号包裹整个命令

### Q: 部署后无法访问？

**A**: 检查：
1. 部署日志是否有错误
2. Start Command 是否正确
3. 端口是否正确（Render 会自动设置 PORT）

### Q: 构建失败？

**A**: 检查：
1. `requirements.txt` 是否包含所有依赖
2. Python 版本是否兼容（Render 默认使用 Python 3.7+）
3. 查看构建日志中的具体错误

### Q: 静态文件无法加载？

**A**: 确保：
1. `static/` 目录存在
2. Flask 的静态文件配置正确（默认已配置）
3. 文件路径正确

## 验证部署

部署成功后：

1. **访问网站**
   - Render 会提供一个 URL，例如：`https://booksearch.onrender.com`
   - 访问此 URL 测试

2. **检查日志**
   - 在 Render Dashboard → Logs 查看实时日志
   - 确认没有错误信息

3. **测试功能**
   - 访问主页：`https://your-app.onrender.com/`
   - 访问预览页：`https://your-app.onrender.com/preview`
   - 测试图片上传和书籍搜索

## 下一步

部署成功后：
1. ✅ 上传书架图片（通过 Web 界面或 Git）
2. ✅ 配置书籍位置
3. ✅ 测试语音搜索功能

## 参考

- Render 文档: https://render.com/docs
- Gunicorn 文档: https://gunicorn.org/

