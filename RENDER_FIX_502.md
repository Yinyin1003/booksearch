# Render 502 Bad Gateway 修复指南

## 问题原因

502 Bad Gateway 通常由以下原因引起：
1. Gunicorn 超时设置太短
2. Worker 进程崩溃
3. 端口绑定配置错误
4. 内存不足

## 解决方案

### 方案 1: 更新 Start Command（推荐）

在 Render Dashboard → Settings → Start Command 中更新为：

```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2 --worker-class sync
```

**参数说明**：
- `--bind 0.0.0.0:$PORT`: 绑定到所有网络接口
- `--timeout 120`: 超时时间 120 秒（处理图片生成等耗时操作）
- `--workers 2`: 使用 2 个 worker 进程
- `--worker-class sync`: 使用同步 worker（适合 I/O 密集型任务）

### 方案 2: 使用配置文件

1. **更新 Start Command**：
```
gunicorn app:app -c gunicorn_config.py
```

2. **配置文件已创建**：`gunicorn_config.py`
   - 已包含超时设置（120秒）
   - 已配置 worker 数量
   - 已设置日志输出

### 方案 3: 简化配置（如果方案1和2都不行）

使用最简单的配置：

```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1
```

**注意**：单 worker 模式适合免费计划，但性能较低。

## 检查清单

### ✅ 1. 确认 Start Command 正确

确保 Start Command 包含：
- ✅ `--bind 0.0.0.0:$PORT`（不是 localhost）
- ✅ `--timeout 120` 或更长
- ✅ `--workers 2`（免费计划建议 1-2 个）

### ✅ 2. 检查环境变量

在 Render Dashboard → Environment 中确认：
- `PORT` 环境变量（Render 会自动设置，通常不需要手动添加）
- `FLASK_DEBUG=False`（生产环境）

### ✅ 3. 查看日志

在 Render Dashboard → Logs 中查看：
- 是否有错误信息
- Worker 是否正常启动
- 是否有超时警告

### ✅ 4. 检查依赖

确保 `requirements.txt` 包含：
```
gunicorn>=20.1.0
```

## 常见错误和解决方案

### 错误 1: WORKER TIMEOUT

**原因**：处理请求时间超过默认超时（30秒）

**解决**：增加超时时间
```
--timeout 120
```

### 错误 2: Connection reset by peer

**原因**：Worker 进程崩溃

**解决**：
1. 减少 worker 数量：`--workers 1`
2. 增加超时：`--timeout 300`
3. 检查代码是否有内存泄漏

### 错误 3: Address already in use

**原因**：端口绑定错误

**解决**：确保使用 `$PORT` 环境变量
```
--bind 0.0.0.0:$PORT
```

### 错误 4: ModuleNotFoundError

**原因**：依赖未安装

**解决**：
1. 检查 `requirements.txt`
2. 查看构建日志
3. 确保所有依赖都已列出

## 推荐的 Start Command 配置

### 免费计划（Free Tier）

```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1 --worker-class sync --log-level info
```

### 付费计划（Starter/Standard）

```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2 --worker-class sync --log-level info --max-requests 1000 --max-requests-jitter 100
```

## 测试步骤

1. **更新 Start Command**
   - 在 Render Dashboard → Settings 中更新
   - 保存更改

2. **手动重新部署**
   - 点击 "Manual Deploy" → "Deploy latest commit"
   - 或推送新代码触发自动部署

3. **查看日志**
   - 等待部署完成
   - 查看 Logs 确认没有错误

4. **测试网站**
   - 访问提供的 URL
   - 测试各个功能

## 如果问题仍然存在

1. **检查应用代码**
   - 确保 `app.py` 中没有阻塞操作
   - 检查图片处理是否超时

2. **联系 Render 支持**
   - 提供错误日志
   - 说明已尝试的解决方案

3. **考虑其他平台**
   - Railway（更简单）
   - Render 付费计划（更多资源）

## 快速修复命令

复制以下命令到 Render 的 Start Command：

```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2 --worker-class sync --log-level info
```

保存后重新部署即可。

