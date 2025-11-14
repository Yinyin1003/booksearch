# Render 502 错误完整修复指南

## 🔍 问题诊断

502 Bad Gateway 通常表示：
1. ✅ Gunicorn 启动失败
2. ✅ 应用崩溃
3. ✅ 超时设置太短
4. ✅ 端口绑定错误

## 🚀 立即修复方案

### 方案 1: 最简单的配置（推荐先试这个）

在 Render Dashboard → Settings → Start Command：

```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --worker-class sync --log-level info --access-logfile - --error-logfile -
```

**为什么这个配置**：
- `--timeout 300`: 5分钟超时（足够处理图片生成）
- `--workers 1`: 单 worker（免费计划更稳定）
- `--log-level info`: 详细日志
- `--access-logfile -`: 输出访问日志到 stdout
- `--error-logfile -`: 输出错误日志到 stdout（方便在 Render 查看）

### 方案 2: 使用配置文件

Start Command：
```
gunicorn app:app -c gunicorn_config.py
```

### 方案 3: 如果还是不行，尝试这个

Start Command：
```
python3 -m gunicorn app:app --bind 0.0.0.0:$PORT --timeout 600 --workers 1 --worker-class sync --preload
```

## 📋 完整检查清单

### ✅ 1. Start Command 检查

确保包含以下所有部分：
- [ ] `gunicorn` 命令
- [ ] `app:app`（第一个是文件名，第二个是应用对象）
- [ ] `--bind 0.0.0.0:$PORT`（注意是 `0.0.0.0` 不是 `localhost`）
- [ ] `--timeout 300` 或更长
- [ ] `--workers 1`（免费计划）
- [ ] `--log-level info`（方便调试）

### ✅ 2. 环境变量检查

在 Render Dashboard → Environment Variables：
- [ ] `FLASK_DEBUG=False`（生产环境）
- [ ] `PYTHONUNBUFFERED=1`（确保日志实时输出）

### ✅ 3. 文件检查

确保以下文件存在：
- [ ] `app.py`（Flask 应用）
- [ ] `requirements.txt`（包含 gunicorn）
- [ ] `static/` 目录（静态文件）
- [ ] `templates/` 目录（HTML 模板）

### ✅ 4. 依赖检查

确保 `requirements.txt` 包含：
```
gunicorn>=20.1.0
Flask>=2.0.0
```

## 🔧 逐步调试

### 步骤 1: 查看日志

1. 在 Render Dashboard → Logs
2. 查看最新的错误信息
3. 寻找以下关键词：
   - `ERROR`
   - `CRITICAL`
   - `WORKER TIMEOUT`
   - `ModuleNotFoundError`
   - `ImportError`

### 步骤 2: 测试本地运行

在本地测试 Gunicorn 是否能正常启动：

```bash
# 安装依赖
pip install -r requirements.txt

# 测试 Gunicorn
gunicorn app:app --bind 0.0.0.0:5001 --timeout 300 --workers 1 --log-level info

# 访问 http://localhost:5001 测试
```

如果本地可以运行，问题可能在 Render 配置。

### 步骤 3: 简化应用测试

创建一个简单的测试文件 `test_app.py`：

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

Start Command 改为：
```
gunicorn test_app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1
```

如果这个可以工作，说明问题在你的应用代码。

## 🐛 常见错误和解决方案

### 错误 1: ModuleNotFoundError: No module named 'gunicorn'

**解决**：确保 `requirements.txt` 包含 `gunicorn>=20.1.0`

### 错误 2: [CRITICAL] WORKER TIMEOUT

**解决**：增加超时时间
```
--timeout 600
```

### 错误 3: Address already in use

**解决**：确保使用 `$PORT` 环境变量
```
--bind 0.0.0.0:$PORT
```

### 错误 4: ImportError: cannot import name 'app'

**解决**：检查 `app.py` 中 Flask 应用对象名是否为 `app`

### 错误 5: 应用启动但立即崩溃

**解决**：
1. 查看日志中的具体错误
2. 检查是否有未捕获的异常
3. 确保所有依赖都已安装

## 📝 推荐的完整配置

### Start Command（复制这个）

```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --worker-class sync --log-level info --access-logfile - --error-logfile - --preload
```

### 环境变量

```
FLASK_DEBUG=False
PYTHONUNBUFFERED=1
```

### Build Command

```
pip install -r requirements.txt
```

## 🔄 重新部署步骤

1. **更新 Start Command**
   - Render Dashboard → Settings
   - 更新 Start Command
   - 保存

2. **手动重新部署**
   - 点击 "Manual Deploy"
   - 选择 "Deploy latest commit"
   - 等待部署完成

3. **查看日志**
   - 等待 2-3 分钟
   - 查看 Logs 确认没有错误
   - 如果看到 "Booting worker" 说明启动成功

4. **测试访问**
   - 访问提供的 URL
   - 如果还是 502，查看日志中的具体错误

## 💡 如果所有方法都不行

### 选项 1: 使用 Railway（更简单）

Railway 对 Python 应用支持更好：
1. 访问 https://railway.app
2. 连接 GitHub 仓库
3. 自动部署（不需要配置 Start Command）

### 选项 2: 联系 Render 支持

提供以下信息：
- 错误日志截图
- Start Command 配置
- 已尝试的解决方案

### 选项 3: 检查应用代码

可能的问题：
- 应用启动时有阻塞操作
- 导入错误
- 内存不足

## 🎯 快速修复命令（复制使用）

**最简单可靠**：
```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --worker-class sync --log-level info
```

**带详细日志**：
```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --worker-class sync --log-level debug --access-logfile - --error-logfile -
```

**使用配置文件**：
```
gunicorn app:app -c gunicorn_config.py
```

---

**重要**：更新 Start Command 后，一定要手动重新部署才能生效！

